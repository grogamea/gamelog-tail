"""Command-line entry point for gamelog-tail."""

import argparse
import sys
from typing import List, Optional

from gamelog_tail.pipeline import build_filters, run
from gamelog_tail.formatters import get_formatter
from gamelog_tail.watcher import FileWatcher
from gamelog_tail.tail import _select_parser


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gamelog-tail",
        description="Real-time log parser and filter for game engine output.",
    )
    p.add_argument("file", nargs="?", help="Log file to watch (omit to read stdin).")
    p.add_argument(
        "--engine",
        choices=["unity", "unreal", "godot", "source", "custom"],
        default=None,
        help="Force a specific engine parser (auto-detected by default).",
    )
    p.add_argument(
        "--level",
        metavar="LEVEL",
        help="Only show entries at or above this log level.",
    )
    p.add_argument(
        "--source",
        metavar="PATTERN",
        help="Only show entries whose source matches PATTERN (regex).",
    )
    p.add_argument(
        "--message",
        metavar="PATTERN",
        help="Only show entries whose message matches PATTERN (regex).",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["plain", "colour", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.add_argument(
        "--follow",
        action="store_true",
        help="Keep watching the file for new lines (like tail -f).",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    formatter = get_formatter(args.fmt)
    filters = build_filters(
        level=args.level,
        source_pattern=args.source,
        message_pattern=args.message,
    )

    def _handle_line(line: str) -> None:
        """Parse a single raw line and emit it if it passes all filters."""
        if parser is None:
            return
        if not parser.can_parse(line):
            return
        entry = parser.parse(line)
        if entry is None:
            return
        for f in filters:
            if not f(entry):
                return
        print(formatter(entry))

    if args.file:
        parser = _select_parser(args.file, engine=args.engine)
        if args.follow:
            watcher = FileWatcher(args.file, _handle_line)
            watcher.start()
        else:
            with open(args.file, "r", errors="replace") as fh:
                run(fh, parser, filters, formatter)
    else:
        parser = _select_parser(None, engine=args.engine)
        run(sys.stdin, parser, filters, formatter)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
