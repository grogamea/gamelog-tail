"""Integration helpers for latency threshold filters.

Bridges the CLI / pipeline layer to :mod:`gamelog_tail.filters_latency`.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_latency import latency_threshold_filter


def build_latency_filters(
    max_ms: Optional[float] = None,
    min_ms: Optional[float] = None,
    field: str = "message",
) -> List[Callable[[LogEntry], bool]]:
    """Build a list of latency filters from optional CLI arguments.

    Returns an empty list when *max_ms* is ``None`` so that callers can
    unconditionally extend their filter pipeline without an extra guard.

    Args:
        max_ms: Upper latency threshold in milliseconds.  When ``None`` no
            filter is created.
        min_ms: Optional lower bound forwarded to
            :func:`~gamelog_tail.filters_latency.latency_threshold_filter`.
        field: Log-entry field to inspect (``"message"`` or ``"source"``).

    Returns:
        A list containing zero or one filter callable.
    """
    if max_ms is None:
        return []
    return [latency_threshold_filter(max_ms, field=field, min_ms=min_ms)]


def apply_latency_filters(
    filters: List[Callable[[LogEntry], bool]],
    entry: LogEntry,
) -> bool:
    """Return ``True`` if *entry* passes all latency filters.

    An empty filter list is treated as "pass everything".
    """
    return all(f(entry) for f in filters)
