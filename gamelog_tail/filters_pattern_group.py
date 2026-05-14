"""
filters_pattern_group.py — Group multiple regex patterns into a single
pass/block filter, with optional label tagging on match.
"""
from __future__ import annotations

import re
from typing import Callable, Iterable, Optional

from gamelog_tail.parsers.base import LogEntry


def pattern_group_filter(
    patterns: Iterable[str],
    *,
    field: str = "message",
    label: Optional[str] = None,
    mode: str = "allow",
) -> Callable[[LogEntry], Optional[LogEntry]]:
    """Return a filter that matches any of *patterns* against *field*.

    Parameters
    ----------
    patterns:
        One or more regular-expression strings.  At least one must be supplied.
    field:
        Which ``LogEntry`` attribute to match against.  Supported values are
        ``"message"`` and ``"source"``.
    label:
        When set and a pattern matches, the entry's ``source`` field is
        prefixed with ``"[<label>] "`` before passing it downstream.  Only
        applied in *allow* mode.
    mode:
        ``"allow"`` — pass entries that match at least one pattern.
        ``"deny"``  — pass entries that match *no* pattern.
    """
    if field not in ("message", "source"):
        raise ValueError(f"field must be 'message' or 'source', got {field!r}")
    if mode not in ("allow", "deny"):
        raise ValueError(f"mode must be 'allow' or 'deny', got {mode!r}")

    compiled = [re.compile(p) for p in patterns]
    if not compiled:
        raise ValueError("patterns must contain at least one entry")

    def _filter(entry: LogEntry) -> Optional[LogEntry]:
        text = getattr(entry, field) or ""
        matched = any(rx.search(text) for rx in compiled)

        if mode == "allow":
            if not matched:
                return None
            if label:
                tagged_source = f"[{label}] {entry.source}" if entry.source else f"[{label}]"
                return LogEntry(
                    timestamp=entry.timestamp,
                    level=entry.level,
                    source=tagged_source,
                    message=entry.message,
                )
            return entry
        else:  # deny
            return None if matched else entry

    return _filter
