"""
tests/test_filters_sequence.py – Tests for sequence_filter and integration helpers.
"""
from __future__ import annotations

import time
from typing import List

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_sequence import sequence_filter
from gamelog_tail.filters_sequence_integration import (
    build_sequence_filters,
    apply_sequence_filters,
)


def _e(msg: str, level: str = "INFO", source: str = "game") -> LogEntry:
    return LogEntry(level=level, message=msg, source=source, timestamp=None, raw=msg)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestSequenceFilterConstruction:
    def test_returns_callable(self):
        f = sequence_filter(["start", "end"])
        assert callable(f)

    def test_too_few_patterns_raises(self):
        with pytest.raises(ValueError, match="at least two"):
            sequence_filter(["only_one"])

    def test_empty_patterns_raises(self):
        with pytest.raises(ValueError):
            sequence_filter([])

    def test_non_positive_window_raises(self):
        with pytest.raises(ValueError, match="window must be positive"):
            sequence_filter(["a", "b"], window=0)

    def test_negative_window_raises(self):
        with pytest.raises(ValueError):
            sequence_filter(["a", "b"], window=-5)


# ---------------------------------------------------------------------------
# Behaviour
# ---------------------------------------------------------------------------

class TestSequenceFilterBehaviour:
    def test_non_matching_entries_pass_through(self):
        f = sequence_filter(["alpha", "beta"])
        result = list(f(_e("nothing here")))
        assert len(result) == 1
        assert result[0].message == "nothing here"

    def test_incomplete_sequence_no_alert(self):
        f = sequence_filter(["alpha", "beta"])
        out1 = list(f(_e("alpha found")))
        assert len(out1) == 1  # no alert yet

    def test_complete_sequence_emits_alert(self):
        f = sequence_filter(["alpha", "beta"], alert_level="WARNING")
        list(f(_e("alpha found")))
        out = list(f(_e("beta found")))
        assert len(out) == 2
        alert = out[1]
        assert alert.level == "WARNING"
        assert "Sequence detected" in alert.message
        assert alert.source == "sequence_filter"

    def test_three_pattern_sequence(self):
        f = sequence_filter(["a", "b", "c"])
        list(f(_e("a")))
        list(f(_e("b")))
        out = list(f(_e("c")))
        assert len(out) == 2

    def test_sequence_resets_after_completion(self):
        f = sequence_filter(["a", "b"])
        list(f(_e("a")))
        list(f(_e("b")))  # completes
        list(f(_e("a")))  # restart
        out = list(f(_e("b")))  # complete again
        assert len(out) == 2

    def test_out_of_order_does_not_trigger(self):
        f = sequence_filter(["a", "b"])
        list(f(_e("b")))  # wrong order
        out = list(f(_e("a")))
        assert len(out) == 1  # no alert

    def test_custom_alert_source(self):
        f = sequence_filter(["a", "b"], alert_source="my_watcher")
        list(f(_e("a")))
        out = list(f(_e("b")))
        assert out[1].source == "my_watcher"


# ---------------------------------------------------------------------------
# Integration helpers
# ---------------------------------------------------------------------------

class TestBuildSequenceFilters:
    def test_no_args_returns_empty(self):
        assert build_sequence_filters() == []

    def test_none_returns_empty(self):
        assert build_sequence_filters(patterns=None) == []

    def test_single_pattern_returns_empty(self):
        assert build_sequence_filters(patterns=["only"]) == []

    def test_two_patterns_returns_one_filter(self):
        result = build_sequence_filters(patterns=["a", "b"])
        assert len(result) == 1
        assert callable(result[0])

    def test_apply_sequence_filters_passes_through(self):
        entries = [_e("hello"), _e("world")]
        out = list(apply_sequence_filters(entries, []))
        assert len(out) == 2

    def test_apply_sequence_filters_emits_alert(self):
        filters = build_sequence_filters(patterns=["start", "stop"])
        entries = [_e("start here"), _e("stop here")]
        out = list(apply_sequence_filters(entries, filters))
        assert len(out) == 3  # 2 originals + 1 alert
        assert any("Sequence detected" in e.message for e in out)
