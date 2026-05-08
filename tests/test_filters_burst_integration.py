"""Tests for gamelog_tail.filters_burst_integration."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gamelog_tail.filters_burst_integration import (
    apply_burst_filters,
    build_burst_filters,
)
from gamelog_tail.parsers.base import LogEntry


def _e(message: str = "msg", level: str = "INFO") -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 6, 1, tzinfo=timezone.utc),
        level=level,
        message=message,
        source=None,
    )


class TestBuildBurstFilters:
    def test_no_args_returns_empty_list(self):
        assert build_burst_filters() == []

    def test_none_args_returns_empty_list(self):
        assert build_burst_filters(max_count=None, window_seconds=None) == []

    def test_max_count_only_returns_one_filter(self):
        result = build_burst_filters(max_count=2)
        assert len(result) == 1
        assert callable(result[0])

    def test_window_only_returns_one_filter(self):
        result = build_burst_filters(window_seconds=3.0)
        assert len(result) == 1

    def test_both_args_returns_one_filter(self):
        result = build_burst_filters(max_count=5, window_seconds=10.0)
        assert len(result) == 1

    def test_key_fields_forwarded(self):
        result = build_burst_filters(max_count=1, key_fields=("level", "message"))
        assert len(result) == 1

    def test_invalid_max_count_propagates(self):
        with pytest.raises(ValueError):
            build_burst_filters(max_count=0)

    def test_invalid_window_propagates(self):
        with pytest.raises(ValueError):
            build_burst_filters(window_seconds=-5)


class TestApplyBurstFilters:
    def test_empty_filters_passes_entry(self):
        assert apply_burst_filters([], _e()) is not None

    def test_passes_entry_within_limit(self):
        filters = build_burst_filters(max_count=3, window_seconds=10)
        assert apply_burst_filters(filters, _e()) is not None

    def test_suppresses_entry_over_limit(self):
        filters = build_burst_filters(max_count=1, window_seconds=10)
        apply_burst_filters(filters, _e())
        result = apply_burst_filters(filters, _e())
        assert result is None

    def test_returns_none_if_any_filter_suppresses(self):
        # Two independent filters; first one will suppress on second call
        f1 = build_burst_filters(max_count=1, window_seconds=10)
        f2 = build_burst_filters(max_count=5, window_seconds=10)
        combined = f1 + f2
        apply_burst_filters(combined, _e())
        assert apply_burst_filters(combined, _e()) is None
