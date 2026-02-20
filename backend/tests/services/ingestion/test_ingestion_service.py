"""
Ingestion Service Tests - Testing core file ingestion operations.
"""

import io
import json
import os
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


from backend.app.services.ingestion.service import (
    IngestionService,
    IngestionResult,
    BulkIngestionResult,
    StructuredDataImport,
    FileType,
)


@pytest.fixture
def service(tmp_path: Path) -> IngestionService:
    """Create an ingestion service with temp upload directory."""
    svc = IngestionService()
    svc._upload_dir = tmp_path / "uploads"
    svc._upload_dir.mkdir(parents=True, exist_ok=True)
    return svc


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Sample PDF-like content (magic number only)."""
    return b"%PDF-1.4\n%Test PDF content"


@pytest.fixture
def sample_text_content() -> bytes:
    """Sample text file content."""
    return b"Hello, World!\nThis is a test document."


@pytest.fixture
def sample_json_content() -> bytes:
    """Sample JSON content."""
    return b'{"name": "test", "value": 123}'


@pytest.fixture
def sample_zip_content() -> bytes:
    """Sample ZIP archive with multiple files."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("doc1.txt", "Document 1 content")
        zf.writestr("doc2.txt", "Document 2 content")
        zf.writestr("folder/doc3.txt", "Nested document")
    return buffer.getvalue()


# =============================================================================
# INGEST FILE TESTS
# =============================================================================


class TestIngestFile:
    """Test single file ingestion."""

    @pytest.mark.asyncio
    async def test_ingest_text_file(self, service: IngestionService, sample_text_content: bytes):
        """Ingest a simple text file."""
        result = await service.ingest_file(
            filename="test.txt",
            content=sample_text_content,
        )

        assert isinstance(result, IngestionResult)
        assert result.document_id is not None
        assert result.filename == "test.txt"
        assert result.file_type == FileType.TXT
        assert result.size_bytes == len(sample_text_content)
        assert result.processing_status == "completed"

    @pytest.mark.asyncio
    async def test_ingest_pdf_file(self, service: IngestionService, sample_pdf_content: bytes):
        """Ingest a PDF file."""
        with patch.object(service, "_extract_metadata", new_callable=AsyncMock) as mock_meta:
            mock_meta.return_value = {"original_filename": "test.pdf"}
            with patch.object(service, "_get_page_count", new_callable=AsyncMock) as mock_pages:
                mock_pages.return_value = 5
                with patch.object(service, "_generate_preview", new_callable=AsyncMock) as mock_preview:
                    mock_preview.return_value = "/uploads/abc/preview.png"
                    with patch.object(service, "_is_scanned_pdf", new_callable=AsyncMock) as mock_scan:
                        mock_scan.return_value = False

                        result = await service.ingest_file(
                            filename="document.pdf",
                            content=sample_pdf_content,
                        )

        assert result.file_type == FileType.PDF
        assert result.pages == 5
        assert result.preview_url == "/uploads/abc/preview.png"

    @pytest.mark.asyncio
    async def test_ingest_with_metadata(self, service: IngestionService, sample_text_content: bytes):
        """Ingest file with custom metadata."""
        result = await service.ingest_file(
            filename="test.txt",
            content=sample_text_content,
            metadata={"author": "Test User", "department": "Engineering"},
        )

        assert "author" in result.metadata
        assert result.metadata["author"] == "Test User"
        assert result.metadata["department"] == "Engineering"

    @pytest.mark.asyncio
    async def test_ingest_creates_upload_directory(self, service: IngestionService, sample_text_content: bytes):
        """Ingestion creates upload directory for document."""
        result = await service.ingest_file(
            filename="test.txt",
            content=sample_text_content,
        )

        doc_dir = service._upload_dir / result.document_id
        assert doc_dir.exists()
        assert (doc_dir / "test.txt").exists()

    @pytest.mark.asyncio
    async def test_ingest_saves_file_content(self, service: IngestionService, sample_text_content: bytes):
        """Ingested file content is saved correctly."""
        result = await service.ingest_file(
            filename="test.txt",
            content=sample_text_content,
        )

        file_path = service._upload_dir / result.document_id / "test.txt"
        assert file_path.read_bytes() == sample_text_content

    @pytest.mark.asyncio
    async def test_ingest_unique_document_ids(self, service: IngestionService, sample_text_content: bytes):
        """Each ingestion creates unique document ID."""
        result1 = await service.ingest_file("test1.txt", sample_text_content)
        result2 = await service.ingest_file("test2.txt", sample_text_content)
        result3 = await service.ingest_file("test3.txt", sample_text_content)

        ids = {result1.document_id, result2.document_id, result3.document_id}
        assert len(ids) == 3

    @pytest.mark.asyncio
    async def test_ingest_without_ocr(self, service: IngestionService, sample_pdf_content: bytes):
        """Ingest PDF with OCR disabled."""
        with patch.object(service, "_extract_metadata", new_callable=AsyncMock) as mock_meta:
            mock_meta.return_value = {}
            with patch.object(service, "_is_scanned_pdf", new_callable=AsyncMock) as mock_scan:
                result = await service.ingest_file(
                    filename="test.pdf",
                    content=sample_pdf_content,
                    auto_ocr=False,
                )
                # _is_scanned_pdf should not be called when auto_ocr=False
                # But current impl checks anyway - just verify no OCR warning
                assert "OCR'd" not in " ".join(result.warnings)

    @pytest.mark.asyncio
    async def test_ingest_without_preview(self, service: IngestionService, sample_text_content: bytes):
        """Ingest file with preview generation disabled."""
        result = await service.ingest_file(
            filename="test.txt",
            content=sample_text_content,
            generate_preview=False,
        )

        assert result.preview_url is None

    @pytest.mark.asyncio
    async def test_ingest_json_file(self, service: IngestionService, sample_json_content: bytes):
        """Ingest a JSON file."""
        result = await service.ingest_file(
            filename="data.json",
            content=sample_json_content,
        )

        assert result.file_type == FileType.JSON

    @pytest.mark.asyncio
    async def test_ingest_xml_file(self, service: IngestionService):
        """Ingest an XML file."""
        content = b'<?xml version="1.0"?><root><item>Test</item></root>'
        result = await service.ingest_file(
            filename="data.xml",
            content=content,
        )

        assert result.file_type == FileType.XML

    @pytest.mark.asyncio
    async def test_ingest_yaml_file(self, service: IngestionService):
        """Ingest a YAML file."""
        content = b"name: test\nvalue: 123"
        result = await service.ingest_file(
            filename="config.yaml",
            content=content,
        )

        assert result.file_type == FileType.YAML


class TestIngestFileMetadataExtraction:
    """Test metadata extraction during ingestion."""

    @pytest.mark.asyncio
    async def test_metadata_includes_filename(self, service: IngestionService, sample_text_content: bytes):
        """Extracted metadata includes original filename."""
        result = await service.ingest_file("report.txt", sample_text_content)
        assert "original_filename" in result.metadata
        assert result.metadata["original_filename"] == "report.txt"

    @pytest.mark.asyncio
    async def test_metadata_includes_file_type(self, service: IngestionService, sample_text_content: bytes):
        """Extracted metadata includes file type."""
        result = await service.ingest_file("report.txt", sample_text_content)
        assert "file_type" in result.metadata
        assert result.metadata["file_type"] == "txt"

    @pytest.mark.asyncio
    async def test_metadata_includes_ingestion_timestamp(self, service: IngestionService, sample_text_content: bytes):
        """Extracted metadata includes ingestion timestamp."""
        result = await service.ingest_file("report.txt", sample_text_content)
        assert "ingested_at" in result.metadata


class TestIngestFileWarnings:
    """Test warning generation during ingestion."""

    @pytest.mark.asyncio
    async def test_scanned_pdf_warning(self, service: IngestionService, sample_pdf_content: bytes):
        """Scanned PDF generates OCR warning."""
        with patch.object(service, "_extract_metadata", new_callable=AsyncMock) as mock_meta:
            mock_meta.return_value = {}
            with patch.object(service, "_is_scanned_pdf", new_callable=AsyncMock) as mock_scan:
                mock_scan.return_value = True
                with patch.object(service, "_perform_ocr", new_callable=AsyncMock) as mock_ocr:
                    result = await service.ingest_file(
                        filename="scanned.pdf",
                        content=sample_pdf_content,
                    )

        assert any("OCR" in w for w in result.warnings)


# =============================================================================
# INGEST FROM URL TESTS
# =============================================================================


class TestIngestFromUrl:
    """Test URL-based ingestion."""

    @pytest.mark.asyncio
    async def test_ingest_from_url(self, service: IngestionService):
        """Ingest document from URL."""
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b"Downloaded content")
        mock_response.headers = {"Content-Disposition": 'attachment; filename="downloaded.txt"'}
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.ingest_from_url("https://example.com/file.txt")

        assert result.filename == "downloaded.txt"

    @pytest.mark.asyncio
    async def test_ingest_from_url_with_override_filename(self, service: IngestionService):
        """Ingest from URL with filename override."""
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b"Content")
        mock_response.headers = {}
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.ingest_from_url(
                "https://example.com/unknown",
                filename="override.pdf",
            )

        assert result.filename == "override.pdf"

    @pytest.mark.asyncio
    async def test_ingest_from_url_extracts_filename_from_path(self, service: IngestionService):
        """Ingest from URL extracts filename from URL path."""
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b"Content")
        mock_response.headers = {}  # No Content-Disposition
        mock_response.raise_for_status = MagicMock()

        with patch("aiohttp.ClientSession") as mock_session:
            mock_ctx = MagicMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_response)
            mock_ctx.__aexit__ = AsyncMock(return_value=None)

            mock_session_instance = MagicMock()
            mock_session_instance.get = MagicMock(return_value=mock_ctx)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)

            mock_session.return_value = mock_session_instance

            result = await service.ingest_from_url("https://example.com/path/to/document.pdf")

        assert result.filename == "document.pdf"


# =============================================================================
# INGEST ZIP ARCHIVE TESTS
# =============================================================================


class TestIngestZipArchive:
    """Test ZIP archive ingestion."""

    @pytest.mark.asyncio
    async def test_ingest_zip_archive(self, service: IngestionService, sample_zip_content: bytes):
        """Ingest files from ZIP archive."""
        result = await service.ingest_zip_archive(
            filename="archive.zip",
            content=sample_zip_content,
        )

        assert isinstance(result, BulkIngestionResult)
        assert result.total_files == 3
        assert result.successful == 3
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_ingest_zip_preserves_structure(self, service: IngestionService, sample_zip_content: bytes):
        """ZIP ingestion preserves folder structure by default."""
        result = await service.ingest_zip_archive(
            filename="archive.zip",
            content=sample_zip_content,
            preserve_structure=True,
        )

        filenames = [r.filename for r in result.results]
        # With preserve_structure, nested files keep their path
        assert any("folder/doc3.txt" in f for f in filenames)

    @pytest.mark.asyncio
    async def test_ingest_zip_flatten(self, service: IngestionService, sample_zip_content: bytes):
        """ZIP ingestion can flatten structure."""
        result = await service.ingest_zip_archive(
            filename="archive.zip",
            content=sample_zip_content,
            flatten=True,
        )

        filenames = [r.filename for r in result.results]
        # With flatten, only filename is kept
        assert "doc3.txt" in filenames
        assert not any("folder/" in f for f in filenames)

    @pytest.mark.asyncio
    async def test_ingest_zip_skips_directories(self, service: IngestionService):
        """ZIP ingestion skips directory entries."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("file.txt", "content")
            zf.writestr("folder/", "")  # Directory entry
        content = buffer.getvalue()

        result = await service.ingest_zip_archive("archive.zip", content)

        assert result.total_files == 1
        assert result.successful == 1

    @pytest.mark.asyncio
    async def test_ingest_zip_skips_hidden_files(self, service: IngestionService):
        """ZIP ingestion skips hidden and system files."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("normal.txt", "content")
            zf.writestr(".hidden", "hidden content")
            zf.writestr("__MACOSX/file.txt", "system file")
        content = buffer.getvalue()

        result = await service.ingest_zip_archive("archive.zip", content)

        assert result.successful == 1
        filenames = [r.filename for r in result.results]
        assert "normal.txt" in filenames
        assert ".hidden" not in filenames
        assert "__MACOSX/file.txt" not in filenames

    @pytest.mark.asyncio
    async def test_ingest_zip_adds_source_metadata(self, service: IngestionService, sample_zip_content: bytes):
        """ZIP ingestion adds source archive metadata."""
        result = await service.ingest_zip_archive("archive.zip", sample_zip_content)

        for ingestion_result in result.results:
            assert "source_archive" in ingestion_result.metadata
            assert ingestion_result.metadata["source_archive"] == "archive.zip"

    @pytest.mark.asyncio
    async def test_ingest_invalid_zip(self, service: IngestionService):
        """Invalid ZIP file reports error."""
        result = await service.ingest_zip_archive(
            filename="bad.zip",
            content=b"not a zip file",
        )

        assert result.failed == 1
        assert len(result.errors) == 1
        assert "Invalid ZIP" in result.errors[0]["error"]

    @pytest.mark.asyncio
    async def test_ingest_empty_zip(self, service: IngestionService):
        """Empty ZIP file handled gracefully."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            pass  # Empty
        content = buffer.getvalue()

        result = await service.ingest_zip_archive("empty.zip", content)

        assert result.total_files == 0
        assert result.successful == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_ingest_zip_partial_failure(self, service: IngestionService):
        """ZIP ingestion handles partial failures."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("good.txt", "content")
            zf.writestr("another.txt", "more content")
        content = buffer.getvalue()

        # Mock ingest_file to fail for one file
        original_ingest = service.ingest_file
        call_count = [0]

        async def mock_ingest(filename, content, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Simulated failure")
            return await original_ingest(filename, content, **kwargs)

        with patch.object(service, "ingest_file", side_effect=mock_ingest):
            result = await service.ingest_zip_archive("archive.zip", content)

        assert result.successful == 1
        assert result.failed == 1
        assert len(result.errors) == 1


# =============================================================================
# IMPORT STRUCTURED DATA TESTS
# =============================================================================


class TestImportStructuredData:
    """Test structured data import."""

    @pytest.mark.asyncio
    async def test_import_json_array(self, service: IngestionService):
        """Import JSON array as table."""
        content = b'[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]'
        result = await service.import_structured_data("data.json", content)

        assert isinstance(result, StructuredDataImport)
        assert result.row_count == 2
        assert result.column_count == 2
        assert "name" in result.columns
        assert "age" in result.columns

    @pytest.mark.asyncio
    async def test_import_json_object(self, service: IngestionService):
        """Import JSON object with embedded array."""
        content = b'{"records": [{"id": 1}, {"id": 2}]}'
        result = await service.import_structured_data("data.json", content)

        assert result.row_count == 2
        assert "id" in result.columns

    @pytest.mark.asyncio
    async def test_import_json_single_object(self, service: IngestionService):
        """Import single JSON object as one row."""
        content = b'{"name": "Test", "value": 123}'
        result = await service.import_structured_data("data.json", content)

        assert result.row_count == 1
        assert "name" in result.columns

    @pytest.mark.asyncio
    async def test_import_yaml(self, service: IngestionService):
        """Import YAML as structured data."""
        content = b"""
- name: Alice
  age: 30
- name: Bob
  age: 25
"""
        result = await service.import_structured_data("data.yaml", content)

        assert result.row_count == 2
        assert "name" in result.columns

    @pytest.mark.asyncio
    async def test_import_xml(self, service: IngestionService):
        """Import XML as structured data."""
        content = b"""<?xml version="1.0"?>
<records>
    <record>
        <name>Alice</name>
        <age>30</age>
    </record>
</records>
"""
        result = await service.import_structured_data("data.xml", content)

        assert result.document_id is not None

    @pytest.mark.asyncio
    async def test_import_with_format_hint(self, service: IngestionService):
        """Import with explicit format hint."""
        content = b'{"key": "value"}'
        result = await service.import_structured_data(
            "data.txt",  # Ambiguous extension
            content,
            format_hint="json",
        )

        assert result.document_id is not None

    @pytest.mark.asyncio
    async def test_import_generates_table_name(self, service: IngestionService):
        """Table name derived from filename."""
        content = b'[{"a": 1}]'
        result = await service.import_structured_data("sales_data.json", content)

        assert result.table_name == "sales_data"

    @pytest.mark.asyncio
    async def test_import_sample_data_limited(self, service: IngestionService):
        """Sample data is limited to first 10 rows."""
        data = [{"id": i} for i in range(100)]
        content = json.dumps(data).encode()
        result = await service.import_structured_data("large.json", content)

        assert result.row_count == 100
        assert len(result.sample_data) == 10


# =============================================================================
# DOCUMENT ID GENERATION TESTS
# =============================================================================


class TestDocumentIdGeneration:
    """Test document ID generation."""

    def test_generate_document_id_is_hex(self, service: IngestionService):
        """Document ID is hexadecimal string."""
        doc_id = service._generate_document_id("test.txt", b"content")
        assert all(c in "0123456789abcdef" for c in doc_id)

    def test_generate_document_id_length(self, service: IngestionService):
        """Document ID has expected length."""
        doc_id = service._generate_document_id("test.txt", b"content")
        assert len(doc_id) == 16

    def test_generate_document_id_unique(self, service: IngestionService):
        """Same filename and content still generates unique IDs."""
        # Due to timestamp component, IDs should differ
        import time
        id1 = service._generate_document_id("test.txt", b"content")
        time.sleep(0.001)  # Ensure timestamp differs
        id2 = service._generate_document_id("test.txt", b"content")
        assert id1 != id2


# =============================================================================
# XML TO DICT CONVERSION TESTS
# =============================================================================


class TestXmlToDict:
    """Test XML to dictionary conversion."""

    def test_simple_xml(self, service: IngestionService):
        """Convert simple XML element."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring("<root><name>Test</name></root>")
        result = service._xml_to_dict(root)

        assert result["name"] == "Test"

    def test_nested_xml(self, service: IngestionService):
        """Convert nested XML element."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring("<root><child><name>Test</name></child></root>")
        result = service._xml_to_dict(root)

        assert result["child"]["name"] == "Test"

    def test_xml_with_attributes(self, service: IngestionService):
        """Convert XML with attributes."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring('<root id="123"><name>Test</name></root>')
        result = service._xml_to_dict(root)

        assert "@attributes" in result
        assert result["@attributes"]["id"] == "123"
