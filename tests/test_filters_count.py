"""Tests for gamelog_tail.filters_count."""
from __future__ import annotations

from datetime import datetime

import pytest

from gamelog_tail.filters_count import first_n_filter
from gamelog_tail.parsers.base import LogEntry


def _e(
    message: str = "msg",
    level: str = "INFO",
    source: str | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2024, 1, 1, 0, 0, 0),
        level=level,
        message=message,
        source=source,
    )


class TestFirstNFilterConstruction:
    def test_returns_callable(self):
        f = first_n_filter(3)
        assert callable(f)

    def test_invalid_n_zero_raises(self):
        with pytest.raises(ValueError, match="n must be >= 1"):
            first_n_filter(0)

    def test_invalid_n_negative_raises(self):
        with pytest.raises(ValueError, match="n must be >= 1"):
            first_n_filter(-5)

    def test_invalid_key_raises(self):
        with pytest.raises(ValueError, match="key must be one of"):
            first_n_filter(1, key="timestamp")


class TestFirstNFilterByMessage:
    def test_first_occurrence_passes(self):
        f = first_n_filter(1)
        assert f(_e("hello")) is True

    def test_second_occurrence_blocked(self):
        f = first_n_filter(1)
        f(_e("hello"))
        assert f(_e("hello")) is False

    def test_different_messages_independent(self):
        f = first_n_filter(1)
        assert f(_e("alpha")) is True
        assert f(_e("beta")) is True

    def test_n_equals_three_passes_three(self):
        f = first_n_filter(3)
        results = [f(_e("x")) for _ in range(4)]
        assert results == [True, True, True, False]


class TestFirstNFilterBySource:
    def test_groups_by_source(self):
        f = first_n_filter(2, key="source")
        assert f(_e(source="Renderer")) is True
        assert f(_e(source="Renderer")) is True
        assert f(_e(source="Renderer")) is False

    def test_none_source_treated_as_own_bucket(self):
        f = first_n_filter(1, key="source")
        assert f(_e(source=None)) is True
        assert f(_e(source=None)) is False
        assert f(_e(source="Audio")) is True


class TestFirstNFilterByLevel:
    def test_groups_by_level(self):
        f = first_n_filter(1, key="level")
        assert f(_e(level="ERROR")) is True
        assert f(_e(level="ERROR")) is False
        assert f(_e(level="WARNING")) is True

    def test_each_level_independent(self):
        f = first_n_filter(2, key="level")
        for _ in range(3):
            f(_e(level="INFO"))
        assert f(_e(level="DEBUG")) is True
