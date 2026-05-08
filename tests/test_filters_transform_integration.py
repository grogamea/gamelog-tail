"""Tests for gamelog_tail.filters_transform_integration."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_transform_integration import (
    build_transform_filters,
    apply_transform_filters,
)


def _e(
    message: str = "hello world",
    level: str = "INFO",
    source: str | None = "Engine",
) -> LogEntry:
    return LogEntry(timestamp=None, level=level, source=source, message=message, raw=message)


class TestBuildTransformFilters:
    def test_empty_args_returns_empty_list(self):
        assert build_transform_filters() == []

    def test_none_args_returns_empty_list(self):
        assert build_transform_filters(truncate=None, redact_patterns=None, tag=None) == []

    def test_truncate_returns_one_filter(self):
        result = build_transform_filters(truncate=20)
        assert len(result) == 1

    def test_redact_patterns_returns_one_per_pattern(self):
        result = build_transform_filters(redact_patterns=[r"\d+", r"secret"])
        assert len(result) == 2

    def test_tag_returns_one_filter(self):
        result = build_transform_filters(tag="staging")
        assert len(result) == 1

    def test_all_args_returns_four_filters(self):
        result = build_transform_filters(
            truncate=50,
            redact_patterns=[r"\d+", r"pass"],
            tag="env",
        )
        assert len(result) == 4

    def test_invalid_truncate_propagates(self):
        with pytest.raises(ValueError):
            build_transform_filters(truncate=0)

    def test_invalid_redact_pattern_propagates(self):
        with pytest.raises(ValueError):
            build_transform_filters(redact_patterns=[""])


class TestApplyTransformFilters:
    def test_empty_filters_returns_entry_unchanged(self):
        entry = _e()
        result = apply_transform_filters([], entry)
        assert result is entry

    def test_truncate_applied(self):
        filters = build_transform_filters(truncate=5)
        entry = _e(message="hello world")
        result = apply_transform_filters(filters, entry)
        assert result is not None
        assert result.message == "hello…"

    def test_redact_applied(self):
        filters = build_transform_filters(redact_patterns=[r"\d+"])
        entry = _e(message="user 42")
        result = apply_transform_filters(filters, entry)
        assert result is not None
        assert "42" not in result.message

    def test_tag_applied(self):
        filters = build_transform_filters(tag="prod")
        entry = _e(source="Renderer")
        result = apply_transform_filters(filters, entry)
        assert result is not None
        assert result.source == "prod:Renderer"

    def test_filters_applied_in_order(self):
        # truncate first, then redact — message is "hello" after truncate,
        # no digits so redact is a no-op.
        filters = build_transform_filters(truncate=5, redact_patterns=[r"\d+"])
        entry = _e(message="hello999")
        result = apply_transform_filters(filters, entry)
        assert result is not None
        assert result.message == "hello…"
