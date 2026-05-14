"""Tests for gamelog_tail.filters_window."""
from __future__ import annotations

import time
from datetime import datetime
from unittest.mock import patch

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_window import sliding_window_filter


def _e(
    msg: str = "hello",
    level: str = "INFO",
    source: str = "Game",
) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        level=level,
        message=msg,
        source=source,
        raw=msg,
    )


class TestSlidingWindowFilterConstruction:
    def test_returns_callable(self):
        f = sliding_window_filter(3, 5.0)
        assert callable(f)

    def test_invalid_max_count_zero_raises(self):
        with pytest.raises(ValueError, match="max_count"):
            sliding_window_filter(0, 5.0)

    def test_invalid_max_count_negative_raises(self):
        with pytest.raises(ValueError, match="max_count"):
            sliding_window_filter(-1, 5.0)

    def test_invalid_window_zero_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            sliding_window_filter(3, 0.0)

    def test_invalid_window_negative_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            sliding_window_filter(3, -1.0)

    def test_invalid_key_raises(self):
        with pytest.raises(ValueError, match="key"):
            sliding_window_filter(3, 5.0, key="message")


class TestSlidingWindowFilterBehaviour:
    def test_passes_entries_within_limit(self):
        f = sliding_window_filter(3, 10.0)
        results = [f(_e()) for _ in range(3)]
        assert all(results)

    def test_suppresses_excess_entries(self):
        f = sliding_window_filter(2, 10.0)
        results = [f(_e()) for _ in range(4)]
        assert results == [True, True, False, False]

    def test_different_sources_tracked_independently(self):
        f = sliding_window_filter(1, 10.0)
        assert f(_e(source="A")) is True
        assert f(_e(source="B")) is True
        assert f(_e(source="A")) is False

    def test_key_level_groups_by_level(self):
        f = sliding_window_filter(1, 10.0, key="level")
        assert f(_e(level="ERROR")) is True
        assert f(_e(level="WARN")) is True
        assert f(_e(level="ERROR")) is False

    def test_old_entries_expire_from_window(self):
        """Entries older than the window should be evicted."""
        ticks = [100.0, 100.5, 106.0]  # third tick is outside 5-s window
        f = sliding_window_filter(2, 5.0)
        with patch("gamelog_tail.filters_window.time.monotonic", side_effect=ticks):
            assert f(_e()) is True   # count=1
            assert f(_e()) is True   # count=2
            assert f(_e()) is True   # first two expired; count=1

    def test_none_source_uses_empty_string_bucket(self):
        entry = LogEntry(
            timestamp=None, level="INFO", message="x", source=None, raw="x"
        )
        f = sliding_window_filter(1, 10.0)
        assert f(entry) is True
        assert f(entry) is False
