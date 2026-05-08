"""Entry transformation filters: truncate, redact, and tag log entries."""

from __future__ import annotations

import re
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def truncate_message_filter(max_length: int) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that truncates entry messages to *max_length* characters."""
    if max_length < 1:
        raise ValueError(f"max_length must be >= 1, got {max_length}")

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        if len(entry.message) <= max_length:
            return entry
        truncated = entry.message[:max_length] + "…"
        return LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            source=entry.source,
            message=truncated,
            raw=entry.raw,
        )

    return _filter


def redact_pattern_filter(
    pattern: str, replacement: str = "[REDACTED]"
) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that replaces *pattern* matches in the message with *replacement*."""
    if not pattern:
        raise ValueError("pattern must not be empty")
    compiled = re.compile(pattern)

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        new_message = compiled.sub(replacement, entry.message)
        if new_message == entry.message:
            return entry
        return LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            source=entry.source,
            message=new_message,
            raw=entry.raw,
        )

    return _filter


def tag_source_filter(
    tag: str, separator: str = ":"
) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that prepends *tag* to the source field (or sets it if absent)."""
    if not tag:
        raise ValueError("tag must not be empty")

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        current = entry.source or ""
        new_source = f"{tag}{separator}{current}" if current else tag
        return LogEntry(
            timestamp=entry.timestamp,
            level=entry.level,
            source=new_source,
            message=entry.message,
            raw=entry.raw,
        )

    return _filter
