"""Tests for gamelog_tail.filters_duplicate_burst."""
from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from gamelog_tail.filters_duplicate_burst import duplicate_burst_filter
from gamelog_tail.parsers.base import LogEntry


def _e(
    message: str = "msg",
    level: str = "INFO",
    source: str | None = None,
) -> LogEntry:
    return LogEntry(level=level, message=message, source=source)


class TestDuplicateBurstFilterConstruction:
    def test_returns_callable(self):
        f = duplicate_burst_filter()
        assert callable(f)

    def test_invalid_max_repeats_raises(self):
        with pytest.raises(ValueError, match="max_repeats"):
            duplicate_burst_filter(max_repeats=0)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            duplicate_burst_filter(window_seconds=0)

    def test_negative_window_raises(self):
        with pytest.raises(ValueError, match="window_seconds"):
            duplicate_burst_filter(window_seconds=-1.0)

    def test_empty_key_fields_raises(self):
        with pytest.raises(ValueError, match="key_fields"):
            duplicate_burst_filter(key_fields=())


class TestDuplicateBurstFilterBehaviour:
    def test_first_occurrence_passes(self):
        f = duplicate_burst_filter(max_repeats=2)
        assert f(_e("hello")) is True

    def test_within_limit_passes(self):
        f = duplicate_burst_filter(max_repeats=3)
        for _ in range(3):
            assert f(_e("hello")) is True

    def test_exceeds_limit_suppressed(self):
        f = duplicate_burst_filter(max_repeats=2)
        f(_e("hello"))
        f(_e("hello"))
        assert f(_e("hello")) is False

    def test_different_messages_independent(self):
        f = duplicate_burst_filter(max_repeats=1)
        assert f(_e("alpha")) is True
        assert f(_e("beta")) is True

    def test_window_expiry_resets_count(self):
        mono_values = iter([0.0, 0.1, 0.2, 20.0, 20.1])
        with patch("gamelog_tail.filters_duplicate_burst.time.monotonic",
                   side_effect=mono_values):
            f = duplicate_burst_filter(max_repeats=2, window_seconds=5.0)
            assert f(_e("x")) is True   # count=1
            assert f(_e("x")) is True   # count=2
            assert f(_e("x")) is False  # count=3, suppressed
            # After window expires (t=20.0), old entries fall off
            assert f(_e("x")) is True   # count=1 in new window
            assert f(_e("x")) is True   # count=2

    def test_key_fields_level_and_message(self):
        f = duplicate_burst_filter(max_repeats=1, key_fields=("level", "message"))
        assert f(_e("crash", level="ERROR")) is True
        assert f(_e("crash", level="WARN")) is True  # different level => different key
        assert f(_e("crash", level="ERROR")) is False  # same key, suppressed

    def test_key_fields_message_only(self):
        f = duplicate_burst_filter(max_repeats=1, key_fields=("message",))
        assert f(_e("dup", level="INFO")) is True
        assert f(_e("dup", level="ERROR")) is False  # same message key
