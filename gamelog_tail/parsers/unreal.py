import re
from datetime import datetime
from typing import Optional
from .base import BaseParser, LogEntry

# Example Unreal Engine log line:
# [2024.01.15-10.23.45:678][  0]LogInit: Display: Engine version: 5.3.0
# [2024.01.15-10.23.45:678][  0]LogTemp: Warning: Something went wrong

UNREAL_PATTERN = re.compile(
    r"^\[(?P<date>\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\]"
    r"\[\s*(?P<frame>\d+)\]"
    r"(?P<category>\w+):\s*"
    r"(?:(?P<level>Display|Warning|Error|Fatal|Verbose|VeryVerbose|Log):\s*)?"
    r"(?P<message>.+)$"
)

LEVEL_MAP = {
    "Fatal": "CRITICAL",
    "Error": "ERROR",
    "Warning": "WARNING",
    "Display": "INFO",
    "Log": "INFO",
    "Verbose": "DEBUG",
    "VeryVerbose": "DEBUG",
}

TIME_FORMAT = "%Y.%m.%d-%H.%M.%S"


class UnrealParser(BaseParser):
    """Parser for Unreal Engine log output."""

    def can_parse(self, line: str) -> bool:
        return bool(UNREAL_PATTERN.match(line))

    def parse(self, line: str) -> Optional[LogEntry]:
        match = UNREAL_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()
        timestamp = self._parse_time(groups["date"])
        level_raw = groups.get("level") or "Log"
        level = LEVEL_MAP.get(level_raw, "INFO")
        category = groups["category"]
        message = groups["message"].strip()
        frame = int(groups["frame"])

        return LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            source="unreal",
            extra={"category": category, "frame": frame, "raw_level": level_raw},
        )

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        try:
            # Strip milliseconds for strptime then add back
            base, ms = time_str.rsplit(":", 1)
            dt = datetime.strptime(base, TIME_FORMAT)
            return dt.replace(microsecond=int(ms) * 1000)
        except (ValueError, AttributeError):
            return None
