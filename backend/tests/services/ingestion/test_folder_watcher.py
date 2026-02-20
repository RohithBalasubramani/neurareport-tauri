"""
Folder Watcher Service Tests - Testing folder monitoring and auto-import.
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


from backend.app.services.ingestion.folder_watcher import (
    FolderWatcherService,
    WatcherConfig,
    WatcherStatus,
    FileEvent,
    WatcherEvent,
)


@pytest.fixture
def service() -> FolderWatcherService:
    """Create a fresh folder watcher service."""
    return FolderWatcherService()


@pytest.fixture
def tmp_watch_dir(tmp_path: Path) -> Path:
    """Create a temporary directory to watch."""
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()
    return watch_dir


@pytest.fixture
def sample_config(tmp_watch_dir: Path) -> WatcherConfig:
    """Create a sample watcher configuration."""
    return WatcherConfig(
        watcher_id="test-watcher-1",
        path=str(tmp_watch_dir),
        recursive=True,
        patterns=["*.txt", "*.pdf"],
        ignore_patterns=["*.tmp"],
        auto_import=False,  # Don't auto-import in most tests
        delete_after_import=False,
        tags=["test"],
    )


# =============================================================================
# WATCHER CREATION TESTS
# =============================================================================


class TestCreateWatcher:
    """Test watcher creation."""

    @pytest.mark.asyncio
    async def test_create_watcher(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Create a new watcher."""
        status = await service.create_watcher(sample_config)

        assert isinstance(status, WatcherStatus)
        assert status.watcher_id == "test-watcher-1"
        assert status.path == sample_config.path

    @pytest.mark.asyncio
    async def test_create_watcher_creates_directory(self, service: FolderWatcherService, tmp_path: Path):
        """Create watcher creates missing directory."""
        new_dir = tmp_path / "new" / "nested" / "watch"
        config = WatcherConfig(
            watcher_id="new-watcher",
            path=str(new_dir),
        )

        await service.create_watcher(config)

        assert new_dir.exists()

    @pytest.mark.asyncio
    async def test_create_watcher_stores_config(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Created watcher is stored in service."""
        await service.create_watcher(sample_config)

        assert sample_config.watcher_id in service._watchers
        assert service._watchers[sample_config.watcher_id] == sample_config

    @pytest.mark.asyncio
    async def test_create_watcher_initializes_stats(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Created watcher has initialized stats."""
        await service.create_watcher(sample_config)

        assert sample_config.watcher_id in service._stats
        assert service._stats[sample_config.watcher_id]["files_processed"] == 0

    @pytest.mark.asyncio
    async def test_create_disabled_watcher_not_running(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Disabled watcher is not started automatically."""
        config = WatcherConfig(
            watcher_id="disabled-watcher",
            path=str(tmp_watch_dir),
            enabled=False,
        )

        status = await service.create_watcher(config)

        assert status.is_running is False

    @pytest.mark.asyncio
    async def test_create_enabled_watcher_started(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Enabled watcher is started automatically."""
        config = WatcherConfig(
            watcher_id="enabled-watcher",
            path=str(tmp_watch_dir),
            enabled=True,
        )

        with patch.object(service, "start_watcher", new_callable=AsyncMock) as mock_start:
            mock_start.return_value = True
            await service.create_watcher(config)
            mock_start.assert_called_once_with("enabled-watcher")


# =============================================================================
# WATCHER START/STOP TESTS
# =============================================================================


class TestStartStopWatcher:
    """Test watcher lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_watcher(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Start a watcher."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        # Simply mark as running without mocking watchdog (may not be installed)
        result = await service.start_watcher(sample_config.watcher_id)

        assert result is True
        assert service._running.get(sample_config.watcher_id) is True

    @pytest.mark.asyncio
    async def test_start_nonexistent_watcher(self, service: FolderWatcherService):
        """Start nonexistent watcher raises error."""
        with pytest.raises(ValueError, match="not found"):
            await service.start_watcher("nonexistent")

    @pytest.mark.asyncio
    async def test_start_already_running(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Starting already running watcher returns True."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)
        service._running[sample_config.watcher_id] = True

        result = await service.start_watcher(sample_config.watcher_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_stop_watcher(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Stop a running watcher."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)
        service._running[sample_config.watcher_id] = True

        result = await service.stop_watcher(sample_config.watcher_id)

        assert result is True
        assert service._running[sample_config.watcher_id] is False

    @pytest.mark.asyncio
    async def test_stop_nonexistent_watcher(self, service: FolderWatcherService):
        """Stop nonexistent watcher returns False."""
        result = await service.stop_watcher("nonexistent")
        assert result is False


# =============================================================================
# WATCHER DELETION TESTS
# =============================================================================


class TestDeleteWatcher:
    """Test watcher deletion."""

    @pytest.mark.asyncio
    async def test_delete_watcher(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Delete a watcher."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        result = await service.delete_watcher(sample_config.watcher_id)

        assert result is True
        assert sample_config.watcher_id not in service._watchers
        assert sample_config.watcher_id not in service._stats

    @pytest.mark.asyncio
    async def test_delete_stops_running_watcher(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Deleting running watcher stops it first."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)
        service._running[sample_config.watcher_id] = True

        with patch.object(service, "stop_watcher", new_callable=AsyncMock) as mock_stop:
            await service.delete_watcher(sample_config.watcher_id)
            mock_stop.assert_called_once_with(sample_config.watcher_id)

    @pytest.mark.asyncio
    async def test_delete_cleans_processed_files(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Deletion cleans up processed files tracking."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)
        service._processed_files[sample_config.watcher_id] = {"hash1", "hash2"}

        await service.delete_watcher(sample_config.watcher_id)

        assert sample_config.watcher_id not in service._processed_files


# =============================================================================
# WATCHER STATUS TESTS
# =============================================================================


class TestGetStatus:
    """Test status retrieval."""

    @pytest.mark.asyncio
    async def test_get_status(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Get watcher status."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        status = service.get_status(sample_config.watcher_id)

        assert status.watcher_id == sample_config.watcher_id
        assert status.path == sample_config.path
        assert status.files_processed == 0

    def test_get_status_nonexistent(self, service: FolderWatcherService):
        """Get status of nonexistent watcher raises error."""
        with pytest.raises(ValueError, match="not found"):
            service.get_status("nonexistent")

    @pytest.mark.asyncio
    async def test_get_status_includes_errors(self, service: FolderWatcherService, sample_config: WatcherConfig):
        """Status includes recent errors."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)
        service._stats[sample_config.watcher_id]["errors"] = ["Error 1", "Error 2"]

        status = service.get_status(sample_config.watcher_id)

        assert len(status.errors) == 2
        assert "Error 1" in status.errors


# =============================================================================
# LIST WATCHERS TESTS
# =============================================================================


class TestListWatchers:
    """Test listing all watchers."""

    def test_list_watchers_empty(self, service: FolderWatcherService):
        """List watchers when none exist."""
        result = service.list_watchers()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_watchers_multiple(self, service: FolderWatcherService, tmp_path: Path):
        """List multiple watchers."""
        for i in range(3):
            config = WatcherConfig(
                watcher_id=f"watcher-{i}",
                path=str(tmp_path / f"watch{i}"),
                enabled=False,
            )
            await service.create_watcher(config)

        result = service.list_watchers()

        assert len(result) == 3
        ids = [w.watcher_id for w in result]
        assert "watcher-0" in ids
        assert "watcher-1" in ids
        assert "watcher-2" in ids


# =============================================================================
# PATTERN MATCHING TESTS
# =============================================================================


class TestPatternMatching:
    """Test file pattern matching."""

    @pytest.mark.asyncio
    async def test_matches_include_pattern(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """File matching include pattern is accepted."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        file_path = tmp_watch_dir / "test.txt"
        result = service._matches_patterns(file_path, sample_config)

        assert result is True

    @pytest.mark.asyncio
    async def test_rejects_non_matching_pattern(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """File not matching include pattern is rejected."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        file_path = tmp_watch_dir / "test.xyz"
        result = service._matches_patterns(file_path, sample_config)

        assert result is False

    @pytest.mark.asyncio
    async def test_ignore_pattern_overrides(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Ignore pattern overrides include pattern."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        file_path = tmp_watch_dir / "test.tmp"  # .tmp is in ignore_patterns
        result = service._matches_patterns(file_path, sample_config)

        assert result is False

    @pytest.mark.asyncio
    async def test_wildcard_pattern_matches_all(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Wildcard pattern matches all files."""
        config = WatcherConfig(
            watcher_id="wildcard-watcher",
            path=str(tmp_watch_dir),
            patterns=["*"],
            enabled=False,
        )
        await service.create_watcher(config)

        assert service._matches_patterns(tmp_watch_dir / "any.file", config) is True
        assert service._matches_patterns(tmp_watch_dir / "another.ext", config) is True


# =============================================================================
# FILE HASH TESTS
# =============================================================================


class TestFileHash:
    """Test file hashing for deduplication."""

    def test_get_file_hash(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Get hash of existing file."""
        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        hash1 = service._get_file_hash(test_file)

        assert len(hash1) == 32  # MD5 hex digest

    def test_get_file_hash_nonexistent(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Hash of nonexistent file is empty."""
        nonexistent = tmp_watch_dir / "nonexistent.txt"
        result = service._get_file_hash(nonexistent)

        assert result == ""

    def test_get_file_hash_changes_with_content(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Hash changes when file content changes (different sizes)."""
        test_file = tmp_watch_dir / "test.txt"

        test_file.write_text("short")
        hash1 = service._get_file_hash(test_file)

        # Use different size content to ensure hash changes
        # (hash uses path + size + mtime, mtime resolution may be low on Windows)
        test_file.write_text("much longer content that will definitely be different")
        hash2 = service._get_file_hash(test_file)

        assert hash1 != hash2


# =============================================================================
# SCAN FOLDER TESTS
# =============================================================================


class TestScanFolder:
    """Test manual folder scanning."""

    @pytest.mark.asyncio
    async def test_scan_folder(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Scan folder for existing files."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        # Create some files
        (tmp_watch_dir / "file1.txt").write_text("content1")
        (tmp_watch_dir / "file2.txt").write_text("content2")

        events = await service.scan_folder(sample_config.watcher_id)

        assert len(events) == 2
        assert all(isinstance(e, FileEvent) for e in events)

    @pytest.mark.asyncio
    async def test_scan_folder_nonexistent_watcher(self, service: FolderWatcherService):
        """Scan nonexistent watcher raises error."""
        with pytest.raises(ValueError, match="not found"):
            await service.scan_folder("nonexistent")

    @pytest.mark.asyncio
    async def test_scan_folder_recursive(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Recursive scan finds nested files."""
        sample_config.enabled = False
        sample_config.recursive = True
        await service.create_watcher(sample_config)

        # Create nested file
        nested_dir = tmp_watch_dir / "nested"
        nested_dir.mkdir()
        (nested_dir / "nested.txt").write_text("nested content")
        (tmp_watch_dir / "root.txt").write_text("root content")

        events = await service.scan_folder(sample_config.watcher_id)

        filenames = [e.filename for e in events]
        assert "nested.txt" in filenames
        assert "root.txt" in filenames

    @pytest.mark.asyncio
    async def test_scan_folder_non_recursive(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Non-recursive scan only finds root files."""
        sample_config.enabled = False
        sample_config.recursive = False
        await service.create_watcher(sample_config)

        # Create nested file
        nested_dir = tmp_watch_dir / "nested"
        nested_dir.mkdir()
        (nested_dir / "nested.txt").write_text("nested content")
        (tmp_watch_dir / "root.txt").write_text("root content")

        events = await service.scan_folder(sample_config.watcher_id)

        filenames = [e.filename for e in events]
        assert "root.txt" in filenames
        assert "nested.txt" not in filenames

    @pytest.mark.asyncio
    async def test_scan_folder_respects_patterns(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Scan respects include/ignore patterns."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        # Create files with different extensions
        (tmp_watch_dir / "included.txt").write_text("included")
        (tmp_watch_dir / "excluded.xyz").write_text("excluded")
        (tmp_watch_dir / "ignored.tmp").write_text("ignored")

        events = await service.scan_folder(sample_config.watcher_id)

        filenames = [e.filename for e in events]
        assert "included.txt" in filenames
        assert "excluded.xyz" not in filenames
        assert "ignored.tmp" not in filenames


# =============================================================================
# HANDLE EVENT TESTS
# =============================================================================


class TestHandleEvent:
    """Test file event handling."""

    @pytest.mark.asyncio
    async def test_handle_event_creates_file_event(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Handle event creates FileEvent."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        event = await service._handle_event(
            sample_config.watcher_id,
            WatcherEvent.CREATED,
            str(test_file),
        )

        assert event is not None
        assert event.event_type == WatcherEvent.CREATED
        assert event.filename == "test.txt"

    @pytest.mark.asyncio
    async def test_handle_event_skips_non_matching(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Handle event skips non-matching files."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        test_file = tmp_watch_dir / "test.xyz"  # Not in patterns
        test_file.write_text("content")

        event = await service._handle_event(
            sample_config.watcher_id,
            WatcherEvent.CREATED,
            str(test_file),
        )

        assert event is None

    @pytest.mark.asyncio
    async def test_handle_event_skips_processed(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Handle event skips already processed files."""
        sample_config.enabled = False
        await service.create_watcher(sample_config)

        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        # Mark as processed
        file_hash = service._get_file_hash(test_file)
        service._processed_files[sample_config.watcher_id].add(file_hash)

        event = await service._handle_event(
            sample_config.watcher_id,
            WatcherEvent.CREATED,
            str(test_file),
        )

        assert event is None

    @pytest.mark.asyncio
    async def test_handle_event_nonexistent_watcher(self, service: FolderWatcherService, tmp_watch_dir: Path):
        """Handle event for nonexistent watcher returns None."""
        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        event = await service._handle_event(
            "nonexistent",
            WatcherEvent.CREATED,
            str(test_file),
        )

        assert event is None


# =============================================================================
# AUTO IMPORT TESTS
# =============================================================================


class TestAutoImport:
    """Test auto-import functionality."""

    @pytest.mark.asyncio
    async def test_auto_import_on_create(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Auto-import is triggered on file creation."""
        sample_config.enabled = False
        sample_config.auto_import = True
        await service.create_watcher(sample_config)

        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            event = await service._handle_event(
                sample_config.watcher_id,
                WatcherEvent.CREATED,
                str(test_file),
            )

        assert event.document_id == "doc-123"

    @pytest.mark.asyncio
    async def test_auto_import_updates_stats(self, service: FolderWatcherService, sample_config: WatcherConfig, tmp_watch_dir: Path):
        """Auto-import updates processed count."""
        sample_config.enabled = False
        sample_config.auto_import = True
        await service.create_watcher(sample_config)

        test_file = tmp_watch_dir / "test.txt"
        test_file.write_text("content")

        with patch("backend.app.services.ingestion.service.ingestion_service") as mock_ingest:
            mock_result = MagicMock()
            mock_result.document_id = "doc-123"
            mock_ingest.ingest_file = AsyncMock(return_value=mock_result)

            await service._handle_event(
                sample_config.watcher_id,
                WatcherEvent.CREATED,
                str(test_file),
            )

        assert service._stats[sample_config.watcher_id]["files_processed"] == 1


# =============================================================================
# WATCHER CONFIG TESTS
# =============================================================================


class TestWatcherConfig:
    """Test WatcherConfig model."""

    def test_config_defaults(self, tmp_watch_dir: Path):
        """Config has sensible defaults."""
        config = WatcherConfig(
            watcher_id="test",
            path=str(tmp_watch_dir),
        )

        assert config.recursive is True
        assert config.patterns == ["*"]
        assert config.ignore_patterns == []
        assert config.auto_import is True
        assert config.delete_after_import is False
        assert config.enabled is True

    def test_config_custom_values(self, tmp_watch_dir: Path):
        """Config accepts custom values."""
        config = WatcherConfig(
            watcher_id="custom",
            path=str(tmp_watch_dir),
            recursive=False,
            patterns=["*.pdf"],
            ignore_patterns=["*.bak"],
            auto_import=False,
            delete_after_import=True,
            target_collection="inbox",
            tags=["important", "review"],
        )

        assert config.recursive is False
        assert config.patterns == ["*.pdf"]
        assert config.delete_after_import is True
        assert config.tags == ["important", "review"]


# =============================================================================
# FILE EVENT TESTS
# =============================================================================


class TestFileEvent:
    """Test FileEvent model."""

    def test_file_event_creation(self):
        """Create FileEvent with required fields."""
        event = FileEvent(
            event_type=WatcherEvent.CREATED,
            path="/path/to/file.txt",
            filename="file.txt",
        )

        assert event.event_type == WatcherEvent.CREATED
        assert event.filename == "file.txt"
        assert event.timestamp is not None

    def test_file_event_optional_fields(self):
        """FileEvent optional fields."""
        event = FileEvent(
            event_type=WatcherEvent.CREATED,
            path="/path/to/file.txt",
            filename="file.txt",
            size_bytes=1234,
            document_id="doc-123",
            error="Some error",
        )

        assert event.size_bytes == 1234
        assert event.document_id == "doc-123"
        assert event.error == "Some error"


# =============================================================================
# WATCHER EVENT ENUM TESTS
# =============================================================================


class TestWatcherEvent:
    """Test WatcherEvent enum."""

    def test_event_types(self):
        """All event types defined."""
        assert WatcherEvent.CREATED.value == "created"
        assert WatcherEvent.MODIFIED.value == "modified"
        assert WatcherEvent.DELETED.value == "deleted"
        assert WatcherEvent.MOVED.value == "moved"
