"""
Convenience helpers to wire :mod:`gamelog_tail.filters_severity` into a
pipeline from CLI-style arguments.
"""

from __future__ import annotations

from typing import Any, Callable

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.filters_severity import severity_burst_filter


def build_severity_filters(
    quiet_min_level: str | None = None,
    burst_trigger_level: str | None = None,
    burst_threshold: int | None = None,
    window_seconds: float | None = None,
) -> list[Callable[[LogEntry], LogEntry | None]]:
    """Return a list containing a severity burst filter if any arg is supplied.

    If *all* arguments are ``None`` an empty list is returned so the caller
    can safely extend its filter list without checking.
    """
    args: dict[str, Any] = {}
    if quiet_min_level is not None:
        args["quiet_min_level"] = quiet_min_level
    if burst_trigger_level is not None:
        args["burst_trigger_level"] = burst_trigger_level
    if burst_threshold is not None:
        args["burst_threshold"] = burst_threshold
    if window_seconds is not None:
        args["window_seconds"] = window_seconds

    if not args:
        return []

    return [severity_burst_filter(**args)]


def apply_severity_filters(
    entry: LogEntry,
    filters: list[Callable[[LogEntry], LogEntry | None]],
) -> LogEntry | None:
    """Run *entry* through each severity filter in order.

    Returns ``None`` as soon as any filter suppresses the entry.
    """
    current: LogEntry | None = entry
    for f in filters:
        if current is None:
            return None
        current = f(current)
    return current
