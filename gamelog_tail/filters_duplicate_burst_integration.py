"""Integration helpers for duplicate_burst_filter in the pipeline."""
from __future__ import annotations

from typing import Callable

from gamelog_tail.filters_duplicate_burst import duplicate_burst_filter
from gamelog_tail.parsers.base import LogEntry


def build_duplicate_burst_filters(
    max_repeats: int | None = None,
    window_seconds: float | None = None,
    key_fields: tuple[str, ...] | None = None,
) -> list[Callable[[LogEntry], bool]]:
    """Build a list of duplicate-burst filters from optional CLI/config args.

    If neither ``max_repeats`` nor ``window_seconds`` is provided the list will
    be empty (feature disabled).

    Args:
        max_repeats: Maximum allowed repetitions within the window.
        window_seconds: Sliding window duration in seconds.
        key_fields: Fields used to identify duplicate entries.

    Returns:
        A list containing zero or one filter callables.
    """
    if max_repeats is None and window_seconds is None:
        return []

    kwargs: dict = {}
    if max_repeats is not None:
        kwargs["max_repeats"] = max_repeats
    if window_seconds is not None:
        kwargs["window_seconds"] = window_seconds
    if key_fields is not None:
        kwargs["key_fields"] = key_fields

    return [duplicate_burst_filter(**kwargs)]


def apply_duplicate_burst_filters(
    filters: list[Callable[[LogEntry], bool]],
    entry: LogEntry,
) -> bool:
    """Apply all duplicate-burst filters to *entry*.

    Returns ``True`` when the entry passes every filter (should be kept).
    """
    return all(f(entry) for f in filters)
