"""Custom/generic log parser supporting user-defined regex patterns."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from gamelog_tail.parsers.base import BaseParser, LogEntry

# Default pattern covers lines like:
# [2024-01-15 10:23:45] [ERROR] (MySystem) Something went wrong
_DEFAULT_PATTERN = re.compile(
    r"^\[(?P<ts>[\d\-: ]+)\]\s+"
    r"\[(?P<level>[A-Z]+)\]\s+"
    r"(?:\((?P<source>[^)]+)\)\s+)?"
    r"(?P<message>.+)$"
)


class CustomParser(BaseParser):
    """Parser that accepts a user-supplied regex with named groups.

    Required named groups: ``message``
    Optional named groups: ``ts`` (timestamp), ``level``, ``source``
    """

    name = "custom"

    def __init__(self, pattern: Optional[re.Pattern] = None) -> None:
        self._pattern: re.Pattern = pattern if pattern is not None else _DEFAULT_PATTERN

    # ------------------------------------------------------------------
    # BaseParser interface
    # ------------------------------------------------------------------

    def can_parse(self, line: str) -> bool:
        """Return True if the line matches the configured pattern."""
        return bool(self._pattern.match(line.rstrip()))

    def parse(self, line: str) -> Optional[LogEntry]:
        """Parse *line* and return a :class:`LogEntry`, or ``None`` on failure."""
        m = self._pattern.match(line.rstrip())
        if not m:
            return None

        groups = m.groupdict()
        timestamp = self._parse_time(groups.get("ts"))
        level = (groups.get("level") or "INFO").upper()
        source = groups.get("source") or None
        message = groups.get("message", "").strip()

        return LogEntry(
            timestamp=timestamp,
            level=level,
            source=source,
            message=message,
            raw=line,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_time(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None
