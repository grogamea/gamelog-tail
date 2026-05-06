"""Tests for gamelog_tail.filters_time."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gamelog_tail.filters_time import time_window_filter
from gamelog_tail.parsers.base import LogEntry


def _e(ts: datetime | None = None, msg: str = "hello") -> LogEntry:
    return LogEntry(timestamp=ts, level="INFO", message=msg, source=None, raw=msg)


DT = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
DT_BEFORE = datetime(2024, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
DT_AFTER = datetime(2024, 6, 1, 13, 0, 0, tzinfo=timezone.utc)


class TestTimeWindowFilterConstruction:
    def test_returns_callable(self):
        f = time_window_filter()
        assert callable(f)

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError, match="start"):
            time_window_filter(start=DT_AFTER, end=DT_BEFORE)

    def test_equal_start_end_ok(self):
        f = time_window_filter(start=DT, end=DT)
        assert callable(f)


class TestTimeWindowFilterBehaviour:
    def test_no_bounds_passes_all(self):
        f = time_window_filter()
        assert f(_e(DT)) is True
        assert f(_e(DT_BEFORE)) is True
        assert f(_e(None)) is True

    def test_no_timestamp_always_passes(self):
        f = time_window_filter(start=DT_AFTER, end=DT_AFTER)
        assert f(_e(None)) is True

    def test_start_only_passes_on_or_after(self):
        f = time_window_filter(start=DT)
        assert f(_e(DT)) is True
        assert f(_e(DT_AFTER)) is True
        assert f(_e(DT_BEFORE)) is False

    def test_end_only_passes_on_or_before(self):
        f = time_window_filter(end=DT)
        assert f(_e(DT)) is True
        assert f(_e(DT_BEFORE)) is True
        assert f(_e(DT_AFTER)) is False

    def test_both_bounds_inclusive(self):
        f = time_window_filter(start=DT, end=DT)
        assert f(_e(DT)) is True
        assert f(_e(DT_BEFORE)) is False
        assert f(_e(DT_AFTER)) is False

    def test_entry_within_window(self):
        f = time_window_filter(start=DT_BEFORE, end=DT_AFTER)
        assert f(_e(DT)) is True

    def test_entry_at_start_boundary(self):
        f = time_window_filter(start=DT_BEFORE, end=DT_AFTER)
        assert f(_e(DT_BEFORE)) is True

    def test_entry_at_end_boundary(self):
        f = time_window_filter(start=DT_BEFORE, end=DT_AFTER)
        assert f(_e(DT_AFTER)) is True
