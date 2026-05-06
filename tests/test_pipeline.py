"""Tests for gamelog_tail.pipeline."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail import pipeline, formatters
from gamelog_tail.filters import by_level, by_message_pattern


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(message: str, level: str = "INFO", source: str = "App") -> LogEntry:
    return LogEntry(message=message, level=level, source=source, raw=message)


class _StubParser:
    """Parser that recognises lines starting with '>>>'."""

    def can_parse(self, line: str) -> bool:
        return line.startswith(">>>")

    def parse(self, line: str) -> LogEntry | None:
        if not self.can_parse(line):
            return None
        body = line[3:].strip()
        level, _, message = body.partition(" ")
        return LogEntry(message=message, level=level.upper(), source="stub", raw=line)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRun:
    def setup_method(self):
        self.parser = _StubParser()

    def test_basic_passthrough(self):
        lines = [">>> INFO hello world"]
        results = list(pipeline.run(lines, self.parser))
        assert len(results) == 1
        assert "hello world" in results[0]

    def test_unrecognised_line_passed_raw(self):
        lines = ["some raw garbage"]
        results = list(pipeline.run(lines, self.parser))
        assert results == ["some raw garbage"]

    def test_empty_lines_skipped(self):
        lines = ["", "   ", "\n"]
        results = list(pipeline.run(lines, self.parser))
        assert results == []

    def test_filter_removes_entries(self):
        lines = [">>> INFO keep this", ">>> DEBUG drop this"]
        filt = by_level("info")
        results = list(pipeline.run(lines, self.parser, filters=[filt]))
        assert len(results) == 1
        assert "keep this" in results[0]

    def test_multiple_filters_all_must_pass(self):
        lines = [
            ">>> INFO buy milk",
            ">>> INFO buy bread",
            ">>> WARNING buy eggs",
        ]
        filters = [by_level("info"), by_message_pattern("milk")]
        results = list(pipeline.run(lines, self.parser, filters=filters))
        assert len(results) == 1
        assert "milk" in results[0]

    def test_custom_formatter_applied(self):
        lines = [">>> ERROR boom"]
        results = list(
            pipeline.run(lines, self.parser, formatter=formatters.as_json)
        )
        import json
        data = json.loads(results[0])
        assert data["level"] == "ERROR"
        assert data["message"] == "boom"

    def test_no_filters_passes_all(self):
        lines = [">>> DEBUG a", ">>> INFO b", ">>> ERROR c"]
        results = list(pipeline.run(lines, self.parser))
        assert len(results) == 3


class TestBuildFilters:
    def test_returns_list(self):
        f1 = by_level("info")
        f2 = by_message_pattern("x")
        result = pipeline.build_filters(f1, f2)
        assert result == [f1, f2]

    def test_empty(self):
        assert pipeline.build_filters() == []
