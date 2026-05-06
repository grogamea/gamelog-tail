"""Log entry filters for gamelog-tail."""

from __future__ import annotations

import re
from typing import Callable, Iterable, Iterator

from gamelog_tail.parsers.base import LogEntry


FilterFn = Callable[[LogEntry], bool]


def by_level(*levels: str) -> FilterFn:
    """Return a filter that matches entries whose level is in *levels*.

    Comparison is case-insensitive.
    """
    normalised = {lvl.upper() for lvl in levels}

    def _filter(entry: LogEntry) -> bool:
        return (entry.level or "").upper() in normalised

    return _filter


def by_message_pattern(pattern: str, flags: int = re.IGNORECASE) -> FilterFn:
    """Return a filter that matches entries whose message contains *pattern*."""
    compiled = re.compile(pattern, flags)

    def _filter(entry: LogEntry) -> bool:
        return bool(compiled.search(entry.message))

    return _filter


def by_source_pattern(pattern: str, flags: int = re.IGNORECASE) -> FilterFn:
    """Return a filter that matches entries whose source matches *pattern*."""
    compiled = re.compile(pattern, flags)

    def _filter(entry: LogEntry) -> bool:
        if entry.source is None:
            return False
        return bool(compiled.search(entry.source))

    return _filter


def combine_any(*filters: FilterFn) -> FilterFn:
    """Return a filter that passes entries matching ANY of *filters* (OR)."""

    def _filter(entry: LogEntry) -> bool:
        return any(f(entry) for f in filters)

    return _filter


def combine_all(*filters: FilterFn) -> FilterFn:
    """Return a filter that passes entries matching ALL of *filters* (AND)."""

    def _filter(entry: LogEntry) -> bool:
        return all(f(entry) for f in filters)

    return _filter


def apply_filters(
    entries: Iterable[LogEntry],
    *filters: FilterFn,
    mode: str = "all",
) -> Iterator[LogEntry]:
    """Yield entries from *entries* that satisfy *filters*.

    *mode* can be ``'all'`` (AND, default) or ``'any'`` (OR).
    """
    if mode == "any":
        combined = combine_any(*filters)
    else:
        combined = combine_all(*filters)

    for entry in entries:
        if combined(entry):
            yield entry
