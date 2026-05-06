"""Tests for gamelog_tail.formatters."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail import formatters


def make_entry(
    message: str = "Something happened",
    level: str | None = "INFO",
    source: str | None = "MySystem",
    timestamp: datetime | None = None,
    raw: str = "",
) -> LogEntry:
    return LogEntry(
        message=message,
        level=level,
        source=source,
        timestamp=timestamp,
        raw=raw,
    )


class TestPlain:
    def test_full_entry(self):
        ts = datetime(2024, 1, 15, 10, 30, 0)
        entry = make_entry(timestamp=ts)
        result = formatters.plain(entry)
        assert "[2024-01-15 10:30:00]" in result
        assert "[INFO]" in result
        assert "(MySystem)" in result
        assert "Something happened" in result

    def test_minimal_entry(self):
        entry = make_entry(level=None, source=None)
        result = formatters.plain(entry)
        assert result == "Something happened"

    def test_no_timestamp(self):
        entry = make_entry()
        result = formatters.plain(entry)
        assert "[INFO]" in result
        assert "[" not in result.split("[")[0]  # no timestamp bracket at start


class TestColoured:
    def test_contains_reset_code(self):
        entry = make_entry(level="ERROR")
        result = formatters.coloured(entry)
        assert "\033[0m" in result

    def test_error_uses_red(self):
        entry = make_entry(level="ERROR")
        result = formatters.coloured(entry)
        assert "\033[31m" in result

    def test_warning_uses_yellow(self):
        entry = make_entry(level="WARNING")
        result = formatters.coloured(entry)
        assert "\033[33m" in result

    def test_unknown_level_no_colour(self):
        entry = make_entry(level="VERBOSE")
        result = formatters.coloured(entry)
        # message still present
        assert "Something happened" in result


class TestAsJson:
    def test_valid_json(self):
        entry = make_entry()
        result = formatters.as_json(entry)
        data = json.loads(result)
        assert data["message"] == "Something happened"
        assert data["level"] == "INFO"
        assert data["source"] == "MySystem"
        assert data["timestamp"] is None

    def test_timestamp_serialised(self):
        ts = datetime(2024, 3, 5, 12, 0, 0)
        entry = make_entry(timestamp=ts)
        data = json.loads(formatters.as_json(entry))
        assert "2024-03-05" in data["timestamp"]

    def test_none_fields(self):
        entry = make_entry(level=None, source=None)
        data = json.loads(formatters.as_json(entry))
        assert data["level"] is None
        assert data["source"] is None


class TestGetFormatter:
    def test_plain(self):
        assert formatters.get_formatter("plain") is formatters.plain

    def test_colour_spellings(self):
        assert formatters.get_formatter("colour") is formatters.coloured
        assert formatters.get_formatter("color") is formatters.coloured

    def test_json(self):
        assert formatters.get_formatter("json") is formatters.as_json

    def test_case_insensitive(self):
        assert formatters.get_formatter("PLAIN") is formatters.plain

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown formatter"):
            formatters.get_formatter("xml")
