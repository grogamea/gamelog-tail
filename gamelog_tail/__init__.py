"""gamelog-tail: Real-time log parser and filter for game engine output."""

from gamelog_tail.pipeline import run, build_filters
from gamelog_tail.formatters import get_formatter, plain, coloured, as_json
from gamelog_tail.filters import by_level, by_message_pattern, by_source_pattern

__all__ = [
    # pipeline
    "run",
    "build_filters",
    # formatters
    "get_formatter",
    "plain",
    "coloured",
    "as_json",
    # filters
    "by_level",
    "by_message_pattern",
    "by_source_pattern",
]
