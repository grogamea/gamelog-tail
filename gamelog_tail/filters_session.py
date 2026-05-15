"""Session-boundary filter: pass only entries that fall within a numbered
log session.  A new session begins each time a sentinel pattern is matched.

Usage::

    f = session_filter(sentinel=r"Game session started", keep_sessions={1, 2})
    # keep_sessions=None  →  keep every session
"""

from __future__ import annotations

import re
from typing import Callable, FrozenSet, Optional, Set

from gamelog_tail.parsers.base import LogEntry


def session_filter(
    sentinel: str,
    keep_sessions: Optional[Set[int]] = None,
    field: str = "message",
) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that segments entries into sessions.

    Parameters
    ----------
    sentinel:
        Regex pattern whose match on *field* increments the session counter.
    keep_sessions:
        Set of 1-based session numbers to retain.  ``None`` keeps all.
    field:
        Which ``LogEntry`` attribute to match against (``message`` or
        ``source``).
    """
    if not sentinel:
        raise ValueError("sentinel pattern must not be empty")
    if field not in ("message", "source"):
        raise ValueError("field must be 'message' or 'source'")
    if keep_sessions is not None and not keep_sessions:
        raise ValueError("keep_sessions must be None or a non-empty set")

    _compiled = re.compile(sentinel)
    _frozen: Optional[FrozenSet[int]] = (
        frozenset(keep_sessions) if keep_sessions is not None else None
    )

    state = {"session": 0}

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        value: str = getattr(entry, field) or ""
        if _compiled.search(value):
            state["session"] += 1

        current = state["session"]
        if current == 0:
            # Before the first sentinel — treat as session 0, always drop
            return None
        if _frozen is None or current in _frozen:
            return entry
        return None

    return _filter
