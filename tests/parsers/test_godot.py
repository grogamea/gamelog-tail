import pytest
from gamelog_tail.parsers.godot import GodotParser


@pytest.fixture
def parser():
    return GodotParser()


class TestCanParse:
    def test_error_with_source(self, parser):
        line = 'ERROR: res://scenes/Main.gd:42 - Node not found'
        assert parser.can_parse(line) is True

    def test_warning_without_source(self, parser):
        line = 'WARNING: AnimationPlayer: Animation idle not found'
        assert parser.can_parse(line) is True

    def test_timed_info(self, parser):
        line = 'INFO: 0:00:01:0234 - Script loaded successfully'
        assert parser.can_parse(line) is True

    def test_user_error(self, parser):
        line = 'USER ERROR: Something went wrong in user script'
        assert parser.can_parse(line) is True

    def test_unrecognised_line(self, parser):
        assert parser.can_parse('Godot Engine v4.1') is False
        assert parser.can_parse('') is False
        assert parser.can_parse('  ') is False


class TestParse:
    def test_error_with_source(self, parser):
        line = 'ERROR: res://scenes/Main.gd:42 - Node not found'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'ERROR'
        assert entry.message == 'Node not found'
        assert entry.source == 'res://scenes/Main.gd:42'
        assert entry.timestamp is None
        assert entry.raw == line

    def test_warning_without_source(self, parser):
        line = 'WARNING: AnimationPlayer: Animation idle not found'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'WARNING'
        assert entry.message == 'AnimationPlayer: Animation idle not found'
        assert entry.source is None

    def test_timed_info(self, parser):
        line = 'INFO: 0:00:03:0512 - Script loaded successfully'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'INFO'
        assert entry.message == 'Script loaded successfully'
        assert entry.timestamp is not None
        assert entry.timestamp.second == 3
        assert entry.timestamp.microsecond == 51200

    def test_user_error_maps_to_error(self, parser):
        line = 'USER ERROR: Something went wrong'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'ERROR'
        assert entry.message == 'Something went wrong'

    def test_user_warning_maps_to_warning(self, parser):
        line = 'USER WARNING: Deprecated function used'
        entry = parser.parse(line)
        assert entry is not None
        assert entry.level == 'WARNING'

    def test_unrecognised_returns_none(self, parser):
        assert parser.parse('not a log line') is None
        assert parser.parse('') is None

    def test_str_representation(self, parser):
        line = 'ERROR: res://main.gd:10 - Crash'
        entry = parser.parse(line)
        result = str(entry)
        assert 'ERROR' in result
        assert 'Crash' in result
