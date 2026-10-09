"""SQLite storage for keywords, muted/focused chats and settings.

The database starts empty: there are no built-in keywords.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .matcher import TEXT, Keyword, KeywordError, compile_keyword, normalize_text_keyword

_SCHEMA = """
CREATE TABLE IF NOT EXISTS keywords (
    pattern  TEXT NOT NULL,
    kind     TEXT NOT NULL,
    -- text keywords are unique ignoring case; regexes are kept verbatim
    dedup    TEXT NOT NULL,
    added_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (kind, dedup)
);
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    title   TEXT NOT NULL,
    state   TEXT NOT NULL CHECK (state IN ('muted', 'focused'))
);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

DEFAULT_SETTINGS = {
    "paused": "0",
    "channels": "0",  # also watch broadcast channels
    "dms": "0",       # also watch private chats
}


def _dedup_key(kw: Keyword) -> str:
    return kw.pattern.casefold() if kw.kind == TEXT else kw.pattern


class Store:
    def __init__(self, path: Path | str):
        self._db = sqlite3.connect(str(path))
        self._db.executescript(_SCHEMA)
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    # --- keywords ---------------------------------------------------------

    def add_keyword(self, kw: Keyword) -> bool:
        """Validate and store a keyword. Returns False if it already existed."""
        if kw.kind == TEXT:
            kw = Keyword(normalize_text_keyword(kw.pattern), TEXT)
        else:
            kw = Keyword(kw.pattern.strip(), kw.kind)
        if not kw.pattern:
            raise KeywordError("A keyword can't be empty.")
        compile_keyword(kw)  # raises KeywordError if unusable
        cur = self._db.execute(
            "INSERT OR IGNORE INTO keywords (pattern, kind, dedup) VALUES (?, ?, ?)",
            (kw.pattern, kw.kind, _dedup_key(kw)),
        )
        self._db.commit()
        return cur.rowcount == 1

    def remove_keyword(self, pattern: str) -> list[Keyword]:
        """Remove a text keyword (case-insensitive) or a regex (exact)."""
        text_key = normalize_text_keyword(pattern).casefold()
        rows = self._db.execute(
            "SELECT pattern, kind FROM keywords "
            "WHERE (kind = 'text' AND dedup = ?) OR (kind = 'regex' AND dedup = ?)",
            (text_key, pattern.strip()),
        ).fetchall()
        self._db.executemany(
            "DELETE FROM keywords WHERE kind = ? AND dedup = ?",
            [(kind, _dedup_key(Keyword(p, kind))) for p, kind in rows],
        )
        self._db.commit()
        return [Keyword(p, kind) for p, kind in rows]

    def clear_keywords(self) -> int:
        cur = self._db.execute("DELETE FROM keywords")
        self._db.commit()
        return cur.rowcount

    def keywords(self) -> list[Keyword]:
        rows = self._db.execute(
            "SELECT pattern, kind FROM keywords ORDER BY added_at, rowid"
        ).fetchall()
        return [Keyword(p, kind) for p, kind in rows]

    # --- chats ------------------------------------------------------------

    def set_chat_state(self, chat_id: int, title: str, state: str | None) -> None:
        """Mark a chat 'muted' or 'focused'; ``None`` clears it."""
        if state is None:
            self._db.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        else:
            self._db.execute(
                "INSERT INTO chats (chat_id, title, state) VALUES (?, ?, ?) "
                "ON CONFLICT(chat_id) DO UPDATE SET title = excluded.title, "
                "state = excluded.state",
                (chat_id, title, state),
            )
        self._db.commit()

    def clear_focus(self) -> int:
        cur = self._db.execute("DELETE FROM chats WHERE state = 'focused'")
        self._db.commit()
        return cur.rowcount

    def chats(self, state: str) -> dict[int, str]:
        rows = self._db.execute(
            "SELECT chat_id, title FROM chats WHERE state = ? ORDER BY title", (state,)
        ).fetchall()
        return dict(rows)

    def chat_state(self, chat_id: int) -> str | None:
        row = self._db.execute(
            "SELECT state FROM chats WHERE chat_id = ?", (chat_id,)
        ).fetchone()
        return row[0] if row else None

    # --- settings ---------------------------------------------------------

    def get(self, key: str) -> str:
        row = self._db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else DEFAULT_SETTINGS[key]

    def get_flag(self, key: str) -> bool:
        return self.get(key) == "1"

    def set_flag(self, key: str, on: bool) -> None:
        self._db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, "1" if on else "0"),
        )
        self._db.commit()
