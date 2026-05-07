"""Field-presence and field-value filters for LogEntry objects."""

from __future__ import annotations

from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def has_source_filter() -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries that have a non-empty source."""

    def _filter(entry: LogEntry) -> bool:
        return bool(entry.source)

    return _filter


def missing_source_filter() -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries whose source is absent/empty."""

    def _filter(entry: LogEntry) -> bool:
        return not entry.source

    return _filter


def has_timestamp_filter() -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries that carry a timestamp."""

    def _filter(entry: LogEntry) -> bool:
        return entry.timestamp is not None

    return _filter


def missing_timestamp_filter() -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries that have no timestamp."""

    def _filter(entry: LogEntry) -> bool:
        return entry.timestamp is None

    return _filter


def message_min_length_filter(min_length: int) -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries whose message is at least
    *min_length* characters long.

    Raises
    ------
    ValueError
        If *min_length* is negative.
    """
    if min_length < 0:
        raise ValueError(f"min_length must be >= 0, got {min_length}")

    def _filter(entry: LogEntry) -> bool:
        return len(entry.message) >= min_length

    return _filter
