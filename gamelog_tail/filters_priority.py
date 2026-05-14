"""Priority-based filter: only pass entries whose level maps to a minimum
priority score, with an optional per-source override map."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from gamelog_tail.parsers.base import LogEntry

# Lower number = higher priority (like syslog)
_PRIORITY: Dict[str, int] = {
    "fatal": 0,
    "error": 1,
    "warning": 2,
    "warn": 2,
    "info": 3,
    "debug": 4,
    "verbose": 5,
    "trace": 6,
}


def _rank(level: str) -> int:
    """Return numeric priority for *level* (case-insensitive). Unknown levels
    are treated as lowest priority (highest number)."""
    return _PRIORITY.get(level.lower(), 99)


def priority_filter(
    min_level: str,
    source_overrides: Optional[Dict[str, str]] = None,
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes entries at *min_level* or higher priority.

    Args:
        min_level: Minimum level name to pass (e.g. ``"warning"``).  Entries
            with a *lower* priority (higher numeric rank) are suppressed.
        source_overrides: Optional mapping of source name -> min_level that
            overrides *min_level* for specific sources.

    Raises:
        ValueError: If *min_level* is not a recognised level name, or if any
            value in *source_overrides* is not recognised.
    """
    if min_level.lower() not in _PRIORITY:
        raise ValueError(f"Unknown level: {min_level!r}")

    overrides: Dict[str, int] = {}
    if source_overrides:
        for src, lvl in source_overrides.items():
            if lvl.lower() not in _PRIORITY:
                raise ValueError(
                    f"Unknown level in source_overrides for {src!r}: {lvl!r}"
                )
            overrides[src] = _rank(lvl)

    default_rank = _rank(min_level)

    def _filter(entry: LogEntry) -> bool:
        threshold = overrides.get(entry.source or "", default_rank)
        entry_rank = _rank(entry.level) if entry.level else 99
        return entry_rank <= threshold

    return _filter
