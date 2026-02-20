"""
Integration tests for template management workflows.

Tests end-to-end template operations including import, edit, and export.
"""
from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services.templates.service import TemplateService
from backend.app.services.templates.errors import TemplateImportError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def integration_dir(tmp_path):
    """Create integration test directories."""
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    excel_uploads = tmp_path / "excel_uploads"
    excel_uploads.mkdir()
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return {
        "uploads": uploads,
        "excel_uploads": excel_uploads,
        "state_dir": state_dir,
    }


@pytest.fixture
def template_service(integration_dir):
    """Create template service for integration tests."""
    return TemplateService(
        uploads_root=integration_dir["uploads"],
        excel_uploads_root=integration_dir["excel_uploads"],
        max_bytes=50 * 1024 * 1024,  # 50 MB
        max_zip_entries=500,
        max_zip_uncompressed_bytes=100 * 1024 * 1024,  # 100 MB
    )


@pytest.fixture
def mock_state_store(monkeypatch):
    """Mock state store for integration tests."""
    templates = {}

    class MockStore:
        def list_templates(self):
            return list(templates.values())

        def get_template_record(self, template_id):
            return templates.get(template_id)

        def upsert_template(self, template_id, name, status, artifacts, connection_id=None,
                           mapping_keys=None, template_type=None, tags=None, description=None):
            templates[template_id] = {
                "id": template_id,
                "name": name,
                "status": status,
                "kind": template_type or "pdf",
                "artifacts": artifacts or {},
                "tags": tags or [],
                "last_connection_id": connection_id,
                "mapping_keys": mapping_keys or [],
                "description": description,
            }

        def delete_template(self, template_id):
            if template_id in templates:
                del templates[template_id]

        def record_template_run(self, template_id):
            if template_id in templates:
                templates[template_id]["run_count"] = templates[template_id].get("run_count", 0) + 1

    store = MockStore()
    monkeypatch.setattr("backend.app.services.templates.service.state_store", store)
    return store


def create_zip_content(files: dict[str, bytes], root_dir: str = "") -> bytes:
    """Create ZIP content from file dictionary."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            path = f"{root_dir}/{name}" if root_dir else name
            zf.writestr(path, content)
    buffer.seek(0)
    return buffer.read()


def create_upload_file(content: bytes, filename: str = "template.zip"):
    """Create upload file mock."""
    from fastapi import UploadFile
    file = io.BytesIO(content)
    return UploadFile(file=file, filename=filename)


# =============================================================================
# Import Workflow Tests
# =============================================================================

class TestImportWorkflow:
    """Tests for template import workflow."""

    @pytest.mark.asyncio
    async def test_import_pdf_template_full_workflow(self, template_service, mock_state_store, integration_dir):
        """Full workflow: Import PDF template and verify structure."""
        # Create a comprehensive PDF template ZIP
        files = {
            "source.pdf": b"%PDF-1.4 test content",
            "template_p1.html": b"<html><body><h1>{title}</h1><p>{content}</p></body></html>",
            "schema_ext.json": json.dumps({
                "scalars": ["title"],
                "row_tokens": ["content"],
                "totals": [],
            }).encode(),
            "manifest.json": json.dumps({
                "version": "1.0",
                "artifacts": {
                    "template_html_url": "template_p1.html",
                    "source_pdf_url": "source.pdf",
                },
            }).encode(),
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content, "report_template.zip")

        # Import
        result = await template_service.import_zip(
            upload=upload,
            display_name="Monthly Report Template",
            correlation_id="integration-test-1",
        )

        # Verify result
        assert result["template_id"] is not None
        assert result["kind"] == "pdf"
        assert "Monthly" in result["name"] or "Report" in result["name"]

        # Verify files were extracted
        template_dir = integration_dir["uploads"] / result["template_id"]
        assert template_dir.exists()
        assert (template_dir / "template_p1.html").exists()
        assert (template_dir / "source.pdf").exists()

        # Verify state was persisted
        template_record = mock_state_store.get_template_record(result["template_id"])
        assert template_record is not None
        assert template_record["kind"] == "pdf"

    @pytest.mark.asyncio
    async def test_import_excel_template_full_workflow(self, template_service, mock_state_store, integration_dir):
        """Full workflow: Import Excel template."""
        files = {
            "source.xlsx": b"PK\x03\x04",  # Excel files start with ZIP signature
            "manifest.json": json.dumps({
                "version": "1.0",
                "artifacts": {},
            }).encode(),
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content, "excel_template.zip")

        result = await template_service.import_zip(
            upload=upload,
            display_name="Sales Dashboard",
            correlation_id="integration-test-2",
        )

        assert result["kind"] == "excel"

        # Verify correct directory used
        template_dir = integration_dir["excel_uploads"] / result["template_id"]
        assert template_dir.exists()

    @pytest.mark.asyncio
    async def test_import_with_nested_directory(self, template_service, mock_state_store, integration_dir):
        """Import ZIP with nested directory structure."""
        files = {
            "source.pdf": b"%PDF",
            "assets/logo.png": b"\x89PNG",
            "styles/main.css": b"body { margin: 0; }",
            "template_p1.html": b"<html><body>Test</body></html>",
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        result = await template_service.import_zip(upload, "Nested Template", "test")

        template_dir = integration_dir["uploads"] / result["template_id"]
        assert (template_dir / "assets" / "logo.png").exists()
        assert (template_dir / "styles" / "main.css").exists()


# =============================================================================
# Export Workflow Tests
# =============================================================================

class TestExportWorkflow:
    """Tests for template export workflow."""

    @pytest.mark.asyncio
    async def test_import_then_export(self, template_service, mock_state_store, integration_dir):
        """Import template, then export it."""
        # Import first
        files = {
            "source.pdf": b"%PDF-1.4",
            "template_p1.html": b"<html><body>Test</body></html>",
            "config.json": json.dumps({"setting": "value"}).encode(),
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        import_result = await template_service.import_zip(upload, "Export Test", "import-corr")
        template_id = import_result["template_id"]

        # Export
        export_result = await template_service.export_zip(template_id, "export-corr")

        assert export_result["template_id"] == template_id
        assert export_result["zip_path"] is not None

        # Verify exported ZIP contents
        export_path = Path(export_result["zip_path"])
        assert export_path.exists()

        with zipfile.ZipFile(export_path, "r") as zf:
            names = zf.namelist()
            assert "template_p1.html" in names
            assert "source.pdf" in names
            assert "config.json" in names

        # Cleanup
        export_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_export_reimport_roundtrip(self, template_service, mock_state_store, integration_dir):
        """Export and reimport should preserve content."""
        # Initial import
        original_html = b"<html><body><h1>Original Content</h1></body></html>"
        files = {
            "source.pdf": b"%PDF-1.4",
            "template_p1.html": original_html,
        }
        zip_content = create_zip_content(files)
        upload1 = create_upload_file(zip_content)

        result1 = await template_service.import_zip(upload1, "Roundtrip Test", "corr-1")
        original_id = result1["template_id"]

        # Export
        export_result = await template_service.export_zip(original_id, "export-corr")
        export_path = Path(export_result["zip_path"])

        # Reimport
        with open(export_path, "rb") as f:
            reimport_content = f.read()
        upload2 = create_upload_file(reimport_content)

        result2 = await template_service.import_zip(upload2, "Reimported", "corr-2")
        reimport_id = result2["template_id"]

        # Verify content preserved
        original_dir = integration_dir["uploads"] / original_id
        reimport_dir = integration_dir["uploads"] / reimport_id

        original_content = (original_dir / "template_p1.html").read_bytes()
        reimport_content = (reimport_dir / "template_p1.html").read_bytes()

        assert original_content == reimport_content == original_html

        # Cleanup
        export_path.unlink(missing_ok=True)


# =============================================================================
# Duplicate Workflow Tests
# =============================================================================

class TestDuplicateWorkflow:
    """Tests for template duplication workflow."""

    @pytest.mark.asyncio
    async def test_duplicate_preserves_content(self, template_service, mock_state_store, integration_dir):
        """Duplicated template should have same content."""
        # Import original
        html_content = b"<html><body>{placeholder}</body></html>"
        files = {
            "source.pdf": b"%PDF",
            "template_p1.html": html_content,
            "data.json": b'{"key": "value"}',
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        original = await template_service.import_zip(upload, "Original", "corr-1")
        original_id = original["template_id"]

        # Duplicate
        duplicate = await template_service.duplicate(original_id, "Duplicate", "corr-2")
        duplicate_id = duplicate["template_id"]

        # Verify different IDs
        assert duplicate_id != original_id

        # Verify same content
        original_dir = integration_dir["uploads"] / original_id
        duplicate_dir = integration_dir["uploads"] / duplicate_id

        assert (original_dir / "template_p1.html").read_bytes() == html_content
        assert (duplicate_dir / "template_p1.html").read_bytes() == html_content
        assert (duplicate_dir / "data.json").read_bytes() == b'{"key": "value"}'

    @pytest.mark.asyncio
    async def test_duplicate_is_independent(self, template_service, mock_state_store, integration_dir):
        """Modifications to duplicate should not affect original."""
        # Import original
        files = {
            "source.pdf": b"%PDF",
            "template_p1.html": b"<html>Original</html>",
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        original = await template_service.import_zip(upload, "Original", "corr-1")
        original_id = original["template_id"]

        # Duplicate
        duplicate = await template_service.duplicate(original_id, "Duplicate", "corr-2")
        duplicate_id = duplicate["template_id"]

        # Modify duplicate
        duplicate_dir = integration_dir["uploads"] / duplicate_id
        (duplicate_dir / "template_p1.html").write_bytes(b"<html>Modified</html>")

        # Original should be unchanged
        original_dir = integration_dir["uploads"] / original_id
        assert (original_dir / "template_p1.html").read_bytes() == b"<html>Original</html>"


# =============================================================================
# Tag Management Workflow Tests
# =============================================================================

class TestTagWorkflow:
    """Tests for tag management workflow."""

    @pytest.mark.asyncio
    async def test_add_tags_to_template(self, template_service, mock_state_store, integration_dir):
        """Add tags to imported template."""
        # Import
        files = {"source.pdf": b"%PDF"}
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        result = await template_service.import_zip(upload, "Tagged Template", "corr-1")
        template_id = result["template_id"]

        # Add tags
        tag_result = await template_service.update_tags(template_id, ["finance", "monthly", "sales"])

        assert "finance" in tag_result["tags"]
        assert "monthly" in tag_result["tags"]
        assert "sales" in tag_result["tags"]

        # Verify in store
        record = mock_state_store.get_template_record(template_id)
        assert "finance" in record["tags"]

    @pytest.mark.asyncio
    async def test_tag_aggregation(self, template_service, mock_state_store, integration_dir):
        """Aggregate tags across multiple templates."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_zip_content(files)

        # Import multiple templates with tags
        for i, tags in enumerate([
            ["finance", "quarterly"],
            ["finance", "monthly"],
            ["sales", "monthly"],
        ]):
            upload = create_upload_file(zip_content, f"template_{i}.zip")
            result = await template_service.import_zip(upload, f"Template{i}", f"corr-{i}")
            await template_service.update_tags(result["template_id"], tags)

        # Get all tags
        all_tags = await template_service.get_all_tags()

        assert "finance" in all_tags["tags"]
        assert "monthly" in all_tags["tags"]
        assert "quarterly" in all_tags["tags"]
        assert "sales" in all_tags["tags"]

        # Finance should have count 2
        assert all_tags["tagCounts"]["finance"] == 2
        assert all_tags["tagCounts"]["monthly"] == 2
        assert all_tags["tagCounts"]["quarterly"] == 1


# =============================================================================
# Full Lifecycle Tests
# =============================================================================

class TestFullLifecycle:
    """Tests for complete template lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_template_lifecycle(self, template_service, mock_state_store, integration_dir):
        """Test complete lifecycle: import -> tag -> duplicate -> export -> delete."""
        # 1. Import
        files = {
            "source.pdf": b"%PDF-1.4",
            "template_p1.html": b"<html><body>{title}</body></html>",
        }
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        import_result = await template_service.import_zip(upload, "Lifecycle Test", "corr-1")
        template_id = import_result["template_id"]

        # Verify import
        assert mock_state_store.get_template_record(template_id) is not None

        # 2. Add tags
        await template_service.update_tags(template_id, ["test", "lifecycle"])
        record = mock_state_store.get_template_record(template_id)
        assert "test" in record["tags"]

        # 3. Duplicate
        duplicate_result = await template_service.duplicate(template_id, "Lifecycle Copy", "corr-2")
        duplicate_id = duplicate_result["template_id"]

        # Verify both exist
        assert mock_state_store.get_template_record(template_id) is not None
        assert mock_state_store.get_template_record(duplicate_id) is not None

        # 4. Export original
        export_result = await template_service.export_zip(template_id, "corr-3")
        assert Path(export_result["zip_path"]).exists()

        # 5. Delete original
        mock_state_store.delete_template(template_id)
        assert mock_state_store.get_template_record(template_id) is None

        # Duplicate should still exist
        assert mock_state_store.get_template_record(duplicate_id) is not None

        # Cleanup
        Path(export_result["zip_path"]).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_multiple_templates_workflow(self, template_service, mock_state_store, integration_dir):
        """Test workflow with multiple templates."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_zip_content(files)

        # Import multiple templates
        template_ids = []
        for i in range(5):
            upload = create_upload_file(zip_content, f"template_{i}.zip")
            result = await template_service.import_zip(upload, f"Template {i}", f"corr-{i}")
            template_ids.append(result["template_id"])

        # Verify all imported
        all_templates = mock_state_store.list_templates()
        assert len(all_templates) == 5

        # Add different tags
        for i, tid in enumerate(template_ids):
            tags = ["common"]
            if i % 2 == 0:
                tags.append("even")
            else:
                tags.append("odd")
            await template_service.update_tags(tid, tags)

        # Verify tag counts
        all_tags = await template_service.get_all_tags()
        assert all_tags["tagCounts"]["common"] == 5
        assert all_tags["tagCounts"]["even"] == 3
        assert all_tags["tagCounts"]["odd"] == 2


# =============================================================================
# Error Recovery Workflow Tests
# =============================================================================

class TestErrorRecoveryWorkflow:
    """Tests for error recovery in workflows."""

    @pytest.mark.asyncio
    async def test_retry_after_failed_import(self, template_service, mock_state_store, integration_dir):
        """Should allow retry after failed import."""
        # First attempt with invalid content
        upload1 = create_upload_file(b"not a zip")
        with pytest.raises(Exception):
            await template_service.import_zip(upload1, "Failed", "corr-1")

        # Retry with valid content
        files = {"source.pdf": b"%PDF"}
        zip_content = create_zip_content(files)
        upload2 = create_upload_file(zip_content)

        result = await template_service.import_zip(upload2, "Retry Success", "corr-2")
        assert result["template_id"] is not None

    @pytest.mark.asyncio
    async def test_workflow_continues_after_partial_failure(
        self, template_service, mock_state_store, integration_dir
    ):
        """Workflow should continue after partial operations fail."""
        files = {"source.pdf": b"%PDF"}
        zip_content = create_zip_content(files)
        upload = create_upload_file(zip_content)

        # Import template
        result = await template_service.import_zip(upload, "Partial Failure Test", "corr-1")
        template_id = result["template_id"]

        # Tags should work
        await template_service.update_tags(template_id, ["test"])

        # Try invalid export (nonexistent)
        with pytest.raises(Exception):
            await template_service.export_zip("nonexistent", "corr-2")

        # Original template should still be accessible
        await template_service.update_tags(template_id, ["still", "works"])
        record = mock_state_store.get_template_record(template_id)
        assert "still" in record["tags"]
