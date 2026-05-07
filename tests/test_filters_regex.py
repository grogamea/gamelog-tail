"""Tests for gamelog_tail.filters_regex."""

from __future__ import annotations

import re
from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_regex import regex_filter, regex_exclude_filter


def _e(
    message: str = "hello world",
    level: str = "INFO",
    source: str | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        level=level,
        message=message,
        source=source,
    )


# ---------------------------------------------------------------------------
# regex_filter construction
# ---------------------------------------------------------------------------

class TestRegexFilterConstruction:
    def test_returns_callable(self):
        f = regex_filter(r"error")
        assert callable(f)

    def test_empty_pattern_raises(self):
        with pytest.raises(ValueError, match="pattern"):
            regex_filter("")

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError, match="field"):
            regex_filter(r"x", field="nonexistent")

    def test_bad_regex_raises(self):
        with pytest.raises(re.error):
            regex_filter(r"[unclosed")


# ---------------------------------------------------------------------------
# regex_filter behaviour
# ---------------------------------------------------------------------------

class TestRegexFilter:
    def test_passes_matching_message(self):
        f = regex_filter(r"world")
        assert f(_e(message="hello world")) is True

    def test_blocks_non_matching_message(self):
        f = regex_filter(r"error")
        assert f(_e(message="all good")) is False

    def test_case_insensitive_flag(self):
        f = regex_filter(r"ERROR", flags=re.IGNORECASE)
        assert f(_e(message="an error occurred")) is True

    def test_matches_on_level_field(self):
        f = regex_filter(r"^WARN", field="level")
        assert f(_e(level="WARNING")) is True
        assert f(_e(level="INFO")) is False

    def test_matches_on_source_field(self):
        f = regex_filter(r"Player", field="source")
        assert f(_e(source="PlayerController")) is True
        assert f(_e(source="AudioManager")) is False

    def test_none_source_returns_false(self):
        f = regex_filter(r"Player", field="source")
        assert f(_e(source=None)) is False

    def test_partial_match_passes(self):
        f = regex_filter(r"\d+")
        assert f(_e(message="loaded 42 assets")) is True


# ---------------------------------------------------------------------------
# regex_exclude_filter behaviour
# ---------------------------------------------------------------------------

class TestRegexExcludeFilter:
    def test_returns_callable(self):
        f = regex_exclude_filter(r"noise")
        assert callable(f)

    def test_blocks_matching_entry(self):
        f = regex_exclude_filter(r"noise")
        assert f(_e(message="background noise")) is False

    def test_passes_non_matching_entry(self):
        f = regex_exclude_filter(r"noise")
        assert f(_e(message="important event")) is True

    def test_empty_pattern_raises(self):
        with pytest.raises(ValueError):
            regex_exclude_filter("")
