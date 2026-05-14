"""Tests for gamelog_tail.filters_pattern_group."""
from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_pattern_group import pattern_group_filter


def _e(
    message: str = "hello world",
    source: str | None = "Engine",
    level: str = "INFO",
) -> LogEntry:
    return LogEntry(timestamp=None, level=level, source=source, message=message)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestPatternGroupFilterConstruction:
    def test_returns_callable(self):
        f = pattern_group_filter([r"error"])
        assert callable(f)

    def test_empty_patterns_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            pattern_group_filter([])

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError, match="field"):
            pattern_group_filter([r"x"], field="level")

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="mode"):
            pattern_group_filter([r"x"], mode="filter")


# ---------------------------------------------------------------------------
# Allow mode
# ---------------------------------------------------------------------------

class TestAllowMode:
    def test_passes_matching_entry(self):
        f = pattern_group_filter([r"crash", r"error"])
        entry = _e(message="NullPointerError occurred")
        assert f(entry) is entry

    def test_blocks_non_matching_entry(self):
        f = pattern_group_filter([r"crash", r"error"])
        assert f(_e(message="everything is fine")) is None

    def test_any_pattern_sufficient(self):
        f = pattern_group_filter([r"alpha", r"beta", r"gamma"])
        assert f(_e(message="beta detected")) is not None

    def test_label_tags_source(self):
        f = pattern_group_filter([r"assert"], label="CRITICAL")
        result = f(_e(message="assertion failed", source="Physics"))
        assert result is not None
        assert result.source == "[CRITICAL] Physics"

    def test_label_with_none_source(self):
        f = pattern_group_filter([r"assert"], label="CRITICAL")
        result = f(_e(message="assertion failed", source=None))
        assert result is not None
        assert result.source == "[CRITICAL]"

    def test_label_not_applied_when_no_match(self):
        f = pattern_group_filter([r"assert"], label="CRITICAL")
        assert f(_e(message="all good")) is None

    def test_message_unchanged_with_label(self):
        f = pattern_group_filter([r"fail"], label="X")
        result = f(_e(message="fail here"))
        assert result.message == "fail here"


# ---------------------------------------------------------------------------
# Deny mode
# ---------------------------------------------------------------------------

class TestDenyMode:
    def test_blocks_matching_entry(self):
        f = pattern_group_filter([r"verbose", r"trace"], mode="deny")
        assert f(_e(message="verbose output")) is None

    def test_passes_non_matching_entry(self):
        f = pattern_group_filter([r"verbose", r"trace"], mode="deny")
        entry = _e(message="important error")
        assert f(entry) is entry

    def test_source_field_deny(self):
        f = pattern_group_filter([r"^Noise"], field="source", mode="deny")
        assert f(_e(source="Noise")) is None
        assert f(_e(source="Physics")) is not None
