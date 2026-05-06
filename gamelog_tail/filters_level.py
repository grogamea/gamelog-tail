"""
Level-range filter: keep only entries whose level falls within
a minimum / maximum severity band.

Severity order (lowest → highest):
    debug < info < warning < error < critical
"""

from __future__ import annotations

from typing import Callable, Iterable, Iterator

from gamelog_tail.parsers.base import LogEntry

# Canonical order used for comparisons.
_LEVELS: list[str] = ["debug", "info", "warning", "error", "critical"]
_LEVEL_RANK: dict[str, int] = {lvl: idx for idx, lvl in enumerate(_LEVELS)}


def _rank(level: str) -> int:
    """Return numeric rank for *level*, case-insensitive.  Unknown → -1."""
    return _LEVEL_RANK.get(level.lower(), -1)


def level_range_filter(
    min_level: str = "debug",
    max_level: str = "critical",
) -> Callable[[Iterable[LogEntry]], Iterator[LogEntry]]:
    """Return a filter that passes entries whose level is within [min_level, max_level].

    Args:
        min_level: Lowest severity to include (inclusive).  Defaults to ``"debug"``.
        max_level: Highest severity to include (inclusive).  Defaults to ``"critical"``.

    Raises:
        ValueError: If either level name is unrecognised or min > max.
    """
    min_level = min_level.lower()
    max_level = max_level.lower()

    if min_level not in _LEVEL_RANK:
        raise ValueError(f"Unknown min_level {min_level!r}. Valid: {_LEVELS}")
    if max_level not in _LEVEL_RANK:
        raise ValueError(f"Unknown max_level {max_level!r}. Valid: {_LEVELS}")

    lo = _rank(min_level)
    hi = _rank(max_level)
    if lo > hi:
        raise ValueError(
            f"min_level {min_level!r} is higher than max_level {max_level!r}"
        )

    def _filter(entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
        for entry in entries:
            rank = _rank(entry.level or "")
            # Entries with unknown / missing levels are always passed through.
            if rank == -1 or lo <= rank <= hi:
                yield entry

    return _filter
