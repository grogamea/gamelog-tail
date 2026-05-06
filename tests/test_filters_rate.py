"""Tests for gamelog_tail.filters_rate."""
from __future__ import annotations

import time

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_rate import rate_limit_filter


def _e(msg: str = "msg", source: str = "Src") -> LogEntry:
    return LogEntry(timestamp=None, level="INFO", message=msg, source=source, raw=msg)


class TestRateLimitFilter:
    def test_returns_callable(self):
        f = rate_limit_filter()
        assert callable(f)

    def test_passes_entries_within_limit(self):
        f = rate_limit_filter(max_per_window=5, window_seconds=60)
        entries = [_e() for _ in range(5)]
        result = list(f(iter(entries)))
        assert len(result) == 5

    def test_suppresses_excess_entries(self):
        f = rate_limit_filter(max_per_window=2, window_seconds=60)
        entries = [_e() for _ in range(5)]
        result = list(f(iter(entries)))
        # Only first 2 pass; rest are suppressed (no notice yet in same window)
        assert len(result) == 2

    def test_independent_limiters_per_call(self):
        """Each call to rate_limit_filter creates an independent limiter."""
        f1 = rate_limit_filter(max_per_window=1, window_seconds=60)
        f2 = rate_limit_filter(max_per_window=1, window_seconds=60)
        e = _e()
        r1 = list(f1([e]))
        r2 = list(f2([e]))
        assert len(r1) == 1
        assert len(r2) == 1

    def test_notice_emitted_after_window_expires(self):
        f = rate_limit_filter(max_per_window=1, window_seconds=0.05)
        entries = [_e(), _e()]  # second is suppressed
        list(f(iter(entries)))
        time.sleep(0.06)
        result = list(f(iter([_e()])))
        assert any("suppressed" in r.message for r in result)

    def test_empty_stream(self):
        f = rate_limit_filter()
        assert list(f(iter([]))) == []
