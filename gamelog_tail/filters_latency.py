"""Filter entries based on a numeric latency value embedded in the message.

Expects messages that contain a latency token of the form ``latency=<number>``
(case-insensitive).  Entries whose latency exceeds *max_ms* are passed through;
all others are suppressed.  This is useful for surfacing only the slow-path
log lines from game-engine network or rendering output.
"""
from __future__ import annotations

import re
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry

_LATENCY_RE = re.compile(r"latency[=:]\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def latency_threshold_filter(
    max_ms: float,
    *,
    field: str = "message",
    min_ms: Optional[float] = None,
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes entries whose latency exceeds *max_ms*.

    Args:
        max_ms: Upper threshold in milliseconds (exclusive lower bound for
            passing entries).  Must be positive.
        field: Which ``LogEntry`` attribute to scan.  Defaults to
            ``"message"``; ``"source"`` is also accepted.
        min_ms: Optional lower bound.  When given, only entries whose latency
            is in the range ``(min_ms, +inf)`` AND ``> max_ms`` are passed.
            In practice this lets callers express a band rather than a single
            threshold.  Must be non-negative and less than *max_ms*.

    Returns:
        A callable ``(LogEntry) -> bool``.

    Raises:
        ValueError: If *max_ms* is not positive, *field* is invalid, or
            *min_ms* is out of range.
    """
    if max_ms <= 0:
        raise ValueError(f"max_ms must be positive, got {max_ms!r}")
    if field not in ("message", "source"):
        raise ValueError(f"field must be 'message' or 'source', got {field!r}")
    if min_ms is not None:
        if min_ms < 0:
            raise ValueError(f"min_ms must be non-negative, got {min_ms!r}")
        if min_ms >= max_ms:
            raise ValueError(
                f"min_ms ({min_ms!r}) must be less than max_ms ({max_ms!r})"
            )

    def _filter(entry: LogEntry) -> bool:
        text = getattr(entry, field, None) or ""
        match = _LATENCY_RE.search(text)
        if match is None:
            return False
        value = float(match.group(1))
        if min_ms is not None and value <= min_ms:
            return False
        return value > max_ms

    return _filter
