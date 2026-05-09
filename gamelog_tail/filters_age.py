"""Filter log entries by age relative to the current time."""

from __future__ import annotations

import datetime
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def max_age_filter(
    max_seconds: float,
    now_fn: Optional[Callable[[], datetime.datetime]] = None,
) -> Callable[[LogEntry], bool]:
    """Return a filter that drops entries older than *max_seconds*.

    Entries without a timestamp are always passed through.

    Args:
        max_seconds: Maximum age in seconds.  Must be positive.
        now_fn: Optional callable returning the current UTC time (useful for
                testing).  Defaults to ``datetime.datetime.utcnow``.

    Returns:
        A callable ``(LogEntry) -> bool`` that returns ``True`` when the entry
        should be kept.

    Raises:
        ValueError: If *max_seconds* is not positive.
    """
    if max_seconds <= 0:
        raise ValueError(f"max_seconds must be positive, got {max_seconds!r}")

    _now = now_fn or datetime.datetime.utcnow

    def _filter(entry: LogEntry) -> bool:
        if entry.timestamp is None:
            return True
        age = (_now() - entry.timestamp).total_seconds()
        return age <= max_seconds

    return _filter


def min_age_filter(
    min_seconds: float,
    now_fn: Optional[Callable[[], datetime.datetime]] = None,
) -> Callable[[LogEntry], bool]:
    """Return a filter that drops entries *newer* than *min_seconds*.

    Useful for skipping very recent (possibly incomplete) log lines.
    Entries without a timestamp are always passed through.

    Args:
        min_seconds: Minimum age in seconds.  Must be positive.
        now_fn: Optional callable returning the current UTC time.

    Returns:
        A callable ``(LogEntry) -> bool``.

    Raises:
        ValueError: If *min_seconds* is not positive.
    """
    if min_seconds <= 0:
        raise ValueError(f"min_seconds must be positive, got {min_seconds!r}")

    _now = now_fn or datetime.datetime.utcnow

    def _filter(entry: LogEntry) -> bool:
        if entry.timestamp is None:
            return True
        age = (_now() - entry.timestamp).total_seconds()
        return age >= min_seconds

    return _filter
