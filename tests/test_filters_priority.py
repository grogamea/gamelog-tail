"""Tests for gamelog_tail.filters_priority."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_priority import priority_filter


def _e(
    level: str = "info",
    message: str = "msg",
    source: str | None = None,
) -> LogEntry:
    return LogEntry(level=level, message=message, source=source)


class TestPriorityFilterConstruction:
    def test_returns_callable(self):
        f = priority_filter("info")
        assert callable(f)

    def test_invalid_min_level_raises(self):
        with pytest.raises(ValueError, match="Unknown level"):
            priority_filter("nonsense")

    def test_invalid_override_level_raises(self):
        with pytest.raises(ValueError, match="Unknown level in source_overrides"):
            priority_filter("info", source_overrides={"Engine": "bogus"})


class TestPriorityFilterBehaviour:
    def test_passes_exact_min_level(self):
        f = priority_filter("warning")
        assert f(_e(level="warning")) is True

    def test_passes_higher_priority_level(self):
        f = priority_filter("warning")
        assert f(_e(level="error")) is True
        assert f(_e(level="fatal")) is True

    def test_suppresses_lower_priority_level(self):
        f = priority_filter("warning")
        assert f(_e(level="info")) is False
        assert f(_e(level="debug")) is False
        assert f(_e(level="trace")) is False

    def test_case_insensitive_level(self):
        f = priority_filter("Warning")
        assert f(_e(level="ERROR")) is True
        assert f(_e(level="verbose")) is False

    def test_unknown_entry_level_treated_as_lowest(self):
        f = priority_filter("debug")
        assert f(_e(level="unknown_level")) is False

    def test_no_level_on_entry_treated_as_lowest(self):
        entry = LogEntry(level=None, message="bare line")
        f = priority_filter("debug")
        assert f(entry) is False


class TestPriorityFilterSourceOverrides:
    def test_override_raises_threshold_for_source(self):
        # Engine source only passes fatal
        f = priority_filter("info", source_overrides={"Engine": "fatal"})
        assert f(_e(level="error", source="Engine")) is False
        assert f(_e(level="fatal", source="Engine")) is True

    def test_override_lowers_threshold_for_source(self):
        # Script source passes even verbose
        f = priority_filter("error", source_overrides={"Script": "verbose"})
        assert f(_e(level="verbose", source="Script")) is True
        assert f(_e(level="info", source="Script")) is True

    def test_non_overridden_source_uses_default(self):
        f = priority_filter("error", source_overrides={"Script": "debug"})
        assert f(_e(level="info", source="Renderer")) is False
        assert f(_e(level="error", source="Renderer")) is True

    def test_source_none_uses_default(self):
        f = priority_filter("warning", source_overrides={"Engine": "fatal"})
        assert f(_e(level="info", source=None)) is False
        assert f(_e(level="warning", source=None)) is True
