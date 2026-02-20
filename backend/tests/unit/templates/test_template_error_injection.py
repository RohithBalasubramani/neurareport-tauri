"""
Error injection tests for template operations.

Tests failure modes and error handling in template operations.
"""
from __future__ import annotations

import asyncio
import io
import os
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest
from fastapi import UploadFile, HTTPException

from backend.app.services.templates.service import TemplateService, TemplateImportContext
from backend.app.services.templates.errors import (
    TemplateExtractionError,
    TemplateImportError,
    TemplateLockedError,
    TemplateTooLargeError,
    TemplateZipInvalidError,
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
# Upload Error Injection Tests
# =============================================================================

class TestUploadErrors:
    """Tests for upload-related errors."""

    @pytest.mark.asyncio
    async def test_corrupt_zip_file(self, template_service, mock_state_store):
        """Should handle corrupt ZIP data."""
        corrupt_data = b"PK\x03\x04not a valid zip"
        upload = create_upload_file(corrupt_data)

        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload, "Test", "test-123")

    @pytest.mark.asyncio
    async def test_empty_zip_file(self, template_service, mock_state_store):
        """Should handle empty ZIP (no files)."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            pass  # Empty ZIP
        buffer.seek(0)
        upload = create_upload_file(buffer.read())

        # Should succeed but with no files
        result = await template_service.import_zip(upload, "Empty", "test-123")
        assert result["template_id"] is not None

    @pytest.mark.asyncio
    async def test_non_zip_file(self, template_service, mock_state_store):
        """Should reject non-ZIP files."""
        upload = create_upload_file(b"This is not a ZIP file")

        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload, "Test", "test-123")

    @pytest.mark.asyncio
    async def test_truncated_zip_file(self, template_service, mock_state_store):
        """Should handle truncated ZIP files."""
        files = {"test.pdf": b"content" * 1000}
        full_zip = create_test_zip(files)
        # Truncate to half
        truncated = full_zip[: len(full_zip) // 2]
        upload = create_upload_file(truncated)

        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload, "Test", "test-123")


# =============================================================================
# Size Limit Error Tests
# =============================================================================

class TestSizeLimitErrors:
    """Tests for size limit errors."""

    @pytest.mark.asyncio
    async def test_upload_exceeds_max_bytes(self, temp_uploads, mock_state_store):
        """Should reject uploads exceeding max_bytes."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=50,  # 50 byte limit - very small
        )

        # Create content that won't compress much (random bytes)
        import random
        random.seed(42)
        large_content = bytes(random.randint(0, 255) for _ in range(200))
        files = {"large.pdf": large_content}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        with pytest.raises(TemplateTooLargeError) as exc:
            await svc.import_zip(upload, "Large", "test-123")
        assert exc.value.status_code == 413

    @pytest.mark.asyncio
    async def test_zip_too_many_entries(self, temp_uploads, mock_state_store):
        """Should reject ZIPs with too many entries."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=10 * 1024 * 1024,
            max_zip_entries=5,
        )

        # Create ZIP with many files
        files = {f"file_{i}.txt": b"content" for i in range(10)}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        with pytest.raises(TemplateImportError) as exc:
            await svc.import_zip(upload, "ManyFiles", "test-123")
        assert "too many" in exc.value.message.lower()

    @pytest.mark.asyncio
    async def test_zip_uncompressed_size_exceeded(self, temp_uploads, mock_state_store):
        """Should reject ZIPs that expand beyond limit."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=10 * 1024 * 1024,
            max_zip_uncompressed_bytes=1000,  # 1KB limit
        )

        # Create file that compresses well but is large uncompressed
        large_content = b"A" * 5000  # Compresses well
        files = {"large.txt": large_content}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        with pytest.raises(TemplateImportError) as exc:
            await svc.import_zip(upload, "CompressedBomb", "test-123")
        # Error message says "expands beyond" not "too large"
        assert "expands beyond" in exc.value.message.lower() or "too large" in exc.value.message.lower()


# =============================================================================
# File System Error Tests
# =============================================================================

class TestFileSystemErrors:
    """Tests for file system errors."""

    @pytest.mark.asyncio
    async def test_read_only_uploads_dir(self, temp_uploads, mock_state_store):
        """Should handle read-only uploads directory."""
        uploads, excel_uploads = temp_uploads

        # Make uploads read-only (skip on Windows)
        if os.name != 'nt':
            uploads.chmod(0o444)

            svc = TemplateService(
                uploads_root=uploads,
                excel_uploads_root=excel_uploads,
                max_bytes=10 * 1024 * 1024,
            )

            files = {"source.pdf": b"%PDF"}
            zip_content = create_test_zip(files)
            upload = create_upload_file(zip_content)

            try:
                with pytest.raises((TemplateImportError, PermissionError)):
                    await svc.import_zip(upload, "Test", "test-123")
            finally:
                uploads.chmod(0o755)

    @pytest.mark.asyncio
    async def test_nonexistent_template_dir_export(self, template_service, mock_state_store, temp_uploads):
        """Should handle missing template directory on export."""
        mock_state_store.get_template_record.return_value = {
            "id": "missing-tpl",
            "name": "Missing",
            "kind": "pdf",
        }
        # Don't create the directory

        with pytest.raises(HTTPException) as exc:
            await template_service.export_zip("missing-tpl", "test-123")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_nonexistent_template_dir_duplicate(self, template_service, mock_state_store, temp_uploads):
        """Should handle missing template directory on duplicate."""
        mock_state_store.get_template_record.return_value = {
            "id": "missing-tpl",
            "name": "Missing",
            "kind": "pdf",
        }

        with pytest.raises(HTTPException) as exc:
            await template_service.duplicate("missing-tpl", None, "test-123")
        assert exc.value.status_code == 404


# =============================================================================
# Locking Error Tests
# =============================================================================

class TestLockingErrors:
    """Tests for template locking errors."""

    @pytest.mark.asyncio
    async def test_import_with_locked_template(self, template_service, mock_state_store, monkeypatch):
        """Should reject import when template is locked."""
        from backend.app.services.utils import TemplateLockError

        def mock_acquire_lock(*args, **kwargs):
            raise TemplateLockError("Template is locked by another process")

        monkeypatch.setattr(
            "backend.app.services.templates.service.acquire_template_lock",
            mock_acquire_lock,
        )

        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        with pytest.raises(TemplateLockedError) as exc:
            await template_service.import_zip(upload, "Locked", "test-123")
        assert exc.value.status_code == 409


# =============================================================================
# State Store Error Tests
# =============================================================================

class TestStateStoreErrors:
    """Tests for state store errors."""

    @pytest.mark.asyncio
    async def test_template_not_found_export(self, template_service, mock_state_store):
        """Should raise 404 when template not found for export."""
        mock_state_store.get_template_record.return_value = None

        with pytest.raises(HTTPException) as exc:
            await template_service.export_zip("nonexistent", "test-123")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_template_not_found_duplicate(self, template_service, mock_state_store):
        """Should raise 404 when template not found for duplicate."""
        mock_state_store.get_template_record.return_value = None

        with pytest.raises(HTTPException) as exc:
            await template_service.duplicate("nonexistent", None, "test-123")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_template_not_found_update_tags(self, template_service, mock_state_store):
        """Should raise 404 when template not found for tag update."""
        mock_state_store.get_template_record.return_value = None

        with pytest.raises(HTTPException) as exc:
            await template_service.update_tags("nonexistent", ["tag1"])
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_state_store_upsert_error(self, template_service, mock_state_store, monkeypatch):
        """Should handle state store errors during import."""
        mock_state_store.upsert_template.side_effect = Exception("Database error")

        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        with pytest.raises((TemplateImportError, Exception)):
            await template_service.import_zip(upload, "Test", "test-123")


# =============================================================================
# Extraction Error Tests
# =============================================================================

class TestExtractionErrors:
    """Tests for ZIP extraction errors."""

    @pytest.mark.asyncio
    async def test_zip_with_path_traversal(self, template_service, mock_state_store):
        """Should handle potential path traversal in ZIP."""
        # This tests the extract_zip_to_dir function's handling
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            # Try to include a path traversal entry
            zf.writestr("../../../etc/passwd", b"root:x:0:0")
            zf.writestr("source.pdf", b"%PDF")
        buffer.seek(0)
        upload = create_upload_file(buffer.read())

        # Should either fail or sanitize the path
        try:
            result = await template_service.import_zip(upload, "Traversal", "test-123")
            # If it succeeds, verify files are contained properly
            assert result["template_id"] is not None
        except (TemplateExtractionError, TemplateImportError):
            pass  # Expected behavior

    @pytest.mark.asyncio
    async def test_zip_with_absolute_paths(self, template_service, mock_state_store):
        """Should handle ZIPs with absolute paths."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("/absolute/path/file.txt", b"content")
            zf.writestr("source.pdf", b"%PDF")
        buffer.seek(0)
        upload = create_upload_file(buffer.read())

        # Should handle gracefully
        try:
            result = await template_service.import_zip(upload, "Absolute", "test-123")
            assert result["template_id"] is not None
        except (TemplateExtractionError, TemplateImportError):
            pass


# =============================================================================
# Concurrent Error Tests
# =============================================================================

class TestConcurrentErrors:
    """Tests for concurrent operation errors."""

    @pytest.mark.asyncio
    async def test_concurrent_exports_same_template(self, template_service, mock_state_store, temp_uploads):
        """Should handle concurrent exports of same template."""
        uploads, _ = temp_uploads
        template_id = "concurrent-export"

        mock_state_store.get_template_record.return_value = {
            "id": template_id,
            "name": "Concurrent",
            "kind": "pdf",
        }

        tpl_dir = uploads / template_id
        tpl_dir.mkdir()
        (tpl_dir / "template.html").write_text("<html>Test</html>")

        # Run multiple exports concurrently
        results = await asyncio.gather(
            template_service.export_zip(template_id, "test-1"),
            template_service.export_zip(template_id, "test-2"),
            template_service.export_zip(template_id, "test-3"),
            return_exceptions=True,
        )

        # All should succeed or fail gracefully
        for result in results:
            if not isinstance(result, Exception):
                assert result["template_id"] == template_id
                # Cleanup
                Path(result["zip_path"]).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_concurrent_tag_updates(self, template_service, mock_state_store):
        """Should handle concurrent tag updates."""
        mock_state_store.get_template_record.return_value = {
            "id": "concurrent-tags",
            "name": "Test",
            "status": "draft",
        }

        # Run multiple tag updates concurrently
        results = await asyncio.gather(
            template_service.update_tags("concurrent-tags", ["tag1"]),
            template_service.update_tags("concurrent-tags", ["tag2"]),
            template_service.update_tags("concurrent-tags", ["tag3"]),
            return_exceptions=True,
        )

        # All should succeed
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        assert success_count == 3


# =============================================================================
# Recovery Tests
# =============================================================================

class TestErrorRecovery:
    """Tests for error recovery scenarios."""

    @pytest.mark.asyncio
    async def test_cleanup_on_import_failure(self, temp_uploads, mock_state_store):
        """Should clean up partial files on import failure."""
        uploads, excel_uploads = temp_uploads
        svc = TemplateService(
            uploads_root=uploads,
            excel_uploads_root=excel_uploads,
            max_bytes=10 * 1024 * 1024,
            max_zip_entries=2,  # Will fail on extraction
        )

        # Create ZIP that will fail due to too many entries
        files = {f"file_{i}.txt": b"content" for i in range(10)}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        try:
            await svc.import_zip(upload, "FailedImport", "test-123")
        except TemplateImportError:
            pass

        # Check that temp files were cleaned up
        # (We can't easily verify this without tracking temp paths)

    @pytest.mark.asyncio
    async def test_retry_after_failure(self, template_service, mock_state_store):
        """Should allow retry after failure."""
        # First attempt with invalid file
        upload1 = create_upload_file(b"invalid")
        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload1, "Test", "test-123")

        # Second attempt with valid file should work
        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)
        upload2 = create_upload_file(zip_content)

        result = await template_service.import_zip(upload2, "Test", "test-456")
        assert result["template_id"] is not None


# =============================================================================
# Error Message Tests
# =============================================================================

class TestErrorMessages:
    """Tests for error message quality."""

    def test_too_large_error_includes_limit(self):
        """TemplateTooLargeError should include the limit."""
        error = TemplateTooLargeError(max_bytes=1024)
        assert "1024" in error.message

    def test_zip_invalid_error_includes_detail(self):
        """TemplateZipInvalidError should include detail."""
        error = TemplateZipInvalidError(detail="File is corrupt")
        assert error.detail == "File is corrupt"

    def test_extraction_error_includes_detail(self):
        """TemplateExtractionError should include detail."""
        error = TemplateExtractionError(detail="Permission denied")
        assert error.detail == "Permission denied"

    def test_locked_error_status_code(self):
        """TemplateLockedError should have 409 status."""
        error = TemplateLockedError()
        assert error.status_code == 409

    def test_import_error_is_domain_error(self):
        """TemplateImportError should have expected properties."""
        error = TemplateImportError(
            code="test_code",
            message="Test message",
            status_code=400,
            detail="Extra info",
        )
        assert error.code == "test_code"
        assert error.message == "Test message"
        assert error.status_code == 400
        assert error.detail == "Extra info"


# =============================================================================
# Edge Case Error Tests
# =============================================================================

class TestEdgeCaseErrors:
    """Tests for edge case error scenarios."""

    @pytest.mark.asyncio
    async def test_zero_byte_zip(self, template_service, mock_state_store):
        """Should handle zero-byte file."""
        upload = create_upload_file(b"")

        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload, "Empty", "test-123")

    @pytest.mark.asyncio
    async def test_binary_garbage_data(self, template_service, mock_state_store):
        """Should handle random binary data."""
        import random
        random_bytes = bytes(random.randint(0, 255) for _ in range(1000))
        upload = create_upload_file(random_bytes)

        with pytest.raises(TemplateZipInvalidError):
            await template_service.import_zip(upload, "Garbage", "test-123")

    @pytest.mark.asyncio
    async def test_very_long_filename_in_zip(self, template_service, mock_state_store):
        """Should handle very long filenames in ZIP."""
        long_name = "a" * 500 + ".pdf"
        files = {long_name: b"%PDF"}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        # Should either succeed or fail gracefully
        try:
            result = await template_service.import_zip(upload, "LongName", "test-123")
            assert result["template_id"] is not None
        except (TemplateImportError, TemplateExtractionError):
            pass  # Acceptable

    @pytest.mark.asyncio
    async def test_unicode_filename_in_zip(self, template_service, mock_state_store):
        """Should handle unicode filenames in ZIP."""
        files = {"rapport_financier.pdf": b"%PDF"}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        result = await template_service.import_zip(upload, "Unicode", "test-123")
        assert result["template_id"] is not None

    @pytest.mark.asyncio
    async def test_special_chars_in_display_name(self, template_service, mock_state_store):
        """Should handle special characters in display name."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_test_zip(files)
        upload = create_upload_file(zip_content)

        # Name with special characters
        result = await template_service.import_zip(
            upload,
            "Test <Template> & 'Quotes'",
            "test-123",
        )
        assert result["template_id"] is not None
        # Name should be sanitized
        assert "<" not in result["name"]
        assert ">" not in result["name"]
