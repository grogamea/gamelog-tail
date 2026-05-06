"""Pipeline integration for the log-entry sampler."""

from __future__ import annotations

from typing import Callable

from gamelog_tail.parsers.base import LogEntry
from gamelog_tail.sampler import Sampler


def sample_filter(rate: int = 10) -> Callable[[LogEntry], bool]:
    """Build a stateful sampling filter for use in :func:`gamelog_tail.pipeline.build_filters`.

    Parameters
    ----------
    rate:
        Emit 1 entry per *rate* entries sharing the same (source, level) bucket.

    Returns
    -------
    Callable[[LogEntry], bool]
        Returns ``True`` when the entry should pass through.
    """
    if rate < 1:
        raise ValueError(f"rate must be >= 1, got {rate}")

    sampler = Sampler(rate=rate)

    def _filter(entry: LogEntry) -> bool:  # noqa: WPS430
        return sampler.should_keep(entry)

    # Expose sampler for introspection / testing.
    _filter.__sampler__ = sampler  # type: ignore[attr-defined]
    return _filter
