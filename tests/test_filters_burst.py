"""Tests for gamelog_tail.filters_burst."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from gamelog_tail.filters_burst import burst_suppress_filter
from gamelog_tail.parsers.base import LogEntry


def _e(
    message: str = "hello",
    level: str = "INFO",
    source: str | None = None,
    ts: datetime | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=ts or datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        level=level,
        message=message,
        source=source,
    )


class TestBurstSuppressFilterConstruction:
    def test_returns_callable(self):
        f = burst_suppress_filter()
        assert callable(f)

    def test_invalid_max_count_raises(self):
        with pytest.raises(ValueError, match="max_count"):
            burst_suppress_filter(max_count=0)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            burst_suppress_filter(window_seconds=0)

    def test_negative_window_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            burst_suppress_filter(window_seconds=-1)

    def test_invalid_key_field_raises(self):
        with pytest.raises(ValueError, match="key_field"):
            burst_suppress_filter(key_fields=("nonexistent",))


class TestBurstSuppressFilterBehaviour:
    def test_first_entries_pass(self):
        f = burst_suppress_filter(max_count=3, window_seconds=10)
        for _ in range(3):
            assert f(_e()) is not None

    def test_excess_entries_suppressed(self):
        f = burst_suppress_filter(max_count=2, window_seconds=10)
        f(_e())
        f(_e())
        assert f(_e()) is None

    def test_different_messages_not_suppressed(self):
        f = burst_suppress_filter(max_count=1, window_seconds=10)
        assert f(_e(message="alpha")) is not None
        assert f(_e(message="beta")) is not None

    def test_different_levels_treated_separately(self):
        f = burst_suppress_filter(max_count=1, window_seconds=10, key_fields=("level", "message"))
        assert f(_e(level="INFO")) is not None
        assert f(_e(level="ERROR")) is not None

    def test_old_events_evicted_from_window(self):
        from datetime import timedelta
        f = burst_suppress_filter(max_count=1, window_seconds=2)
        t0 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        t1 = t0 + timedelta(seconds=3)  # outside window
        assert f(_e(ts=t0)) is not None
        # first entry is now outside the window; new one should pass
        assert f(_e(ts=t1)) is not None

    def test_source_key_field(self):
        f = burst_suppress_filter(max_count=1, window_seconds=10, key_fields=("source", "message"))
        assert f(_e(source="sys")) is not None
        assert f(_e(source="app")) is not None  # different source, separate bucket
        assert f(_e(source="sys")) is None  # same source, suppressed

    def test_entry_without_timestamp_uses_now(self):
        f = burst_suppress_filter(max_count=2, window_seconds=10)
        e = LogEntry(timestamp=None, level="INFO", message="no ts", source=None)
        assert f(e) is not None
