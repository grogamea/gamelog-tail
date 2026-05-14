"""Filter that suppresses entries when the same message bursts repeatedly.

Combines deduplication logic with a sliding window to suppress messages
that repeat more than `max_repeats` times within `window_seconds`.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Callable, Deque

from gamelog_tail.parsers.base import LogEntry


class _RepeatWindow:
    """Tracks timestamps of a single message key within a sliding window."""

    def __init__(self, window_seconds: float) -> None:
        self._window = window_seconds
        self._timestamps: Deque[float] = deque()

    def record(self, ts: float) -> int:
        """Record an occurrence and return the current count within the window."""
        cutoff = ts - self._window
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        self._timestamps.append(ts)
        return len(self._timestamps)


def duplicate_burst_filter(
    max_repeats: int = 3,
    window_seconds: float = 10.0,
    key_fields: tuple[str, ...] = ("level", "message"),
) -> Callable[[LogEntry], bool]:
    """Return a filter that suppresses bursts of identical log entries.

    Args:
        max_repeats: Number of allowed occurrences within the window before
            subsequent entries are suppressed.
        window_seconds: Sliding window size in seconds.
        key_fields: Fields used to compute the identity of an entry.

    Returns:
        A callable that returns ``True`` when the entry should be kept.
    """
    if max_repeats < 1:
        raise ValueError(f"max_repeats must be >= 1, got {max_repeats}")
    if window_seconds <= 0:
        raise ValueError(f"window_seconds must be > 0, got {window_seconds}")
    if not key_fields:
        raise ValueError("key_fields must not be empty")

    _windows: dict[tuple, _RepeatWindow] = defaultdict(
        lambda: _RepeatWindow(window_seconds)
    )

    def _key(entry: LogEntry) -> tuple:
        parts = []
        for field in key_fields:
            parts.append(getattr(entry, field, None))
        return tuple(parts)

    def _filter(entry: LogEntry) -> bool:
        now = time.monotonic()
        k = _key(entry)
        count = _windows[k].record(now)
        return count <= max_repeats

    return _filter
