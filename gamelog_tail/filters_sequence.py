"""
filters_sequence.py – Filter that detects ordered sequences of log patterns
and emits an alert entry when the full sequence is matched within a time window.
"""
from __future__ import annotations

import re
import time
from typing import Callable, Iterable, List, Optional

from gamelog_tail.parsers.base import LogEntry


class _SequenceTracker:
    """Tracks progress through an ordered list of regex patterns."""

    def __init__(self, patterns: List[str], window: float) -> None:
        self._patterns = [re.compile(p) for p in patterns]
        self._window = window
        self._index = 0
        self._start: Optional[float] = None

    def feed(self, entry: LogEntry) -> bool:
        """Return True when the final pattern in the sequence is matched."""
        now = time.monotonic()

        # Reset if the time window has expired
        if self._start is not None and (now - self._start) > self._window:
            self._index = 0
            self._start = None

        if self._patterns[self._index].search(entry.message):
            if self._index == 0:
                self._start = now
            self._index += 1
            if self._index == len(self._patterns):
                self._index = 0
                self._start = None
                return True
        return False


def sequence_filter(
    patterns: Iterable[str],
    window: float = 60.0,
    alert_level: str = "ERROR",
    alert_source: str = "sequence_filter",
) -> Callable[[LogEntry], Iterable[LogEntry]]:
    """Return a stateful filter that watches for an ordered pattern sequence.

    When all *patterns* are matched in order within *window* seconds the filter
    emits a synthetic alert :class:`LogEntry` in addition to the triggering
    entry.  Non-matching entries are passed through unchanged.

    Args:
        patterns:     Ordered list of regex strings to match against ``message``.
        window:       Maximum seconds allowed between first and last pattern match.
        alert_level:  Level assigned to the synthetic alert entry.
        alert_source: Source assigned to the synthetic alert entry.

    Raises:
        ValueError: If fewer than two patterns are supplied or *window* <= 0.
    """
    pattern_list = list(patterns)
    if len(pattern_list) < 2:
        raise ValueError("sequence_filter requires at least two patterns")
    if window <= 0:
        raise ValueError("window must be positive")

    tracker = _SequenceTracker(pattern_list, window)

    def _filter(entry: LogEntry) -> Iterable[LogEntry]:
        yield entry
        if tracker.feed(entry):
            yield LogEntry(
                level=alert_level,
                message=(
                    f"Sequence detected: {len(pattern_list)} patterns matched "
                    f"within {window}s"
                ),
                source=alert_source,
                timestamp=entry.timestamp,
                raw=entry.raw,
            )

    return _filter
