"""Tests for gamelog_tail.aggregator."""
import pytest

from gamelog_tail.aggregator import AggregateStats, aggregate
from gamelog_tail.parsers.base import LogEntry


def _e(level: str, source: str | None = None, message: str = "msg") -> LogEntry:
    return LogEntry(level=level, message=message, source=source)


class TestAggregateStatsRecord:
    def test_total_increments(self):
        stats = AggregateStats()
        stats.record(_e("INFO"))
        stats.record(_e("ERROR"))
        assert stats.total == 2

    def test_by_level_counter(self):
        stats = AggregateStats()
        for _ in range(3):
            stats.record(_e("INFO"))
        stats.record(_e("ERROR"))
        assert stats.by_level["INFO"] == 3
        assert stats.by_level["ERROR"] == 1

    def test_by_source_counter(self):
        stats = AggregateStats()
        stats.record(_e("INFO", source="Engine"))
        stats.record(_e("INFO", source="Engine"))
        stats.record(_e("INFO", source="Audio"))
        assert stats.by_source["Engine"] == 2
        assert stats.by_source["Audio"] == 1

    def test_errors_collected(self):
        stats = AggregateStats()
        entry = _e("ERROR", message="boom")
        stats.record(entry)
        assert entry in stats.errors

    def test_warnings_collected(self):
        stats = AggregateStats()
        entry = _e("WARNING", message="careful")
        stats.record(entry)
        assert entry in stats.warnings

    def test_warn_alias_collected(self):
        stats = AggregateStats()
        entry = _e("WARN")
        stats.record(entry)
        assert entry in stats.warnings

    def test_none_level_stored_as_unknown(self):
        stats = AggregateStats()
        stats.record(_e(None))
        assert stats.by_level["UNKNOWN"] == 1


class TestAggregate:
    def test_aggregate_function(self):
        entries = [_e("INFO"), _e("ERROR"), _e("WARNING")]
        stats = aggregate(entries)
        assert stats.total == 3
        assert stats.by_level["ERROR"] == 1

    def test_empty_list(self):
        stats = aggregate([])
        assert stats.total == 0


class TestTopSources:
    def test_returns_top_n(self):
        stats = AggregateStats()
        for _ in range(5):
            stats.record(_e("INFO", source="A"))
        for _ in range(3):
            stats.record(_e("INFO", source="B"))
        stats.record(_e("INFO", source="C"))
        top = stats.top_sources(2)
        assert top[0] == ("A", 5)
        assert top[1] == ("B", 3)
        assert len(top) == 2


class TestSummary:
    def test_summary_keys(self):
        stats = aggregate([_e("INFO"), _e("ERROR")])
        s = stats.summary()
        assert set(s.keys()) == {
            "total", "by_level", "by_source", "error_count", "warning_count"
        }

    def test_summary_counts(self):
        stats = aggregate([_e("ERROR"), _e("ERROR"), _e("WARNING")])
        s = stats.summary()
        assert s["error_count"] == 2
        assert s["warning_count"] == 1
