import pytest
from datetime import datetime
from gamelog_tail.parsers.unreal import UnrealParser


@pytest.fixture
def parser():
    return UnrealParser()


class TestCanParse:
    def test_full_format_with_level(self, parser):
        line = "[2024.01.15-10.23.45:678][  0]LogTemp: Warning: Something went wrong"
        assert parser.can_parse(line) is True

    def test_full_format_without_level(self, parser):
        line = "[2024.01.15-10.23.45:678][  0]LogInit: Display: Engine version: 5.3.0"
        assert parser.can_parse(line) is True

    def test_unrecognised_line(self, parser):
        assert parser.can_parse("random log output") is False

    def test_unity_format_not_matched(self, parser):
        line = "[10:23:45] [INFO] Player spawned at (0, 0, 0)"
        assert parser.can_parse(line) is False


class TestParse:
    def test_warning_level(self, parser):
        line = "[2024.01.15-10.23.45:678][  0]LogTemp: Warning: Something went wrong"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "WARNING"
        assert entry.message == "Something went wrong"
        assert entry.source == "unreal"
        assert entry.extra["category"] == "LogTemp"
        assert entry.extra["frame"] == 0

    def test_error_level(self, parser):
        line = "[2024.01.15-10.23.45:000][100]LogRHI: Error: GPU crashed"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "ERROR"
        assert entry.message == "GPU crashed"
        assert entry.extra["frame"] == 100

    def test_display_maps_to_info(self, parser):
        line = "[2024.01.15-10.23.45:678][  0]LogInit: Display: Engine version: 5.3.0"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "INFO"

    def test_no_explicit_level_defaults_to_info(self, parser):
        line = "[2024.01.15-10.23.45:100][  5]LogNet: Connection established"
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == "INFO"
        assert entry.message == "Connection established"

    def test_timestamp_parsed(self, parser):
        line = "[2024.01.15-10.23.45:678][  0]LogTemp: Warning: test"
        entry = parser.parse(line)
        assert entry.timestamp is not None
        assert isinstance(entry.timestamp, datetime)
        assert entry.timestamp.year == 2024
        assert entry.timestamp.month == 1
        assert entry.timestamp.day == 15
        assert entry.timestamp.hour == 10
        assert entry.timestamp.microsecond == 678000

    def test_unrecognised_returns_none(self, parser):
        assert parser.parse("not a valid log line") is None
