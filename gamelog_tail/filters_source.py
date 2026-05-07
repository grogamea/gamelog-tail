"""Source-based allow/deny list filter for log entries."""

from __future__ import annotations

from typing import Callable, Collection

from gamelog_tail.parsers.base import LogEntry


def source_allowlist_filter(
    allowed: Collection[str],
    *,
    case_sensitive: bool = False,
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes only entries whose source is in *allowed*.

    Entries with no source (``None``) are **always dropped**.

    Args:
        allowed: Collection of source strings to keep.
        case_sensitive: When ``False`` (default) comparison is case-insensitive.

    Returns:
        A callable suitable for use in a filter pipeline.
    """
    if not allowed:
        raise ValueError("allowed must contain at least one source")

    if case_sensitive:
        _allowed = frozenset(allowed)
    else:
        _allowed = frozenset(s.lower() for s in allowed)

    def _filter(entry: LogEntry) -> bool:
        if entry.source is None:
            return False
        candidate = entry.source if case_sensitive else entry.source.lower()
        return candidate in _allowed

    return _filter


def source_denylist_filter(
    denied: Collection[str],
    *,
    case_sensitive: bool = False,
) -> Callable[[LogEntry], bool]:
    """Return a filter that drops entries whose source is in *denied*.

    Entries with no source (``None``) are **always passed**.

    Args:
        denied: Collection of source strings to drop.
        case_sensitive: When ``False`` (default) comparison is case-insensitive.

    Returns:
        A callable suitable for use in a filter pipeline.
    """
    if not denied:
        raise ValueError("denied must contain at least one source")

    if case_sensitive:
        _denied = frozenset(denied)
    else:
        _denied = frozenset(s.lower() for s in denied)

    def _filter(entry: LogEntry) -> bool:
        if entry.source is None:
            return True
        candidate = entry.source if case_sensitive else entry.source.lower()
        return candidate not in _denied

    return _filter
