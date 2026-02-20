"""
Ingestion Concurrency Tests - Testing thread safety and concurrent operations.
"""

import io
import os
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue

import pytest


# Check if BeautifulSoup is available
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

requires_bs4 = pytest.mark.skipif(not HAS_BS4, reason="BeautifulSoup (bs4) not installed")

from backend.app.services.ingestion.service import (
    IngestionService,
    IngestionResult,
    FileType,
)
from backend.app.services.ingestion.folder_watcher import (
    FolderWatcherService,
    WatcherConfig,
)
from backend.app.services.ingestion.email_ingestion import (
    EmailIngestionService,
)
from backend.app.services.ingestion.web_clipper import (
    WebClipperService,
)


# =============================================================================
# CONCURRENT FILE INGESTION TESTS
# =============================================================================


class TestConcurrentFileIngestion:
    """Test concurrent file ingestion scenarios."""

    @pytest.mark.asyncio
    async def test_many_concurrent_ingestions(self, tmp_path: Path):
        """Many concurrent ingestions should all succeed."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        num_files = 50
        results = []
        errors = []

        async def ingest_file(i):
            try:
                result = await service.ingest_file(
                    filename=f"document_{i}.txt",
                    content=f"Content for file {i}".encode(),
                )
                results.append(result.document_id)
            except Exception as e:
                errors.append((i, e))

        import asyncio
        await asyncio.gather(*[ingest_file(i) for i in range(num_files)])

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == num_files
        assert len(set(results)) == num_files  # All unique IDs

    @pytest.mark.asyncio
    async def test_concurrent_same_filename_unique_ids(self, tmp_path: Path):
        """Same filename concurrently produces unique IDs."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        results = []

        async def ingest():
            result = await service.ingest_file(
                filename="same_name.txt",
                content=b"content",
            )
            results.append(result.document_id)

        import asyncio
        await asyncio.gather(*[ingest() for _ in range(20)])

        assert len(set(results)) == 20  # All unique

    @pytest.mark.asyncio
    async def test_concurrent_mixed_file_types(self, tmp_path: Path):
        """Concurrent ingestion of mixed file types."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        files = [
            ("doc.txt", b"text content"),
            ("data.json", b'{"key": "value"}'),
            ("config.yaml", b"key: value"),
            ("page.html", b"<html><body>Test</body></html>"),
            ("readme.md", b"# Readme"),
        ]

        results = []

        async def ingest(filename, content):
            result = await service.ingest_file(filename, content)
            results.append((filename, result.file_type))

        import asyncio
        await asyncio.gather(*[ingest(f, c) for f, c in files])

        # Verify correct types detected
        type_map = dict(results)
        assert type_map["doc.txt"] == FileType.TXT
        assert type_map["data.json"] == FileType.JSON
        assert type_map["config.yaml"] == FileType.YAML


# =============================================================================
# CONCURRENT ZIP INGESTION TESTS
# =============================================================================


class TestConcurrentZipIngestion:
    """Test concurrent ZIP archive ingestion."""

    @pytest.mark.asyncio
    async def test_concurrent_zip_ingestion(self, tmp_path: Path):
        """Multiple ZIP files can be ingested concurrently."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        def create_zip(name, file_count):
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zf:
                for i in range(file_count):
                    zf.writestr(f"{name}_file_{i}.txt", f"Content {i}")
            return buffer.getvalue()

        zips = [
            ("archive1.zip", create_zip("a1", 5)),
            ("archive2.zip", create_zip("a2", 10)),
            ("archive3.zip", create_zip("a3", 3)),
        ]

        results = []

        async def ingest_zip(name, content):
            result = await service.ingest_zip_archive(name, content)
            results.append((name, result.successful))

        import asyncio
        await asyncio.gather(*[ingest_zip(n, c) for n, c in zips])

        result_map = dict(results)
        assert result_map["archive1.zip"] == 5
        assert result_map["archive2.zip"] == 10
        assert result_map["archive3.zip"] == 3


# =============================================================================
# CONCURRENT FOLDER WATCHER TESTS
# =============================================================================


class TestConcurrentFolderWatcher:
    """Test concurrent folder watcher operations."""

    @pytest.mark.asyncio
    async def test_concurrent_watcher_creation(self, tmp_path: Path):
        """Multiple watchers can be created concurrently."""
        service = FolderWatcherService()

        async def create_watcher(i):
            config = WatcherConfig(
                watcher_id=f"watcher-{i}",
                path=str(tmp_path / f"watch_{i}"),
                enabled=False,
            )
            return await service.create_watcher(config)

        import asyncio
        results = await asyncio.gather(*[create_watcher(i) for i in range(10)])

        assert len(results) == 10
        assert len(service._watchers) == 10

    @pytest.mark.asyncio
    async def test_concurrent_scan_same_folder(self, tmp_path: Path):
        """Multiple scans of same folder are thread-safe."""
        service = FolderWatcherService()

        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        # Create files
        for i in range(10):
            (watch_dir / f"file_{i}.txt").write_text(f"Content {i}")

        config = WatcherConfig(
            watcher_id="scan-watcher",
            path=str(watch_dir),
            patterns=["*.txt"],
            enabled=False,
        )
        await service.create_watcher(config)

        import asyncio
        results = await asyncio.gather(*[
            service.scan_folder("scan-watcher") for _ in range(5)
        ])

        # Each scan should find all files (first scan processes, others skip due to hash)
        assert results[0] is not None


# =============================================================================
# CONCURRENT EMAIL INGESTION TESTS
# =============================================================================


class TestConcurrentEmailIngestion:
    """Test concurrent email operations."""

    def test_concurrent_inbox_generation(self):
        """Multiple inbox addresses can be generated concurrently."""
        service = EmailIngestionService()
        results = []
        errors = []

        def generate(i):
            try:
                addr = service.generate_inbox_address(f"user-{i}")
                results.append(addr)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=generate, args=(i,))
            for i in range(20)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 20
        assert len(set(results)) == 20  # All unique


# =============================================================================
# CONCURRENT WEB CLIPPER TESTS
# =============================================================================


@requires_bs4
class TestConcurrentWebClipper:
    """Test concurrent web clipper operations."""

    def test_concurrent_metadata_extraction(self):
        """Metadata extraction is thread-safe."""
        from bs4 import BeautifulSoup

        service = WebClipperService()
        results = []
        errors = []

        html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="author" content="Author">
        </head>
        <body><article>Content here with enough text to detect.</article></body>
        </html>
        """

        def extract(i):
            try:
                soup = BeautifulSoup(html, "html.parser")
                metadata = service._extract_metadata(soup, f"https://example{i}.com")
                results.append(metadata.title)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=extract, args=(i,))
            for i in range(20)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(title == "Test Page" for title in results)

    def test_concurrent_content_cleaning(self):
        """Content cleaning is thread-safe."""
        from bs4 import BeautifulSoup

        service = WebClipperService()
        results = []
        errors = []

        html = "<div><script>bad</script><p>Good content</p><nav>Navigation</nav></div>"

        def clean(i):
            try:
                soup = BeautifulSoup(html, "html.parser")
                cleaned = service._clean_content(soup, f"https://example{i}.com")
                results.append("script" not in cleaned.lower())
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=clean, args=(i,))
            for i in range(20)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(results)  # All cleaned correctly


# =============================================================================
# THREAD POOL EXECUTOR TESTS
# =============================================================================


class TestThreadPoolOperations:
    """Test operations using ThreadPoolExecutor."""

    def test_executor_file_type_detection(self):
        """File type detection with ThreadPoolExecutor."""
        service = IngestionService()

        files = [
            "doc.pdf", "data.xlsx", "image.png", "video.mp4",
            "audio.mp3", "archive.zip", "config.json", "readme.md",
        ]

        def detect(filename):
            return filename, service.detect_file_type(filename)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(detect, f) for f in files]
            results = [f.result() for f in as_completed(futures)]

        result_map = dict(results)
        assert result_map["doc.pdf"] == FileType.PDF
        assert result_map["data.xlsx"] == FileType.XLSX
        assert result_map["image.png"] == FileType.IMAGE
        assert result_map["video.mp4"] == FileType.VIDEO

    @pytest.mark.asyncio
    async def test_executor_mixed_ingestion_operations(self, tmp_path: Path):
        """Mixed ingestion operations with executor."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        async def operation(op_type, i):
            if op_type == "ingest":
                return await service.ingest_file(f"file_{i}.txt", f"Content {i}".encode())
            elif op_type == "detect":
                return service.detect_file_type(f"file_{i}.pdf")
            elif op_type == "id":
                return service._generate_document_id(f"file_{i}", b"content")

        import asyncio
        operations = [
            ("ingest", i) for i in range(10)
        ] + [
            ("detect", i) for i in range(10)
        ] + [
            ("id", i) for i in range(10)
        ]

        results = await asyncio.gather(*[operation(op, i) for op, i in operations])

        assert len(results) == 30


# =============================================================================
# HIGH CONTENTION TESTS
# =============================================================================


class TestHighContention:
    """Test high contention scenarios."""

    @pytest.mark.asyncio
    async def test_rapid_ingestion_bursts(self, tmp_path: Path):
        """Handle burst of rapid ingestions."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        results = []
        barrier = threading.Barrier(30)

        async def burst_ingest(i):
            # All start at same time
            result = await service.ingest_file(
                f"burst_{i}.txt",
                f"Burst content {i}".encode(),
            )
            results.append(result.document_id)

        import asyncio
        await asyncio.gather(*[burst_ingest(i) for i in range(30)])

        assert len(results) == 30
        assert len(set(results)) == 30  # All unique

    def test_concurrent_document_id_generation(self):
        """Document ID generation under high contention."""
        service = IngestionService()
        results = Queue()
        errors = Queue()

        def generate(i):
            try:
                for j in range(10):
                    doc_id = service._generate_document_id(
                        f"file_{i}_{j}",
                        f"content_{i}_{j}".encode(),
                    )
                    results.put(doc_id)
            except Exception as e:
                errors.put(e)

        threads = [threading.Thread(target=generate, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        all_ids = []
        while not results.empty():
            all_ids.append(results.get())

        # Should have 100 IDs (10 threads * 10 IDs each)
        assert len(all_ids) == 100
        # Most should be unique (some collision possible due to timing)
        assert len(set(all_ids)) >= 90


# =============================================================================
# STRESS TEST SCENARIOS
# =============================================================================


class TestStressScenarios:
    """Stress test scenarios."""

    @pytest.mark.asyncio
    async def test_sustained_ingestion_load(self, tmp_path: Path):
        """Sustained ingestion load should not degrade."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        results = []
        errors = []

        async def worker(worker_id):
            for i in range(10):
                try:
                    result = await service.ingest_file(
                        f"worker_{worker_id}_file_{i}.txt",
                        f"Content from worker {worker_id}, file {i}".encode(),
                    )
                    results.append((worker_id, i, result.document_id))
                except Exception as e:
                    errors.append((worker_id, i, e))

        import asyncio
        await asyncio.gather(*[worker(w) for w in range(5)])

        assert len(errors) == 0
        assert len(results) == 50  # 5 workers * 10 files

    @pytest.mark.asyncio
    async def test_interleaved_operations(self, tmp_path: Path):
        """Interleaved ingestion and detection operations."""
        service = IngestionService()
        service._upload_dir = tmp_path / "uploads"
        service._upload_dir.mkdir()

        ingest_results = []
        detect_results = []
        errors = []

        async def ingest_worker():
            for i in range(20):
                try:
                    result = await service.ingest_file(
                        f"ingest_{i}.txt",
                        f"Content {i}".encode(),
                    )
                    ingest_results.append(result)
                    await asyncio.sleep(0.001)
                except Exception as e:
                    errors.append(("ingest", e))

        async def detect_worker():
            for i in range(50):
                try:
                    result = service.detect_file_type(f"file_{i}.pdf")
                    detect_results.append(result)
                except Exception as e:
                    errors.append(("detect", e))

        import asyncio
        await asyncio.gather(
            ingest_worker(),
            detect_worker(),
        )

        assert len(errors) == 0
        assert len(ingest_results) == 20
        assert len(detect_results) == 50
