"""Log entry sampler: keeps only 1-in-N entries per source/level bucket."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Tuple

from gamelog_tail.parsers.base import LogEntry


class Sampler:
    """Passes every Nth log entry for a given (source, level) bucket.

    Parameters
    ----------
    rate:
        Keep 1 entry for every *rate* entries seen in a bucket.
        Must be >= 1.  A rate of 1 means keep everything.
    """

    def __init__(self, rate: int = 10) -> None:
        if rate < 1:
            raise ValueError(f"rate must be >= 1, got {rate}")
        self._rate = rate
        self._counters: Dict[Tuple[str, str], int] = defaultdict(int)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def should_keep(self, entry: LogEntry) -> bool:
        """Return True if this entry should be forwarded downstream."""
        key = self._bucket_key(entry)
        self._counters[key] += 1
        return self._counters[key] % self._rate == 1

    def reset(self) -> None:
        """Clear all counters (useful between log sessions)."""
        self._counters.clear()

    @property
    def rate(self) -> int:
        return self._rate

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _bucket_key(entry: LogEntry) -> Tuple[str, str]:
        source = entry.source or ""
        level = entry.level or ""
        return (source, level)


def sample_filter(rate: int = 10) -> object:
    """Return a pipeline-compatible filter that samples log entries.

    The returned callable accepts a :class:`~gamelog_tail.parsers.base.LogEntry`
    and returns ``True`` when the entry should be kept.
    """
    sampler = Sampler(rate=rate)

    def _filter(entry: LogEntry) -> bool:
        return sampler.should_keep(entry)

    _filter.__sampler__ = sampler  # expose for testing / introspection
    return _filter
