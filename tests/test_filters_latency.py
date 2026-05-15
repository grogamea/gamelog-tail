"""Tests for gamelog_tail.filters_latency."""
from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_latency import latency_threshold_filter


def _e(message: str, source: str | None = None) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        level="INFO",
        message=message,
        source=source,
    )


class TestLatencyThresholdFilterConstruction:
    def test_returns_callable(self):
        f = latency_threshold_filter(100.0)
        assert callable(f)

    def test_invalid_zero_max_raises(self):
        with pytest.raises(ValueError, match="max_ms must be positive"):
            latency_threshold_filter(0)

    def test_invalid_negative_max_raises(self):
        with pytest.raises(ValueError, match="max_ms must be positive"):
            latency_threshold_filter(-5.0)

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError, match="field must be"):
            latency_threshold_filter(50.0, field="level")

    def test_invalid_min_ms_negative_raises(self):
        with pytest.raises(ValueError, match="min_ms must be non-negative"):
            latency_threshold_filter(100.0, min_ms=-1.0)

    def test_min_ms_gte_max_ms_raises(self):
        with pytest.raises(ValueError, match="min_ms"):
            latency_threshold_filter(100.0, min_ms=100.0)

    def test_min_ms_greater_than_max_ms_raises(self):
        with pytest.raises(ValueError, match="min_ms"):
            latency_threshold_filter(100.0, min_ms=200.0)


class TestLatencyThresholdFilterBehaviour:
    def test_passes_entry_above_threshold(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("render latency=150ms done")) is True

    def test_blocks_entry_at_threshold(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("render latency=100ms done")) is False

    def test_blocks_entry_below_threshold(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("render latency=50ms done")) is False

    def test_no_latency_token_blocked(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("no timing info here")) is False

    def test_colon_separator_accepted(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("net latency: 200 ms")) is True

    def test_case_insensitive(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("LATENCY=500")) is True

    def test_float_latency_value(self):
        f = latency_threshold_filter(100.0)
        assert f(_e("latency=100.1")) is True

    def test_source_field_scanned(self):
        f = latency_threshold_filter(50.0, field="source")
        entry = _e("normal message", source="net/latency=75")
        assert f(entry) is True

    def test_source_field_no_match(self):
        f = latency_threshold_filter(50.0, field="source")
        entry = _e("latency=200", source="renderer")
        assert f(entry) is False

    def test_min_ms_lower_bound_respected(self):
        f = latency_threshold_filter(200.0, min_ms=100.0)
        # value=150 is NOT > max_ms=200, so blocked
        assert f(_e("latency=150")) is False

    def test_min_ms_passes_above_max(self):
        f = latency_threshold_filter(200.0, min_ms=100.0)
        assert f(_e("latency=250")) is True

    def test_min_ms_blocks_below_min(self):
        f = latency_threshold_filter(200.0, min_ms=100.0)
        # value=50 <= min_ms=100
        assert f(_e("latency=50")) is False
