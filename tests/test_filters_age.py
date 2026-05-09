"""Tests for gamelog_tail.filters_age."""

from __future__ import annotations

import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_age import max_age_filter, min_age_filter


_BASE = datetime.datetime(2024, 6, 1, 12, 0, 0)


def _e(
    message: str = "hello",
    timestamp: datetime.datetime | None = _BASE,
) -> LogEntry:
    return LogEntry(level="INFO", message=message, timestamp=timestamp)


def _now_at(offset_seconds: float):
    """Return a now_fn that reports *offset_seconds* after _BASE."""
    t = _BASE + datetime.timedelta(seconds=offset_seconds)
    return lambda: t


# ---------------------------------------------------------------------------
# max_age_filter
# ---------------------------------------------------------------------------

class TestMaxAgeFilter:
    def test_returns_callable(self):
        f = max_age_filter(60)
        assert callable(f)

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            max_age_filter(0)

    def test_invalid_negative_raises(self):
        with pytest.raises(ValueError):
            max_age_filter(-5)

    def test_passes_entry_within_age(self):
        f = max_age_filter(60, now_fn=_now_at(30))
        assert f(_e()) is True

    def test_passes_entry_exactly_at_limit(self):
        f = max_age_filter(60, now_fn=_now_at(60))
        assert f(_e()) is True

    def test_blocks_entry_too_old(self):
        f = max_age_filter(60, now_fn=_now_at(61))
        assert f(_e()) is False

    def test_passes_entry_without_timestamp(self):
        f = max_age_filter(60, now_fn=_now_at(9999))
        assert f(_e(timestamp=None)) is True


# ---------------------------------------------------------------------------
# min_age_filter
# ---------------------------------------------------------------------------

class TestMinAgeFilter:
    def test_returns_callable(self):
        f = min_age_filter(5)
        assert callable(f)

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            min_age_filter(0)

    def test_invalid_negative_raises(self):
        with pytest.raises(ValueError):
            min_age_filter(-1)

    def test_passes_entry_old_enough(self):
        f = min_age_filter(5, now_fn=_now_at(10))
        assert f(_e()) is True

    def test_passes_entry_exactly_at_limit(self):
        f = min_age_filter(5, now_fn=_now_at(5))
        assert f(_e()) is True

    def test_blocks_entry_too_new(self):
        f = min_age_filter(5, now_fn=_now_at(3))
        assert f(_e()) is False

    def test_passes_entry_without_timestamp(self):
        f = min_age_filter(5, now_fn=_now_at(0))
        assert f(_e(timestamp=None)) is True
