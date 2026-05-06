"""Deduplication filter: suppress repeated identical log lines within a time window."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Optional, Tuple

from gamelog_tail.parsers.base import LogEntry


class Deduplicator:
    """Suppress consecutive duplicate log entries within *window_seconds*.

    Two entries are considered duplicates when they share the same
    ``level``, ``source``, and ``message``.  Timestamp differences are
    ignored so that rapidly repeating lines are collapsed.

    Args:
        window_seconds: How long (in seconds) a seen entry is remembered.
            Pass 0 to deduplicate only *immediately* adjacent duplicates.
        max_tracked: Maximum number of distinct entries to track at once.
    """

    def __init__(self, window_seconds: float = 5.0, max_tracked: int = 256) -> None:
        self._window = timedelta(seconds=window_seconds)
        self._max_tracked = max_tracked
        # Each element: (key, first_seen_at, count)
        self._seen: Deque[Tuple[Tuple, datetime, int]] = deque()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_duplicate(self, entry: LogEntry) -> bool:
        """Return ``True`` if *entry* is a duplicate and should be suppressed."""
        now = entry.timestamp or datetime.utcnow()
        key = self._key(entry)
        self._expire(now)

        for i, (seen_key, first_seen, _count) in enumerate(self._seen):
            if seen_key == key:
                # Refresh count in-place
                self._seen[i] = (seen_key, first_seen, _count + 1)
                return True

        # New entry — track it
        if len(self._seen) >= self._max_tracked:
            self._seen.popleft()
        self._seen.append((key, now, 1))
        return False

    def reset(self) -> None:
        """Clear all tracked entries."""
        self._seen.clear()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _key(entry: LogEntry) -> Tuple:
        return (entry.level, entry.source, entry.message)

    def _expire(self, now: datetime) -> None:
        while self._seen and (now - self._seen[0][1]) > self._window:
            self._seen.popleft()


def build_deduplicator(window_seconds: float = 5.0) -> Deduplicator:
    """Convenience factory used by the pipeline."""
    return Deduplicator(window_seconds=window_seconds)
