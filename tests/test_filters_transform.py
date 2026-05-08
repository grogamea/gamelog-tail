"""Tests for gamelog_tail.filters_transform."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_transform import (
    truncate_message_filter,
    redact_pattern_filter,
    tag_source_filter,
)


def _e(
    message: str = "hello world",
    level: str = "INFO",
    source: str | None = "Engine",
    timestamp=None,
) -> LogEntry:
    return LogEntry(timestamp=timestamp, level=level, source=source, message=message, raw=message)


# ---------------------------------------------------------------------------
# truncate_message_filter
# ---------------------------------------------------------------------------

class TestTruncateMessageFilter:
    def test_returns_callable(self):
        f = truncate_message_filter(10)
        assert callable(f)

    def test_invalid_max_raises(self):
        with pytest.raises(ValueError):
            truncate_message_filter(0)

    def test_short_message_unchanged(self):
        f = truncate_message_filter(50)
        entry = _e(message="short")
        assert f(entry) is entry

    def test_exact_length_unchanged(self):
        f = truncate_message_filter(5)
        entry = _e(message="hello")
        assert f(entry) is entry

    def test_long_message_truncated(self):
        f = truncate_message_filter(5)
        entry = _e(message="hello world")
        result = f(entry)
        assert result is not entry
        assert result.message == "hello…"

    def test_other_fields_preserved(self):
        f = truncate_message_filter(3)
        entry = _e(message="abcdef", level="WARN", source="Sys")
        result = f(entry)
        assert result.level == "WARN"
        assert result.source == "Sys"


# ---------------------------------------------------------------------------
# redact_pattern_filter
# ---------------------------------------------------------------------------

class TestRedactPatternFilter:
    def test_returns_callable(self):
        f = redact_pattern_filter(r"\d+")
        assert callable(f)

    def test_empty_pattern_raises(self):
        with pytest.raises(ValueError):
            redact_pattern_filter("")

    def test_no_match_returns_same_entry(self):
        f = redact_pattern_filter(r"\d+")
        entry = _e(message="no digits here")
        assert f(entry) is entry

    def test_match_replaced_with_default(self):
        f = redact_pattern_filter(r"\d+")
        entry = _e(message="user 42 logged in")
        result = f(entry)
        assert result.message == "user [REDACTED] logged in"

    def test_custom_replacement(self):
        f = redact_pattern_filter(r"password=\S+", replacement="password=***")
        entry = _e(message="login password=secret123")
        result = f(entry)
        assert result.message == "login password=***"

    def test_other_fields_preserved(self):
        f = redact_pattern_filter(r"\d+")
        entry = _e(message="score 99", level="DEBUG", source="Game")
        result = f(entry)
        assert result.level == "DEBUG"
        assert result.source == "Game"


# ---------------------------------------------------------------------------
# tag_source_filter
# ---------------------------------------------------------------------------

class TestTagSourceFilter:
    def test_returns_callable(self):
        f = tag_source_filter("prod")
        assert callable(f)

    def test_empty_tag_raises(self):
        with pytest.raises(ValueError):
            tag_source_filter("")

    def test_prepends_tag_to_existing_source(self):
        f = tag_source_filter("prod")
        entry = _e(source="Engine")
        result = f(entry)
        assert result.source == "prod:Engine"

    def test_sets_tag_when_no_source(self):
        f = tag_source_filter("prod")
        entry = _e(source=None)
        result = f(entry)
        assert result.source == "prod"

    def test_custom_separator(self):
        f = tag_source_filter("env", separator="/")
        entry = _e(source="Renderer")
        result = f(entry)
        assert result.source == "env/Renderer"

    def test_message_unchanged(self):
        f = tag_source_filter("x")
        entry = _e(message="boom", source="A")
        result = f(entry)
        assert result.message == "boom"
