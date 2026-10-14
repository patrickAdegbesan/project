"""Auto-replies: answer common questions for you, as you.

A rule is one or more *triggers* and the reply text you wrote. A trigger is
terms joined by ``+``; every term must appear in the message (in any order,
using the same matching as keywords). ``class + time`` fires on "What time is
class?" and "class starts what time abeg".

Safety limits, so Telegram doesn't treat the account as a spammer:
each person gets a given reply once per cooldown; replies wait a few random
seconds; there's a per-chat and an overall hourly cap; and if Telegram says
"slow down", auto-replies switch themselves off and tell you.
"""

from __future__ import annotations

import asyncio
import html
import logging
import random
import time
from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from .kinds import CHANNEL, DM
from .matcher import Keyword, KeywordError, compile_keyword, normalize_text_keyword
from .storage import Store

log = logging.getLogger("kwalert.autoreply")

DELAY_RANGE = (5.0, 20.0)  # seconds to wait before replying
PER_CHAT_PER_HOUR = 10
TOTAL_PER_HOUR = 30
MAX_PENDING_APPROVALS = 200


class RuleError(ValueError):
    pass


class SendBlocked(Exception):
    """You aren't allowed to write in that chat (read-only, banned, ...)."""


class SlowDown(Exception):
    """Telegram rate-limited or spam-limited the account."""


@dataclass(frozen=True)
class Rule:
    id: int
    triggers: tuple[str, ...]
    reply: str


def parse_trigger(raw: str) -> str:
    """Normalise ``"Class+  time"`` to ``"Class + time"`` and validate the terms."""
    terms = [normalize_text_keyword(t) for t in raw.split("+")]
    terms = [t for t in terms if t]
    if not terms:
        raise RuleError(f"Empty trigger: {raw!r}")
    for t in terms:
        try:
            compile_keyword(Keyword(t))
        except KeywordError as exc:
            raise RuleError(f"{t!r}: {exc}") from exc
    return " + ".join(terms)


def parse_rule(arg: str) -> tuple[list[str], str]:
    """``"class + time, lecture + time => Class is 10am"`` -> (triggers, reply)."""
    if "=>" not in arg:
        raise RuleError("Put => between the question words and your reply.")
    left, reply = arg.split("=>", 1)
    reply = reply.strip()
    if not reply:
        raise RuleError("The reply after => is empty.")
    raw_triggers = [t for t in left.replace("\n", ",").split(",") if t.strip()]
    if not raw_triggers:
        raise RuleError("Add the question words before =>.")
    triggers = []
    for raw in raw_triggers:
        t = parse_trigger(raw)
        if t.casefold() not in (x.casefold() for x in triggers):
            triggers.append(t)
    return triggers, reply


class RuleMatcher:
    def __init__(self, rules: list[Rule] | None = None):
        self._compiled: list[tuple[Rule, list[list[Any]]]] = []
        self.set_rules(rules or [])

    def set_rules(self, rules: list[Rule]) -> None:
        compiled = []
        for rule in rules:
            triggers = []
            for trig in rule.triggers:
                try:
                    triggers.append([compile_keyword(Keyword(t)) for t in trig.split(" + ")])
                except KeywordError:
                    continue
            if triggers:
                compiled.append((rule, triggers))
        self._compiled = compiled

    @property
    def rules(self) -> list[Rule]:
        return [r for r, _ in self._compiled]

    def find(self, text: str) -> Rule | None:
        """First rule (lowest number) with a trigger whose terms are all in ``text``."""
        if not text:
            return None
        for rule, triggers in self._compiled:
            if any(all(rx.search(text) for rx in terms) for terms in triggers):
                return rule
        return None


def load_rules(store: Store) -> list[Rule]:
    return [Rule(rid, tuple(trig), reply) for rid, trig, reply in store.rules()]


class RateLimiter:
    def __init__(self, per_chat: int = PER_CHAT_PER_HOUR, total: int = TOTAL_PER_HOUR,
                 window: float = 3600.0, clock: Callable[[], float] = time.monotonic):
        self.per_chat, self.total, self.window, self.clock = per_chat, total, window, clock
        self._chat: dict[int, deque[float]] = defaultdict(deque)
        self._all: deque[float] = deque()

    def _trim(self, q: deque[float], now: float) -> None:
        while q and now - q[0] >= self.window:
            q.popleft()

    def allow(self, chat_id: int) -> bool:
        now = self.clock()
        q = self._chat[chat_id]
        self._trim(q, now)
        self._trim(self._all, now)
        return len(q) < self.per_chat and len(self._all) < self.total

    def record(self, chat_id: int) -> None:
        now = self.clock()
        self._chat[chat_id].append(now)
        self._all.append(now)


@dataclass
class Incoming:
    """A message someone else sent, with what's needed to answer it."""
    chat_id: int
    chat_kind: str
    chat_title: str
    msg_id: int
    text: str
    sender_id: int
    sender_name: str
    sender_is_contact: bool
    chat_ref: Any = None    # what ``send`` needs to reach the chat
    sender_ref: Any = None  # what ``send`` needs to reach the person privately


Send = Callable[[Any, str, "int | None"], Awaitable[None]]
Notify = Callable[[str], Awaitable[None]]
AskApproval = Callable[[int, str], Awaitable[None]]


def should_autoreply(store: Store, chat_id: int, kind: str) -> bool:
    if store.get_flag("paused") or not store.get_flag("autoreply"):
        return False
    if kind == CHANNEL:
        return False  # replying there would post to every subscriber
    if kind == DM:
        return True
    focused = store.chats("focused")
    if focused:
        return chat_id in focused
    return store.chat_state(chat_id) != "muted"


def _e(text: str) -> str:
    return html.escape(text, quote=False)


def _short(text: str, n: int = 200) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


class AutoReplier:
    def __init__(
        self,
        store: Store,
        rules: RuleMatcher,
        send: Send,
        notify: Notify,
        ask_approval: AskApproval,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        delay_range: tuple[float, float] = DELAY_RANGE,
        limiter: RateLimiter | None = None,
        clock: Callable[[], float] = time.time,
    ):
        self.store, self.rules = store, rules
        self.send, self.notify, self.ask_approval = send, notify, ask_approval
        self.sleep, self.delay_range = sleep, delay_range
        self.limiter = limiter or RateLimiter()
        self.clock = clock
        self._inflight: set[tuple[int, int, int]] = set()
        self._pending: OrderedDict[int, tuple[Rule, Incoming]] = OrderedDict()
        self._next_id = 1
        self._tasks: set[asyncio.Task] = set()

    def reload(self) -> None:
        self.rules.set_rules(load_rules(self.store))

    def _key(self, rule: Rule, msg: Incoming) -> tuple[int, int, int]:
        return (rule.id, msg.chat_id, msg.sender_id)

    async def on_message(self, msg: Incoming) -> asyncio.Task | None:
        """Decide whether to answer; returns the scheduled send task, if any."""
        if not should_autoreply(self.store, msg.chat_id, msg.chat_kind):
            return None
        rule = self.rules.find(msg.text)
        if rule is None:
            return None
        key = self._key(rule, msg)
        cooldown = float(self.store.get("cooldown_hours")) * 3600
        if key in self._inflight or self.store.was_replied(
            rule.id, msg.chat_id, msg.sender_id, since=self.clock() - cooldown
        ):
            return None
        self._inflight.add(key)

        if self.store.get_flag("approve"):
            pid = self._next_id
            self._next_id += 1
            self._pending[pid] = (rule, msg)
            while len(self._pending) > MAX_PENDING_APPROVALS:
                _, (old_rule, old_msg) = self._pending.popitem(last=False)
                self._inflight.discard(self._key(old_rule, old_msg))
            await self.ask_approval(pid, self.describe(rule, msg))
            return None

        task = asyncio.create_task(self._deliver(rule, msg, delay=True))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    def describe(self, rule: Rule, msg: Incoming) -> str:
        return (
            f"❓ <b>{_e(msg.sender_name)}</b> in <b>{_e(msg.chat_title)}</b>:\n"
            f"<i>{_e(_short(msg.text))}</i>\n\n"
            f"Reply #{rule.id} would send:\n{_e(_short(rule.reply, 400))}"
        )

    async def approve(self, pid: int) -> bool | None:
        """Send a pending reply. None if it no longer exists, else whether it was sent."""
        item = self._pending.pop(pid, None)
        if item is None:
            return None
        return await self._deliver(*item, delay=False)

    def skip(self, pid: int) -> bool:
        item = self._pending.pop(pid, None)
        if item is None:
            return False
        rule, msg = item
        # Count it as handled so you aren't asked about this person again.
        self.store.mark_replied(rule.id, msg.chat_id, msg.sender_id, self.clock())
        self._inflight.discard(self._key(rule, msg))
        return True

    async def _deliver(self, rule: Rule, msg: Incoming, delay: bool) -> bool:
        """Send the reply; returns whether it went out."""
        key = self._key(rule, msg)
        try:
            if delay:
                await self.sleep(random.uniform(*self.delay_range))
                if not should_autoreply(self.store, msg.chat_id, msg.chat_kind):
                    return False  # paused or switched off while waiting
            if not self.limiter.allow(msg.chat_id):
                log.info("Hourly limit reached; not replying in %s", msg.chat_title)
                await self.notify(
                    f"⏳ Didn't auto-reply to {_e(msg.sender_name)} in "
                    f"<b>{_e(msg.chat_title)}</b>: hourly safety limit reached."
                )
                return False

            privately = (
                self.store.get("reply_in") == "dm"
                and msg.chat_kind != DM
                and msg.sender_is_contact
                and msg.sender_ref is not None
            )
            if privately:
                await self.send(msg.sender_ref, rule.reply, None)
            else:
                await self.send(msg.chat_ref, rule.reply, msg.msg_id)
            self.limiter.record(msg.chat_id)
            self.store.mark_replied(rule.id, msg.chat_id, msg.sender_id, self.clock())
            where = "privately" if privately else f"in <b>{_e(msg.chat_title)}</b>"
            await self.notify(f"↩️ Auto-replied to {_e(msg.sender_name)} {where} (reply #{rule.id})")
            return True
        except SlowDown as exc:
            self.store.set_flag("autoreply", False)
            await self.notify(
                "🛑 Telegram asked this account to slow down, so auto-replies are now "
                f"<b>off</b> to protect it ({_e(str(exc))}). Send <code>/autoreply on</code> "
                "later to restart."
            )
        except SendBlocked as exc:
            await self.notify(
                f"⚠️ Couldn't auto-reply in <b>{_e(msg.chat_title)}</b>: {_e(str(exc))}. "
                "Use /mute on that chat if you can't post there."
            )
        except Exception:
            log.exception("Auto-reply failed")
        finally:
            self._inflight.discard(key)
        return False
