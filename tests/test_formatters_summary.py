"""Tests for gamelog_tail.formatters_summary."""
import json

import pytest

from gamelog_tail.aggregator import aggregate
from gamelog_tail.formatters_summary import (
    get_summary_formatter,
    json_summary,
    plain_summary,
)
from gamelog_tail.parsers.base import LogEntry


def _e(level, source=None):
    return LogEntry(level=level, message="x", source=source)


@pytest.fixture()
def stats():
    return aggregate(
        [
            _e("INFO", source="Engine"),
            _e("INFO", source="Engine"),
            _e("WARNING", source="Audio"),
            _e("ERROR"),
        ]
    )


class TestPlainSummary:
    def test_contains_total(self, stats):
        out = plain_summary(stats)
        assert "Total entries" in out
        assert "4" in out

    def test_contains_levels(self, stats):
        out = plain_summary(stats)
        assert "INFO" in out
        assert "ERROR" in out
        assert "WARNING" in out

    def test_contains_sources(self, stats):
        out = plain_summary(stats)
        assert "Engine" in out
        assert "Audio" in out

    def test_contains_error_warning_counts(self, stats):
        out = plain_summary(stats)
        assert "Errors" in out
        assert "Warnings" in out


class TestJsonSummary:
    def test_valid_json(self, stats):
        out = json_summary(stats)
        parsed = json.loads(out)
        assert isinstance(parsed, dict)

    def test_total_present(self, stats):
        parsed = json.loads(json_summary(stats))
        assert parsed["total"] == 4

    def test_by_level_present(self, stats):
        parsed = json.loads(json_summary(stats))
        assert "by_level" in parsed
        assert parsed["by_level"]["INFO"] == 2


class TestGetSummaryFormatter:
    def test_plain(self, stats):
        fmt = get_summary_formatter("plain")
        assert "Total" in fmt(stats)

    def test_json(self, stats):
        fmt = get_summary_formatter("json")
        json.loads(fmt(stats))  # must not raise

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown summary formatter"):
            get_summary_formatter("xml")
