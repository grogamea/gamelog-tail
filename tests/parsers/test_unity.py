"""Tests for the Unity log parser."""

import pytest
from gamelog_tail.parsers.unity import UnityParser
from gamelog_tail.parsers.base import LogEntry


@pytest.fixture
def parser():
    return UnityParser()


class TestCanParse:
    def test_full_format(self, parser):
        line = "12:34:56.789 [Warning] UnityEngine.Debug: Player fell off map"
        assert parser.can_parse(line) is True

    def test_simple_format(self, parser):
        assert parser.can_parse("ERROR: Shader compilation failed") is True

    def test_unrecognised_line(self, parser):
        assert parser.can_parse("just some random text") is False

    def test_empty_line(self, parser):
        assert parser.can_parse("") is False


class TestParse:
    def test_full_format_fields(self, parser):
        line = "12:34:56.789 [Warning] UnityEngine.Debug: Player fell off map"
        entry = parser.parse(line)
        assert isinstance(entry, LogEntry)
        assert entry.level == "warning"
        assert entry.source == "UnityEngine.Debug"
        assert entry.message == "Player fell off map"
        assert entry.timestamp is not None

    def test_error_level_mapping(self, parser):
        line = "00:00:01.000 [Exception] MyScript: NullReferenceException"
        entry = parser.parse(line)
        assert entry.level == "error"

    def test_simple_format_fields(self, parser):
        line = "ERROR: Shader compilation failed"
        entry = parser.parse(line)
        assert entry.level == "error"
        assert entry.message == "Shader compilation failed"
        assert entry.timestamp is None
        assert entry.source is None

    def test_no_source_in_full_format(self, parser):
        line = "08:00:00.000 [Info] Application started successfully"
        entry = parser.parse(line)
        assert entry.level == "info"
        assert entry.message == "Application started successfully"

    def test_safe_parse_fallback(self, parser):
        line = "completely unparseable @@@ line"
        entry = parser.safe_parse(line)
        assert entry.raw == line
        assert entry.message == line.strip()

    def test_engine_name(self, parser):
        assert parser.engine_name == "Unity"

    def test_str_representation(self, parser):
        line = "12:00:00.000 [Error] Game: Crash detected"
        entry = parser.parse(line)
        result = str(entry)
        assert "ERROR" in result
        assert "Crash detected" in result
