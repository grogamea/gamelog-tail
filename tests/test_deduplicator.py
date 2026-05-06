"""Tests for gamelog_tail.deduplicator."""

from datetime import datetime, timedelta

import pytest

from gamelog_tail.deduplicator import Deduplicator, build_deduplicator
from gamelog_tail.parsers.base import LogEntry


def _e(
    message: str = "hello",
    level: str = "INFO",
    source: str | None = "Game",
    ts: datetime | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=ts or datetime(2024, 1, 1, 12, 0, 0),
        level=level,
        source=source,
        message=message,
    )


class TestIsDuplicate:
    def test_first_occurrence_not_duplicate(self):
        d = Deduplicator(window_seconds=5)
        assert d.is_duplicate(_e("msg")) is False

    def test_immediate_repeat_is_duplicate(self):
        d = Deduplicator(window_seconds=5)
        entry = _e("msg")
        d.is_duplicate(entry)
        assert d.is_duplicate(entry) is True

    def test_different_message_not_duplicate(self):
        d = Deduplicator(window_seconds=5)
        d.is_duplicate(_e("msg A"))
        assert d.is_duplicate(_e("msg B")) is False

    def test_different_level_not_duplicate(self):
        d = Deduplicator(window_seconds=5)
        d.is_duplicate(_e("msg", level="INFO"))
        assert d.is_duplicate(_e("msg", level="ERROR")) is False

    def test_different_source_not_duplicate(self):
        d = Deduplicator(window_seconds=5)
        d.is_duplicate(_e("msg", source="A"))
        assert d.is_duplicate(_e("msg", source="B")) is False

    def test_expired_entry_not_duplicate(self):
        d = Deduplicator(window_seconds=2)
        t0 = datetime(2024, 1, 1, 12, 0, 0)
        d.is_duplicate(_e("msg", ts=t0))
        # Advance timestamp beyond window
        t1 = t0 + timedelta(seconds=3)
        assert d.is_duplicate(_e("msg", ts=t1)) is False

    def test_within_window_still_duplicate(self):
        d = Deduplicator(window_seconds=10)
        t0 = datetime(2024, 1, 1, 12, 0, 0)
        d.is_duplicate(_e("msg", ts=t0))
        t1 = t0 + timedelta(seconds=5)
        assert d.is_duplicate(_e("msg", ts=t1)) is True

    def test_reset_clears_state(self):
        d = Deduplicator(window_seconds=60)
        d.is_duplicate(_e("msg"))
        d.reset()
        assert d.is_duplicate(_e("msg")) is False

    def test_max_tracked_evicts_oldest(self):
        d = Deduplicator(window_seconds=60, max_tracked=3)
        t = datetime(2024, 1, 1, 12, 0, 0)
        d.is_duplicate(_e("a", ts=t))
        d.is_duplicate(_e("b", ts=t))
        d.is_duplicate(_e("c", ts=t))
        # Adding a 4th evicts "a"
        d.is_duplicate(_e("d", ts=t))
        # "a" should no longer be tracked
        assert d.is_duplicate(_e("a", ts=t)) is False


class TestBuildDeduplicator:
    def test_returns_deduplicator_instance(self):
        d = build_deduplicator(window_seconds=3)
        assert isinstance(d, Deduplicator)

    def test_custom_window(self):
        d = build_deduplicator(window_seconds=0)
        t = datetime(2024, 1, 1)
        d.is_duplicate(_e("x", ts=t))
        # With window=0 the entry expires immediately on the next call
        t2 = t + timedelta(seconds=1)
        assert d.is_duplicate(_e("x", ts=t2)) is False
