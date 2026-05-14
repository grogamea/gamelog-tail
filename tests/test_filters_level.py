"""Tests for gamelog_tail.filters_level."""

from __future__ import annotations

import pytest

from gamelog_tail.filters_level import level_range_filter, _LEVELS
from gamelog_tail.parsers.base import LogEntry


def _e(level: str | None, message: str = "msg") -> LogEntry:
    return LogEntry(level=level, message=message)


# ---------------------------------------------------------------------------
# Construction / validation
# ---------------------------------------------------------------------------

class TestLevelRangeFilterConstruction:
    def test_returns_callable(self):
        f = level_range_filter()
        assert callable(f)

    def test_invalid_min_raises(self):
        with pytest.raises(ValueError, match="min_level"):
            level_range_filter(min_level="verbose")

    def test_invalid_max_raises(self):
        with pytest.raises(ValueError, match="max_level"):
            level_range_filter(max_level="fatal")

    def test_min_greater_than_max_raises(self):
        with pytest.raises(ValueError, match="higher than"):
            level_range_filter(min_level="error", max_level="info")

    def test_equal_min_max_is_valid(self):
        f = level_range_filter(min_level="warning", max_level="warning")
        assert callable(f)


# ---------------------------------------------------------------------------
# Filtering behaviour
# ---------------------------------------------------------------------------

class TestLevelRangeFilterBehaviour:
    def test_default_passes_all_known_levels(self):
        f = level_range_filter()
        entries = [_e(lvl) for lvl in _LEVELS]
        result = list(f(iter(entries)))
        assert len(result) == len(_LEVELS)

    def test_min_info_excludes_debug(self):
        f = level_range_filter(min_level="info")
        entries = [_e("debug"), _e("info"), _e("warning")]
        result = list(f(iter(entries)))
        levels = [e.level for e in result]
        assert "debug" not in levels
        assert "info" in levels
        assert "warning" in levels

    def test_max_warning_excludes_error_and_critical(self):
        f = level_range_filter(max_level="warning")
        entries = [_e("info"), _e("warning"), _e("error"), _e("critical")]
        result = list(f(iter(entries)))
        levels = [e.level for e in result]
        assert "error" not in levels
        assert "critical" not in levels
        assert "info" in levels
        assert "warning" in levels

    def test_exact_single_level(self):
        f = level_range_filter(min_level="error", max_level="error")
        entries = [_e("warning"), _e("error"), _e("critical")]
        result = list(f(iter(entries)))
        assert [e.level for e in result] == ["error"]

    def test_case_insensitive_level_on_entry(self):
        f = level_range_filter(min_level="info", max_level="error")
        entries = [_e("WARNING"), _e("DEBUG")]
        result = list(f(iter(entries)))
        assert len(result) == 1
        assert result[0].level == "WARNING"

    def test_none_level_entry_excluded(self):
        """Entries with no level (level=None) should be excluded by the filter."""
        f = level_range_filter(min_level="debug", max_level="critical")
        entries = [_e(None), _e("info"), _e(None)]
        result = list(f(iter(entries)))
        levels = [e.level for e in result]
        assert None not in levels
        assert "info" in levels
        assert len(result) == 1

    def test_empty_input_returns_empty(self):
        """Filtering an empty stream should yield an empty result."""
        f = level_range_filter(min_level="info", max_level="error")
        result = list(f(iter([])))
        assert result == []
