"""Route log entries to different output channels based on level or source.

A routing filter does not suppress entries; instead it attaches a
``route`` key to ``LogEntry.extra`` so that downstream formatters or
writers can direct the entry to the appropriate sink (e.g. a file,
channel, or alert queue).
"""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional

from gamelog_tail.parsers.base import LogEntry

_FilterFn = Callable[[LogEntry], Optional[LogEntry]]

_VALID_LEVELS = {"debug", "info", "warning", "error", "fatal"}


def level_route_filter(
    routing: Dict[str, str],
    default: str = "default",
) -> _FilterFn:
    """Tag each entry with a route name derived from its level.

    Args:
        routing: Mapping of lower-case level name -> route name.
                 Unknown levels fall back to *default*.
        default: Route name used when the entry level is not in *routing*.

    Returns:
        A filter callable that always returns the (possibly mutated) entry.

    Raises:
        ValueError: If *routing* is empty or any key is not a recognised level.
    """
    if not routing:
        raise ValueError("routing mapping must not be empty")
    for key in routing:
        if key.lower() not in _VALID_LEVELS:
            raise ValueError(f"unrecognised level key in routing: {key!r}")

    normalised: Dict[str, str] = {k.lower(): v for k, v in routing.items()}

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        level_key = (entry.level or "").lower()
        route = normalised.get(level_key, default)
        if entry.extra is None:
            entry = LogEntry(
                timestamp=entry.timestamp,
                level=entry.level,
                source=entry.source,
                message=entry.message,
                raw=entry.raw,
                extra={"route": route},
            )
        else:
            entry.extra["route"] = route
        return entry

    return _filter


def source_route_filter(
    patterns: List[str],
    route: str,
    fallback: str = "default",
) -> _FilterFn:
    """Tag entries whose source matches any of *patterns* with *route*.

    Args:
        patterns: List of regex patterns matched against ``entry.source``.
        route:    Route name assigned when a pattern matches.
        fallback: Route name used when no pattern matches or source is absent.

    Returns:
        A filter callable that always returns the (possibly mutated) entry.

    Raises:
        ValueError: If *patterns* is empty or *route* is blank.
    """
    if not patterns:
        raise ValueError("patterns list must not be empty")
    if not route or not route.strip():
        raise ValueError("route must be a non-empty string")

    compiled = [re.compile(p) for p in patterns]

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        source = entry.source or ""
        matched = any(rx.search(source) for rx in compiled)
        chosen = route if matched else fallback
        if entry.extra is None:
            entry = LogEntry(
                timestamp=entry.timestamp,
                level=entry.level,
                source=entry.source,
                message=entry.message,
                raw=entry.raw,
                extra={"route": chosen},
            )
        else:
            entry.extra["route"] = chosen
        return entry

    return _filter
