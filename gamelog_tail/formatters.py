"""Output formatters for log entries."""

from __future__ import annotations

import json
from typing import Callable

from gamelog_tail.parsers.base import LogEntry

# Colour codes for terminal output
_LEVEL_COLOURS = {
    "ERROR": "\033[31m",    # red
    "WARNING": "\033[33m",  # yellow
    "INFO": "\033[36m",     # cyan
    "DEBUG": "\033[37m",    # white
}
_RESET = "\033[0m"
_BOLD = "\033[1m"

Formatter = Callable[[LogEntry], str]


def plain(entry: LogEntry) -> str:
    """Format a log entry as a plain text line."""
    parts = []
    if entry.timestamp:
        parts.append(f"[{entry.timestamp}]")
    if entry.level:
        parts.append(f"[{entry.level.upper()}]")
    if entry.source:
        parts.append(f"({entry.source})")
    parts.append(entry.message)
    return " ".join(parts)


def coloured(entry: LogEntry) -> str:
    """Format a log entry with ANSI colour codes based on level."""
    level_key = (entry.level or "").upper()
    colour = _LEVEL_COLOURS.get(level_key, "")

    parts = []
    if entry.timestamp:
        parts.append(f"[{entry.timestamp}]")
    if entry.level:
        parts.append(f"{_BOLD}{colour}[{entry.level.upper()}]{_RESET}")
    if entry.source:
        parts.append(f"({entry.source})")
    parts.append(f"{colour}{entry.message}{_RESET}")
    return " ".join(parts)


def as_json(entry: LogEntry) -> str:
    """Format a log entry as a JSON object."""
    data = {
        "message": entry.message,
        "level": entry.level,
        "source": entry.source,
        "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
        "raw": entry.raw,
    }
    return json.dumps(data, default=str)


def get_formatter(name: str) -> Formatter:
    """Return a formatter callable by name.

    Supported names: 'plain', 'colour'/'color', 'json'.
    Raises ValueError for unknown names.
    """
    _map: dict[str, Formatter] = {
        "plain": plain,
        "colour": coloured,
        "color": coloured,
        "json": as_json,
    }
    try:
        return _map[name.lower()]
    except KeyError:
        raise ValueError(
            f"Unknown formatter {name!r}. Choose from: {', '.join(_map)}"
        )
