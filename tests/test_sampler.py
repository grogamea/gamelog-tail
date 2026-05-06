"""Tests for gamelog_tail.sampler."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.sampler import Sampler, sample_filter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _e(source: str = "Game", level: str = "INFO", msg: str = "hello") -> LogEntry:
    return LogEntry(level=level, message=msg, source=source)


# ---------------------------------------------------------------------------
# Sampler.__init__
# ---------------------------------------------------------------------------

class TestSamplerInit:
    def test_valid_rate(self):
        s = Sampler(rate=5)
        assert s.rate == 5

    def test_rate_one_keeps_all(self):
        s = Sampler(rate=1)
        assert all(s.should_keep(_e()) for _ in range(20))

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError, match="rate must be >= 1"):
            Sampler(rate=0)


# ---------------------------------------------------------------------------
# Sampler.should_keep
# ---------------------------------------------------------------------------

class TestShouldKeep:
    def test_first_entry_always_kept(self):
        s = Sampler(rate=5)
        assert s.should_keep(_e()) is True

    def test_nth_entry_kept(self):
        s = Sampler(rate=3)
        results = [s.should_keep(_e()) for _ in range(9)]
        # positions 0, 3, 6 should be True
        assert results == [True, False, False, True, False, False, True, False, False]

    def test_different_buckets_independent(self):
        s = Sampler(rate=2)
        e_a = _e(source="A", level="INFO")
        e_b = _e(source="B", level="INFO")
        # Each bucket starts fresh
        assert s.should_keep(e_a) is True
        assert s.should_keep(e_b) is True
        assert s.should_keep(e_a) is False
        assert s.should_keep(e_b) is False

    def test_none_source_treated_as_empty_string(self):
        s = Sampler(rate=2)
        e = LogEntry(level="WARN", message="x", source=None)
        assert s.should_keep(e) is True
        assert s.should_keep(e) is False


# ---------------------------------------------------------------------------
# Sampler.reset
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_clears_counters(self):
        s = Sampler(rate=3)
        for _ in range(3):
            s.should_keep(_e())
        s.reset()
        # After reset the first entry should be kept again
        assert s.should_keep(_e()) is True


# ---------------------------------------------------------------------------
# sample_filter factory
# ---------------------------------------------------------------------------

class TestSampleFilter:
    def test_returns_callable(self):
        f = sample_filter(rate=4)
        assert callable(f)

    def test_exposes_sampler(self):
        f = sample_filter(rate=4)
        assert isinstance(f.__sampler__, Sampler)

    def test_filters_correctly(self):
        f = sample_filter(rate=2)
        results = [f(_e()) for _ in range(4)]
        assert results == [True, False, True, False]

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            sample_filter(rate=0)
