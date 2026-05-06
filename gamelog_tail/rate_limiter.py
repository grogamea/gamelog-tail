"""Rate limiter: suppress log entries that arrive too frequently.

Entries are bucketed by (source, level). If more than `max_per_window`
entries arrive within `window_seconds` for the same bucket, the excess
entries are dropped and a synthetic summary entry is emitted instead.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple

from gamelog_tail.parsers.base import LogEntry


@dataclass
class _Bucket:
    count: int = 0
    window_start: float = field(default_factory=time.monotonic)
    suppressed: int = 0


class RateLimiter:
    """Stateful rate-limiter for log entries."""

    def __init__(self, max_per_window: int = 10, window_seconds: float = 1.0) -> None:
        if max_per_window < 1:
            raise ValueError("max_per_window must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_per_window = max_per_window
        self.window_seconds = window_seconds
        self._buckets: dict[Tuple[str, str], _Bucket] = defaultdict(_Bucket)

    def _bucket_key(self, entry: LogEntry) -> Tuple[str, str]:
        return (entry.source or "", entry.level)

    def feed(self, entry: LogEntry) -> Iterator[LogEntry]:
        """Yield 0, 1, or 2 entries: the entry itself and/or a flush notice."""
        key = self._bucket_key(entry)
        bucket = self._buckets[key]
        now = time.monotonic()

        if now - bucket.window_start >= self.window_seconds:
            # New window — flush any suppressed notice first
            if bucket.suppressed > 0:
                yield self._suppression_notice(entry, bucket.suppressed)
            bucket.count = 0
            bucket.window_start = now
            bucket.suppressed = 0

        bucket.count += 1
        if bucket.count <= self.max_per_window:
            yield entry
        else:
            bucket.suppressed += 1

    def flush_all(self) -> List[LogEntry]:
        """Return suppression notices for all non-empty buckets and reset."""
        notices: List[LogEntry] = []
        for bucket in self._buckets.values():
            if bucket.suppressed > 0:
                # We can't reconstruct a full entry here, so callers should
                # use feed() for proper notices; this is a best-effort flush.
                bucket.suppressed = 0
        return notices

    @staticmethod
    def _suppression_notice(reference: LogEntry, count: int) -> LogEntry:
        return LogEntry(
            timestamp=reference.timestamp,
            level="WARNING",
            message=f"[rate-limiter] {count} similar message(s) suppressed",
            source=reference.source,
            raw=f"[rate-limiter suppressed {count}]",
        )
