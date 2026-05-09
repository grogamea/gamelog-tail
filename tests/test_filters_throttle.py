"""Tests for gamelog_tail.filters_throttle."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from gamelog_tail.filters_throttle import throttle_filter, _ThrottleState
from gamelog_tail.parsers.base import LogEntry


def _e(
    msg: str = "hello",
    level: str = "INFO",
    source: str | None = "Game",
) -> LogEntry:
    return LogEntry(level=level, message=msg, source=source)


class TestThrottleFilterConstruction:
    def test_returns_callable(self):
        filt = throttle_filter()
        assert callable(filt)

    def test_invalid_max_raises(self):
        with pytest.raises(ValueError, match="max_per_window"):
            throttle_filter(max_per_window=0)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError, match="window"):
            throttle_filter(window=0)

    def test_invalid_key_raises(self):
        with pytest.raises(ValueError, match="key"):
            throttle_filter(key="unknown")


class TestThrottleFilterBehaviour:
    def test_passes_entries_within_limit(self):
        filt = throttle_filter(max_per_window=3, window=60.0)
        for _ in range(3):
            assert filt(_e()) is not None

    def test_suppresses_excess_entries(self):
        filt = throttle_filter(max_per_window=2, window=60.0)
        filt(_e())
        filt(_e())
        assert filt(_e()) is None

    def test_different_sources_tracked_separately(self):
        filt = throttle_filter(max_per_window=1, window=60.0, key="source")
        assert filt(_e(source="A")) is not None
        assert filt(_e(source="B")) is not None
        assert filt(_e(source="A")) is None

    def test_different_levels_tracked_separately(self):
        filt = throttle_filter(max_per_window=1, window=60.0, key="level")
        assert filt(_e(level="INFO")) is not None
        assert filt(_e(level="ERROR")) is not None
        assert filt(_e(level="INFO")) is None

    def test_window_reset_allows_new_entries(self):
        filt = throttle_filter(max_per_window=1, window=1.0)
        assert filt(_e()) is not None
        assert filt(_e()) is None
        with patch("gamelog_tail.filters_throttle.time.monotonic", return_value=time.monotonic() + 2.0):
            assert filt(_e()) is not None

    def test_source_level_key_combines_both(self):
        filt = throttle_filter(max_per_window=1, window=60.0, key="source_level")
        assert filt(_e(source="A", level="INFO")) is not None
        assert filt(_e(source="A", level="ERROR")) is not None
        assert filt(_e(source="A", level="INFO")) is None


class TestThrottleState:
    def test_first_tick_returns_one(self):
        state = _ThrottleState(window=10.0)
        assert state.tick(0.0) == 1

    def test_consecutive_ticks_increment(self):
        state = _ThrottleState(window=10.0)
        state.tick(0.0)
        assert state.tick(1.0) == 2

    def test_tick_after_window_resets(self):
        state = _ThrottleState(window=5.0)
        state.tick(0.0)
        state.tick(1.0)
        assert state.tick(10.0) == 1
