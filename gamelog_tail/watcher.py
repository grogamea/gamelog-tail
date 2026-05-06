"""File watcher that detects log rotation and new content."""

import os
import time
from typing import Callable, Optional


class FileWatcher:
    """Watches a log file for new lines, handling rotation and truncation."""

    def __init__(
        self,
        path: str,
        callback: Callable[[str], None],
        poll_interval: float = 0.25,
    ) -> None:
        self.path = path
        self.callback = callback
        self.poll_interval = poll_interval
        self._inode: Optional[int] = None
        self._offset: int = 0
        self._running: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin watching; blocks until :meth:`stop` is called."""
        self._running = True
        self._open_file()
        try:
            while self._running:
                self._poll()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            pass

    def stop(self) -> None:
        """Signal the watch loop to exit."""
        self._running = False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _open_file(self) -> None:
        """Record the current inode and seek to EOF for initial open."""
        try:
            stat = os.stat(self.path)
            self._inode = stat.st_ino
            self._offset = stat.st_size
        except FileNotFoundError:
            self._inode = None
            self._offset = 0

    def _poll(self) -> None:
        try:
            stat = os.stat(self.path)
        except FileNotFoundError:
            # File removed; wait for it to reappear.
            self._inode = None
            self._offset = 0
            return

        rotated = self._inode is not None and stat.st_ino != self._inode
        truncated = stat.st_size < self._offset

        if rotated or truncated:
            # New file or same file truncated — start from beginning.
            self._inode = stat.st_ino
            self._offset = 0

        if self._inode is None:
            self._inode = stat.st_ino

        if stat.st_size > self._offset:
            with open(self.path, "r", errors="replace") as fh:
                fh.seek(self._offset)
                for line in fh:
                    self.callback(line.rstrip("\n"))
                self._offset = fh.tell()
