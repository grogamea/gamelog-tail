import re
from datetime import datetime
from typing import Optional
from gamelog_tail.parsers.base import BaseParser, LogEntry

# Godot log format examples:
# ERROR: res://scenes/Main.gd:42 - Node not found
# WARNING: AnimationPlayer: Animation 'idle' not found
# INFO: 0:00:01:0234 - Script loaded successfully
# Godot 4 format: USER ERROR: some message

GODOT_FULL_RE = re.compile(
    r'^(?P<level>ERROR|WARNING|INFO|DEBUG|USER ERROR|USER WARNING|USER SCRIPT ERROR):\s+'
    r'(?:(?P<source>[^:]+\.gd:\d+)\s+-\s+)?'
    r'(?P<message>.+)$'
)

GODOT_TIMED_RE = re.compile(
    r'^(?P<level>ERROR|WARNING|INFO|DEBUG):\s+'
    r'(?P<time>\d+:\d{2}:\d{2}:\d{4})\s+-\s+'
    r'(?P<message>.+)$'
)

LEVEL_MAP = {
    'ERROR': 'ERROR',
    'USER ERROR': 'ERROR',
    'USER SCRIPT ERROR': 'ERROR',
    'WARNING': 'WARNING',
    'USER WARNING': 'WARNING',
    'INFO': 'INFO',
    'DEBUG': 'DEBUG',
}


class GodotParser(BaseParser):
    """Parser for Godot Engine log output."""

    def can_parse(self, line: str) -> bool:
        return bool(GODOT_FULL_RE.match(line) or GODOT_TIMED_RE.match(line))

    def parse(self, line: str) -> Optional[LogEntry]:
        match = GODOT_TIMED_RE.match(line)
        if match:
            timestamp = self._parse_time(match.group('time'))
            level = LEVEL_MAP.get(match.group('level'), 'INFO')
            return LogEntry(
                timestamp=timestamp,
                level=level,
                message=match.group('message').strip(),
                source=None,
                raw=line,
            )

        match = GODOT_FULL_RE.match(line)
        if match:
            level = LEVEL_MAP.get(match.group('level'), 'INFO')
            source = match.group('source')
            return LogEntry(
                timestamp=None,
                level=level,
                message=match.group('message').strip(),
                source=source,
                raw=line,
            )

        return None

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """Parse Godot elapsed time string (H:MM:SS:MMMM) into a datetime."""
        try:
            parts = time_str.split(':')
            hours, minutes, seconds, millis = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
            return datetime(
                year=1970, month=1, day=1,
                hour=min(hours, 23),
                minute=minutes,
                second=seconds,
                microsecond=millis * 100,
            )
        except (ValueError, IndexError):
            return None
