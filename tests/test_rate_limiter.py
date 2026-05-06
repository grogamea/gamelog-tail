"""Tests for gamelog_tail.rate_limiter."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.rate_limiter import RateLimiter


def _e(msg: str = "hello", level: str = "INFO", source: str | None = "Game") -> LogEntry:
    return LogEntry(timestamp=None, level=level, message=msg, source=source, raw=msg)


class TestRateLimiterInit:
    def test_invalid_max(self):
        with pytest.raises(ValueError):
            RateLimiter(max_per_window=0)

    def test_invalid_window(self):
        with pytest.raises(ValueError):
            RateLimiter(window_seconds=0)


class TestFeedWithinLimit:
    def test_first_entry_passes(self):
        rl = RateLimiter(max_per_window=3, window_seconds=60)
        result = list(rl.feed(_e()))
        assert len(result) == 1
        assert result[0].message == "hello"

    def test_entries_up_to_limit_all_pass(self):
        rl = RateLimiter(max_per_window=3, window_seconds=60)
        results = []
        for _ in range(3):
            results.extend(rl.feed(_e()))
        assert len(results) == 3

    def test_different_sources_tracked_separately(self):
        rl = RateLimiter(max_per_window=1, window_seconds=60)
        r1 = list(rl.feed(_e(source="A")))
        r2 = list(rl.feed(_e(source="B")))
        assert len(r1) == 1
        assert len(r2) == 1


class TestFeedExceedsLimit:
    def test_excess_entry_is_suppressed(self):
        rl = RateLimiter(max_per_window=2, window_seconds=60)
        list(rl.feed(_e()))  # 1
        list(rl.feed(_e()))  # 2
        result = list(rl.feed(_e()))  # 3 — over limit
        assert result == []

    def test_suppression_notice_emitted_on_next_window(self):
        rl = RateLimiter(max_per_window=1, window_seconds=0.05)
        list(rl.feed(_e()))  # passes
        list(rl.feed(_e()))  # suppressed
        time.sleep(0.06)  # new window
        result = list(rl.feed(_e()))
        # Should contain notice + the new entry
        assert len(result) == 2
        messages = [r.message for r in result]
        assert any("suppressed" in m for m in messages)

    def test_notice_has_warning_level(self):
        rl = RateLimiter(max_per_window=1, window_seconds=0.05)
        list(rl.feed(_e()))
        list(rl.feed(_e()))  # suppressed
        time.sleep(0.06)
        result = list(rl.feed(_e()))
        notice = next(r for r in result if "suppressed" in r.message)
        assert notice.level == "WARNING"


class TestWindowReset:
    def test_count_resets_after_window(self):
        rl = RateLimiter(max_per_window=2, window_seconds=0.05)
        list(rl.feed(_e()))
        list(rl.feed(_e()))
        time.sleep(0.06)
        result = list(rl.feed(_e()))
        # After window reset, entry should pass (ignoring any notice)
        normal = [r for r in result if "suppressed" not in r.message]
        assert len(normal) == 1
