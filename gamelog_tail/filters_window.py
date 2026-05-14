"""Sliding-window count filter: pass only entries whose rolling count
within *window_seconds* does not exceed *max_count*.

Unlike the burst filter (which suppresses once a burst is detected and
then waits for quiet), this filter enforces a strict sliding-window
rate cap on every individual (level, source) bucket.
"""
from __future__ import annotations

import time
from collections import deque
from typing import Callable, Deque

from gamelog_tail.parsers.base import LogEntry


class _SlidingWindow:
    """Tracks event timestamps inside a rolling time window."""

    def __init__(self, window_seconds: float) -> None:
        self._window = window_seconds
        self._timestamps: Deque[float] = deque()

    def record(self, now: float) -> int:
        """Record *now* and return the current count inside the window."""
        self._timestamps.append(now)
        cutoff = now - self._window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()
        return len(self._timestamps)


def sliding_window_filter(
    max_count: int,
    window_seconds: float,
    *,
    key: str = "source",
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes at most *max_count* entries per *key*
    within any rolling *window_seconds* interval.

    *key* may be ``"source"`` (default) or ``"level"``.

    Raises
    ------
    ValueError
        If *max_count* < 1, *window_seconds* <= 0, or *key* is invalid.
    """
    if max_count < 1:
        raise ValueError("max_count must be >= 1")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be > 0")
    if key not in {"source", "level"}:
        raise ValueError("key must be 'source' or 'level'")

    buckets: dict[str, _SlidingWindow] = {}

    def _filter(entry: LogEntry) -> bool:
        bucket_key = (entry.source or "") if key == "source" else (entry.level or "")
        if bucket_key not in buckets:
            buckets[bucket_key] = _SlidingWindow(window_seconds)
        count = buckets[bucket_key].record(time.monotonic())
        return count <= max_count

    return _filter
