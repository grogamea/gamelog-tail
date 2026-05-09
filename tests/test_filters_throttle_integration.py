"""Tests for gamelog_tail.filters_throttle_integration."""
from __future__ import annotations

import pytest

from gamelog_tail.filters_throttle_integration import (
    build_throttle_filters,
    apply_throttle_filters,
)
from gamelog_tail.parsers.base import LogEntry


def _e(msg: str = "hi", level: str = "INFO", source: str | None = "Sys") -> LogEntry:
    return LogEntry(level=level, message=msg, source=source)


class TestBuildThrottleFilters:
    def test_no_args_returns_empty_list(self):
        assert build_throttle_filters() == []

    def test_none_args_returns_empty_list(self):
        assert build_throttle_filters(max_per_window=None, window=None) == []

    def test_max_only_returns_one_filter(self):
        result = build_throttle_filters(max_per_window=3)
        assert len(result) == 1
        assert callable(result[0])

    def test_window_only_returns_one_filter(self):
        result = build_throttle_filters(window=30.0)
        assert len(result) == 1
        assert callable(result[0])

    def test_both_args_returns_one_filter(self):
        result = build_throttle_filters(max_per_window=2, window=5.0)
        assert len(result) == 1

    def test_key_forwarded_to_filter(self):
        result = build_throttle_filters(max_per_window=1, key="level")
        assert len(result) == 1

    def test_invalid_max_propagates_error(self):
        with pytest.raises(ValueError):
            build_throttle_filters(max_per_window=0)

    def test_invalid_key_propagates_error(self):
        with pytest.raises(ValueError):
            build_throttle_filters(max_per_window=1, key="bad")


class TestApplyThrottleFilters:
    def test_empty_filters_passes_entry(self):
        entry = _e()
        assert apply_throttle_filters(entry, []) is entry

    def test_passes_entry_within_limit(self):
        filters = build_throttle_filters(max_per_window=2, window=60.0)
        assert apply_throttle_filters(_e(), filters) is not None

    def test_suppresses_entry_over_limit(self):
        filters = build_throttle_filters(max_per_window=1, window=60.0)
        apply_throttle_filters(_e(), filters)  # consume the allowance
        assert apply_throttle_filters(_e(), filters) is None

    def test_none_short_circuits(self):
        # Manually inject a filter that always blocks
        always_block = lambda e: None  # noqa: E731
        never_called = lambda e: (_ for _ in ()).throw(AssertionError("should not be called"))  # noqa: E731
        result = apply_throttle_filters(None, [always_block, never_called])
        assert result is None
