"""
filters_sequence_integration.py – Build sequence filters from CLI / config args.
"""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_sequence import sequence_filter


def build_sequence_filters(
    patterns: Optional[List[str]] = None,
    window: float = 60.0,
    alert_level: str = "ERROR",
    alert_source: str = "sequence_filter",
) -> List[Callable[[LogEntry], Iterable[LogEntry]]]:
    """Return a list containing a single sequence filter, or an empty list.

    A filter is only created when *patterns* contains at least two entries.

    Args:
        patterns:     Ordered regex patterns to watch for.
        window:       Time window in seconds for the sequence to complete.
        alert_level:  Level for the synthetic alert entry.
        alert_source: Source for the synthetic alert entry.
    """
    if not patterns or len(patterns) < 2:
        return []
    return [
        sequence_filter(
            patterns=patterns,
            window=window,
            alert_level=alert_level,
            alert_source=alert_source,
        )
    ]


def apply_sequence_filters(
    entries: Iterable[LogEntry],
    filters: List[Callable[[LogEntry], Iterable[LogEntry]]],
) -> Iterable[LogEntry]:
    """Apply every sequence filter in *filters* to each entry in *entries*."""
    for entry in entries:
        current: Iterable[LogEntry] = [entry]
        for f in filters:
            current = (out for e in current for out in f(e))
        yield from current
