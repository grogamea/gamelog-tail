"""Keyword-based log entry filters.

Provides allowlist and denylist filters that match against the
message field using a list of plain-text keywords (case-insensitive).
"""

from __future__ import annotations

from typing import Callable, Iterable

from gamelog_tail.parsers.base import LogEntry


def keyword_allowlist_filter(
    keywords: Iterable[str],
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes entries whose message contains
    at least one of the given keywords (case-insensitive).

    Args:
        keywords: Non-empty iterable of keyword strings to match.

    Raises:
        ValueError: If *keywords* is empty.
    """
    normalised = [kw.lower() for kw in keywords]
    if not normalised:
        raise ValueError("keyword_allowlist_filter requires at least one keyword")

    def _filter(entry: LogEntry) -> bool:
        msg = entry.message.lower()
        return any(kw in msg for kw in normalised)

    return _filter


def keyword_denylist_filter(
    keywords: Iterable[str],
) -> Callable[[LogEntry], bool]:
    """Return a filter that blocks entries whose message contains
    any of the given keywords (case-insensitive).

    Args:
        keywords: Non-empty iterable of keyword strings to match.

    Raises:
        ValueError: If *keywords* is empty.
    """
    normalised = [kw.lower() for kw in keywords]
    if not normalised:
        raise ValueError("keyword_denylist_filter requires at least one keyword")

    def _filter(entry: LogEntry) -> bool:
        msg = entry.message.lower()
        return not any(kw in msg for kw in normalised)

    return _filter
