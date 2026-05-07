"""Tests for gamelog_tail.filters_keyword."""

from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_keyword import (
    keyword_allowlist_filter,
    keyword_denylist_filter,
)


def _e(message: str) -> LogEntry:
    return LogEntry(level="INFO", message=message)


# ---------------------------------------------------------------------------
# keyword_allowlist_filter
# ---------------------------------------------------------------------------

class TestKeywordAllowlistFilter:
    def test_returns_callable(self):
        f = keyword_allowlist_filter(["error"])
        assert callable(f)

    def test_empty_keywords_raises(self):
        with pytest.raises(ValueError, match="at least one keyword"):
            keyword_allowlist_filter([])

    def test_passes_entry_containing_keyword(self):
        f = keyword_allowlist_filter(["crash"])
        assert f(_e("game crash detected")) is True

    def test_blocks_entry_without_keyword(self):
        f = keyword_allowlist_filter(["crash"])
        assert f(_e("everything is fine")) is False

    def test_case_insensitive_match(self):
        f = keyword_allowlist_filter(["CRASH"])
        assert f(_e("game crash detected")) is True

    def test_passes_on_any_keyword_match(self):
        f = keyword_allowlist_filter(["alpha", "beta"])
        assert f(_e("beta version loaded")) is True

    def test_blocks_when_no_keyword_matches(self):
        f = keyword_allowlist_filter(["alpha", "beta"])
        assert f(_e("gamma version loaded")) is False

    def test_partial_word_match(self):
        f = keyword_allowlist_filter(["err"])
        assert f(_e("error occurred")) is True


# ---------------------------------------------------------------------------
# keyword_denylist_filter
# ---------------------------------------------------------------------------

class TestKeywordDenylistFilter:
    def test_returns_callable(self):
        f = keyword_denylist_filter(["spam"])
        assert callable(f)

    def test_empty_keywords_raises(self):
        with pytest.raises(ValueError, match="at least one keyword"):
            keyword_denylist_filter([])

    def test_blocks_entry_containing_keyword(self):
        f = keyword_denylist_filter(["spam"])
        assert f(_e("spam message incoming")) is False

    def test_passes_entry_without_keyword(self):
        f = keyword_denylist_filter(["spam"])
        assert f(_e("legitimate log line")) is True

    def test_case_insensitive_block(self):
        f = keyword_denylist_filter(["SPAM"])
        assert f(_e("spam message incoming")) is False

    def test_blocks_on_any_keyword_match(self):
        f = keyword_denylist_filter(["ignore", "skip"])
        assert f(_e("skip this entry")) is False

    def test_passes_when_no_keyword_matches(self):
        f = keyword_denylist_filter(["ignore", "skip"])
        assert f(_e("process this entry")) is True
