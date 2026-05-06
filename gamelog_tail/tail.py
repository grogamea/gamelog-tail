"""Core tail loop: read lines, parse them, and apply filters."""

from __future__ import annotations

import sys
import time
from typing import IO, Iterable, Iterator, Sequence

from gamelog_tail.filters import FilterFn, apply_filters
from gamelog_tail.parsers.base import BaseParser, LogEntry


def _select_parser(
    parsers: Sequence[BaseParser], line: str
) -> BaseParser | None:
    """Return the first parser in *parsers* that claims it can parse *line*."""
    for parser in parsers:
        if parser.can_parse(line):
            return parser
    return None


def parse_stream(
    stream: IO[str],
    parsers: Sequence[BaseParser],
    *,
    fallback_raw: bool = True,
) -> Iterator[LogEntry]:
    """Yield :class:`~gamelog_tail.parsers.base.LogEntry` objects from *stream*.

    If no parser recognises a line and *fallback_raw* is ``True``, a minimal
    entry is emitted with the raw text as the message.
    """
    for raw_line in stream:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        parser = _select_parser(parsers, line)
        if parser is not None:
            entry = parser.parse(line)
            if entry is not None:
                yield entry
        elif fallback_raw:
            yield LogEntry(
                timestamp=None,
                level=None,
                source=None,
                message=line,
                raw=line,
            )


def tail_file(
    path: str,
    parsers: Sequence[BaseParser],
    filters: Iterable[FilterFn] = (),
    *,
    poll_interval: float = 0.1,
    output: IO[str] = sys.stdout,
) -> None:
    """Follow *path* in real time, printing filtered log entries to *output*.

    Opens the file, seeks to the end, then polls for new lines.  Press
    Ctrl-C to stop.
    """
    filter_list = list(filters)

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        fh.seek(0, 2)  # seek to end
        try:
            while True:
                line = fh.readline()
                if not line:
                    time.sleep(poll_interval)
                    continue
                stripped = line.rstrip("\n")
                if not stripped:
                    continue
                parser = _select_parser(parsers, stripped)
                entry: LogEntry | None = None
                if parser is not None:
                    entry = parser.parse(stripped)
                else:
                    entry = LogEntry(
                        timestamp=None,
                        level=None,
                        source=None,
                        message=stripped,
                        raw=stripped,
                    )
                if entry is None:
                    continue
                if filter_list:
                    matched = list(apply_filters([entry], *filter_list))
                    if not matched:
                        continue
                print(str(entry), file=output)
        except KeyboardInterrupt:
            pass
