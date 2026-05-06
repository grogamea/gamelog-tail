"""High-level pipeline: parse → filter → aggregate → format → emit."""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from gamelog_tail import filters as _filters
from gamelog_tail.aggregator import AggregateStats, aggregate
from gamelog_tail.formatters import get_formatter
from gamelog_tail.formatters_summary import get_summary_formatter
from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.tail import parse_stream


def build_filters(
    levels: Optional[List[str]] = None,
    message_pattern: Optional[str] = None,
    source_pattern: Optional[str] = None,
) -> List[Callable[[LogEntry], bool]]:
    """Construct a list of filter callables from CLI-style arguments."""
    result: List[Callable[[LogEntry], bool]] = []
    if levels:
        result.append(_filters.by_level(*levels))
    if message_pattern:
        result.append(_filters.by_message_pattern(message_pattern))
    if source_pattern:
        result.append(_filters.by_source_pattern(source_pattern))
    return result


def run(
    lines: Iterable[str],
    *,
    parser_hint: Optional[str] = None,
    levels: Optional[List[str]] = None,
    message_pattern: Optional[str] = None,
    source_pattern: Optional[str] = None,
    formatter: str = "plain",
    print_fn: Callable[[str], None] = print,
    collect_stats: bool = False,
) -> Optional[AggregateStats]:
    """Run the full pipeline over *lines*.

    Returns an :class:`AggregateStats` instance when *collect_stats* is
    ``True``, otherwise ``None``.
    """
    active_filters = build_filters(
        levels=levels,
        message_pattern=message_pattern,
        source_pattern=source_pattern,
    )
    fmt = get_formatter(formatter)
    entries: List[LogEntry] = []

    for entry in parse_stream(lines, parser_hint=parser_hint):
        if all(f(entry) for f in active_filters):
            print_fn(fmt(entry))
            if collect_stats:
                entries.append(entry)

    if collect_stats:
        return aggregate(entries)
    return None
