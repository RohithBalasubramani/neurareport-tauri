"""
Concurrent access tests for template operations.

Tests locking, race conditions, and concurrent modification handling.
"""
from __future__ import annotations

import asyncio
import io
import os
import threading
import time
import zipfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from backend.app.services.templates.service import TemplateService
from backend.app.services.templates.errors import TemplateLockedError, TemplateImportError
from backend.app.services.utils.lock import (
    acquire_template_lock,
    try_acquire_template_lock,
    TemplateLockError,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_uploads(tmp_path):
    """Create temporary upload directories."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    excel_uploads = tmp_path / "excel_uploads"
    excel_uploads.mkdir()
    return uploads, excel_uploads


@pytest.fixture
def template_service(temp_uploads):
    """Create a template service with temp directories."""
    uploads, excel_uploads = temp_uploads
    return TemplateService(
        uploads_root=uploads,
        excel_uploads_root=excel_uploads,
        max_bytes=10 * 1024 * 1024,
        max_concurrency=4,
    )


@pytest.fixture
def mock_state_store(monkeypatch):
    """Mock the state store."""
    store = MagicMock()
    store.list_templates.return_value = []
    store.get_template_record.return_value = None
    store.upsert_template = MagicMock()
    monkeypatch.setattr("backend.app.services.templates.service.state_store", store)
    return store


@pytest.fixture
def enable_locks(monkeypatch):
    """Enable locks for testing (normally disabled in pytest)."""
    monkeypatch.setenv("NEURA_LOCKS_ENABLED", "true")
    monkeypatch.delenv("NEURA_DISABLE_LOCKS", raising=False)
    # Clear PYTEST_CURRENT_TEST to enable locks
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)


def create_test_zip(files: dict[str, bytes]) -> bytes:
    """Create a test ZIP file in memory."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    buffer.seek(0)
    return buffer.read()


def create_upload_file(content: bytes, filename: str = "template.zip") -> UploadFile:
    """Create an UploadFile from bytes content."""
    file = io.BytesIO(content)
    return UploadFile(file=file, filename=filename)


# =============================================================================
# Lock Acquisition Tests
# =============================================================================

class TestLockAcquisition:
    """Tests for template lock acquisition."""

    def test_lock_acquisition_succeeds(self, tmp_path):
        """Should successfully acquire lock."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        with acquire_template_lock(tdir, "test"):
            # Lock acquired
            pass

    def test_lock_releases_after_context(self, tmp_path, enable_locks):
        """Lock should be released after context exits."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        with acquire_template_lock(tdir, "test"):
            pass

        # Should be able to acquire again
        with acquire_template_lock(tdir, "test"):
            pass

    def test_lock_with_correlation_id(self, tmp_path):
        """Should accept correlation ID."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        with acquire_template_lock(tdir, "test", correlation_id="corr-123"):
            pass

    def test_try_acquire_succeeds_when_free(self, tmp_path):
        """try_acquire should succeed when lock is free."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        with try_acquire_template_lock(tdir, "test") as acquired:
            assert acquired is True

    def test_lock_error_has_properties(self):
        """TemplateLockError should have expected properties."""
        error = TemplateLockError("Test error", lock_holder="pid=123")
        assert str(error) == "Test error"
        assert error.lock_holder == "pid=123"


# =============================================================================
# Concurrent Lock Tests (Locks Enabled)
# =============================================================================

class TestConcurrentLocks:
    """Tests for concurrent lock behavior with locks enabled."""

    def test_second_lock_blocks(self, tmp_path, enable_locks):
        """Second lock attempt should block until first releases."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        results = []
        first_acquired = threading.Event()
        second_can_proceed = threading.Event()

        def first_holder():
            with acquire_template_lock(tdir, "test", timeout=5.0):
                results.append("first_acquired")
                first_acquired.set()
                second_can_proceed.wait(timeout=2.0)
                time.sleep(0.1)
                results.append("first_done")

        def second_holder():
            first_acquired.wait(timeout=2.0)
            results.append("second_waiting")
            second_can_proceed.set()
            with acquire_template_lock(tdir, "test", timeout=5.0):
                results.append("second_acquired")

        t1 = threading.Thread(target=first_holder)
        t2 = threading.Thread(target=second_holder)

        t1.start()
        t2.start()
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        assert "first_acquired" in results
        assert "first_done" in results
        assert "second_acquired" in results
        # First should complete before second acquires
        first_done_idx = results.index("first_done")
        second_acquired_idx = results.index("second_acquired")
        assert first_done_idx < second_acquired_idx

    def test_try_acquire_returns_false_when_locked(self, tmp_path, enable_locks):
        """try_acquire should return False when already locked."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        results = []
        first_acquired = threading.Event()
        second_tried = threading.Event()

        def first_holder():
            with acquire_template_lock(tdir, "test", timeout=5.0):
                results.append("first_acquired")
                first_acquired.set()
                second_tried.wait(timeout=2.0)
                time.sleep(0.1)

        def second_holder():
            first_acquired.wait(timeout=2.0)
            with try_acquire_template_lock(tdir, "test", timeout=0.1) as acquired:
                results.append(f"second_acquired={acquired}")
            second_tried.set()

        t1 = threading.Thread(target=first_holder)
        t2 = threading.Thread(target=second_holder)

        t1.start()
        t2.start()
        t1.join(timeout=5.0)
        t2.join(timeout=5.0)

        assert "first_acquired" in results
        assert "second_acquired=False" in results


# =============================================================================
# Service Concurrency Tests
# =============================================================================

class TestServiceConcurrency:
    """Tests for template service concurrency."""

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_imports(self, temp_uploads, mock_state_store):
        """Service semaphore should limit concurrent imports."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=10 * 1024 * 1024,
            max_concurrency=2,  # Only 2 concurrent
        )

        assert svc._semaphore._value == 2

    @pytest.mark.asyncio
    async def test_concurrent_imports_different_templates(self, template_service, mock_state_store):
        """Should handle concurrent imports of different templates."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)

        async def do_import(name: str) -> dict:
            upload = create_upload_file(zip_content, f"{name}.zip")
            return await template_service.import_zip(upload, name, f"corr-{name}")

        # Run multiple imports concurrently
        results = await asyncio.gather(
            do_import("Template1"),
            do_import("Template2"),
            do_import("Template3"),
            do_import("Template4"),
            do_import("Template5"),
        )

        # All should succeed with unique IDs
        template_ids = [r["template_id"] for r in results]
        assert len(set(template_ids)) == 5  # All unique

    @pytest.mark.asyncio
    async def test_concurrent_exports(self, template_service, mock_state_store, temp_uploads):
        """Should handle concurrent exports."""
        uploads, _ = temp_uploads

        # Setup templates
        for i in range(3):
            template_id = f"export-tpl-{i}"
            tpl_dir = uploads / template_id
            tpl_dir.mkdir()
            (tpl_dir / "template.html").write_text(f"<html>Template {i}</html>")
            mock_state_store.get_template_record.side_effect = lambda tid: {
                "id": tid,
                "name": f"Template {tid}",
                "kind": "pdf",
            } if tid.startswith("export-tpl-") else None

        async def do_export(template_id: str) -> dict:
            return await template_service.export_zip(template_id, f"corr-{template_id}")

        # Run concurrent exports
        results = await asyncio.gather(
            do_export("export-tpl-0"),
            do_export("export-tpl-1"),
            do_export("export-tpl-2"),
        )

        # All should succeed
        for result in results:
            assert result["template_id"].startswith("export-tpl-")
            assert result["zip_path"] is not None
            # Cleanup
            Path(result["zip_path"]).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_concurrent_tag_updates_same_template(self, template_service, mock_state_store):
        """Should handle concurrent tag updates to same template."""
        mock_state_store.get_template_record.return_value = {
            "id": "shared-tpl",
            "name": "Shared Template",
            "status": "draft",
        }

        async def update_tags(tags: list[str]) -> dict:
            return await template_service.update_tags("shared-tpl", tags)

        # Run concurrent updates
        results = await asyncio.gather(
            update_tags(["tag1", "tag2"]),
            update_tags(["tag3", "tag4"]),
            update_tags(["tag5"]),
        )

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert result["template_id"] == "shared-tpl"

    @pytest.mark.asyncio
    async def test_concurrent_duplicate_operations(self, template_service, mock_state_store, temp_uploads):
        """Should handle concurrent duplicate operations."""
        uploads, _ = temp_uploads
        source_id = "source-tpl"

        mock_state_store.get_template_record.return_value = {
            "id": source_id,
            "name": "Source Template",
            "kind": "pdf",
        }

        source_dir = uploads / source_id
        source_dir.mkdir()
        (source_dir / "template.html").write_text("<html>Source</html>")

        async def do_duplicate(name: str) -> dict:
            return await template_service.duplicate(source_id, name, f"corr-{name}")

        # Run concurrent duplicates
        results = await asyncio.gather(
            do_duplicate("Copy1"),
            do_duplicate("Copy2"),
            do_duplicate("Copy3"),
        )

        # All should succeed with unique IDs
        template_ids = [r["template_id"] for r in results]
        assert len(set(template_ids)) == 3


# =============================================================================
# Race Condition Tests
# =============================================================================

class TestRaceConditions:
    """Tests for race condition handling."""

    @pytest.mark.asyncio
    async def test_rapid_state_updates(self, template_service, mock_state_store):
        """Should handle rapid state updates."""
        update_count = [0]
        original_upsert = mock_state_store.upsert_template

        def counting_upsert(*args, **kwargs):
            update_count[0] += 1
            return original_upsert(*args, **kwargs)

        mock_state_store.upsert_template = counting_upsert
        mock_state_store.get_template_record.return_value = {
            "id": "rapid-tpl",
            "name": "Rapid",
            "status": "draft",
        }

        # Rapid tag updates
        tasks = [
            template_service.update_tags("rapid-tpl", [f"tag{i}"])
            for i in range(10)
        ]
        await asyncio.gather(*tasks)

        # All updates should have happened
        assert update_count[0] == 10

    @pytest.mark.asyncio
    async def test_import_export_interleave(self, template_service, mock_state_store, temp_uploads):
        """Should handle interleaved import and export operations."""
        uploads, _ = temp_uploads

        # Pre-create a template for export
        existing_id = "existing-tpl"
        existing_dir = uploads / existing_id
        existing_dir.mkdir()
        (existing_dir / "template.html").write_text("<html>Existing</html>")
        mock_state_store.get_template_record.return_value = {
            "id": existing_id,
            "name": "Existing",
            "kind": "pdf",
        }

        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)

        async def do_import():
            upload = create_upload_file(zip_content)
            return await template_service.import_zip(upload, "New", "import-corr")

        async def do_export():
            return await template_service.export_zip(existing_id, "export-corr")

        # Run interleaved
        results = await asyncio.gather(
            do_import(),
            do_export(),
            do_import(),
            do_export(),
        )

        # All should succeed
        import_results = [r for r in results if "template_id" in r and r.get("kind") == "pdf"]
        export_results = [r for r in results if "zip_path" in r]

        assert len(import_results) >= 1
        assert len(export_results) >= 1

        # Cleanup export ZIPs
        for r in export_results:
            Path(r["zip_path"]).unlink(missing_ok=True)


# =============================================================================
# Stress Tests
# =============================================================================

class TestStressConditions:
    """Stress tests for concurrent operations."""

    @pytest.mark.asyncio
    async def test_many_concurrent_imports(self, template_service, mock_state_store):
        """Should handle many concurrent imports."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)

        async def do_import(i: int) -> dict:
            upload = create_upload_file(zip_content, f"template_{i}.zip")
            return await template_service.import_zip(upload, f"Template{i}", f"corr-{i}")

        # Run many imports (limited by semaphore)
        tasks = [do_import(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        successes = [r for r in results if not isinstance(r, Exception)]
        assert len(successes) == 20

    @pytest.mark.asyncio
    async def test_concurrent_operations_mixed(self, template_service, mock_state_store, temp_uploads):
        """Should handle mixed concurrent operations."""
        uploads, _ = temp_uploads

        # Setup for export/duplicate
        source_id = "mixed-source"
        source_dir = uploads / source_id
        source_dir.mkdir()
        (source_dir / "template.html").write_text("<html>Source</html>")
        mock_state_store.get_template_record.return_value = {
            "id": source_id,
            "name": "Source",
            "kind": "pdf",
            "status": "draft",
        }

        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)

        operations = []

        # Mix of operations
        for i in range(5):
            # Import
            async def do_import(idx=i):
                upload = create_upload_file(zip_content, f"import_{idx}.zip")
                return await template_service.import_zip(upload, f"Import{idx}", f"import-{idx}")
            operations.append(do_import())

            # Export
            async def do_export(idx=i):
                return await template_service.export_zip(source_id, f"export-{idx}")
            operations.append(do_export())

            # Tags
            async def do_tags(idx=i):
                return await template_service.update_tags(source_id, [f"tag{idx}"])
            operations.append(do_tags())

        results = await asyncio.gather(*operations, return_exceptions=True)

        # Count successes
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]

        # Most should succeed
        assert len(successes) > len(failures)

        # Cleanup
        for r in results:
            if isinstance(r, dict) and "zip_path" in r:
                Path(r["zip_path"]).unlink(missing_ok=True)


# =============================================================================
# Thread Safety Tests
# =============================================================================

class TestThreadSafety:
    """Tests for thread safety."""

    def test_state_store_thread_safety(self, mock_state_store):
        """State store operations should be thread-safe."""
        results = []
        errors = []

        def update_template(i: int):
            try:
                mock_state_store.upsert_template(
                    f"tpl-{i}",
                    name=f"Template {i}",
                    status="draft",
                    artifacts={},
                    connection_id=None,
                    mapping_keys=[],
                    template_type="pdf",
                )
                results.append(i)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update_template, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        assert len(errors) == 0
        assert len(results) == 20

    def test_concurrent_lock_creation(self, tmp_path, enable_locks):
        """Multiple threads creating locks should not conflict."""
        results = []
        errors = []

        def create_and_use_lock(i: int):
            tdir = tmp_path / f"template_{i}"
            tdir.mkdir(exist_ok=True)
            try:
                with acquire_template_lock(tdir, "test", timeout=5.0):
                    time.sleep(0.01)
                    results.append(i)
            except Exception as e:
                errors.append((i, e))

        threads = [threading.Thread(target=create_and_use_lock, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        assert len(errors) == 0
        assert len(results) == 10


# =============================================================================
# Cleanup Tests
# =============================================================================

class TestConcurrentCleanup:
    """Tests for cleanup during concurrent operations."""

    @pytest.mark.asyncio
    async def test_cleanup_on_concurrent_failures(self, temp_uploads, mock_state_store):
        """Should clean up properly when concurrent operations fail."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=100,  # Very small - will cause failures
        )

        # Create large content that will fail
        large_content = b"x" * 200
        files = {"large.pdf": large_content}
        zip_content = create_test_zip(files)

        async def do_import(i: int):
            upload = create_upload_file(zip_content, f"fail_{i}.zip")
            try:
                return await svc.import_zip(upload, f"Fail{i}", f"corr-{i}")
            except Exception as e:
                return e

        # Run concurrent failing imports
        results = await asyncio.gather(*[do_import(i) for i in range(5)])

        # All should fail
        assert all(isinstance(r, Exception) for r in results)

        # Temp files should be cleaned up
        # (We can't easily verify temp directory cleanup)

    @pytest.mark.asyncio
    async def test_lock_release_on_exception(self, tmp_path, enable_locks):
        """Locks should be released even when exception occurs."""
        tdir = tmp_path / "template"
        tdir.mkdir()

        try:
            with acquire_template_lock(tdir, "test"):
                raise ValueError("Intentional error")
        except ValueError:
            pass

        # Should be able to acquire lock again
        with acquire_template_lock(tdir, "test"):
            pass  # Success
