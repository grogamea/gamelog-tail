"""Filter that passes only the first N matching entries per key.

Useful for suppressing repeated identical log categories while still
showing the first few occurrences.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def first_n_filter(
    n: int,
    key: str = "message",
) -> Callable[[LogEntry], bool]:
    """Return a filter that passes only the first *n* entries sharing the same key.

    Args:
        n: Maximum number of entries to pass per unique key value.  Must be >= 1.
        key: Which attribute of :class:`LogEntry` to group by.  Supported values
            are ``"message"``, ``"source"``, and ``"level"``.

    Returns:
        A callable that returns ``True`` when the entry should be kept.

    Raises:
        ValueError: If *n* is less than 1 or *key* is not a supported field.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n!r}")

    _supported_keys = {"message", "source", "level"}
    if key not in _supported_keys:
        raise ValueError(
            f"key must be one of {sorted(_supported_keys)}, got {key!r}"
        )

    counts: dict[Optional[str], int] = defaultdict(int)

    def _filter(entry: LogEntry) -> bool:
        bucket: Optional[str] = getattr(entry, key, None)
        counts[bucket] += 1
        return counts[bucket] <= n

    return _filter
