"""Tests for gamelog_tail.filters_routing."""
from __future__ import annotations

import pytest

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_routing import level_route_filter, source_route_filter


def _e(
    level: str = "info",
    source: str | None = "Engine",
    message: str = "hello",
    extra: dict | None = None,
) -> LogEntry:
    return LogEntry(
        timestamp=None,
        level=level,
        source=source,
        message=message,
        raw=message,
        extra=extra,
    )


# ---------------------------------------------------------------------------
# level_route_filter
# ---------------------------------------------------------------------------

class TestLevelRouteFilter:
    def test_returns_callable(self):
        f = level_route_filter({"error": "alerts"})
        assert callable(f)

    def test_empty_routing_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            level_route_filter({})

    def test_invalid_level_key_raises(self):
        with pytest.raises(ValueError, match="unrecognised level"):
            level_route_filter({"verbose": "sink"})

    def test_known_level_gets_route(self):
        f = level_route_filter({"error": "alerts", "warning": "warnings"})
        result = f(_e(level="error"))
        assert result is not None
        assert result.extra["route"] == "alerts"

    def test_unknown_level_uses_default(self):
        f = level_route_filter({"error": "alerts"}, default="misc")
        result = f(_e(level="debug"))
        assert result.extra["route"] == "misc"

    def test_case_insensitive_level(self):
        f = level_route_filter({"warning": "warn_sink"})
        result = f(_e(level="WARNING"))
        assert result.extra["route"] == "warn_sink"

    def test_existing_extra_preserved(self):
        f = level_route_filter({"info": "info_sink"})
        entry = _e(level="info", extra={"foo": "bar"})
        result = f(entry)
        assert result.extra["foo"] == "bar"
        assert result.extra["route"] == "info_sink"

    def test_entry_without_level_uses_default(self):
        f = level_route_filter({"error": "alerts"}, default="fallback")
        result = f(_e(level=None))
        assert result.extra["route"] == "fallback"


# ---------------------------------------------------------------------------
# source_route_filter
# ---------------------------------------------------------------------------

class TestSourceRouteFilter:
    def test_returns_callable(self):
        f = source_route_filter(["Engine"], route="engine_sink")
        assert callable(f)

    def test_empty_patterns_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            source_route_filter([], route="sink")

    def test_blank_route_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            source_route_filter(["Engine"], route="   ")

    def test_matching_source_gets_route(self):
        f = source_route_filter([r"Engine"], route="engine_sink")
        result = f(_e(source="Engine"))
        assert result.extra["route"] == "engine_sink"

    def test_non_matching_source_uses_fallback(self):
        f = source_route_filter([r"Engine"], route="engine_sink", fallback="other")
        result = f(_e(source="Renderer"))
        assert result.extra["route"] == "other"

    def test_missing_source_uses_fallback(self):
        f = source_route_filter([r"Engine"], route="engine_sink", fallback="none")
        result = f(_e(source=None))
        assert result.extra["route"] == "none"

    def test_regex_partial_match(self):
        f = source_route_filter([r"^Audio"], route="audio_sink")
        result = f(_e(source="AudioManager"))
        assert result.extra["route"] == "audio_sink"

    def test_existing_extra_preserved(self):
        f = source_route_filter([r"Engine"], route="engine_sink")
        entry = _e(source="Engine", extra={"x": 1})
        result = f(entry)
        assert result.extra["x"] == 1
        assert result.extra["route"] == "engine_sink"
