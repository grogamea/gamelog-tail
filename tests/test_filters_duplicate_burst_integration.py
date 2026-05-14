"""Tests for gamelog_tail.filters_duplicate_burst_integration."""
from __future__ import annotations

import pytest

from gamelog_tail.filters_duplicate_burst_integration import (
    apply_duplicate_burst_filters,
    build_duplicate_burst_filters,
)
from gamelog_tail.parsers.base import LogEntry


def _e(message: str = "msg", level: str = "INFO") -> LogEntry:
    return LogEntry(level=level, message=message)


class TestBuildDuplicateBurstFilters:
    def test_no_args_returns_empty_list(self):
        result = build_duplicate_burst_filters()
        assert result == []

    def test_none_args_returns_empty_list(self):
        result = build_duplicate_burst_filters(max_repeats=None, window_seconds=None)
        assert result == []

    def test_max_repeats_only_returns_one_filter(self):
        result = build_duplicate_burst_filters(max_repeats=2)
        assert len(result) == 1
        assert callable(result[0])

    def test_window_only_returns_one_filter(self):
        result = build_duplicate_burst_filters(window_seconds=30.0)
        assert len(result) == 1
        assert callable(result[0])

    def test_both_args_returns_one_filter(self):
        result = build_duplicate_burst_filters(max_repeats=5, window_seconds=60.0)
        assert len(result) == 1

    def test_custom_key_fields_propagated(self):
        result = build_duplicate_burst_filters(
            max_repeats=2, key_fields=("message",)
        )
        assert len(result) == 1

    def test_invalid_max_repeats_raises(self):
        with pytest.raises(ValueError):
            build_duplicate_burst_filters(max_repeats=0)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            build_duplicate_burst_filters(window_seconds=-5.0)


class TestApplyDuplicateBurstFilters:
    def test_empty_filters_always_passes(self):
        assert apply_duplicate_burst_filters([], _e()) is True

    def test_passes_when_within_limit(self):
        filters = build_duplicate_burst_filters(max_repeats=3)
        entry = _e("hello")
        for _ in range(3):
            assert apply_duplicate_burst_filters(filters, entry) is True

    def test_suppresses_when_over_limit(self):
        filters = build_duplicate_burst_filters(max_repeats=2)
        entry = _e("boom")
        apply_duplicate_burst_filters(filters, entry)
        apply_duplicate_burst_filters(filters, entry)
        assert apply_duplicate_burst_filters(filters, entry) is False

    def test_different_messages_not_suppressed(self):
        filters = build_duplicate_burst_filters(max_repeats=1)
        assert apply_duplicate_burst_filters(filters, _e("a")) is True
        assert apply_duplicate_burst_filters(filters, _e("b")) is True
