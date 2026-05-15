"""Tests for gamelog_tail.filters_latency_integration."""
from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_latency_integration import (
    build_latency_filters,
    apply_latency_filters,
)


def _e(message: str) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 0, 0, 0),
        level="DEBUG",
        message=message,
        source=None,
    )


class TestBuildLatencyFilters:
    def test_no_max_ms_returns_empty(self):
        assert build_latency_filters() == []

    def test_none_max_ms_returns_empty(self):
        assert build_latency_filters(max_ms=None) == []

    def test_max_ms_returns_one_filter(self):
        result = build_latency_filters(max_ms=100.0)
        assert len(result) == 1
        assert callable(result[0])

    def test_filter_passes_high_latency(self):
        filters = build_latency_filters(max_ms=100.0)
        assert apply_latency_filters(filters, _e("latency=200")) is True

    def test_filter_blocks_low_latency(self):
        filters = build_latency_filters(max_ms=100.0)
        assert apply_latency_filters(filters, _e("latency=50")) is False

    def test_with_min_ms_forwarded(self):
        filters = build_latency_filters(max_ms=200.0, min_ms=50.0)
        assert len(filters) == 1
        # 100 is NOT > max_ms=200, so blocked
        assert apply_latency_filters(filters, _e("latency=100")) is False
        assert apply_latency_filters(filters, _e("latency=300")) is True

    def test_field_forwarded(self):
        filters = build_latency_filters(max_ms=50.0, field="source")
        entry = LogEntry(
            timestamp=datetime(2024, 1, 1),
            level="INFO",
            message="plain message",
            source="net/latency=80",
        )
        assert apply_latency_filters(filters, entry) is True


class TestApplyLatencyFilters:
    def test_empty_filters_passes_everything(self):
        assert apply_latency_filters([], _e("latency=999")) is True
        assert apply_latency_filters([], _e("no timing")) is True
