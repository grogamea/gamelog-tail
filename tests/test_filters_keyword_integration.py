"""Tests for gamelog_tail.filters_keyword_integration."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_keyword_integration import (
    build_keyword_filters,
    apply_keyword_filters,
)


def _e(message: str, level: str = "INFO") -> LogEntry:
    return LogEntry(level=level, message=message)


_ENTRIES = [
    _e("player spawned"),
    _e("crash detected in physics"),
    _e("heartbeat ok"),
    _e("fatal error in renderer"),
    _e("heartbeat ok"),
]


class TestBuildKeywordFilters:
    def test_empty_args_returns_empty_list(self):
        assert build_keyword_filters() == []

    def test_none_args_returns_empty_list(self):
        assert build_keyword_filters(None, None) == []

    def test_allow_returns_one_filter(self):
        filters = build_keyword_filters(keyword_allow=["crash"])
        assert len(filters) == 1

    def test_deny_returns_one_filter(self):
        filters = build_keyword_filters(keyword_deny=["heartbeat"])
        assert len(filters) == 1

    def test_both_returns_two_filters(self):
        filters = build_keyword_filters(
            keyword_allow=["crash", "fatal"],
            keyword_deny=["heartbeat"],
        )
        assert len(filters) == 2

    def test_empty_sequence_not_added(self):
        filters = build_keyword_filters(keyword_allow=[], keyword_deny=[])
        assert filters == []


class TestApplyKeywordFilters:
    def test_no_filters_returns_all(self):
        result = apply_keyword_filters(_ENTRIES)
        assert result == _ENTRIES

    def test_allow_filter_keeps_matching(self):
        result = apply_keyword_filters(_ENTRIES, keyword_allow=["crash", "fatal"])
        messages = [e.message for e in result]
        assert "crash detected in physics" in messages
        assert "fatal error in renderer" in messages
        assert "player spawned" not in messages

    def test_deny_filter_removes_matching(self):
        result = apply_keyword_filters(_ENTRIES, keyword_deny=["heartbeat"])
        messages = [e.message for e in result]
        assert all("heartbeat" not in m for m in messages)
        assert len(result) == 3

    def test_combined_allow_and_deny(self):
        result = apply_keyword_filters(
            _ENTRIES,
            keyword_allow=["crash", "fatal", "heartbeat"],
            keyword_deny=["heartbeat"],
        )
        messages = [e.message for e in result]
        assert "crash detected in physics" in messages
        assert "fatal error in renderer" in messages
        assert all("heartbeat" not in m for m in messages)

    def test_returns_list(self):
        result = apply_keyword_filters(_ENTRIES)
        assert isinstance(result, list)
