"""
Severity-based burst filter: suppress entries whose level drops below a
dynamic threshold when the error rate is low, and relax the threshold when
bursts of high-severity entries are detected.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Callable, Deque

from gamelog_tail.parsers.base import LogEntry

_LEVEL_RANK = {
    "debug": 0,
    "info": 1,
    "warning": 2,
    "error": 3,
    "fatal": 4,
}


class SeverityBurstFilter:
    """Dynamically raise the minimum visible level during quiet periods.

    During a burst (>= *burst_threshold* high-severity entries within
    *window_seconds*) all entries pass.  Outside a burst only entries at or
    above *quiet_min_level* are forwarded.
    """

    def __init__(
        self,
        quiet_min_level: str = "warning",
        burst_trigger_level: str = "error",
        burst_threshold: int = 3,
        window_seconds: float = 10.0,
    ) -> None:
        if quiet_min_level not in _LEVEL_RANK:
            raise ValueError(f"Unknown level: {quiet_min_level!r}")
        if burst_trigger_level not in _LEVEL_RANK:
            raise ValueError(f"Unknown level: {burst_trigger_level!r}")
        if burst_threshold < 1:
            raise ValueError("burst_threshold must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")

        self._quiet_rank = _LEVEL_RANK[quiet_min_level]
        self._trigger_rank = _LEVEL_RANK[burst_trigger_level]
        self._burst_threshold = burst_threshold
        self._window = window_seconds
        self._timestamps: Deque[float] = deque()

    def _in_burst(self, now: float) -> bool:
        cutoff = now - self._window
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        return len(self._timestamps) >= self._burst_threshold

    def should_pass(self, entry: LogEntry) -> bool:
        now = time.monotonic()
        rank = _LEVEL_RANK.get((entry.level or "").lower(), 1)
        if rank >= self._trigger_rank:
            self._timestamps.append(now)
        return self._in_burst(now) or rank >= self._quiet_rank


def severity_burst_filter(
    quiet_min_level: str = "warning",
    burst_trigger_level: str = "error",
    burst_threshold: int = 3,
    window_seconds: float = 10.0,
) -> Callable[[LogEntry], LogEntry | None]:
    """Return a stateful filter that applies :class:`SeverityBurstFilter` logic."""
    sbf = SeverityBurstFilter(
        quiet_min_level=quiet_min_level,
        burst_trigger_level=burst_trigger_level,
        burst_threshold=burst_threshold,
        window_seconds=window_seconds,
    )

    def _filter(entry: LogEntry) -> LogEntry | None:
        return entry if sbf.should_pass(entry) else None

    return _filter
