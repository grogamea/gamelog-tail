"""Integration helpers that wire keyword filters into the pipeline.

This module is imported by *pipeline.py* to extend ``build_filters`` with
``keyword_allow`` and ``keyword_deny`` support without modifying the core
pipeline module.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_keyword import (
    keyword_allowlist_filter,
    keyword_denylist_filter,
)


def build_keyword_filters(
    keyword_allow: Optional[Sequence[str]] = None,
    keyword_deny: Optional[Sequence[str]] = None,
) -> List[Callable[[LogEntry], bool]]:
    """Build and return a list of keyword-based filter callables.

    Args:
        keyword_allow: If provided and non-empty, add an allowlist filter.
        keyword_deny:  If provided and non-empty, add a denylist filter.

    Returns:
        A (possibly empty) list of filter callables ready to pass to
        :func:`gamelog_tail.pipeline.run`.
    """
    filters: List[Callable[[LogEntry], bool]] = []

    if keyword_allow:
        filters.append(keyword_allowlist_filter(keyword_allow))

    if keyword_deny:
        filters.append(keyword_denylist_filter(keyword_deny))

    return filters


def apply_keyword_filters(
    entries: Sequence[LogEntry],
    keyword_allow: Optional[Sequence[str]] = None,
    keyword_deny: Optional[Sequence[str]] = None,
) -> List[LogEntry]:
    """Convenience function: apply keyword filters to a list of entries.

    Useful for one-shot batch processing rather than streaming pipelines.

    Args:
        entries:       The log entries to filter.
        keyword_allow: Optional allowlist keywords.
        keyword_deny:  Optional denylist keywords.

    Returns:
        Filtered list of :class:`~gamelog_tail.parsers.base.LogEntry`.
    """
    filters = build_keyword_filters(keyword_allow, keyword_deny)
    result = list(entries)
    for f in filters:
        result = [e for e in result if f(e)]
    return result
