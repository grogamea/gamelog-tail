"""Tests for gamelog_tail.filters_field."""

from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_field import (
    has_source_filter,
    missing_source_filter,
    has_timestamp_filter,
    missing_timestamp_filter,
    message_min_length_filter,
)


def _e(
    message: str = "hello",
    source: str | None = None,
    timestamp: datetime | None = None,
    level: str = "INFO",
) -> LogEntry:
    return LogEntry(level=level, message=message, source=source, timestamp=timestamp)


# ---------------------------------------------------------------------------
# has_source_filter
# ---------------------------------------------------------------------------

class TestHasSourceFilter:
    def test_returns_callable(self):
        assert callable(has_source_filter())

    def test_passes_entry_with_source(self):
        f = has_source_filter()
        assert f(_e(source="MySystem")) is True

    def test_blocks_entry_without_source(self):
        f = has_source_filter()
        assert f(_e(source=None)) is False

    def test_blocks_entry_with_empty_string_source(self):
        f = has_source_filter()
        assert f(_e(source="")) is False


# ---------------------------------------------------------------------------
# missing_source_filter
# ---------------------------------------------------------------------------

class TestMissingSourceFilter:
    def test_passes_entry_without_source(self):
        f = missing_source_filter()
        assert f(_e(source=None)) is True

    def test_blocks_entry_with_source(self):
        f = missing_source_filter()
        assert f(_e(source="Physics")) is False


# ---------------------------------------------------------------------------
# has_timestamp_filter
# ---------------------------------------------------------------------------

class TestHasTimestampFilter:
    def test_passes_entry_with_timestamp(self):
        f = has_timestamp_filter()
        assert f(_e(timestamp=datetime(2024, 1, 1, 12, 0, 0))) is True

    def test_blocks_entry_without_timestamp(self):
        f = has_timestamp_filter()
        assert f(_e(timestamp=None)) is False


# ---------------------------------------------------------------------------
# missing_timestamp_filter
# ---------------------------------------------------------------------------

class TestMissingTimestampFilter:
    def test_passes_entry_without_timestamp(self):
        f = missing_timestamp_filter()
        assert f(_e(timestamp=None)) is True

    def test_blocks_entry_with_timestamp(self):
        f = missing_timestamp_filter()
        assert f(_e(timestamp=datetime(2024, 6, 15, 8, 30))) is False


# ---------------------------------------------------------------------------
# message_min_length_filter
# ---------------------------------------------------------------------------

class TestMessageMinLengthFilter:
    def test_returns_callable(self):
        assert callable(message_min_length_filter(0))

    def test_passes_message_equal_to_min(self):
        f = message_min_length_filter(5)
        assert f(_e(message="hello")) is True

    def test_passes_message_longer_than_min(self):
        f = message_min_length_filter(3)
        assert f(_e(message="long message")) is True

    def test_blocks_message_shorter_than_min(self):
        f = message_min_length_filter(10)
        assert f(_e(message="short")) is False

    def test_zero_min_passes_empty_message(self):
        f = message_min_length_filter(0)
        assert f(_e(message="")) is True

    def test_negative_min_raises(self):
        with pytest.raises(ValueError, match="min_length must be >= 0"):
            message_min_length_filter(-1)
