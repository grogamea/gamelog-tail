"""Tests for gamelog_tail.filters_session."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_session import session_filter


def _e(msg: str, source: str = "engine") -> LogEntry:
    return LogEntry(level="INFO", message=msg, source=source, timestamp=None, raw=msg)


class TestSessionFilterConstruction:
    def test_returns_callable(self):
        f = session_filter(sentinel=r"Session start")
        assert callable(f)

    def test_empty_sentinel_raises(self):
        with pytest.raises(ValueError, match="sentinel"):
            session_filter(sentinel="")

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError, match="field"):
            session_filter(sentinel=r"start", field="level")

    def test_empty_keep_sessions_raises(self):
        with pytest.raises(ValueError, match="keep_sessions"):
            session_filter(sentinel=r"start", keep_sessions=set())


class TestSessionFilterBehaviour:
    def test_entries_before_first_sentinel_are_dropped(self):
        f = session_filter(sentinel=r"START")
        assert f(_e("hello")) is None

    def test_sentinel_entry_itself_is_kept_in_session_1(self):
        f = session_filter(sentinel=r"START")
        entry = _e("START")
        assert f(entry) is entry

    def test_entries_after_sentinel_are_kept(self):
        f = session_filter(sentinel=r"START")
        f(_e("START"))  # triggers session 1
        entry = _e("normal log")
        assert f(entry) is entry

    def test_keep_sessions_filters_to_specified_session(self):
        f = session_filter(sentinel=r"START", keep_sessions={2})
        f(_e("START"))  # session 1
        assert f(_e("session 1 entry")) is None
        f(_e("START"))  # session 2
        entry = _e("session 2 entry")
        assert f(entry) is entry

    def test_keep_sessions_multiple(self):
        f = session_filter(sentinel=r"START", keep_sessions={1, 3})
        f(_e("START"))  # session 1
        assert f(_e("s1")) is not None
        f(_e("START"))  # session 2
        assert f(_e("s2")) is None
        f(_e("START"))  # session 3
        assert f(_e("s3")) is not None

    def test_field_source_matches_on_source(self):
        f = session_filter(sentinel=r"boot", field="source")
        assert f(_e("anything", source="boot-loader")) is not None

    def test_none_keep_sessions_keeps_all_sessions(self):
        f = session_filter(sentinel=r"START", keep_sessions=None)
        f(_e("START"))  # session 1
        f(_e("START"))  # session 2
        assert f(_e("any")) is not None
