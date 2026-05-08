"""Integration helpers: build burst-suppression filters from CLI/config args."""

from __future__ import annotations

from typing import Callable

from gamelog_tail.filters_burst import burst_suppress_filter
from gamelog_tail.parsers.base import LogEntry


def build_burst_filters(
    max_count: int | None = None,
    window_seconds: float | None = None,
    key_fields: tuple[str, ...] | None = None,
) -> list[Callable[[LogEntry], LogEntry | None]]:
    """Return a list of burst-suppression filters based on provided arguments.

    If neither *max_count* nor *window_seconds* is given, an empty list is
    returned so callers can always extend a filter pipeline unconditionally.

    Args:
        max_count: Max occurrences before suppression (default 3 when enabled).
        window_seconds: Rolling window length in seconds (default 5.0).
        key_fields: Tuple of LogEntry field names to use as the burst key.
    """
    if max_count is None and window_seconds is None:
        return []

    kwargs: dict = {}
    if max_count is not None:
        kwargs["max_count"] = max_count
    if window_seconds is not None:
        kwargs["window_seconds"] = window_seconds
    if key_fields is not None:
        kwargs["key_fields"] = key_fields

    return [burst_suppress_filter(**kwargs)]


def apply_burst_filters(
    filters: list[Callable[[LogEntry], LogEntry | None]],
    entry: LogEntry,
) -> LogEntry | None:
    """Pass *entry* through every burst filter; return None if any suppresses it."""
    for f in filters:
        if f(entry) is None:
            return None
    return entry
