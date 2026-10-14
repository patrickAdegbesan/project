"""Runs two Telegram connections side by side.

* ``user`` - logged in as YOU. Reads every chat you're in (no admin, no bot in
  the group). The only thing it ever sends is the auto-replies you wrote.
* ``bot``  - your own private bot from @BotFather. It sends you the alerts (so
  your phone actually rings) and takes your commands (/add, /list, ...).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from telethon import Button, TelegramClient, events, errors, utils
from telethon.sessions import StringSession
from telethon.tl import functions, types

from .autoreply import AutoReplier, Incoming, RuleMatcher, SendBlocked, SlowDown, load_rules
from .core import (
    BOT_COMMANDS,
    AlertDeduper,
    ChatInfo,
    Commands,
    format_alert,
    should_watch,
    split_message,
)
from .kinds import CHANNEL, DM, GROUP
from .matcher import Matcher
from .storage import Store

log = logging.getLogger("kwalert")

# After a restart, missed messages are caught up for alerts, but questions
# older than this are not auto-answered (someone has probably replied already).
AUTOREPLY_MAX_AGE = dt.timedelta(minutes=15)


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
    bot.parse_mode = "html"  # so message.text round-trips when editing Send/Skip prompts

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

    async def notify(text: str, buttons=None) -> None:
        try:
            parts = split_message(text)
            for i, part in enumerate(parts):
                await bot.send_message(
                    owner_id, part, parse_mode="html", link_preview=False,
                    buttons=buttons if i == len(parts) - 1 else None,
                )
        except (ValueError, errors.PeerIdInvalidError, errors.UserIsBlockedError):
            log.warning(
                "Can't message you yet. Open @%s in Telegram and press START.",
                bot_me.username,
            )

    async def send_as_you(target, text: str, reply_to: int | None) -> None:
        """Send an auto-reply from your account, translating Telegram's refusals."""
        try:
            await user.send_message(target, text, reply_to=reply_to, link_preview=False)
        except (errors.FloodWaitError, errors.PeerFloodError) as exc:
            raise SlowDown(str(exc)) from exc
        except (
            errors.ChatWriteForbiddenError,
            errors.ChatAdminRequiredError,
            errors.ChatRestrictedError,
            errors.UserBannedInChannelError,
            errors.SlowModeWaitError,
            errors.ChatSendPlainForbiddenError,
            errors.UserIsBlockedError,
            errors.ForbiddenError,  # any other "you may not post here"
        ) as exc:
            raise SendBlocked(str(exc)) from exc

    async def ask_approval(pid: int, text: str) -> None:
        await notify(
            text,
            buttons=[[Button.inline("✅ Send", f"ar:s:{pid}"), Button.inline("Skip", f"ar:k:{pid}")]],
        )

    replier = AutoReplier(store, RuleMatcher(load_rules(store)), send_as_you, notify, ask_approval)
    commands = Commands(store, matcher, list_chats, replier)

    async def maybe_autoreply(event) -> None:
        if event.chat_id == bot_me.id or not event.raw_text:
            return
        if dt.datetime.now(dt.timezone.utc) - event.date > AUTOREPLY_MAX_AGE:
            return
        sender = await event.get_sender()
        # Only answer real people: not bots, not anonymous admins or channels.
        if not isinstance(sender, types.User) or sender.bot or sender.is_self:
            return
        chat = await event.get_chat()
        await replier.on_message(
            Incoming(
                chat_id=event.chat_id,
                chat_kind=chat_kind(event),
                chat_title=utils.get_display_name(chat) or "Unknown chat",
                msg_id=event.id,
                text=event.raw_text,
                sender_id=sender.id,
                sender_name=utils.get_display_name(sender) or "Someone",
                sender_is_contact=bool(sender.contact),
                chat_ref=await event.get_input_chat(),
                sender_ref=await event.get_input_sender(),
            )
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
        try:
            await maybe_autoreply(event)
        except Exception:
            log.exception("Failed to auto-reply")

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

    @bot.on(events.CallbackQuery(pattern=rb"^ar:"))
    async def _approval(event):
        if event.sender_id != owner_id:
            await event.answer()
            return
        m = re.match(rb"^ar:([sk]):(\d+)$", event.data)
        if not m:
            await event.answer()
            return
        pid = int(m.group(2))
        original = (await event.get_message()).text or ""
        gone = "⌛ Already handled, or expired because the program restarted."
        if m.group(1) == b"s":
            await event.answer("Sending…")
            sent = await replier.approve(pid)
            outcome = gone if sent is None else ("✅ Sent" if sent else "❌ Not sent (see the message above)")
        else:
            done = replier.skip(pid)
            await event.answer("Skipped")
            outcome = "⏭ Skipped" if done else gone
        await event.edit(f"{original}\n\n<b>{outcome}</b>", parse_mode="html", buttons=None)

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

    n, r = len(store.keywords()), len(store.rules())
    await notify(
        "✅ <b>Keyword alerts are running.</b>\n"
        + (f"Watching for {n} keyword(s). /list to see them."
           if n else "You have no keywords yet. Add some, e.g. <code>/add school fees, result</code>")
        + "\n"
        + (f"{r} auto-reply rule(s), auto-replies {'on' if store.get_flag('autoreply') else 'OFF'}. /replies to see them."
           if r else "No auto-replies yet. Example: <code>/reply class + time => Class is 10am</code>")
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
