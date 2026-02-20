"""
Folder Watcher Service
Monitors local folders for new files and auto-imports them.
"""
from __future__ import annotations

import logging
import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WatcherEvent(str, Enum):
    """Types of file system events."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class WatcherConfig(BaseModel):
    """Configuration for a folder watcher."""
    watcher_id: str
    path: str
    recursive: bool = True
    patterns: List[str] = Field(default_factory=lambda: ["*"])  # Glob patterns
    ignore_patterns: List[str] = Field(default_factory=list)
    auto_import: bool = True
    delete_after_import: bool = False
    target_collection: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class FileEvent(BaseModel):
    """A file system event."""
    event_type: WatcherEvent
    path: str
    filename: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: Optional[int] = None
    document_id: Optional[str] = None
    error: Optional[str] = None


class WatcherStatus(BaseModel):
    """Status of a folder watcher."""
    watcher_id: str
    path: str
    is_running: bool
    files_processed: int = 0
    files_pending: int = 0
    last_event: Optional[datetime] = None
    errors: List[str] = Field(default_factory=list)


class FolderWatcherService:
    """
    Service for monitoring folders and auto-importing files.
    Uses watchdog for cross-platform file system monitoring.
    """

    def __init__(self):
        self._watchers: Dict[str, WatcherConfig] = {}
        self._running: Dict[str, bool] = {}
        self._stats: Dict[str, Dict[str, Any]] = {}
        self._processed_files: Dict[str, Set[str]] = {}  # Track processed files by hash

    async def create_watcher(self, config: WatcherConfig) -> WatcherStatus:
        """
        Create a new folder watcher.

        Args:
            config: Watcher configuration

        Returns:
            WatcherStatus
        """
        # Validate path exists
        path = Path(config.path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        self._watchers[config.watcher_id] = config
        self._running[config.watcher_id] = False
        self._stats[config.watcher_id] = {
            "files_processed": 0,
            "files_pending": 0,
            "last_event": None,
            "errors": [],
        }
        self._processed_files[config.watcher_id] = set()

        if config.enabled:
            await self.start_watcher(config.watcher_id)

        return self.get_status(config.watcher_id)

    async def start_watcher(self, watcher_id: str) -> bool:
        """
        Start a folder watcher.

        Args:
            watcher_id: Watcher ID

        Returns:
            True if started successfully
        """
        if watcher_id not in self._watchers:
            raise ValueError(f"Watcher {watcher_id} not found")

        if self._running.get(watcher_id):
            return True  # Already running

        config = self._watchers[watcher_id]

        try:
            # Using watchdog for file system monitoring
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler, FileSystemEvent

            class Handler(FileSystemEventHandler):
                def __init__(self, service, watcher_id):
                    self.service = service
                    self.watcher_id = watcher_id

                def on_created(self, event: FileSystemEvent):
                    if not event.is_directory:
                        asyncio.create_task(
                            self.service._handle_event(
                                self.watcher_id,
                                WatcherEvent.CREATED,
                                event.src_path,
                            )
                        )

                def on_modified(self, event: FileSystemEvent):
                    if not event.is_directory:
                        asyncio.create_task(
                            self.service._handle_event(
                                self.watcher_id,
                                WatcherEvent.MODIFIED,
                                event.src_path,
                            )
                        )

            observer = Observer()
            handler = Handler(self, watcher_id)
            observer.schedule(handler, config.path, recursive=config.recursive)
            observer.start()

            self._running[watcher_id] = True
            logger.info(f"Started watcher {watcher_id} on {config.path}")

            return True

        except ImportError:
            logger.warning("watchdog not installed, using polling fallback")
            # Fallback to polling
            asyncio.create_task(self._poll_folder(watcher_id))
            self._running[watcher_id] = True
            return True

        except Exception as e:
            logger.error(f"Failed to start watcher {watcher_id}: {e}")
            self._stats[watcher_id]["errors"].append(str(e))
            return False

    async def stop_watcher(self, watcher_id: str) -> bool:
        """
        Stop a folder watcher.

        Args:
            watcher_id: Watcher ID

        Returns:
            True if stopped successfully
        """
        if watcher_id not in self._running:
            return False

        self._running[watcher_id] = False
        logger.info(f"Stopped watcher {watcher_id}")
        return True

    async def delete_watcher(self, watcher_id: str) -> bool:
        """
        Delete a folder watcher.

        Args:
            watcher_id: Watcher ID

        Returns:
            True if deleted successfully
        """
        await self.stop_watcher(watcher_id)

        if watcher_id in self._watchers:
            del self._watchers[watcher_id]
        if watcher_id in self._stats:
            del self._stats[watcher_id]
        if watcher_id in self._processed_files:
            del self._processed_files[watcher_id]

        return True

    def get_status(self, watcher_id: str) -> WatcherStatus:
        """
        Get status of a folder watcher.

        Args:
            watcher_id: Watcher ID

        Returns:
            WatcherStatus
        """
        if watcher_id not in self._watchers:
            raise ValueError(f"Watcher {watcher_id} not found")

        config = self._watchers[watcher_id]
        stats = self._stats.get(watcher_id, {})

        return WatcherStatus(
            watcher_id=watcher_id,
            path=config.path,
            is_running=self._running.get(watcher_id, False),
            files_processed=stats.get("files_processed", 0),
            files_pending=stats.get("files_pending", 0),
            last_event=stats.get("last_event"),
            errors=stats.get("errors", [])[-10:],  # Last 10 errors
        )

    def list_watchers(self) -> List[WatcherStatus]:
        """
        List all folder watchers.

        Returns:
            List of WatcherStatus
        """
        return [self.get_status(wid) for wid in self._watchers]

    async def scan_folder(self, watcher_id: str) -> List[FileEvent]:
        """
        Manually scan a watched folder for existing files.

        Args:
            watcher_id: Watcher ID

        Returns:
            List of FileEvents for found files
        """
        if watcher_id not in self._watchers:
            raise ValueError(f"Watcher {watcher_id} not found")

        config = self._watchers[watcher_id]
        path = Path(config.path)
        events = []

        if config.recursive:
            files = path.rglob("*")
        else:
            files = path.glob("*")

        for file_path in files:
            if file_path.is_file():
                if self._matches_patterns(file_path, config):
                    event = await self._handle_event(
                        watcher_id,
                        WatcherEvent.CREATED,
                        str(file_path),
                    )
                    if event:
                        events.append(event)

        return events

    async def _handle_event(
        self,
        watcher_id: str,
        event_type: WatcherEvent,
        file_path: str,
    ) -> Optional[FileEvent]:
        """Handle a file system event."""
        config = self._watchers.get(watcher_id)
        if not config:
            return None

        path = Path(file_path)

        # Check if file matches patterns
        if not self._matches_patterns(path, config):
            return None

        # Check if already processed (by content hash)
        file_hash = self._get_file_hash(path)
        if file_hash in self._processed_files.get(watcher_id, set()):
            return None

        event = FileEvent(
            event_type=event_type,
            path=str(path),
            filename=path.name,
            size_bytes=path.stat().st_size if path.exists() else None,
        )

        # Auto-import if configured
        if config.auto_import and event_type in (WatcherEvent.CREATED, WatcherEvent.MODIFIED):
            try:
                from .service import ingestion_service

                content = path.read_bytes()
                result = await ingestion_service.ingest_file(
                    filename=path.name,
                    content=content,
                    metadata={
                        "source": "folder_watcher",
                        "watcher_id": watcher_id,
                        "original_path": str(path),
                        "tags": config.tags,
                        "collection": config.target_collection,
                    },
                )
                event.document_id = result.document_id

                # Mark as processed
                self._processed_files[watcher_id].add(file_hash)
                self._stats[watcher_id]["files_processed"] += 1

                # Delete if configured
                if config.delete_after_import:
                    path.unlink()

            except Exception as e:
                event.error = "File import failed"
                self._stats[watcher_id]["errors"].append(f"{path.name}: import failed")
                logger.error(f"Failed to import {file_path}: {e}")

        self._stats[watcher_id]["last_event"] = datetime.now(timezone.utc)
        return event

    async def _poll_folder(self, watcher_id: str, interval: float = 5.0):
        """Polling fallback for when watchdog is not available."""
        config = self._watchers.get(watcher_id)
        if not config:
            return

        seen_files: Dict[str, float] = {}

        while self._running.get(watcher_id, False):
            try:
                path = Path(config.path)
                current_files = {}

                if config.recursive:
                    files = path.rglob("*")
                else:
                    files = path.glob("*")

                for file_path in files:
                    if file_path.is_file():
                        mtime = file_path.stat().st_mtime
                        current_files[str(file_path)] = mtime

                        # Check for new or modified files
                        if str(file_path) not in seen_files:
                            await self._handle_event(watcher_id, WatcherEvent.CREATED, str(file_path))
                        elif seen_files[str(file_path)] != mtime:
                            await self._handle_event(watcher_id, WatcherEvent.MODIFIED, str(file_path))

                seen_files = current_files

            except Exception as e:
                logger.error(f"Polling error for watcher {watcher_id}: {e}")

            await asyncio.sleep(interval)

    def _matches_patterns(self, path: Path, config: WatcherConfig) -> bool:
        """Check if file matches include/exclude patterns."""
        import fnmatch

        filename = path.name

        # Check ignore patterns first
        for pattern in config.ignore_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False

        # Check include patterns
        if config.patterns == ["*"]:
            return True

        for pattern in config.patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True

        return False

    def _get_file_hash(self, path: Path) -> str:
        """Get hash of file for deduplication."""
        if not path.exists():
            return ""

        # Use file path + size + mtime for quick hash
        stat = path.stat()
        return hashlib.md5(f"{path}:{stat.st_size}:{stat.st_mtime}".encode()).hexdigest()


# Singleton instance
folder_watcher_service = FolderWatcherService()
