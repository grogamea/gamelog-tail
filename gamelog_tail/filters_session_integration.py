"""Integration helpers that wire session_filter into the CLI pipeline."""

from __future__ import annotations

from typing import Callable, List, Optional, Set

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_session import session_filter


def build_session_filters(
    sentinel: Optional[str] = None,
    keep_sessions: Optional[Set[int]] = None,
    field: str = "message",
) -> List[Callable[[LogEntry], Optional[LogEntry]]]:
    """Build a list containing at most one session filter.

    Returns an empty list when *sentinel* is ``None`` or empty so callers can
    safely extend their filter chain without extra guards.
    """
    if not sentinel:
        return []
    return [session_filter(sentinel=sentinel, keep_sessions=keep_sessions, field=field)]


def apply_session_filters(
    entries: List[LogEntry],
    filters: List[Callable[[LogEntry], Optional[LogEntry]]],
) -> List[LogEntry]:
    """Apply every session filter in *filters* to *entries* and return survivors."""
    result = list(entries)
    for f in filters:
        result = [e for e in result if f(e) is not None]
    return result
