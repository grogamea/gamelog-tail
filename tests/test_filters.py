"""Tests for gamelog_tail.filters."""

from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters import (
    apply_filters,
    by_level,
    by_message_pattern,
    by_source_pattern,
    combine_all,
    combine_any,
)


def make_entry(
    message: str = "test",
    level: str | None = None,
    source: str | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        level=level,
        source=source,
        message=message,
        raw=message,
    )


class TestByLevel:
    def test_matches_exact(self):
        f = by_level("WARNING")
        assert f(make_entry(level="WARNING")) is True

    def test_case_insensitive(self):
        f = by_level("warning")
        assert f(make_entry(level="WARNING")) is True

    def test_no_match(self):
        f = by_level("ERROR")
        assert f(make_entry(level="WARNING")) is False

    def test_multiple_levels(self):
        f = by_level("ERROR", "WARNING")
        assert f(make_entry(level="ERROR")) is True
        assert f(make_entry(level="WARNING")) is True
        assert f(make_entry(level="INFO")) is False

    def test_none_level(self):
        f = by_level("ERROR")
        assert f(make_entry(level=None)) is False


class TestByMessagePattern:
    def test_substring_match(self):
        f = by_message_pattern("null")
        assert f(make_entry(message="NullReferenceException")) is True

    def test_no_match(self):
        f = by_message_pattern("crash")
        assert f(make_entry(message="everything is fine")) is False

    def test_regex_pattern(self):
        f = by_message_pattern(r"error\s+\d+")
        assert f(make_entry(message="error 42 occurred")) is True


class TestBySourcePattern:
    def test_matches_source(self):
        f = by_source_pattern("Player")
        assert f(make_entry(source="PlayerController")) is True

    def test_none_source_no_match(self):
        f = by_source_pattern("Player")
        assert f(make_entry(source=None)) is False


class TestCombine:
    def test_combine_any(self):
        f = combine_any(by_level("ERROR"), by_message_pattern("crash"))
        assert f(make_entry(level="WARNING", message="crash detected")) is True
        assert f(make_entry(level="ERROR", message="ok")) is True
        assert f(make_entry(level="INFO", message="all good")) is False

    def test_combine_all(self):
        f = combine_all(by_level("ERROR"), by_message_pattern("crash"))
        assert f(make_entry(level="ERROR", message="crash!")) is True
        assert f(make_entry(level="ERROR", message="ok")) is False


class TestApplyFilters:
    def _entries(self):
        return [
            make_entry(level="INFO", message="started"),
            make_entry(level="WARNING", message="low memory"),
            make_entry(level="ERROR", message="crash"),
            make_entry(level="ERROR", message="another error"),
        ]

    def test_filter_by_level(self):
        result = list(apply_filters(self._entries(), by_level("ERROR")))
        assert len(result) == 2

    def test_filter_mode_any(self):
        result = list(
            apply_filters(
                self._entries(),
                by_level("WARNING"),
                by_message_pattern("crash"),
                mode="any",
            )
        )
        assert len(result) == 2

    def test_no_filters_passes_all(self):
        # combine_all with zero filters: all() on empty is True
        result = list(apply_filters(self._entries()))
        assert len(result) == 4
