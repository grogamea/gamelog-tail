"""Parser for Source engine (Half-Life 2, CS:GO, etc.) log format."""
import re
from datetime import datetime
from typing import Optional

from gamelog_tail.parsers.base import BaseParser, LogEntry

# L 01/23/2024 - 14:05:32: [category] message
_FULL_RE = re.compile(
    r'^L\s+(?P<date>\d{2}/\d{2}/\d{4})\s+-\s+(?P<time>\d{2}:\d{2}:\d{2}):\s+'
    r'(?:\[(?P<category>[^\]]+)\]\s+)?(?P<message>.+)$'
)

# L 01/23/2024 - 14:05:32: message (no category)
_SIMPLE_RE = re.compile(
    r'^L\s+(?P<date>\d{2}/\d{2}/\d{4})\s+-\s+(?P<time>\d{2}:\d{2}:\d{2}):\s+(?P<message>.+)$'
)

_LEVEL_KEYWORDS = {
    'error': 'ERROR',
    'warning': 'WARNING',
    'warn': 'WARNING',
    'bad': 'WARNING',
    'failed': 'ERROR',
    'invalid': 'ERROR',
}


class SourceParser(BaseParser):
    """Parser for Source engine log output."""

    def can_parse(self, line: str) -> bool:
        return bool(_FULL_RE.match(line) or _SIMPLE_RE.match(line))

    def parse(self, line: str) -> Optional[LogEntry]:
        m = _FULL_RE.match(line) or _SIMPLE_RE.match(line)
        if not m:
            return None

        groups = m.groupdict()
        timestamp = self._parse_time(groups['date'], groups['time'])
        message = groups['message'].strip()
        source = groups.get('category') or None

        level = 'INFO'
        lower = message.lower()
        for keyword, lvl in _LEVEL_KEYWORDS.items():
            if keyword in lower:
                level = lvl
                break

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source=source,
            raw=line,
        )

    @staticmethod
    def _parse_time(date_str: str, time_str: str) -> Optional[datetime]:
        try:
            return datetime.strptime(f'{date_str} {time_str}', '%m/%d/%Y %H:%M:%S')
        except ValueError:
            return None
