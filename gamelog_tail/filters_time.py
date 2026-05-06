"""Time-window filter: keep only entries whose timestamp falls within a range."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def time_window_filter(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes entries whose timestamp is within [start, end].

    Either bound may be *None*, meaning that side is unbounded.
    Entries with no timestamp are always passed through.

    Args:
        start: Inclusive lower bound (timezone-aware or naive, matched against
               the entry timestamp in the same manner).
        end:   Inclusive upper bound.

    Returns:
        A callable ``(LogEntry) -> bool``.

    Raises:
        ValueError: If both *start* and *end* are provided and *start* > *end*.
    """
    if start is not None and end is not None and start > end:
        raise ValueError(
            f"start ({start!r}) must not be later than end ({end!r})"
        )

    def _filter(entry: LogEntry) -> bool:
        ts = entry.timestamp
        if ts is None:
            return True
        if start is not None and ts < start:
            return False
        if end is not None and ts > end:
            return False
        return True

    return _filter
