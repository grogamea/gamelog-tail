"""Tests for gamelog_tail.filters_context_integration."""
from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_context_integration import (
    build_context_filters,
    apply_context_filters,
)


def _e(msg: str, level: str = "INFO") -> LogEntry:
    return LogEntry(level=level, message=msg)


class TestBuildContextFilters:
    def test_no_args_returns_empty(self):
        assert build_context_filters() == []

    def test_none_args_returns_empty(self):
        assert build_context_filters(level=None, pattern=None) == []

    def test_level_returns_one_filter(self):
        result = build_context_filters(level="ERROR")
        assert len(result) == 1 and callable(result[0])

    def test_pattern_returns_one_filter(self):
        result = build_context_filters(pattern="crash")
        assert len(result) == 1 and callable(result[0])

    def test_level_and_pattern_returns_one_filter(self):
        result = build_context_filters(level="ERROR", pattern="crash")
        assert len(result) == 1


class TestBuildContextFiltersBehaviour:
    def test_level_trigger(self):
        filters = build_context_filters(level="ERROR", before=1, after=1)
        entries = [_e("a"), _e("b", "ERROR"), _e("c")]
        result = list(apply_context_filters(entries, filters))
        assert result == entries

    def test_pattern_trigger(self):
        filters = build_context_filters(pattern="boom", before=0, after=1)
        entries = [_e("boom"), _e("aftermath"), _e("unrelated")]
        result = list(apply_context_filters(entries, filters))
        assert result == [entries[0], entries[1]]

    def test_either_predicate_triggers(self):
        filters = build_context_filters(
            level="ERROR", pattern="boom", before=0, after=0
        )
        entries = [_e("boom"), _e("quiet"), _e("x", "ERROR")]
        result = list(apply_context_filters(entries, filters))
        assert result == [entries[0], entries[2]]

    def test_no_match_emits_nothing(self):
        filters = build_context_filters(level="ERROR", before=1, after=1)
        entries = [_e("a"), _e("b"), _e("c")]
        result = list(apply_context_filters(entries, filters))
        assert result == []


class TestApplyContextFilters:
    def test_empty_filters_passes_all(self):
        entries = [_e("a"), _e("b")]
        result = list(apply_context_filters(entries, []))
        assert result == entries
