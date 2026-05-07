"""Filter entries using arbitrary regular expressions against any field."""

from __future__ import annotations

import re
from typing import Callable, Optional

from gamelog_tail.parsers.base import LogEntry


def regex_filter(
    pattern: str,
    *,
    field: str = "message",
    flags: int = 0,
) -> Callable[[LogEntry], bool]:
    """Return a filter that keeps entries whose *field* matches *pattern*.

    Parameters
    ----------
    pattern:
        Regular-expression pattern string.
    field:
        Attribute name on :class:`LogEntry` to match against.  Defaults to
        ``"message"``; other useful values are ``"source"`` and ``"level"``.
    flags:
        Optional :mod:`re` flags (e.g. ``re.IGNORECASE``).

    Raises
    ------
    ValueError
        If *pattern* is empty or *field* is not a valid ``LogEntry`` attribute.
    re.error
        If *pattern* is not a valid regular expression.
    """
    if not pattern:
        raise ValueError("pattern must not be empty")

    _VALID_FIELDS = {"message", "level", "source"}
    if field not in _VALID_FIELDS:
        raise ValueError(
            f"field must be one of {sorted(_VALID_FIELDS)!r}, got {field!r}"
        )

    compiled = re.compile(pattern, flags)

    def _filter(entry: LogEntry) -> bool:
        value: Optional[str] = getattr(entry, field, None)
        if value is None:
            return False
        return compiled.search(value) is not None

    return _filter


def regex_exclude_filter(
    pattern: str,
    *,
    field: str = "message",
    flags: int = 0,
) -> Callable[[LogEntry], bool]:
    """Return a filter that *drops* entries whose *field* matches *pattern*.

    This is the inverse of :func:`regex_filter`.
    """
    _inner = regex_filter(pattern, field=field, flags=flags)

    def _filter(entry: LogEntry) -> bool:
        return not _inner(entry)

    return _filter
