"""Build transform filters from CLI / config arguments."""

from __future__ import annotations

from typing import Callable, List, Optional

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_transform import (
    truncate_message_filter,
    redact_pattern_filter,
    tag_source_filter,
)


def build_transform_filters(
    truncate: Optional[int] = None,
    redact_patterns: Optional[List[str]] = None,
    tag: Optional[str] = None,
    tag_separator: str = ":",
) -> List[Callable[[LogEntry], Optional[LogEntry]]]:
    """Return a list of transform filters based on provided arguments.

    Args:
        truncate: If given, truncate messages to this many characters.
        redact_patterns: List of regex patterns whose matches are redacted.
        tag: If given, prepend this tag to the source field.
        tag_separator: Separator used when prepending the tag.

    Returns:
        Ordered list of filter callables (may be empty).
    """
    filters: List[Callable[[LogEntry], Optional[LogEntry]]] = []

    if truncate is not None:
        filters.append(truncate_message_filter(truncate))

    for pattern in redact_patterns or []:
        filters.append(redact_pattern_filter(pattern))

    if tag is not None:
        filters.append(tag_source_filter(tag, separator=tag_separator))

    return filters


def apply_transform_filters(
    filters: List[Callable[[LogEntry], Optional[LogEntry]]],
    entry: LogEntry,
) -> Optional[LogEntry]:
    """Apply each transform filter in sequence, returning the (possibly mutated) entry.

    If any filter returns ``None`` the entry is dropped and ``None`` is returned.
    """
    current: Optional[LogEntry] = entry
    for f in filters:
        if current is None:
            return None
        current = f(current)
    return current
