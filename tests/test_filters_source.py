"""Tests for gamelog_tail.filters_source."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_source import source_allowlist_filter, source_denylist_filter


def _e(source: str | None, message: str = "msg") -> LogEntry:
    return LogEntry(level="INFO", message=message, source=source)


# ---------------------------------------------------------------------------
# source_allowlist_filter
# ---------------------------------------------------------------------------

class TestSourceAllowlistFilter:
    def test_returns_callable(self):
        f = source_allowlist_filter(["Engine"])
        assert callable(f)

    def test_empty_allowed_raises(self):
        with pytest.raises(ValueError, match="allowed"):
            source_allowlist_filter([])

    def test_passes_matching_source(self):
        f = source_allowlist_filter(["Engine", "Renderer"])
        assert f(_e("Engine")) is True

    def test_drops_non_matching_source(self):
        f = source_allowlist_filter(["Engine"])
        assert f(_e("Audio")) is False

    def test_drops_none_source(self):
        f = source_allowlist_filter(["Engine"])
        assert f(_e(None)) is False

    def test_case_insensitive_by_default(self):
        f = source_allowlist_filter(["engine"])
        assert f(_e("ENGINE")) is True

    def test_case_sensitive_respects_case(self):
        f = source_allowlist_filter(["engine"], case_sensitive=True)
        assert f(_e("ENGINE")) is False
        assert f(_e("engine")) is True

    def test_multiple_sources_all_pass(self):
        f = source_allowlist_filter(["A", "B", "C"])
        for src in ("a", "b", "c"):
            assert f(_e(src)) is True


# ---------------------------------------------------------------------------
# source_denylist_filter
# ---------------------------------------------------------------------------

class TestSourceDenylistFilter:
    def test_returns_callable(self):
        f = source_denylist_filter(["Spam"])
        assert callable(f)

    def test_empty_denied_raises(self):
        with pytest.raises(ValueError, match="denied"):
            source_denylist_filter([])

    def test_drops_matching_source(self):
        f = source_denylist_filter(["Spam"])
        assert f(_e("Spam")) is False

    def test_passes_non_matching_source(self):
        f = source_denylist_filter(["Spam"])
        assert f(_e("Engine")) is True

    def test_passes_none_source(self):
        f = source_denylist_filter(["Spam"])
        assert f(_e(None)) is True

    def test_case_insensitive_by_default(self):
        f = source_denylist_filter(["spam"])
        assert f(_e("SPAM")) is False

    def test_case_sensitive_respects_case(self):
        f = source_denylist_filter(["spam"], case_sensitive=True)
        assert f(_e("SPAM")) is True
        assert f(_e("spam")) is False

    def test_multiple_sources_all_blocked(self):
        f = source_denylist_filter(["X", "Y"])
        for src in ("x", "y"):
            assert f(_e(src)) is False
