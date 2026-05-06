"""Human-readable and JSON summary formatters for AggregateStats."""
from __future__ import annotations

import json
from typing import Callable

from gamelog_tail.aggregator import AggregateStats


def plain_summary(stats: AggregateStats) -> str:
    """Return a multi-line plain-text summary."""
    lines = [
        f"Total entries : {stats.total}",
        "By level      :",
    ]
    for level, count in sorted(stats.by_level.items()):
        lines.append(f"  {level:<12} {count}")
    if stats.by_source:
        lines.append("Top sources   :")
        for source, count in stats.top_sources():
            lines.append(f"  {source:<30} {count}")
    lines.append(f"Errors        : {len(stats.errors)}")
    lines.append(f"Warnings      : {len(stats.warnings)}")
    return "\n".join(lines)


def json_summary(stats: AggregateStats) -> str:
    """Return a JSON-encoded summary string."""
    return json.dumps(stats.summary(), indent=2)


_FORMATTERS: dict[str, Callable[[AggregateStats], str]] = {
    "plain": plain_summary,
    "json": json_summary,
}


def get_summary_formatter(name: str) -> Callable[[AggregateStats], str]:
    """Retrieve a summary formatter by name.

    Raises :class:`ValueError` for unknown names.
    """
    try:
        return _FORMATTERS[name]
    except KeyError:
        raise ValueError(
            f"Unknown summary formatter {name!r}. "
            f"Available: {list(_FORMATTERS)}"
        )
