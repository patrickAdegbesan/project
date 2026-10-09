"""Keyword matching.

Two kinds of keyword:

* ``text``  - what you normally type. Case-insensitive, whole words only, so
  ``account`` does not fire on ``accountability``. Spaces in a phrase also
  match hyphens/underscores/slashes and repeated spaces, so ``school fees``
  matches ``School-Fees`` and ``school   fees``. A ``*`` is a wildcard for
  "any letters", so ``fee*`` matches ``fee``, ``fees`` and ``feeding``.
* ``regex`` - a raw regular expression for anything the above can't express.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TEXT = "text"
REGEX = "regex"

_SEPARATOR = r"[\s\-_/]+"


class KeywordError(ValueError):
    """Raised when a keyword can't be turned into a pattern."""


@dataclass(frozen=True)
class Keyword:
    pattern: str
    kind: str = TEXT

    def label(self) -> str:
        return f"/{self.pattern}/" if self.kind == REGEX else self.pattern


def normalize_text_keyword(raw: str) -> str:
    """Trim and collapse whitespace; keyword case is kept only for display."""
    return " ".join(raw.split())


def _compile_text(pattern: str) -> re.Pattern[str]:
    words = normalize_text_keyword(pattern).split(" ")
    if not any(ch not in "*" for word in words for ch in word):
        raise KeywordError("A keyword needs at least one real character.")
    parts = []
    for word in words:
        pieces = [re.escape(piece) for piece in word.split("*")]
        parts.append(r"\w*".join(pieces))
    body = _SEPARATOR.join(parts)
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


def compile_keyword(keyword: Keyword) -> re.Pattern[str]:
    if keyword.kind == TEXT:
        return _compile_text(keyword.pattern)
    if keyword.kind == REGEX:
        try:
            return re.compile(keyword.pattern, re.IGNORECASE)
        except re.error as exc:
            raise KeywordError(f"Invalid regex: {exc}") from exc
    raise KeywordError(f"Unknown keyword kind: {keyword.kind}")


@dataclass(frozen=True)
class Match:
    keyword: Keyword
    start: int
    end: int


class Matcher:
    """Holds the compiled keywords and finds them in message text."""

    def __init__(self, keywords: list[Keyword] | None = None):
        self._compiled: list[tuple[Keyword, re.Pattern[str]]] = []
        self.set_keywords(keywords or [])

    def set_keywords(self, keywords: list[Keyword]) -> None:
        compiled = []
        for kw in keywords:
            try:
                compiled.append((kw, compile_keyword(kw)))
            except KeywordError:
                # A bad entry in the database must not stop the others.
                continue
        self._compiled = compiled

    @property
    def keywords(self) -> list[Keyword]:
        return [kw for kw, _ in self._compiled]

    def find(self, text: str) -> list[Match]:
        """Return the first hit of every keyword found in ``text``, in text order."""
        if not text:
            return []
        hits = []
        for kw, rx in self._compiled:
            m = rx.search(text)
            if m and m.end() > m.start():
                hits.append(Match(kw, m.start(), m.end()))
        hits.sort(key=lambda h: h.start)
        return hits


def snippet(text: str, match: Match, radius: int = 120) -> tuple[str, str, str]:
    """Cut ``text`` around ``match``; returns (before, matched, after)."""
    start = max(0, match.start - radius)
    end = min(len(text), match.end + radius)
    before = ("…" if start > 0 else "") + text[start:match.start]
    after = text[match.end:end] + ("…" if end < len(text) else "")
    return before, text[match.start:match.end], after
