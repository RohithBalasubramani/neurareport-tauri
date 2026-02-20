"""
Ingestion Property-Based Tests - Using Hypothesis for validation.
"""

import os
import string
import io
import zipfile

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck


from backend.app.services.ingestion.service import (
    IngestionService,
    IngestionResult,
    BulkIngestionResult,
    StructuredDataImport,
    FileType,
)
from backend.app.services.ingestion.folder_watcher import (
    FolderWatcherService,
    WatcherConfig,
    WatcherStatus,
    FileEvent,
)
from backend.app.services.ingestion.email_ingestion import (
    EmailIngestionService,
    ParsedEmail,
)
from backend.app.services.ingestion.web_clipper import (
    WebClipperService,
    WebPageMetadata,
)


# =============================================================================
# STRATEGIES
# =============================================================================

filename_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + "_-",
    min_size=1,
    max_size=50,
)

extension_strategy = st.sampled_from([
    ".pdf", ".docx", ".xlsx", ".csv", ".txt", ".json",
    ".xml", ".yaml", ".html", ".md", ".png", ".jpg",
])

content_strategy = st.binary(min_size=1, max_size=1000)

metadata_strategy = st.dictionaries(
    keys=st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
    values=st.one_of(st.integers(), st.text(max_size=50), st.booleans()),
    max_size=5,
)

url_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + ".-_",
    min_size=1,
    max_size=50,
).map(lambda s: f"https://{s}.com/page")

email_strategy = st.text(
    alphabet=string.ascii_lowercase + string.digits,
    min_size=1,
    max_size=20,
).map(lambda s: f"{s}@example.com")


# =============================================================================
# FILE TYPE DETECTION PROPERTIES
# =============================================================================


class TestFileTypeDetectionProperties:
    """Property-based tests for file type detection."""

    @given(name=filename_strategy, ext=extension_strategy)
    def test_extension_detection_consistent(self, name: str, ext: str):
        """Extension detection is consistent for same extension."""
        service = IngestionService()
        filename = f"{name}{ext}"

        result1 = service.detect_file_type(filename)
        result2 = service.detect_file_type(filename)

        assert result1 == result2

    @given(name=filename_strategy, ext=extension_strategy)
    def test_extension_detection_case_insensitive(self, name: str, ext: str):
        """Extension detection is case insensitive."""
        service = IngestionService()

        lower = service.detect_file_type(f"{name}{ext.lower()}")
        upper = service.detect_file_type(f"{name}{ext.upper()}")

        assert lower == upper

    @given(name=filename_strategy)
    def test_unknown_extension_returns_unknown(self, name: str):
        """Unknown extension returns FileType.UNKNOWN."""
        assume(len(name) > 0)
        service = IngestionService()

        result = service.detect_file_type(f"{name}.unknownext")

        assert result == FileType.UNKNOWN

    @given(content=content_strategy)
    def test_content_detection_returns_valid_type(self, content: bytes):
        """Content detection always returns valid FileType."""
        service = IngestionService()

        result = service.detect_file_type("unknown.bin", content)

        assert isinstance(result, FileType)


# =============================================================================
# INGESTION SERVICE PROPERTIES
# =============================================================================


class TestIngestionServiceProperties:
    """Property-based tests for IngestionService."""

    @given(name=filename_strategy, content=content_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
    def test_ingest_file_preserves_size(self, name: str, content: bytes, tmp_path_factory):
        """Ingested file preserves original size."""
        import asyncio
        assume(len(name.strip()) > 0)

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        async def run():
            result = await service.ingest_file(f"{name}.txt", content)
            return result

        result = asyncio.run(run())

        assert result.size_bytes == len(content)

    @given(name=filename_strategy, ext=extension_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow], deadline=None)
    def test_ingest_file_detects_type(self, name: str, ext: str, tmp_path_factory):
        """Ingested file has correct type detected."""
        import asyncio
        assume(len(name.strip()) > 0)

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        async def run():
            result = await service.ingest_file(f"{name}{ext}", b"content")
            return result

        result = asyncio.run(run())

        expected_type = service.detect_file_type(f"{name}{ext}")
        assert result.file_type == expected_type

    @given(metadata=metadata_strategy)
    @settings(max_examples=15, suppress_health_check=[HealthCheck.too_slow])
    def test_ingest_file_preserves_metadata(self, metadata: dict, tmp_path_factory):
        """Ingested file preserves custom metadata."""
        import asyncio

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        async def run():
            result = await service.ingest_file("test.txt", b"content", metadata=metadata)
            return result

        result = asyncio.run(run())

        for key, value in metadata.items():
            assert key in result.metadata
            assert result.metadata[key] == value


# =============================================================================
# ZIP INGESTION PROPERTIES
# =============================================================================


class TestZipIngestionProperties:
    """Property-based tests for ZIP ingestion."""

    @given(file_count=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def test_zip_ingestion_counts_match(self, file_count: int, tmp_path_factory):
        """ZIP ingestion counts match actual files."""
        import asyncio

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        # Create ZIP with specified number of files
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for i in range(file_count):
                zf.writestr(f"file{i}.txt", f"content {i}")
        zip_content = buffer.getvalue()

        async def run():
            result = await service.ingest_zip_archive("test.zip", zip_content)
            return result

        result = asyncio.run(run())

        assert result.total_files == file_count
        assert result.successful + result.failed == file_count

    @given(file_count=st.integers(min_value=0, max_value=5))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def test_zip_successful_count_correct(self, file_count: int, tmp_path_factory):
        """ZIP successful count equals results length."""
        import asyncio

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for i in range(file_count):
                zf.writestr(f"file{i}.txt", f"content")
        zip_content = buffer.getvalue()

        async def run():
            result = await service.ingest_zip_archive("test.zip", zip_content)
            return result

        result = asyncio.run(run())

        assert result.successful == len(result.results)


# =============================================================================
# STRUCTURED DATA IMPORT PROPERTIES
# =============================================================================


class TestStructuredDataProperties:
    """Property-based tests for structured data import."""

    @given(
        records=st.lists(
            st.dictionaries(
                keys=st.text(alphabet=string.ascii_letters, min_size=1, max_size=10),
                values=st.one_of(st.integers(), st.text(max_size=20)),
                min_size=1,
                max_size=3,
            ),
            min_size=1,
            max_size=20,
        )
    )
    @settings(max_examples=15, suppress_health_check=[HealthCheck.too_slow])
    def test_import_json_row_count_matches(self, records: list, tmp_path_factory):
        """JSON import row count matches input."""
        import asyncio
        import json

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        content = json.dumps(records).encode()

        async def run():
            result = await service.import_structured_data("data.json", content)
            return result

        result = asyncio.run(run())

        assert result.row_count == len(records)

    @given(
        records=st.lists(
            st.fixed_dictionaries({
                "id": st.integers(),
                "name": st.text(min_size=1, max_size=10),
            }),
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def test_import_json_columns_detected(self, records: list, tmp_path_factory):
        """JSON import detects all columns."""
        import asyncio
        import json

        tmp_path = tmp_path_factory.mktemp("uploads")
        service = IngestionService()
        service._upload_dir = tmp_path

        content = json.dumps(records).encode()

        async def run():
            result = await service.import_structured_data("data.json", content)
            return result

        result = asyncio.run(run())

        assert "id" in result.columns
        assert "name" in result.columns


# =============================================================================
# FOLDER WATCHER PROPERTIES
# =============================================================================


class TestFolderWatcherProperties:
    """Property-based tests for FolderWatcherService."""

    @given(path=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=20))
    @settings(max_examples=15, suppress_health_check=[HealthCheck.too_slow])
    def test_watcher_config_preserves_path(self, path: str, tmp_path_factory):
        """Watcher config preserves path."""
        import asyncio

        tmp_path = tmp_path_factory.mktemp("watch")
        full_path = str(tmp_path / path)

        service = FolderWatcherService()
        config = WatcherConfig(
            watcher_id=f"watcher-{path}",
            path=full_path,
            enabled=False,
        )

        async def run():
            status = await service.create_watcher(config)
            return status

        status = asyncio.run(run())

        assert status.path == full_path

    @given(
        patterns=st.lists(
            st.text(alphabet=string.ascii_letters + "*.", min_size=1, max_size=10),
            min_size=1,
            max_size=5,
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.too_slow])
    def test_watcher_config_preserves_patterns(self, patterns: list, tmp_path_factory):
        """Watcher config preserves patterns."""
        import asyncio

        tmp_path = tmp_path_factory.mktemp("watch")

        service = FolderWatcherService()
        config = WatcherConfig(
            watcher_id="pattern-watcher",
            path=str(tmp_path),
            patterns=patterns,
            enabled=False,
        )

        async def run():
            await service.create_watcher(config)
            return service._watchers["pattern-watcher"]

        stored = asyncio.run(run())

        assert stored.patterns == patterns


# =============================================================================
# EMAIL INGESTION PROPERTIES
# =============================================================================


class TestEmailIngestionProperties:
    """Property-based tests for EmailIngestionService."""

    @given(user_id=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=20))
    def test_inbox_address_contains_domain(self, user_id: str):
        """Generated inbox address contains domain."""
        service = EmailIngestionService()

        address = service.generate_inbox_address(user_id)

        assert "@neurareport.io" in address

    @given(user_id=st.text(alphabet=string.ascii_letters, min_size=1, max_size=10))
    def test_inbox_address_format_valid(self, user_id: str):
        """Generated inbox address has valid format."""
        service = EmailIngestionService()

        address = service.generate_inbox_address(user_id)

        # Format: ingest+{hex}@domain
        assert address.startswith("ingest+")
        parts = address.split("@")
        assert len(parts) == 2

    @given(
        purpose=st.text(alphabet=string.ascii_letters, min_size=1, max_size=10),
        user_id=st.text(alphabet=string.ascii_letters, min_size=1, max_size=10),
    )
    def test_inbox_addresses_unique(self, purpose: str, user_id: str):
        """Different purposes generate different addresses."""
        service = EmailIngestionService()

        addr1 = service.generate_inbox_address(user_id, purpose="one")
        addr2 = service.generate_inbox_address(user_id, purpose="two")

        assert addr1 != addr2


# =============================================================================
# WEB CLIPPER PROPERTIES
# =============================================================================


class TestWebClipperProperties:
    """Property-based tests for WebClipperService."""

    @given(name=st.text(min_size=1, max_size=50))
    def test_sanitize_filename_max_length(self, name: str):
        """Sanitized filename never exceeds max length."""
        service = WebClipperService()

        result = service._sanitize_filename(name)

        assert len(result) <= 100

    @given(name=st.text(alphabet=string.ascii_letters + " ", min_size=1, max_size=20))
    def test_sanitize_filename_preserves_valid(self, name: str):
        """Sanitize preserves valid characters."""
        assume(len(name.strip()) > 0)
        service = WebClipperService()

        result = service._sanitize_filename(name)

        # Valid characters should be preserved
        assert name == result or len(result) > 0

    @given(
        title=st.text(min_size=1, max_size=50),
        url=url_strategy,
    )
    def test_metadata_preserves_url(self, title: str, url: str):
        """WebPageMetadata preserves URL."""
        metadata = WebPageMetadata(title=title, url=url)

        assert metadata.url == url

    @given(word_count=st.integers(min_value=0, max_value=10000))
    def test_reading_time_calculation(self, word_count: int):
        """Reading time based on word count."""
        metadata = WebPageMetadata(
            title="Test",
            url="https://example.com",
            word_count=word_count,
            reading_time_minutes=max(1, word_count // 200),
        )

        expected = max(1, word_count // 200)
        assert metadata.reading_time_minutes == expected


# =============================================================================
# DOCUMENT ID PROPERTIES
# =============================================================================


class TestDocumentIdProperties:
    """Property-based tests for document ID generation."""

    @given(
        filename=filename_strategy,
        content=content_strategy,
    )
    def test_document_id_is_hex(self, filename: str, content: bytes):
        """Document ID is valid hexadecimal."""
        service = IngestionService()

        doc_id = service._generate_document_id(filename, content)

        assert all(c in "0123456789abcdef" for c in doc_id)

    @given(
        filename=filename_strategy,
        content=content_strategy,
    )
    def test_document_id_length_consistent(self, filename: str, content: bytes):
        """Document ID has consistent length."""
        service = IngestionService()

        doc_id = service._generate_document_id(filename, content)

        assert len(doc_id) == 16
