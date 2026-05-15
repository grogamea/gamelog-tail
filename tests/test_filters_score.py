"""Tests for gamelog_tail.filters_score."""
from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_score import score_filter


def _e(
    message: str = "msg",
    level: str = "INFO",
    source: str | None = None,
) -> LogEntry:
    return LogEntry(level=level, message=message, source=source)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestScoreFilterConstruction:
    def test_returns_callable(self):
        f = score_filter([(lambda e: True, 1.0)])
        assert callable(f)

    def test_empty_rules_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            score_filter([])

    def test_zero_min_score_raises(self):
        with pytest.raises(ValueError, match="min_score"):
            score_filter([(lambda e: True, 1.0)], min_score=0)

    def test_negative_min_score_raises(self):
        with pytest.raises(ValueError, match="min_score"):
            score_filter([(lambda e: True, 1.0)], min_score=-5)


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------

class TestScoreFilterBehaviour:
    def test_single_rule_passes_when_matched(self):
        f = score_filter([(lambda e: e.level == "ERROR", 1.0)])
        entry = _e(level="ERROR")
        assert f(entry) is entry

    def test_single_rule_blocks_when_unmatched(self):
        f = score_filter([(lambda e: e.level == "ERROR", 1.0)])
        assert f(_e(level="INFO")) is None

    def test_multiple_rules_cumulative_score(self):
        rules = [
            (lambda e: e.level == "ERROR", 2.0),
            (lambda e: "crash" in e.message, 3.0),
        ]
        f = score_filter(rules, min_score=4.0)
        # Only ERROR matches -> score 2.0 < 4.0 -> blocked
        assert f(_e(level="ERROR", message="normal")) is None
        # Only crash matches -> score 3.0 < 4.0 -> blocked
        assert f(_e(level="INFO", message="crash")) is None
        # Both match -> score 5.0 >= 4.0 -> passes
        entry = _e(level="ERROR", message="crash")
        assert f(entry) is entry

    def test_exact_threshold_passes(self):
        f = score_filter([(lambda e: True, 2.5)], min_score=2.5)
        entry = _e()
        assert f(entry) is entry

    def test_fractional_weights_accumulate(self):
        rules = [
            (lambda e: "warn" in e.message.lower(), 0.4),
            (lambda e: e.source is not None, 0.4),
            (lambda e: e.level == "WARNING", 0.4),
        ]
        f = score_filter(rules, min_score=1.0)
        # All three match -> 1.2 >= 1.0 -> passes
        entry = _e(level="WARNING", message="warn here", source="sys")
        assert f(entry) is entry
        # Only two match -> 0.8 < 1.0 -> blocked
        assert f(_e(level="WARNING", message="warn here")) is None

    def test_no_rules_match_blocks_entry(self):
        f = score_filter(
            [(lambda e: e.level == "CRITICAL", 10.0)],
            min_score=1.0,
        )
        assert f(_e(level="DEBUG")) is None
