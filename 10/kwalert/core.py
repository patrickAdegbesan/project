"""Telegram-independent logic: which chats to watch, alert text, bot commands.

Kept separate from ``app.py`` so it can be tested without a Telegram login.
"""

from __future__ import annotations

import html
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Awaitable, Callable

from .autoreply import AutoReplier, RuleError, parse_rule
from .kinds import CHANNEL, DM, GROUP
from .matcher import REGEX, TEXT, Keyword, KeywordError, Match, Matcher, snippet
from .storage import Store


@dataclass(frozen=True)
class ChatInfo:
    chat_id: int
    title: str
    kind: str  # GROUP | CHANNEL | DM


ListChats = Callable[[], Awaitable[list[ChatInfo]]]


def should_watch(store: Store, chat_id: int, kind: str) -> bool:
    if store.get_flag("paused"):
        return False
    focused = store.chats("focused")
    if focused:
        # "Only these chats" is an explicit choice, so it beats the type switches.
        return chat_id in focused
    if kind == CHANNEL and not store.get_flag("channels"):
        return False
    if kind == DM and not store.get_flag("dms"):
        return False
    return store.chat_state(chat_id) != "muted"


class AlertDeduper:
    """Remembers which keywords were already alerted for each message.

    An edited message only alerts again for keywords that are new in the edit.
    """

    def __init__(self, capacity: int = 5000):
        self._seen: OrderedDict[tuple[int, int], set[Keyword]] = OrderedDict()
        self._capacity = capacity

    def fresh(self, chat_id: int, msg_id: int, matches: list[Match]) -> list[Match]:
        key = (chat_id, msg_id)
        seen = self._seen.pop(key, set())
        new = [m for m in matches if m.keyword not in seen]
        seen.update(m.keyword for m in matches)
        self._seen[key] = seen
        while len(self._seen) > self._capacity:
            self._seen.popitem(last=False)
        return new


def _e(text: str) -> str:
    return html.escape(text, quote=False)


def format_alert(
    chat_title: str,
    sender: str | None,
    text: str,
    matches: list[Match],
    link: str | None,
    edited: bool = False,
) -> str:
    labels = ", ".join(f"<b>{_e(m.keyword.label())}</b>" for m in matches)
    before, hit, after = snippet(text, matches[0])
    lines = [
        f"🔔 {labels}" + (" <i>(edited message)</i>" if edited else ""),
        f"💬 <b>{_e(chat_title)}</b>",
    ]
    if sender:
        lines.append(f"👤 {_e(sender)}")
    lines.append("")
    lines.append(f"{_e(before)}<b><u>{_e(hit)}</u></b>{_e(after)}")
    if link:
        lines.append("")
        lines.append(f'<a href="{html.escape(link)}">Open message</a>')
    return "\n".join(lines)


def split_message(text: str, limit: int = 4000) -> list[str]:
    """Split on line breaks so each part fits in one Telegram message."""
    parts, current = [], ""
    for line in text.split("\n"):
        while len(line) > limit:
            if current:
                parts.append(current)
                current = ""
            parts.append(line[:limit])
            line = line[limit:]
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            parts.append(current)
            current = line
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts or [""]


HELP = """<b>Keyword alerts &amp; auto-replies</b>
You choose every keyword and every reply. There are none until you add some.

<b>Keywords</b>
/add <i>word or phrase</i> — add one, or several separated by commas
   e.g. <code>/add school fees, result, account number</code>
   <code>*</code> means "any letters": <code>fee*</code> matches fee, fees
/regex <i>pattern</i> — add a regular expression
/remove <i>keyword</i> — remove one or several (commas)
/list — show your keywords
/clear yes — delete all keywords
/test <i>some text</i> — see which keywords would fire

<b>Auto-replies</b> (sent from your account, as you)
/reply <i>words</i> => <i>your answer</i> — add a reply rule
   e.g. <code>/reply class + time, lecture + time => Class is 10am in LT2</code>
   <code>+</code> means the message must contain ALL those words (any order);
   commas give alternatives.
/replies — list your reply rules
/delreply <i>number</i> — delete a rule
/editreply <i>number</i> => <i>new answer</i> — change a rule's answer
/testreply <i>some text</i> — see which rule would answer
/autoreply on|off — switch auto-replies on or off
/approve on|off — ask me before each reply (off = fully automatic)
/replyin chat|dm — reply in the chat where asked (default), or privately
   to people saved in your contacts (others still get it in the chat)
/cooldown <i>hours</i> — don't answer the same person the same rule again
   within this time (default 12)

<b>Chats</b>
/groups — numbered list of chats being watched
/mute <i>numbers</i> — ignore those chats (no alerts, no auto-replies) (e.g. <code>/mute 2 5</code>)
/unmute <i>numbers</i>
/only <i>numbers</i> — watch ONLY those chats
/only off — go back to watching all chats
/channels on|off — also watch channels (off by default)
/dms on|off — also watch private chats (off by default)

<b>General</b>
/pause, /resume — stop or restart all alerts and auto-replies
/status — current settings

Matching ignores capital letters and only matches whole words, so
<code>account</code> won't fire on "accountability". Your own messages are ignored.
Auto-replies never post in broadcast channels and each person gets a given
answer only once per cooldown."""

BOT_COMMANDS = [
    ("add", "Add keywords (comma-separated)"),
    ("remove", "Remove keywords"),
    ("list", "Show your keywords"),
    ("test", "Test text against your keywords"),
    ("reply", "Add an auto-reply: words => answer"),
    ("replies", "List auto-reply rules"),
    ("delreply", "Delete an auto-reply rule"),
    ("editreply", "Change an auto-reply's answer"),
    ("testreply", "Test text against reply rules"),
    ("autoreply", "Turn auto-replies on/off"),
    ("approve", "Ask me before each auto-reply"),
    ("groups", "List watched chats"),
    ("mute", "Mute chats by number"),
    ("unmute", "Unmute chats by number"),
    ("only", "Watch only these chats"),
    ("pause", "Pause alerts and auto-replies"),
    ("resume", "Resume alerts"),
    ("status", "Show settings"),
    ("help", "How to use this bot"),
]

_COMMAND_RE = re.compile(r"^/(\w+)(?:@\w+)?(?:\s+(.*))?$", re.DOTALL)


def _split_list(arg: str) -> list[str]:
    return [p.strip() for p in re.split(r"[,\n]", arg) if p.strip()]


def _numbers(arg: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", arg)]


def _on_off(arg: str) -> bool | None:
    word = arg.strip().lower()
    if word in ("on", "yes", "1", "true"):
        return True
    if word in ("off", "no", "0", "false"):
        return False
    return None


class Commands:
    """Turns a bot message from the owner into a reply (HTML)."""

    def __init__(
        self,
        store: Store,
        matcher: Matcher,
        list_chats: ListChats,
        replier: AutoReplier | None = None,
    ):
        self.store = store
        self.matcher = matcher
        self.list_chats = list_chats
        self.replier = replier

    def _reload(self) -> None:
        self.matcher.set_keywords(self.store.keywords())

    async def handle(self, text: str) -> str | None:
        m = _COMMAND_RE.match(text.strip())
        if not m:
            return "Send /help to see what I can do."
        cmd, arg = m.group(1).lower(), (m.group(2) or "").strip()
        handler = getattr(self, f"cmd_{cmd}", None)
        if handler is None:
            return f"Unknown command /{_e(cmd)}. Send /help."
        return await handler(arg)

    # --- keywords ---------------------------------------------------------

    async def cmd_start(self, arg: str) -> str:
        return HELP

    async def cmd_help(self, arg: str) -> str:
        return HELP

    async def cmd_add(self, arg: str) -> str:
        items = _split_list(arg)
        if not items:
            return "Usage: <code>/add school fees, result, account</code>"
        return self._add_many([Keyword(i, TEXT) for i in items])

    async def cmd_regex(self, arg: str) -> str:
        if not arg:
            return "Usage: <code>/regex \\bfees?\\b</code>"
        return self._add_many([Keyword(arg, REGEX)])

    def _add_many(self, keywords: list[Keyword]) -> str:
        lines = []
        for kw in keywords:
            try:
                added = self.store.add_keyword(kw)
            except KeywordError as exc:
                lines.append(f"❌ {_e(kw.label())}: {_e(str(exc))}")
                continue
            lines.append(f"{'✅ Added' if added else 'ℹ️ Already have'} {_e(kw.label())}")
        self._reload()
        return "\n".join(lines)

    async def cmd_remove(self, arg: str) -> str:
        items = _split_list(arg)
        if not items:
            return "Usage: <code>/remove school fees</code> (see /list)"
        lines = []
        for item in items:
            removed = self.store.remove_keyword(item)
            if removed:
                lines += [f"🗑 Removed {_e(k.label())}" for k in removed]
            else:
                lines.append(f"Not found: {_e(item)}")
        self._reload()
        return "\n".join(lines)

    async def cmd_delete(self, arg: str) -> str:
        return await self.cmd_remove(arg)

    async def cmd_list(self, arg: str) -> str:
        kws = self.store.keywords()
        if not kws:
            return "You have no keywords yet. Add some with /add."
        rows = [f"{i}. {_e(k.label())}" for i, k in enumerate(kws, 1)]
        return f"<b>Your keywords ({len(kws)})</b>\n" + "\n".join(rows)

    async def cmd_clear(self, arg: str) -> str:
        if arg.lower() != "yes":
            return "This deletes ALL keywords. Send <code>/clear yes</code> to confirm."
        n = self.store.clear_keywords()
        self._reload()
        return f"Deleted {n} keyword(s)."

    async def cmd_test(self, arg: str) -> str:
        if not arg:
            return "Usage: <code>/test School fees are due on Friday</code>"
        if not self.matcher.keywords:
            return "You have no keywords yet. Add some with /add."
        hits = self.matcher.find(arg)
        if not hits:
            return "No keyword matched."
        return "Would alert for: " + ", ".join(f"<b>{_e(h.keyword.label())}</b>" for h in hits)

    # --- auto-replies -----------------------------------------------------

    def _reload_rules(self) -> None:
        if self.replier:
            self.replier.reload()

    async def cmd_reply(self, arg: str) -> str:
        if not arg:
            return (
                "Usage: <code>/reply class + time => Class is 10am in LT2</code>\n"
                "Several triggers: <code>/reply class + time, lecture + start => ...</code>"
            )
        try:
            triggers, reply = parse_rule(arg)
        except RuleError as exc:
            return f"❌ {_e(str(exc))}"
        rule_id = self.store.add_rule(triggers, reply)
        self._reload_rules()
        lines = [f"✅ Added reply #{rule_id}", "When a message contains:"]
        lines += [f"  • {_e(t)}" for t in triggers]
        lines += ["I'll reply:", _e(reply)]
        if not self.store.get_flag("autoreply"):
            lines.append("\n⚠️ Auto-replies are off. Send <code>/autoreply on</code>.")
        return "\n".join(lines)

    async def cmd_replies(self, arg: str) -> str:
        rules = self.store.rules()
        if not rules:
            return "No auto-reply rules yet. Add one with /reply."
        blocks = []
        for rid, triggers, reply in rules:
            trig = "  |  ".join(_e(t) for t in triggers)
            blocks.append(f"<b>#{rid}</b>  {trig}\n→ {_e(reply)}")
        state = "on" if self.store.get_flag("autoreply") else "OFF"
        mode = "ask me first" if self.store.get_flag("approve") else "automatic"
        return f"<b>Auto-replies ({state}, {mode})</b>\n\n" + "\n\n".join(blocks)

    async def cmd_delreply(self, arg: str) -> str:
        nums = _numbers(arg)
        if not nums:
            return "Usage: <code>/delreply 2</code> (numbers from /replies)"
        lines = [
            f"🗑 Deleted reply #{n}" if self.store.delete_rule(n) else f"No reply #{n}"
            for n in nums
        ]
        self._reload_rules()
        return "\n".join(lines)

    async def cmd_editreply(self, arg: str) -> str:
        m = re.match(r"^#?(\d+)\s*=>\s*(.+)$", arg, re.DOTALL)
        if not m:
            return "Usage: <code>/editreply 2 => Class has moved to 11am</code>"
        rid, reply = int(m.group(1)), m.group(2).strip()
        if not self.store.update_rule_reply(rid, reply):
            return f"No reply #{rid}. See /replies."
        self._reload_rules()
        return f"✏️ Reply #{rid} now says:\n{_e(reply)}"

    async def cmd_testreply(self, arg: str) -> str:
        if not arg:
            return "Usage: <code>/testreply what time is class?</code>"
        if not self.replier or not self.replier.rules.rules:
            return "No auto-reply rules yet. Add one with /reply."
        rule = self.replier.rules.find(arg)
        if rule is None:
            return "No reply rule matched."
        return f"Reply #{rule.id} would answer:\n{_e(rule.reply)}"

    async def cmd_autoreply(self, arg: str) -> str:
        return await self._flag("autoreply", arg, "Auto-reply")

    async def cmd_approve(self, arg: str) -> str:
        on = _on_off(arg)
        if on is None:
            state = "on (I ask you first)" if self.store.get_flag("approve") else "off (fully automatic)"
            return f"Approval is {state}. Use <code>/approve on</code> or <code>/approve off</code>."
        self.store.set_flag("approve", on)
        if on:
            return "I'll ask you before sending each auto-reply, with Send / Skip buttons."
        return "Auto-replies are now sent automatically."

    async def cmd_replyin(self, arg: str) -> str:
        where = arg.strip().lower()
        if where not in ("chat", "dm"):
            current = self.store.get("reply_in")
            return (
                f"Replies currently go to: <b>{current}</b>.\n"
                "<code>/replyin chat</code> — reply to their message in the chat where they asked\n"
                "<code>/replyin dm</code> — message them privately if they're in your contacts "
                "(others still get the answer in the chat)"
            )
        self.store.set("reply_in", where)
        if where == "dm":
            return (
                "Replies will go privately to people in your contacts; everyone else gets "
                "the answer in the chat. (Private messages are limited to contacts so "
                "Telegram doesn't flag your account for messaging strangers.)"
            )
        return "Replies will go to the chat where the question was asked."

    async def cmd_cooldown(self, arg: str) -> str:
        try:
            hours = float(arg)
        except ValueError:
            return (
                f"Cooldown is {self.store.get('cooldown_hours')} hours. "
                "Usage: <code>/cooldown 24</code>"
            )
        if not 0 <= hours <= 24 * 30:
            return "Pick between 0 and 720 hours."
        self.store.set("cooldown_hours", f"{hours:g}")
        return f"The same person won't get the same answer again within {hours:g} hours."

    # --- chats ------------------------------------------------------------

    async def _chat_listing(self) -> list[ChatInfo]:
        chats = await self.list_chats()
        allowed = {GROUP}
        if self.store.get_flag("channels"):
            allowed.add(CHANNEL)
        if self.store.get_flag("dms"):
            allowed.add(DM)
        focused = self.store.chats("focused")
        # Focused chats always show, so they can be found and un-focused.
        chats = [c for c in chats if c.kind in allowed or c.chat_id in focused]
        return sorted(chats, key=lambda c: (c.title.casefold(), c.chat_id))

    async def cmd_groups(self, arg: str) -> str:
        chats = await self._chat_listing()
        if not chats:
            return "You're not in any groups that I can see."
        focused = self.store.chats("focused")
        rows = []
        for i, c in enumerate(chats, 1):
            if focused:
                mark = "🎯" if c.chat_id in focused else "⏸"
            else:
                mark = "🔇" if self.store.chat_state(c.chat_id) == "muted" else "✅"
            rows.append(f"{i}. {mark} {_e(c.title)}")
        legend = (
            "🎯 watched (only mode) · ⏸ not watched"
            if focused
            else "✅ watched · 🔇 muted"
        )
        return f"<b>Your chats</b>\n{legend}\n\n" + "\n".join(rows)

    async def cmd_chats(self, arg: str) -> str:
        return await self.cmd_groups(arg)

    async def _pick(self, arg: str) -> tuple[list[ChatInfo], list[int]]:
        chats = await self._chat_listing()
        picked, bad = [], []
        for n in _numbers(arg):
            if 1 <= n <= len(chats):
                picked.append(chats[n - 1])
            else:
                bad.append(n)
        return picked, bad

    async def _set_state(self, arg: str, state: str | None, verb: str) -> str:
        if not _numbers(arg):
            return f"Usage: <code>/{verb} 2 5</code> — numbers from /groups"
        picked, bad = await self._pick(arg)
        for c in picked:
            self.store.set_chat_state(c.chat_id, c.title, state)
        lines = [f"{verb.capitalize()}d: {_e(c.title)}" for c in picked]
        if bad:
            lines.append(f"No chat with number {', '.join(map(str, bad))}. See /groups.")
        return "\n".join(lines)

    async def cmd_mute(self, arg: str) -> str:
        return await self._set_state(arg, "muted", "mute")

    async def cmd_unmute(self, arg: str) -> str:
        return await self._set_state(arg, None, "unmute")

    async def cmd_only(self, arg: str) -> str:
        if arg.lower() in ("off", "all", "none"):
            n = self.store.clear_focus()
            return f"Watching all chats again (cleared {n} from the only-list)."
        if not _numbers(arg):
            return "Usage: <code>/only 1 4</code> to watch only those chats, <code>/only off</code> to undo."
        picked, bad = await self._pick(arg)
        for c in picked:
            self.store.set_chat_state(c.chat_id, c.title, "focused")
        lines = [f"🎯 Now watching: {_e(c.title)}" for c in picked]
        if bad:
            lines.append(f"No chat with number {', '.join(map(str, bad))}. See /groups.")
        if picked:
            lines.append("All other chats are ignored until <code>/only off</code>.")
        return "\n".join(lines)

    async def _flag(self, key: str, arg: str, name: str) -> str:
        on = _on_off(arg)
        if on is None:
            state = "on" if self.store.get_flag(key) else "off"
            return f"{name} watching is {state}. Use <code>/{key} on</code> or <code>/{key} off</code>."
        self.store.set_flag(key, on)
        return f"{name} watching turned {'on' if on else 'off'}."

    async def cmd_channels(self, arg: str) -> str:
        return await self._flag("channels", arg, "Channel")

    async def cmd_dms(self, arg: str) -> str:
        return await self._flag("dms", arg, "Private chat")

    # --- general ----------------------------------------------------------

    async def cmd_pause(self, arg: str) -> str:
        self.store.set_flag("paused", True)
        return "⏸ Alerts and auto-replies paused. Send /resume to restart."

    async def cmd_resume(self, arg: str) -> str:
        self.store.set_flag("paused", False)
        return "▶️ Alerts and auto-replies resumed."

    async def cmd_status(self, arg: str) -> str:
        focused = self.store.chats("focused")
        muted = self.store.chats("muted")
        onoff = lambda key: "on" if self.store.get_flag(key) else "off"  # noqa: E731
        lines = [
            "<b>Status</b>",
            f"Alerts: {'⏸ paused' if self.store.get_flag('paused') else '▶️ running'}",
            f"Keywords: {len(self.store.keywords())}",
            f"Auto-replies: {onoff('autoreply')} · {len(self.store.rules())} rule(s) · "
            f"{'ask me first' if self.store.get_flag('approve') else 'automatic'} · "
            f"to {self.store.get('reply_in')} · cooldown {self.store.get('cooldown_hours')}h",
            f"Channels: {onoff('channels')} · Private chats: {onoff('dms')}",
        ]
        if focused:
            lines.append(f"Only watching {len(focused)} chat(s): " + ", ".join(map(_e, focused.values())))
        else:
            lines.append(f"Muted chats: {len(muted)}")
        if not self.store.keywords():
            lines.append("\n⚠️ No keywords yet, so nothing will alert. Use /add.")
        return "\n".join(lines)
