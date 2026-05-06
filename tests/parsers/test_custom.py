"""Tests for gamelog_tail.parsers.custom.CustomParser."""
from __future__ import annotations

import re
from datetime import datetime

import pytest

from gamelog_tail.parsers.custom import CustomParser


@pytest.fixture()
def parser() -> CustomParser:
    return CustomParser()


class TestCanParse:
    def test_full_format(self, parser: CustomParser) -> None:
        line = "[2024-01-15 10:23:45] [ERROR] (MySystem) Something went wrong"
        assert parser.can_parse(line) is True

    def test_without_source(self, parser: CustomParser) -> None:
        line = "[2024-01-15 10:23:45] [INFO] Application started"
        assert parser.can_parse(line) is True

    def test_unrecognised_line(self, parser: CustomParser) -> None:
        assert parser.can_parse("random log noise") is False

    def test_empty_line(self, parser: CustomParser) -> None:
        assert parser.can_parse("") is False


class TestParse:
    def test_full_format(self, parser: CustomParser) -> None:
        line = "[2024-01-15 10:23:45] [ERROR] (MySystem) Something went wrong"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "ERROR"
        assert entry.source == "MySystem"
        assert entry.message == "Something went wrong"
        assert entry.timestamp == datetime(2024, 1, 15, 10, 23, 45)
        assert entry.raw == line

    def test_without_source(self, parser: CustomParser) -> None:
        line = "[2024-01-15 08:00:00] [INFO] Application started"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "INFO"
        assert entry.source is None
        assert entry.message == "Application started"

    def test_unrecognised_returns_none(self, parser: CustomParser) -> None:
        assert parser.parse("not a valid line") is None

    def test_warning_level(self, parser: CustomParser) -> None:
        line = "[2024-06-01 12:00:00] [WARNING] (Renderer) Low memory"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "WARNING"


class TestCustomPattern:
    def test_custom_regex(self) -> None:
        pattern = re.compile(
            r"^(?P<level>DEBUG|INFO|WARN|ERROR)\s+(?P<message>.+)$"
        )
        p = CustomParser(pattern=pattern)
        assert p.can_parse("ERROR disk full") is True
        assert p.can_parse("[2024-01-01 00:00:00] [INFO] x") is False

    def test_custom_pattern_parse(self) -> None:
        pattern = re.compile(
            r"^(?P<level>DEBUG|INFO|WARN|ERROR)\s+(?P<message>.+)$"
        )
        p = CustomParser(pattern=pattern)
        entry = p.parse("WARN low battery")
        assert entry is not None
        assert entry.level == "WARN"
        assert entry.message == "low battery"
        assert entry.timestamp is None
        assert entry.source is None
