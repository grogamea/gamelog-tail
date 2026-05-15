"""Tests for gamelog_tail.filters_session_integration."""

from __future__ import annotations

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_session_integration import (
    build_session_filters,
    apply_session_filters,
)


def _e(msg: str) -> LogEntry:
    return LogEntry(level="INFO", message=msg, source="engine", timestamp=None, raw=msg)


class TestBuildSessionFilters:
    def test_no_sentinel_returns_empty(self):
        assert build_session_filters() == []

    def test_none_sentinel_returns_empty(self):
        assert build_session_filters(sentinel=None) == []

    def test_empty_string_sentinel_returns_empty(self):
        assert build_session_filters(sentinel="") == []

    def test_valid_sentinel_returns_one_filter(self):
        filters = build_session_filters(sentinel=r"START")
        assert len(filters) == 1
        assert callable(filters[0])

    def test_keep_sessions_forwarded(self):
        filters = build_session_filters(sentinel=r"START", keep_sessions={1})
        assert len(filters) == 1


class TestApplySessionFilters:
    def test_empty_filters_returns_all(self):
        entries = [_e("a"), _e("b")]
        assert apply_session_filters(entries, []) == entries

    def test_filter_applied_to_entries(self):
        filters = build_session_filters(sentinel=r"START", keep_sessions={1})
        entries = [_e("START"), _e("hello"), _e("START"), _e("second session")]
        result = apply_session_filters(entries, filters)
        messages = [e.message for e in result]
        assert "START" in messages
        assert "hello" in messages
        assert "second session" not in messages

    def test_pre_sentinel_entries_dropped(self):
        filters = build_session_filters(sentinel=r"START")
        entries = [_e("early"), _e("START"), _e("after")]
        result = apply_session_filters(entries, filters)
        assert all(e.message != "early" for e in result)
