"""Runs two Telegram connections side by side.

* ``user`` - logged in as YOU. Reads every chat you're in (no admin, no bot in
  the group). It never sends anything into your groups.
* ``bot``  - your own private bot from @BotFather. It sends you the alerts (so
  your phone actually rings) and takes your commands (/add, /list, ...).
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from telethon import TelegramClient, events, errors, utils
from telethon.sessions import StringSession
from telethon.tl import functions, types

from .core import (
    BOT_COMMANDS,
    CHANNEL,
    DM,
    GROUP,
    AlertDeduper,
    ChatInfo,
    Commands,
    format_alert,
    should_watch,
    split_message,
)
from .matcher import Matcher
from .storage import Store

log = logging.getLogger("kwalert")


@dataclass
class Config:
    api_id: int
    api_hash: str
    bot_token: str
    data_dir: Path
    session_string: str | None


def load_config() -> Config:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    missing = [k for k in ("TG_API_ID", "TG_API_HASH", "TG_BOT_TOKEN") if not os.getenv(k)]
    if missing:
        sys.exit(
            "Missing settings: " + ", ".join(missing) + "\n"
            "Copy .env.example to .env and fill it in (see README.md)."
        )
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return Config(
        api_id=int(os.environ["TG_API_ID"]),
        api_hash=os.environ["TG_API_HASH"],
        bot_token=os.environ["TG_BOT_TOKEN"],
        data_dir=data_dir,
        session_string=os.getenv("TG_SESSION") or None,
    )


def make_user_client(cfg: Config) -> TelegramClient:
    session = (
        StringSession(cfg.session_string)
        if cfg.session_string
        else str(cfg.data_dir / "user")
    )
    # catch_up: after a restart, fetch messages that arrived while offline.
    return TelegramClient(session, cfg.api_id, cfg.api_hash, catch_up=True)


def chat_kind(event) -> str:
    if event.is_private:
        return DM
    if event.is_group:
        return GROUP
    return CHANNEL


def message_link(chat, chat_id: int, msg_id: int) -> str | None:
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{msg_id}"
    real_id, peer_type = utils.resolve_id(chat_id)
    if peer_type is types.PeerChannel:
        return f"https://t.me/c/{real_id}/{msg_id}"
    return None  # old-style small groups have no message links


async def run(cfg: Config) -> None:
    store = Store(cfg.data_dir / "kwalert.db")
    matcher = Matcher(store.keywords())
    deduper = AlertDeduper()

    user = make_user_client(cfg)
    bot = TelegramClient(str(cfg.data_dir / "bot"), cfg.api_id, cfg.api_hash)

    print("Logging in to your Telegram account (first time: enter phone + code)...")
    await user.start()
    await bot.start(bot_token=cfg.bot_token)

    me = await user.get_me()
    bot_me = await bot.get_me()
    owner_id = me.id
    log.info("Watching as %s; alerts via @%s", utils.get_display_name(me), bot_me.username)

    # Loading dialogs tells Telegram this client is active in every chat, so it
    # pushes their new messages (needed for big supergroups).
    await user.get_dialogs()

    async def list_chats() -> list[ChatInfo]:
        chats = []
        async for d in user.iter_dialogs():
            if d.is_group:
                kind = GROUP
            elif d.is_channel:
                kind = CHANNEL
            elif d.is_user and d.id not in (owner_id, bot_me.id):
                kind = DM
            else:
                continue
            chats.append(ChatInfo(d.id, d.name or "Untitled", kind))
        return chats

    commands = Commands(store, matcher, list_chats)

    async def notify(text: str) -> None:
        try:
            for part in split_message(text):
                await bot.send_message(owner_id, part, parse_mode="html", link_preview=False)
        except (ValueError, errors.PeerIdInvalidError, errors.UserIsBlockedError):
            log.warning(
                "Can't message you yet. Open @%s in Telegram and press START.",
                bot_me.username,
            )

    async def on_message(event, edited: bool = False) -> None:
        if event.chat_id == bot_me.id:
            return  # never alert on the alert bot's own chat
        if not should_watch(store, event.chat_id, chat_kind(event)):
            return
        text = event.raw_text or ""
        matches = matcher.find(text)
        if not matches:
            return
        fresh = deduper.fresh(event.chat_id, event.id, matches)
        if not fresh:
            return
        chat = await event.get_chat()
        sender = await event.get_sender()
        alert = format_alert(
            chat_title=utils.get_display_name(chat) or "Unknown chat",
            sender=utils.get_display_name(sender) if sender else None,
            text=text,
            matches=fresh,
            link=message_link(chat, event.chat_id, event.id),
            edited=edited,
        )
        await notify(alert)

    # incoming=True skips messages you send yourself.
    @user.on(events.NewMessage(incoming=True))
    async def _new(event):
        try:
            await on_message(event)
        except Exception:
            log.exception("Failed to process a message")

    @user.on(events.MessageEdited(incoming=True))
    async def _edited(event):
        try:
            await on_message(event, edited=True)
        except Exception:
            log.exception("Failed to process an edited message")

    @bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def _command(event):
        if event.sender_id != owner_id:
            return  # the bot only listens to you
        try:
            reply = await commands.handle(event.raw_text or "")
        except Exception:
            log.exception("Command failed")
            reply = "Something went wrong running that command. Check the logs."
        if reply:
            for part in split_message(reply):
                await event.respond(part, parse_mode="html", link_preview=False)

    try:
        await bot(
            functions.bots.SetBotCommandsRequest(
                scope=types.BotCommandScopeDefault(),
                lang_code="",
                commands=[types.BotCommand(c, d) for c, d in BOT_COMMANDS],
            )
        )
    except Exception:
        log.warning("Could not set the bot's command menu (not critical).")

    n = len(store.keywords())
    await notify(
        "✅ <b>Keyword alerts are running.</b>\n"
        + (f"Watching for {n} keyword(s). /list to see them."
           if n else "You have no keywords yet. Add some, e.g. <code>/add school fees, result</code>")
    )
    print(f"Running. Open @{bot_me.username} in Telegram and send /help. Ctrl+C to stop.")

    await asyncio.gather(user.run_until_disconnected(), bot.run_until_disconnected())


async def print_session_string(cfg: Config) -> None:
    """Log in once on your own computer and print a session string, for hosts
    where you can't type the login code (Railway, Render, ...)."""
    client = TelegramClient(StringSession(), cfg.api_id, cfg.api_hash)
    await client.start()
    print("\nYour TG_SESSION value (keep it secret, it is a login to your account):\n")
    print(client.session.save())
    await client.disconnect()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.getLogger("telethon").setLevel(logging.WARNING)
    cfg = load_config()
    if "--session-string" in sys.argv[1:]:
        asyncio.run(print_session_string(cfg))
        return
    try:
        asyncio.run(run(cfg))
    except KeyboardInterrupt:
        print("\nStopped.")
