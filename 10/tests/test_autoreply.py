import asyncio

import pytest

from kwalert.autoreply import (
    AutoReplier,
    Incoming,
    RateLimiter,
    Rule,
    RuleError,
    RuleMatcher,
    SendBlocked,
    SlowDown,
    load_rules,
    parse_rule,
    should_autoreply,
)
from kwalert.core import Commands
from kwalert.kinds import CHANNEL, DM, GROUP
from kwalert.matcher import Matcher
from kwalert.storage import Store


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "t.db")
    yield s
    s.close()


# --- parsing & matching ---------------------------------------------------

def test_parse_rule():
    triggers, reply = parse_rule("class+time, Lecture +  START,class + time => Class is 10am\nin LT2")
    assert triggers == ["class + time", "Lecture + START"]
    assert reply == "Class is 10am\nin LT2"


@pytest.mark.parametrize("bad", ["class + time", "=> hi", "class => ", " + => hi", "* => hi"])
def test_parse_rule_errors(bad):
    with pytest.raises(RuleError):
        parse_rule(bad)


def test_all_terms_required_any_order():
    rm = RuleMatcher([Rule(1, ("class + time",), "10am")])
    assert rm.find("What time is class?").id == 1
    assert rm.find("class starts what time abeg").id == 1
    assert rm.find("is there class today") is None
    assert rm.find("classic time") is None  # whole words only


def test_alternative_triggers_and_lowest_rule_wins():
    rm = RuleMatcher([
        Rule(1, ("assignment + submit", "assignment + due"), "Friday"),
        Rule(2, ("assignment",), "general"),
    ])
    assert rm.find("when is the assignment due?").id == 1
    assert rm.find("assignment wahala").id == 2


def test_starts_with_no_rules(store):
    assert load_rules(store) == []


# --- where replies are allowed --------------------------------------------

def test_should_autoreply(store):
    assert should_autoreply(store, 1, GROUP)
    assert should_autoreply(store, 2, DM)
    assert not should_autoreply(store, 3, CHANNEL)
    store.set_chat_state(1, "G", "muted")
    assert not should_autoreply(store, 1, GROUP)
    store.set_flag("autoreply", False)
    assert not should_autoreply(store, 2, DM)
    store.set_flag("autoreply", True)
    store.set_flag("paused", True)
    assert not should_autoreply(store, 2, DM)


def test_rate_limiter():
    now = [0.0]
    lim = RateLimiter(per_chat=2, total=3, window=60, clock=lambda: now[0])
    for chat in (1, 1):
        assert lim.allow(chat)
        lim.record(chat)
    assert not lim.allow(1)
    assert lim.allow(2)
    lim.record(2)
    assert not lim.allow(3)  # total cap
    now[0] = 61
    assert lim.allow(1)


# --- the replier ------------------------------------------------------------

class Harness:
    def __init__(self, store, rules, fail=None):
        self.sent, self.notes, self.asked = [], [], []
        self.fail = fail
        self.now = 1_000_000.0

        async def send(target, text, reply_to):
            if self.fail:
                raise self.fail
            self.sent.append((target, text, reply_to))

        async def notify(text):
            self.notes.append(text)

        async def ask(pid, text):
            self.asked.append((pid, text))

        async def no_sleep(_):
            pass

        for trig, reply in rules:
            store.add_rule(trig, reply)
        self.replier = AutoReplier(
            store, RuleMatcher(load_rules(store)), send, notify, ask,
            sleep=no_sleep, clock=lambda: self.now,
        )

    def msg(self, text, sender=10, chat=-100, kind=GROUP, contact=False, msg_id=1):
        return Incoming(
            chat_id=chat, chat_kind=kind, chat_title="Class of 2026", msg_id=msg_id,
            text=text, sender_id=sender, sender_name=f"user{sender}",
            sender_is_contact=contact, chat_ref=f"chat{chat}", sender_ref=f"user{sender}",
        )

    def feed(self, *msgs):
        async def go():
            for m in msgs:
                task = await self.replier.on_message(m)
                if task:
                    await task
        asyncio.run(go())


RULES = [(["class + time"], "Class is 10am in LT2")]


def test_each_asker_gets_one_reply(store):
    h = Harness(store, RULES)
    h.feed(
        h.msg("what time is class?", sender=1, msg_id=1),
        h.msg("Class na what time?", sender=2, msg_id=2),
        h.msg("abeg what time is class", sender=1, msg_id=3),  # asked again
        h.msg("hello everyone", sender=3, msg_id=4),
    )
    assert h.sent == [
        ("chat-100", "Class is 10am in LT2", 1),
        ("chat-100", "Class is 10am in LT2", 2),
    ]
    assert len(h.notes) == 2 and "Auto-replied" in h.notes[0]


def test_cooldown_expires(store):
    h = Harness(store, RULES)
    h.feed(h.msg("class time?"))
    h.now += 13 * 3600
    h.feed(h.msg("class time?", msg_id=2))
    assert len(h.sent) == 2


def test_same_person_other_chat_is_answered(store):
    h = Harness(store, RULES)
    h.feed(h.msg("class time?", chat=-1), h.msg("class time?", chat=-2))
    assert len(h.sent) == 2


def test_no_reply_in_channels_or_when_off(store):
    h = Harness(store, RULES)
    h.feed(h.msg("class time?", kind=CHANNEL))
    store.set_flag("autoreply", False)
    h.feed(h.msg("class time?", sender=2))
    assert h.sent == []


def test_dm_mode_only_for_contacts(store):
    h = Harness(store, RULES)
    store.set("reply_in", "dm")
    h.feed(h.msg("class time?", sender=1, contact=True), h.msg("class time?", sender=2))
    assert h.sent == [("user1", "Class is 10am in LT2", None), ("chat-100", "Class is 10am in LT2", 1)]


def test_private_chat_questions_answered_in_place(store):
    h = Harness(store, RULES)
    store.set("reply_in", "dm")
    h.feed(h.msg("class time?", chat=55, kind=DM, contact=True))
    assert h.sent == [("chat55", "Class is 10am in LT2", 1)]


def test_approval_flow(store):
    h = Harness(store, RULES)
    store.set_flag("approve", True)
    h.feed(h.msg("class time?", sender=1), h.msg("class time?", sender=2))
    h.feed(h.msg("class time?", sender=1, msg_id=9))  # still pending: not asked twice
    assert h.sent == [] and [pid for pid, _ in h.asked] == [1, 2]
    assert "user1" in h.asked[0][1] and "Class is 10am" in h.asked[0][1]
    assert asyncio.run(h.replier.approve(1)) is True
    assert h.sent == [("chat-100", "Class is 10am in LT2", 1)]
    assert h.replier.skip(2)
    assert asyncio.run(h.replier.approve(2)) is None  # already handled
    h.feed(h.msg("class time?", sender=2, msg_id=10))
    assert len(h.asked) == 2  # skipped person isn't asked about again


def test_slowdown_turns_autoreply_off(store):
    h = Harness(store, RULES, fail=SlowDown("FLOOD_WAIT_300"))
    h.feed(h.msg("class time?"))
    assert not store.get_flag("autoreply")
    assert "slow down" in h.notes[0]


def test_approved_but_blocked_reports_not_sent(store):
    h = Harness(store, RULES, fail=SendBlocked("CHAT_WRITE_FORBIDDEN"))
    store.set_flag("approve", True)
    h.feed(h.msg("class time?"))
    assert asyncio.run(h.replier.approve(1)) is False


def test_blocked_chat_reports_and_allows_retry(store):
    h = Harness(store, RULES, fail=SendBlocked("CHAT_WRITE_FORBIDDEN"))
    h.feed(h.msg("class time?"))
    assert "Couldn't auto-reply" in h.notes[0]
    h.fail = None
    h.feed(h.msg("class time?", msg_id=2))
    assert len(h.sent) == 1  # not marked as answered after the failure


def test_hourly_limit(store):
    h = Harness(store, RULES)
    h.replier.limiter = RateLimiter(per_chat=1, total=10)
    h.feed(h.msg("class time?", sender=1), h.msg("class time?", sender=2))
    assert len(h.sent) == 1
    assert "hourly safety limit" in h.notes[-1]


# --- bot commands -----------------------------------------------------------

@pytest.fixture
def cmds(store):
    async def list_chats():
        return []

    h = Harness(store, [])
    return Commands(store, Matcher([]), list_chats, h.replier)


def run(cmds, text):
    return asyncio.run(cmds.handle(text))


def test_reply_commands_flow(cmds, store):
    assert "No auto-reply rules" in run(cmds, "/replies")
    out = run(cmds, "/reply class + time, lecture + start => Class is <10am>")
    assert "Added reply #1" in out and "&lt;10am&gt;" in out
    assert "#1" in run(cmds, "/testreply when does lecture start?")
    assert "No reply rule matched" in run(cmds, "/testreply hello")
    assert "lecture + start" in run(cmds, "/replies")
    assert "now says" in run(cmds, "/editreply 1 => Moved to 11am")
    assert "Moved to 11am" in run(cmds, "/testreply class time")
    assert "Deleted reply #1" in run(cmds, "/delreply 1")
    assert "No auto-reply rules" in run(cmds, "/replies")


def test_reply_command_errors(cmds):
    assert "❌" in run(cmds, "/reply class time")
    assert "No reply #7" in run(cmds, "/editreply 7 => x")
    assert "No reply #7" in run(cmds, "/delreply 7")


def test_settings_commands(cmds, store):
    run(cmds, "/approve on")
    assert store.get_flag("approve")
    run(cmds, "/replyin dm")
    assert store.get("reply_in") == "dm"
    assert "currently" in run(cmds, "/replyin elsewhere")
    run(cmds, "/cooldown 24")
    assert store.get("cooldown_hours") == "24"
    assert "between" in run(cmds, "/cooldown -1")
    run(cmds, "/autoreply off")
    assert not store.get_flag("autoreply")
    assert "Auto-replies: off" in run(cmds, "/status")


def test_help_mentions_replies(cmds):
    assert "/reply" in run(cmds, "/help")
