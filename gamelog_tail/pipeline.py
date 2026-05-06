"""Composable pipeline: parse → filter → format."""

from __future__ import annotations

from typing import Iterable, Iterator

from gamelog_tail.parsers.base import BaseParser, LogEntry
from gamelog_tail.filters import FilterFn
from gamelog_tail.formatters import Formatter, plain


def run(
    lines: Iterable[str],
    parser: BaseParser,
    filters: Iterable[FilterFn] | None = None,
    formatter: Formatter = plain,
) -> Iterator[str]:
    """Parse *lines*, apply every filter, then format surviving entries.

    Yields one formatted string per entry that passes all filters.
    Lines that the parser cannot recognise are yielded as-is (raw).
    """
    filter_list = list(filters or [])

    for line in lines:
        line = line.rstrip("\n")
        if not line:
            continue

        entry: LogEntry | None = parser.parse(line)
        if entry is None:
            yield line
            continue

        if all(f(entry) for f in filter_list):
            yield formatter(entry)


def build_filters(*filter_fns: FilterFn) -> list[FilterFn]:
    """Convenience helper to collect filter callables into a list."""
    return list(filter_fns)
