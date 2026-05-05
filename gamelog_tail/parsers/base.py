"""Base log entry parser interface for gamelog-tail."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LogEntry:
    """Represents a parsed log entry from a game engine."""

    raw: str
    timestamp: Optional[datetime] = None
    level: Optional[str] = None
    source: Optional[str] = None
    message: str = ""
    extra: dict = field(default_factory=dict)

    def __str__(self) -> str:
        parts = []
        if self.timestamp:
            parts.append(self.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if self.level:
            parts.append(f"[{self.level.upper()}]")
        if self.source:
            parts.append(f"({self.source})")
        parts.append(self.message)
        return " ".join(parts)


class BaseParser(ABC):
    """Abstract base class for game engine log parsers."""

    #: Human-readable name for this parser
    engine_name: str = "unknown"

    @abstractmethod
    def can_parse(self, line: str) -> bool:
        """Return True if this parser can handle the given log line."""
        ...

    @abstractmethod
    def parse(self, line: str) -> LogEntry:
        """Parse a raw log line into a LogEntry."""
        ...

    def safe_parse(self, line: str) -> LogEntry:
        """Parse a line, falling back to a raw entry on failure."""
        try:
            return self.parse(line)
        except Exception:
            return LogEntry(raw=line, message=line.strip())
