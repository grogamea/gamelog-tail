"""Tests for gamelog_tail.filters_window_integration."""
from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_window_integration import (
    apply_window_filters,
    build_window_filters,
)


def _e(msg: str = "m", source: str = "S") -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1),
        level="INFO",
        message=msg,
        source=source,
        raw=msg,
    )


class TestBuildWindowFilters:
    def test_no_args_returns_empty(self):
        assert build_window_filters() == []

    def test_none_args_returns_empty(self):
        assert build_window_filters(None, None) == []

    def test_only_max_count_returns_empty(self):
        assert build_window_filters(max_count=3) == []

    def test_only_window_returns_empty(self):
        assert build_window_filters(window_seconds=5.0) == []

    def test_both_args_returns_one_filter(self):
        filters = build_window_filters(max_count=2, window_seconds=5.0)
        assert len(filters) == 1
        assert callable(filters[0])

    def test_invalid_max_count_propagates(self):
        with pytest.raises(ValueError):
            build_window_filters(max_count=0, window_seconds=5.0)

    def test_key_forwarded(self):
        filters = build_window_filters(max_count=1, window_seconds=5.0, key="level")
        assert len(filters) == 1


class TestApplyWindowFilters:
    def test_empty_filters_passes_all(self):
        entries = [_e("a"), _e("b"), _e("c")]
        assert apply_window_filters(entries, []) == entries

    def test_filter_limits_output(self):
        filters = build_window_filters(max_count=2, window_seconds=60.0)
        entries = [_e() for _ in range(5)]
        result = apply_window_filters(entries, filters)
        assert len(result) == 2

    def test_multiple_filters_applied_in_order(self):
        f1 = build_window_filters(max_count=3, window_seconds=60.0)
        f2 = build_window_filters(max_count=2, window_seconds=60.0, key="level")
        entries = [_e() for _ in range(5)]
        # f1 alone keeps 3; f2 (applied on those 3) keeps 2
        result = apply_window_filters(entries, f1 + f2)
        assert len(result) == 2
