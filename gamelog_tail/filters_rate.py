"""Pipeline-compatible filter wrapper around RateLimiter."""
from __future__ import annotations

from typing import Callable, Iterable, Iterator

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.rate_limiter import RateLimiter


def rate_limit_filter(
    max_per_window: int = 10,
    window_seconds: float = 1.0,
) -> Callable[[Iterable[LogEntry]], Iterator[LogEntry]]:
    """Return a filter function that applies rate-limiting to a stream.

    The returned callable is compatible with the filter protocol used by
    :func:`gamelog_tail.pipeline.build_filters`.

    Example::

        filters = [rate_limit_filter(max_per_window=5, window_seconds=2.0)]
        run(stream, parser, filters, formatter)
    """
    limiter = RateLimiter(max_per_window=max_per_window, window_seconds=window_seconds)

    def _filter(entries: Iterable[LogEntry]) -> Iterator[LogEntry]:
        for entry in entries:
            yield from limiter.feed(entry)

    return _filter
