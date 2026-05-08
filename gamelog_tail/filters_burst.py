"""Burst detection filter: suppress repeated identical messages within a time window."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Callable, Deque

from gamelog_tail.parsers.base import LogEntry


class _BurstWindow:
    """Tracks occurrence timestamps for a single message key."""

    def __init__(self, window_seconds: float, max_count: int) -> None:
        self._window = window_seconds
        self._max = max_count
        self._times: Deque[float] = deque()

    def record(self, ts: float) -> bool:
        """Record an event at *ts* (epoch seconds). Return True if within burst."""
        cutoff = ts - self._window
        while self._times and self._times[0] < cutoff:
            self._times.popleft()
        self._times.append(ts)
        return len(self._times) > self._max


def burst_suppress_filter(
    max_count: int = 3,
    window_seconds: float = 5.0,
    key_fields: tuple[str, ...] = ("level", "message"),
) -> Callable[[LogEntry], LogEntry | None]:
    """Return a filter that drops entries repeated more than *max_count* times
    within *window_seconds*.

    Args:
        max_count: Number of identical entries allowed before suppression begins.
        window_seconds: Rolling time window in seconds.
        key_fields: LogEntry fields used to build the deduplication key.
    """
    if max_count < 1:
        raise ValueError("max_count must be >= 1")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")
    allowed = {"level", "message", "source"}
    for f in key_fields:
        if f not in allowed:
            raise ValueError(f"Invalid key_field {f!r}; choose from {allowed}")

    _windows: dict[tuple, _BurstWindow] = {}

    def _filter(entry: LogEntry) -> LogEntry | None:
        key = tuple(getattr(entry, f, None) for f in key_fields)
        if key not in _windows:
            _windows[key] = _BurstWindow(window_seconds, max_count)
        ts = entry.timestamp.timestamp() if entry.timestamp else datetime.now(timezone.utc).timestamp()
        if _windows[key].record(ts):
            return None
        return entry

    return _filter
