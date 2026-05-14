"""Integration helpers: build context-window filters from CLI/config args."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_context import context_window_filter
from gamelog_tail.filters import by_level, by_message_pattern


def build_context_filters(
    level: str | None = None,
    pattern: str | None = None,
    before: int = 2,
    after: int = 2,
) -> list[Callable[[Iterable[LogEntry]], Iterator[LogEntry]]]:
    """Build a list of context-window filters from optional trigger criteria.

    At most one filter is returned.  If neither *level* nor *pattern* is
    supplied the list is empty.

    Args:
        level: Trigger on entries whose level matches this string.
        pattern: Trigger on entries whose message matches this regex.
        before: Lines of pre-context to include.
        after: Lines of post-context to include.
    """
    if level is None and pattern is None:
        return []

    predicates: list[Callable[[LogEntry], bool]] = []

    if level is not None:
        _level_filter = by_level(level)

        def _level_pred(entry: LogEntry) -> bool:
            return next(iter(_level_filter([entry])), None) is not None

        predicates.append(_level_pred)

    if pattern is not None:
        _msg_filter = by_message_pattern(pattern)

        def _msg_pred(entry: LogEntry) -> bool:
            return next(iter(_msg_filter([entry])), None) is not None

        predicates.append(_msg_pred)

    def _combined(entry: LogEntry) -> bool:
        return any(p(entry) for p in predicates)

    return [context_window_filter(_combined, before=before, after=after)]


def apply_context_filters(
    entries: Iterable[LogEntry],
    filters: list[Callable[[Iterable[LogEntry]], Iterator[LogEntry]]],
) -> Iterable[LogEntry]:
    """Apply a list of context filters sequentially."""
    result: Iterable[LogEntry] = entries
    for f in filters:
        result = f(result)
    return result
