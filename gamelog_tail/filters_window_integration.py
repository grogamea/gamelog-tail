"""Integration helpers for the sliding-window count filter."""
from __future__ import annotations

from typing import Callable, List, Optional

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_window import sliding_window_filter


def build_window_filters(
    max_count: Optional[int] = None,
    window_seconds: Optional[float] = None,
    key: str = "source",
) -> List[Callable[[LogEntry], bool]]:
    """Build a list containing a sliding-window filter when both
    *max_count* and *window_seconds* are provided; otherwise return
    an empty list.
    """
    if max_count is None or window_seconds is None:
        return []
    return [sliding_window_filter(max_count, window_seconds, key=key)]


def apply_window_filters(
    entries: List[LogEntry],
    filters: List[Callable[[LogEntry], bool]],
) -> List[LogEntry]:
    """Apply *filters* (produced by :func:`build_window_filters`) to
    *entries* and return the surviving entries in order.
    """
    result = entries
    for f in filters:
        result = [e for e in result if f(e)]
    return result
