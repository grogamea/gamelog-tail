"""Tests for gamelog_tail.filters_severity."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_severity import (
    SeverityBurstFilter,
    severity_burst_filter,
)


def _e(level: str, msg: str = "msg") -> LogEntry:
    return LogEntry(level=level, message=msg, source=None, timestamp=None, raw=msg)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestSeverityBurstFilterConstruction:
    def test_valid_construction(self):
        sbf = SeverityBurstFilter()
        assert sbf is not None

    def test_invalid_quiet_level_raises(self):
        with pytest.raises(ValueError, match="Unknown level"):
            SeverityBurstFilter(quiet_min_level="verbose")

    def test_invalid_trigger_level_raises(self):
        with pytest.raises(ValueError, match="Unknown level"):
            SeverityBurstFilter(burst_trigger_level="critical")

    def test_burst_threshold_zero_raises(self):
        with pytest.raises(ValueError, match="burst_threshold"):
            SeverityBurstFilter(burst_threshold=0)

    def test_window_zero_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            SeverityBurstFilter(window_seconds=0.0)


# ---------------------------------------------------------------------------
# Quiet period behaviour
# ---------------------------------------------------------------------------

class TestQuietPeriod:
    def _make(self) -> SeverityBurstFilter:
        return SeverityBurstFilter(
            quiet_min_level="warning",
            burst_trigger_level="error",
            burst_threshold=3,
            window_seconds=5.0,
        )

    def test_debug_blocked_in_quiet(self):
        sbf = self._make()
        assert sbf.should_pass(_e("debug")) is False

    def test_info_blocked_in_quiet(self):
        sbf = self._make()
        assert sbf.should_pass(_e("info")) is False

    def test_warning_passes_in_quiet(self):
        sbf = self._make()
        assert sbf.should_pass(_e("warning")) is True

    def test_error_passes_in_quiet(self):
        sbf = self._make()
        assert sbf.should_pass(_e("error")) is True


# ---------------------------------------------------------------------------
# Burst detection
# ---------------------------------------------------------------------------

class TestBurstDetection:
    def _make(self) -> SeverityBurstFilter:
        return SeverityBurstFilter(
            quiet_min_level="warning",
            burst_trigger_level="error",
            burst_threshold=3,
            window_seconds=5.0,
        )

    def test_burst_allows_debug(self):
        sbf = self._make()
        t = 100.0
        with patch("gamelog_tail.filters_severity.time.monotonic", side_effect=[t, t, t, t]):
            sbf.should_pass(_e("error"))
            sbf.should_pass(_e("error"))
            sbf.should_pass(_e("error"))
            assert sbf.should_pass(_e("debug")) is True

    def test_expired_timestamps_not_counted(self):
        sbf = self._make()
        early = 0.0
        later = 10.0
        with patch("gamelog_tail.filters_severity.time.monotonic", side_effect=[early, early, early, later]):
            sbf.should_pass(_e("error"))
            sbf.should_pass(_e("error"))
            sbf.should_pass(_e("error"))
            # window has passed — should be quiet again
            assert sbf.should_pass(_e("debug")) is False


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

class TestSeverityBurstFilterFactory:
    def test_returns_callable(self):
        f = severity_burst_filter()
        assert callable(f)

    def test_passes_warning_in_quiet(self):
        f = severity_burst_filter(quiet_min_level="warning")
        assert f(_e("warning")) is not None

    def test_blocks_info_in_quiet(self):
        f = severity_burst_filter(quiet_min_level="warning")
        assert f(_e("info")) is None
