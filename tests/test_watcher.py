"""Tests for gamelog_tail.watcher.FileWatcher."""

import os
import threading
import time

import pytest

from gamelog_tail.watcher import FileWatcher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_watcher(watcher: FileWatcher, duration: float) -> None:
    """Run watcher.start() in a thread, stop it after *duration* seconds."""
    def _stopper():
        time.sleep(duration)
        watcher.stop()

    t = threading.Thread(target=_stopper, daemon=True)
    t.start()
    watcher.start()
    t.join(timeout=duration + 1)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFileWatcher:
    def test_reads_new_lines(self, tmp_path):
        log = tmp_path / "game.log"
        log.write_text("")
        collected: list[str] = []

        watcher = FileWatcher(str(log), collected.append, poll_interval=0.05)

        def _write_and_stop():
            time.sleep(0.1)
            with open(str(log), "a") as fh:
                fh.write("line one\nline two\n")
            time.sleep(0.2)
            watcher.stop()

        t = threading.Thread(target=_write_and_stop, daemon=True)
        t.start()
        watcher.start()
        t.join(timeout=2)

        assert "line one" in collected
        assert "line two" in collected

    def test_handles_truncation(self, tmp_path):
        log = tmp_path / "game.log"
        log.write_text("old content\n")
        collected: list[str] = []

        watcher = FileWatcher(str(log), collected.append, poll_interval=0.05)
        # Pre-position offset at EOF.
        watcher._open_file()

        # Truncate and write fresh content.
        log.write_text("fresh line\n")
        watcher._poll()

        assert "fresh line" in collected

    def test_handles_missing_file(self, tmp_path):
        log = tmp_path / "missing.log"
        watcher = FileWatcher(str(log), lambda _: None, poll_interval=0.05)
        # Should not raise even when file does not exist.
        watcher._open_file()
        watcher._poll()
        assert watcher._inode is None
        assert watcher._offset == 0

    def test_stop_exits_loop(self, tmp_path):
        log = tmp_path / "game.log"
        log.write_text("")
        watcher = FileWatcher(str(log), lambda _: None, poll_interval=0.05)

        start = time.monotonic()
        _run_watcher(watcher, duration=0.3)
        elapsed = time.monotonic() - start

        assert elapsed < 2.0, "Watcher did not stop in time"
