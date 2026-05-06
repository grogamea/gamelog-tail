"""Pipeline-compatible filter factory that wraps :class:`Deduplicator`.

Usage in a pipeline::

    from gamelog_tail.filters_dedup import dedup_filter
    filters = [dedup_filter(window_seconds=3)]
"""

from __future__ import annotations

from typing import Callable

from gamelog_tail.deduplicator import Deduplicator
from gamelog_tail.parsers.base import LogEntry

# A filter is any callable (LogEntry) -> bool where True means *keep*.
Filter = Callable[[LogEntry], bool]


def dedup_filter(window_seconds: float = 5.0, max_tracked: int = 256) -> Filter:
    """Return a stateful filter that drops duplicate log entries.

    The returned callable keeps a :class:`Deduplicator` instance in its
    closure so it can be used directly in the ``filters`` list passed to
    :func:`gamelog_tail.pipeline.run`.

    Args:
        window_seconds: Seconds within which identical entries are suppressed.
        max_tracked: Maximum distinct entries held in memory at once.

    Returns:
        A callable ``(LogEntry) -> bool`` — returns ``False`` for duplicates.
    """
    deduplicator = Deduplicator(window_seconds=window_seconds, max_tracked=max_tracked)

    def _filter(entry: LogEntry) -> bool:  # noqa: WPS430
        return not deduplicator.is_duplicate(entry)

    _filter.__name__ = "dedup_filter"
    _filter.__doc__ = (
        f"Dedup filter (window={window_seconds}s, max_tracked={max_tracked})"
    )
    return _filter
