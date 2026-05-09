"""Integration helpers: build throttle filters from CLI/config arguments."""
from __future__ import annotations

from typing import Callable, List, Optional

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_throttle import throttle_filter


def build_throttle_filters(
    max_per_window: Optional[int] = None,
    window: Optional[float] = None,
    key: Optional[str] = None,
) -> List[Callable[[LogEntry], Optional[LogEntry]]]:
    """Return a list of throttle filters based on provided arguments.

    If neither *max_per_window* nor *window* is supplied, returns an empty
    list so callers can safely chain the result without special-casing.

    Args:
        max_per_window: Maximum entries per window (default 5 when enabled).
        window: Window size in seconds (default 10.0 when enabled).
        key: Bucketing key – ``'source_level'``, ``'source'``, or ``'level'``.
             Defaults to ``'source_level'``.

    Returns:
        A list containing zero or one throttle filter callables.
    """
    if max_per_window is None and window is None:
        return []

    kwargs: dict = {}
    if max_per_window is not None:
        kwargs["max_per_window"] = max_per_window
    if window is not None:
        kwargs["window"] = window
    if key is not None:
        kwargs["key"] = key

    return [throttle_filter(**kwargs)]


def apply_throttle_filters(
    entry: LogEntry,
    filters: List[Callable[[LogEntry], Optional[LogEntry]]],
) -> Optional[LogEntry]:
    """Pass *entry* through every throttle filter in sequence.

    Returns the entry if all filters pass it, or ``None`` if any filter
    suppresses it.
    """
    current: Optional[LogEntry] = entry
    for filt in filters:
        if current is None:
            return None
        current = filt(current)
    return current
