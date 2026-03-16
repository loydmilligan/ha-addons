"""File watcher for .tasks/ directory changes."""

import asyncio
import logging
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class TasksFileHandler(FileSystemEventHandler):
    """Handle file system events for .tasks/ directory."""

    def __init__(self, callback: Callable[[], None], debounce_ms: int = 100):
        self.callback = callback
        self.debounce_ms = debounce_ms
        self._pending_call: Optional[asyncio.TimerHandle] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async callbacks."""
        self._loop = loop

    def _schedule_callback(self):
        """Schedule debounced callback."""
        if self._loop is None:
            return

        # Cancel pending call if exists
        if self._pending_call is not None:
            self._pending_call.cancel()

        # Schedule new call
        self._pending_call = self._loop.call_later(
            self.debounce_ms / 1000.0, self._execute_callback
        )

    def _execute_callback(self):
        """Execute the callback."""
        self._pending_call = None
        logger.info("[WATCHER] Executing reload callback after debounce")
        try:
            if asyncio.iscoroutinefunction(self.callback):
                asyncio.create_task(self.callback())
            else:
                self.callback()
        except Exception as e:
            logger.error(f"[WATCHER] Error in file change callback: {e}")

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification."""
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return
        logger.info(f"[WATCHER] File MODIFIED: {event.src_path}")
        self._schedule_callback()

    def on_created(self, event: FileSystemEvent):
        """Handle file creation."""
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return
        logger.info(f"[WATCHER] File CREATED: {event.src_path}")
        self._schedule_callback()

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion."""
        if event.is_directory:
            return
        if not event.src_path.endswith(".md"):
            return
        logger.info(f"[WATCHER] File DELETED: {event.src_path}")
        self._schedule_callback()

    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename (catches atomic writes: temp -> target)."""
        if event.is_directory:
            return
        # Check destination path for atomic writes
        dest_path = getattr(event, 'dest_path', '')
        if dest_path.endswith(".md"):
            logger.info(f"[WATCHER] File MOVED: {event.src_path} -> {dest_path}")
            self._schedule_callback()
        elif event.src_path.endswith(".md"):
            logger.info(f"[WATCHER] File MOVED (src): {event.src_path}")
            self._schedule_callback()


class TasksWatcher:
    """Watch .tasks/ directory for changes."""

    def __init__(self, path: str, callback: Callable[[], None], debounce_ms: int = 100):
        self.path = path
        self.callback = callback
        self.debounce_ms = debounce_ms
        self.observer: Optional[Observer] = None
        self.handler: Optional[TasksFileHandler] = None

    def start(self, loop: asyncio.AbstractEventLoop):
        """Start watching for file changes."""
        if self.observer is not None:
            return

        # Ensure path exists
        path = Path(self.path)
        if not path.exists():
            logger.warning(f"Tasks path does not exist: {self.path}")
            return

        self.handler = TasksFileHandler(self.callback, self.debounce_ms)
        self.handler.set_loop(loop)

        self.observer = Observer()
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()

        # Log what files exist at startup
        md_files = list(Path(self.path).rglob("*.md"))
        logger.info(f"[WATCHER] Started watching: {self.path}")
        logger.info(f"[WATCHER] Found {len(md_files)} .md files: {[f.name for f in md_files]}")

    def stop(self):
        """Stop watching for file changes."""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.handler = None
            logger.info("Stopped file watcher")
