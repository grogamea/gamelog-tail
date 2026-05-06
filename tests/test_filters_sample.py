"""Tests for gamelog_tail.filters_sample."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_sample import sample_filter
from gamelog_tail.sampler import Sampler


def _e(source: str = "Engine", level: str = "DEBUG", msg: str = "tick") -> LogEntry:
    return LogEntry(level=level, message=msg, source=source)


class TestSampleFilter:
    def test_returns_callable(self):
        f = sample_filter(rate=5)
        assert callable(f)

    def test_rate_one_passes_everything(self):
        f = sample_filter(rate=1)
        assert all(f(_e()) for _ in range(10))

    def test_rate_three_passes_every_third(self):
        f = sample_filter(rate=3)
        results = [f(_e()) for _ in range(6)]
        assert results == [True, False, False, True, False, False]

    def test_exposes_sampler_attribute(self):
        f = sample_filter(rate=2)
        assert hasattr(f, "__sampler__")
        assert isinstance(f.__sampler__, Sampler)

    def test_invalid_rate_raises_value_error(self):
        with pytest.raises(ValueError, match="rate must be >= 1"):
            sample_filter(rate=-1)

    def test_independent_buckets(self):
        f = sample_filter(rate=2)
        ea = _e(source="A")
        eb = _e(source="B")
        # Both buckets start fresh — first call for each should pass
        assert f(ea) is True
        assert f(eb) is True
        assert f(ea) is False
        assert f(eb) is False
