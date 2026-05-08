"""Tests for gamelog_tail.filters_severity_integration."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_severity_integration import (
    build_severity_filters,
    apply_severity_filters,
)


def _e(level: str, msg: str = "msg") -> LogEntry:
    return LogEntry(level=level, message=msg, source=None, timestamp=None, raw=msg)


# ---------------------------------------------------------------------------
# build_severity_filters
# ---------------------------------------------------------------------------

class TestBuildSeverityFilters:
    def test_no_args_returns_empty_list(self):
        assert build_severity_filters() == []

    def test_all_none_returns_empty_list(self):
        result = build_severity_filters(
            quiet_min_level=None,
            burst_trigger_level=None,
            burst_threshold=None,
            window_seconds=None,
        )
        assert result == []

    def test_quiet_min_level_returns_one_filter(self):
        result = build_severity_filters(quiet_min_level="error")
        assert len(result) == 1
        assert callable(result[0])

    def test_burst_threshold_returns_one_filter(self):
        result = build_severity_filters(burst_threshold=5)
        assert len(result) == 1

    def test_all_args_returns_one_filter(self):
        result = build_severity_filters(
            quiet_min_level="warning",
            burst_trigger_level="error",
            burst_threshold=2,
            window_seconds=3.0,
        )
        assert len(result) == 1

    def test_invalid_level_propagates_error(self):
        with pytest.raises(ValueError):
            build_severity_filters(quiet_min_level="nonsense")


# ---------------------------------------------------------------------------
# apply_severity_filters
# ---------------------------------------------------------------------------

class TestApplySeverityFilters:
    def test_empty_filters_passes_entry(self):
        entry = _e("debug")
        assert apply_severity_filters(entry, []) is entry

    def test_filter_blocks_entry(self):
        # quiet_min_level=error means warning is blocked
        filters = build_severity_filters(quiet_min_level="error")
        assert apply_severity_filters(_e("warning"), filters) is None

    def test_filter_passes_entry(self):
        filters = build_severity_filters(quiet_min_level="warning")
        assert apply_severity_filters(_e("error"), filters) is not None

    def test_none_short_circuits(self):
        """If a filter returns None the rest are skipped."""
        called = []

        def _always_block(e: LogEntry) -> LogEntry | None:
            return None

        def _should_not_run(e: LogEntry) -> LogEntry | None:
            called.append(True)
            return e

        apply_severity_filters(_e("info"), [_always_block, _should_not_run])
        assert called == []
