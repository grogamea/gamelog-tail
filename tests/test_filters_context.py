"""Tests for gamelog_tail.filters_context."""
from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_context import context_window_filter


def _e(msg: str, level: str = "INFO") -> LogEntry:
    return LogEntry(level=level, message=msg)


def _is_error(entry: LogEntry) -> bool:
    return entry.level == "ERROR"


class TestContextWindowFilterConstruction:
    def test_returns_callable(self):
        f = context_window_filter(_is_error)
        assert callable(f)

    def test_negative_before_raises(self):
        with pytest.raises(ValueError, match="before"):
            context_window_filter(_is_error, before=-1)

    def test_negative_after_raises(self):
        with pytest.raises(ValueError, match="after"):
            context_window_filter(_is_error, after=-1)

    def test_zero_before_and_after_allowed(self):
        f = context_window_filter(_is_error, before=0, after=0)
        assert callable(f)


class TestContextWindowFilterBehaviour:
    def test_emits_only_trigger_when_no_context(self):
        f = context_window_filter(_is_error, before=0, after=0)
        entries = [_e("a"), _e("b", "ERROR"), _e("c")]
        result = list(f(entries))
        assert result == [entries[1]]

    def test_emits_pre_context(self):
        f = context_window_filter(_is_error, before=2, after=0)
        entries = [_e("a"), _e("b"), _e("c", "ERROR"), _e("d")]
        result = list(f(entries))
        assert result == [entries[0], entries[1], entries[2]]

    def test_emits_post_context(self):
        f = context_window_filter(_is_error, before=0, after=2)
        entries = [_e("a", "ERROR"), _e("b"), _e("c"), _e("d")]
        result = list(f(entries))
        assert result == [entries[0], entries[1], entries[2]]

    def test_emits_both_contexts(self):
        f = context_window_filter(_is_error, before=1, after=1)
        entries = [_e("a"), _e("b", "ERROR"), _e("c"), _e("d")]
        result = list(f(entries))
        assert result == [entries[0], entries[1], entries[2]]

    def test_no_trigger_emits_nothing(self):
        f = context_window_filter(_is_error, before=2, after=2)
        entries = [_e("a"), _e("b"), _e("c")]
        result = list(f(entries))
        assert result == []

    def test_consecutive_triggers_merged(self):
        f = context_window_filter(_is_error, before=1, after=1)
        entries = [
            _e("a"),
            _e("b", "ERROR"),
            _e("c", "ERROR"),
            _e("d"),
            _e("e"),
        ]
        result = list(f(entries))
        # a(pre), b(trigger), c(trigger+post-of-b), d(post-of-c)
        assert result == [entries[0], entries[1], entries[2], entries[3]]

    def test_pre_context_capped_at_available(self):
        f = context_window_filter(_is_error, before=5, after=0)
        entries = [_e("a"), _e("b", "ERROR")]
        result = list(f(entries))
        assert result == [entries[0], entries[1]]

    def test_empty_stream(self):
        f = context_window_filter(_is_error, before=2, after=2)
        assert list(f([])) == []
