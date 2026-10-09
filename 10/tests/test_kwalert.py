import asyncio

import pytest

from kwalert.core import (
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
from kwalert.matcher import REGEX, Keyword, KeywordError, Matcher, compile_keyword
from kwalert.storage import Store


def hits(keywords, text):
    return [m.keyword.pattern for m in Matcher(keywords).find(text)]


# --- matching -------------------------------------------------------------

def test_case_insensitive_phrase():
    assert hits([Keyword("school fees")], "Please pay your SCHOOL FEES today") == ["school fees"]


def test_phrase_tolerates_hyphens_and_extra_spaces():
    kw = [Keyword("school fees")]
    assert hits(kw, "school-fees deadline") == ["school fees"]
    assert hits(kw, "school    fees") == ["school fees"]
    assert hits(kw, "school\nfees") == ["school fees"]


def test_whole_words_only():
    assert hits([Keyword("account")], "accountability matters") == []
    assert hits([Keyword("account")], "send your account, please") == ["account"]


def test_wildcard():
    kw = [Keyword("fee*")]
    assert hits(kw, "the fee is") == ["fee*"]
    assert hits(kw, "the fees are") == ["fee*"]
    assert hits(kw, "coffee") == []


def test_regex_keyword():
    assert hits([Keyword(r"\d{10}", REGEX)], "acct 0123456789 gtb") == [r"\d{10}"]


def test_invalid_keywords_rejected():
    with pytest.raises(KeywordError):
        compile_keyword(Keyword("*"))
    with pytest.raises(KeywordError):
        compile_keyword(Keyword("(", REGEX))


def test_special_characters_are_literal():
    assert hits([Keyword("N50,000")], "pay n50,000 now") == ["N50,000"]
    assert hits([Keyword("c++")], "learn C++ today") == ["c++"]


def test_matches_sorted_by_position():
    assert hits([Keyword("result"), Keyword("exam")], "exam result out") == ["exam", "result"]


def test_no_keywords_means_no_matches():
    assert Matcher([]).find("school fees result account") == []


# --- storage --------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "t.db")
    yield s
    s.close()


def test_store_starts_empty(store):
    assert store.keywords() == []


def test_add_dedups_ignoring_case(store):
    assert store.add_keyword(Keyword("School  Fees")) is True
    assert store.add_keyword(Keyword("school fees")) is False
    assert store.keywords() == [Keyword("School Fees")]


def test_remove_is_case_insensitive(store):
    store.add_keyword(Keyword("Result"))
    assert store.remove_keyword("RESULT") == [Keyword("Result")]
    assert store.keywords() == []


def test_settings_default_and_persist(tmp_path):
    s = Store(tmp_path / "t.db")
    assert s.get_flag("paused") is False
    s.set_flag("paused", True)
    s.add_keyword(Keyword("result"))
    s.close()
    s2 = Store(tmp_path / "t.db")
    assert s2.get_flag("paused") is True
    assert s2.keywords() == [Keyword("result")]


# --- chat filtering -------------------------------------------------------

def test_should_watch_rules(store):
    assert should_watch(store, 1, GROUP)
    assert not should_watch(store, 2, CHANNEL)
    assert not should_watch(store, 3, DM)
    store.set_flag("channels", True)
    assert should_watch(store, 2, CHANNEL)
    store.set_chat_state(1, "Class", "muted")
    assert not should_watch(store, 1, GROUP)
    store.set_chat_state(5, "Parents", "focused")
    assert should_watch(store, 5, GROUP)
    assert not should_watch(store, 6, GROUP)
    store.set_flag("paused", True)
    assert not should_watch(store, 5, GROUP)


# --- alerts ---------------------------------------------------------------

def test_deduper_only_new_keywords_on_edit():
    m = Matcher([Keyword("fees"), Keyword("result")])
    d = AlertDeduper()
    first = d.fresh(1, 10, m.find("fees due"))
    assert [x.keyword.pattern for x in first] == ["fees"]
    assert d.fresh(1, 10, m.find("fees due")) == []
    edit = d.fresh(1, 10, m.find("fees due, result out"))
    assert [x.keyword.pattern for x in edit] == ["result"]


def test_format_alert_escapes_html():
    text = "<script> school fees & more"
    matches = Matcher([Keyword("school fees")]).find(text)
    out = format_alert("Class <A>", "Ada", text, matches, "https://t.me/c/1/2")
    assert "<script>" not in out
    assert "Class &lt;A&gt;" in out
    assert "<b><u>school fees</u></b>" in out
    assert 'href="https://t.me/c/1/2"' in out


def test_split_message():
    parts = split_message("\n".join(["x" * 30] * 10), limit=100)
    assert all(len(p) <= 100 for p in parts)
    assert "\n".join(parts).count("x") == 300


# --- bot commands ---------------------------------------------------------

CHATS = [
    ChatInfo(-100, "Zeta Group", GROUP),
    ChatInfo(-200, "alpha group", GROUP),
    ChatInfo(-300, "News", CHANNEL),
]


@pytest.fixture
def cmds(store):
    async def list_chats():
        return CHATS

    return Commands(store, Matcher(store.keywords()), list_chats)


def run(cmds, text):
    return asyncio.run(cmds.handle(text))


def test_add_list_remove_flow(cmds):
    assert "no keywords" in run(cmds, "/list")
    out = run(cmds, "/add school fees, result,  account number ")
    assert out.count("Added") == 3
    assert "school fees" in run(cmds, "/list")
    assert "school fees" in run(cmds, "/test SCHOOL FEES due")
    run(cmds, "/remove result")
    assert "result" not in run(cmds, "/list")
    assert "No keyword matched" in run(cmds, "/test result is out")


def test_add_bad_regex_reports_error(cmds):
    assert "Invalid regex" in run(cmds, "/regex (")


def test_command_with_bot_suffix(cmds):
    assert "Added" in run(cmds, "/add@my_alert_bot fees")


def test_groups_sorted_and_mute_by_number(cmds, store):
    out = run(cmds, "/groups")
    assert out.index("alpha group") < out.index("Zeta Group")
    assert "News" not in out  # channels off by default
    run(cmds, "/mute 2")
    assert store.chat_state(-100) == "muted"
    assert "No chat with number 9" in run(cmds, "/mute 9")
    run(cmds, "/unmute 2")
    assert store.chat_state(-100) is None


def test_only_mode(cmds, store):
    run(cmds, "/only 1")
    assert should_watch(store, -200, GROUP)
    assert not should_watch(store, -100, GROUP)
    run(cmds, "/only off")
    assert should_watch(store, -100, GROUP)


def test_clear_needs_confirmation(cmds, store):
    run(cmds, "/add a, b")
    assert "confirm" in run(cmds, "/clear")
    assert len(store.keywords()) == 2
    run(cmds, "/clear yes")
    assert store.keywords() == []


def test_unknown_and_plain_text(cmds):
    assert "Unknown command" in run(cmds, "/nope")
    assert "/help" in run(cmds, "hello")
