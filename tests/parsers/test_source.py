"""Tests for the Source engine log parser."""
from datetime import datetime

import pytest

from gamelog_tail.parsers.source import SourceParser


@pytest.fixture()
def parser() -> SourceParser:
    return SourceParser()


class TestCanParse:
    def test_full_format_with_category(self, parser):
        line = 'L 01/23/2024 - 14:05:32: [server] Player connected'
        assert parser.can_parse(line) is True

    def test_full_format_without_category(self, parser):
        line = 'L 01/23/2024 - 14:05:32: Server started'
        assert parser.can_parse(line) is True

    def test_unrecognised_line(self, parser):
        assert parser.can_parse('random log text') is False

    def test_empty_line(self, parser):
        assert parser.can_parse('') is False

    def test_partial_match(self, parser):
        assert parser.can_parse('L 01/23/2024 -') is False


class TestParse:
    def test_full_format_with_category(self, parser):
        line = 'L 01/23/2024 - 14:05:32: [server] Player connected'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.message == 'Player connected'
        assert entry.source == 'server'
        assert entry.level == 'INFO'
        assert entry.timestamp == datetime(2024, 1, 23, 14, 5, 32)
        assert entry.raw == line

    def test_full_format_without_category(self, parser):
        line = 'L 01/23/2024 - 14:05:32: Server started'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.message == 'Server started'
        assert entry.source is None
        assert entry.level == 'INFO'

    def test_error_level_inferred(self, parser):
        line = 'L 01/23/2024 - 14:05:32: [net] Connection failed'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'ERROR'

    def test_warning_level_inferred(self, parser):
        line = 'L 01/23/2024 - 14:05:32: [physics] Bad hull'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'WARNING'

    def test_unrecognised_returns_none(self, parser):
        assert parser.parse('not a source log line') is None

    def test_timestamp_parsed_correctly(self, parser):
        line = 'L 06/15/2023 - 09:00:01: [game] Round started'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.timestamp == datetime(2023, 6, 15, 9, 0, 1)
