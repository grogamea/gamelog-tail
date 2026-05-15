"""Score-based filter: assign numeric weights to log entries and pass only
those whose accumulated score meets a minimum threshold.

Each rule is a (predicate, weight) pair.  The filter sums the weights of all
matching rules for an entry; if the total is >= *min_score* the entry passes.
"""
from __future__ import annotations

from typing import Callable, Iterable, Tuple

from gamelog_tail.parsers.base import LogEntry

# A single scoring rule: (predicate, numeric weight)
ScoringRule = Tuple[Callable[[LogEntry], bool], float]


def score_filter(
    rules: Iterable[ScoringRule],
    min_score: float = 1.0,
) -> Callable[[LogEntry], LogEntry | None]:
    """Return a filter that passes entries whose total rule-score >= *min_score*.

    Args:
        rules:      Iterable of (predicate, weight) pairs.  All rules are
                    evaluated; weights of matching rules are summed.
        min_score:  Minimum cumulative score required to pass.  Must be > 0.

    Returns:
        A callable ``filter(entry) -> entry | None``.

    Raises:
        ValueError: if *rules* is empty or *min_score* is not positive.
    """
    rule_list = list(rules)
    if not rule_list:
        raise ValueError("score_filter requires at least one scoring rule")
    if min_score <= 0:
        raise ValueError(f"min_score must be > 0, got {min_score!r}")

    def _filter(entry: LogEntry) -> LogEntry | None:
        total = sum(weight for pred, weight in rule_list if pred(entry))
        return entry if total >= min_score else None

    return _filter
