"""Context window filter: emit N lines before and after a matching entry."""
from __future__ import annotations

from collections import deque
from typing import Callable, Iterable, Iterator

from gamelog_tail.parsers.base import LogEntry


class _ContextWindow:
    """Accumulates pre/post context around trigger entries."""

    def __init__(self, before: int, after: int) -> None:
        self._before = before
        self._after = after
        self._pre: deque[LogEntry] = deque(maxlen=before)
        self._emit_countdown = 0
        self._pending: list[LogEntry] = []

    def feed(
        self,
        entry: LogEntry,
        predicate: Callable[[LogEntry], bool],
    ) -> list[LogEntry]:
        """Return entries that should be emitted given this new entry."""
        to_emit: list[LogEntry] = []

        if predicate(entry):
            # Flush buffered pre-context
            to_emit.extend(self._pre)
            self._pre.clear()
            to_emit.append(entry)
            self._emit_countdown = self._after
        elif self._emit_countdown > 0:
            to_emit.append(entry)
            self._emit_countdown -= 1
        else:
            if self._before > 0:
                self._pre.append(entry)

        return to_emit


def context_window_filter(
    predicate: Callable[[LogEntry], bool],
    before: int = 2,
    after: int = 2,
) -> Callable[[Iterable[LogEntry]], Iterator[LogEntry]]:
    """Return a filter that emits entries near those matching *predicate*.

    Args:
        predicate: Function that returns True for 'trigger' entries.
        before: Number of entries to emit before each trigger.
        after: Number of entries to emit after each trigger.

    Raises:
        ValueError: If *before* or *after* are negative.
    """
    if before < 0:
        raise ValueError(f"before must be >= 0, got {before}")
    if after < 0:
        raise ValueError(f"after must be >= 0, got {after}")

    def _filter(entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
        window = _ContextWindow(before, after)
        for entry in entries:
            yield from window.feed(entry, predicate)

    return _filter
