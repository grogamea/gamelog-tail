"""Log entry aggregation and statistics tracking."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gamelog_tail.parsers.base import LogEntry


@dataclass
class AggregateStats:
    """Accumulated statistics for a stream of log entries."""

    total: int = 0
    by_level: Counter = field(default_factory=Counter)
    by_source: Counter = field(default_factory=Counter)
    errors: List[LogEntry] = field(default_factory=list)
    warnings: List[LogEntry] = field(default_factory=list)

    def record(self, entry: LogEntry) -> None:
        """Update stats with a new log entry."""
        self.total += 1
        level = (entry.level or "UNKNOWN").upper()
        self.by_level[level] += 1
        if entry.source:
            self.by_source[entry.source] += 1
        if level == "ERROR":
            self.errors.append(entry)
        elif level in ("WARNING", "WARN"):
            self.warnings.append(entry)

    def top_sources(self, n: int = 5) -> List[tuple]:
        """Return the *n* most common sources."""
        return self.by_source.most_common(n)

    def summary(self) -> Dict[str, object]:
        """Return a plain-dict summary suitable for display or serialisation."""
        return {
            "total": self.total,
            "by_level": dict(self.by_level),
            "by_source": dict(self.by_source),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


def aggregate(entries: List[LogEntry]) -> AggregateStats:
    """Build an :class:`AggregateStats` from an iterable of entries."""
    stats = AggregateStats()
    for entry in entries:
        stats.record(entry)
    return stats
