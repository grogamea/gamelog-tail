"""Throttle filter: suppress entries from a source/level pair for a cooldown
period after the first occurrence within a burst.

Usage::

    filt = throttle_filter(cooldown=5.0, max_per_window=3)
    entry = filt(entry)  # returns entry or None
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


class _ThrottleState:
    """Tracks hit count and window start for a single bucket."""

    def __init__(self, window: float) -> None:
        self.window = window
        self.window_start: float = 0.0
        self.count: int = 0

    def tick(self, now: float) -> int:
        """Record a hit and return the count within the current window."""
        if now - self.window_start >= self.window:
            self.window_start = now
            self.count = 0
        self.count += 1
        return self.count


def throttle_filter(
    max_per_window: int = 5,
    window: float = 10.0,
    key: str = "source_level",
) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that passes at most *max_per_window* entries per *window*
    seconds for each unique key.

    Args:
        max_per_window: Maximum entries allowed in one window period.
        window: Window duration in seconds.
        key: Bucketing strategy – ``'source_level'`` (default), ``'source'``,
             or ``'level'``.

    Raises:
        ValueError: If *max_per_window* < 1 or *window* <= 0 or *key* unknown.
    """
    if max_per_window < 1:
        raise ValueError("max_per_window must be >= 1")
    if window <= 0:
        raise ValueError("window must be > 0")
    valid_keys = {"source_level", "source", "level"}
    if key not in valid_keys:
        raise ValueError(f"key must be one of {sorted(valid_keys)}")

    states: dict[str, _ThrottleState] = defaultdict(lambda: _ThrottleState(window))

    def _bucket(entry: LogEntry) -> str:
        if key == "source_level":
            return f"{entry.source or ''}::{entry.level}"
        if key == "source":
            return entry.source or ""
        return entry.level

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        bucket = _bucket(entry)
        count = states[bucket].tick(time.monotonic())
        return entry if count <= max_per_window else None

    return _filter
