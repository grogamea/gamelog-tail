"""Log parser for Unity engine output format."""

import re
from datetime import datetime
from typing import Optional

from .base import BaseParser, LogEntry

# Unity log pattern: timestamp optional, level tag, message
# Example: 12:34:56.789 [Warning] UnityEngine.Debug: Something happened
_UNITY_PATTERN = re.compile(
    r"^(?P<time>\d{2}:\d{2}:\d{2}\.\d{3})\s+"
    r"(?P<level>\[(?:Info|Warning|Error|Exception|Assert)\])\s+"
    r"(?:(?P<source>[\w\.]+):\s+)?(?P<message>.+)$"
)

# Simpler fallback: lines starting with a known Unity level tag
_UNITY_SIMPLE_PATTERN = re.compile(
    r"^(?P<level>INFO|WARNING|ERROR|EXCEPTION):\s+(?P<message>.+)$",
    re.IGNORECASE,
)

_LEVEL_MAP = {
    "[info]": "info",
    "[warning]": "warning",
    "[error]": "error",
    "[exception]": "error",
    "[assert]": "warning",
    "info": "info",
    "warning": "warning",
    "error": "error",
    "exception": "error",
}


class UnityParser(BaseParser):
    """Parser for Unity engine log output."""

    engine_name = "Unity"

    def can_parse(self, line: str) -> bool:
        return bool(
            _UNITY_PATTERN.match(line) or _UNITY_SIMPLE_PATTERN.match(line)
        )

    def parse(self, line: str) -> LogEntry:
        stripped = line.strip()

        m = _UNITY_PATTERN.match(stripped)
        if m:
            ts = _parse_time(m.group("time"))
            level_raw = m.group("level").lower()
            return LogEntry(
                raw=line,
                timestamp=ts,
                level=_LEVEL_MAP.get(level_raw, "info"),
                source=m.group("source"),
                message=m.group("message").strip(),
            )

        m = _UNITY_SIMPLE_PATTERN.match(stripped)
        if m:
            level_raw = m.group("level").lower()
            return LogEntry(
                raw=line,
                level=_LEVEL_MAP.get(level_raw, "info"),
                message=m.group("message").strip(),
            )

        return LogEntry(raw=line, message=stripped)


def _parse_time(time_str: str) -> Optional[datetime]:
    """Parse HH:MM:SS.mmm into a datetime with today's date."""
    try:
        today = datetime.today().date()
        t = datetime.strptime(time_str, "%H:%M:%S.%f").time()
        return datetime.combine(today, t)
    except ValueError:
        return None
