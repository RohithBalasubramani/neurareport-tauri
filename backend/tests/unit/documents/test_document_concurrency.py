"""
Document Concurrency Tests - Testing thread safety and concurrent operations.
"""

import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from queue import Queue

import pytest


from backend.app.services.documents.service import (
    Document,
    DocumentService,
    DocumentContent,
)
from backend.app.services.documents.collaboration import (
    CollaborationService,
)


@pytest.fixture
def doc_service(tmp_path: Path) -> DocumentService:
    """Create a document service with temporary storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


@pytest.fixture
def collab_service() -> CollaborationService:
    """Create a collaboration service."""
    return CollaborationService()


class TestConcurrentDocumentCreation:
    """Test concurrent document creation scenarios."""

    def test_many_concurrent_creates(self, doc_service: DocumentService):
        """Many concurrent creates should all succeed."""
        num_docs = 50
        results = []
        errors = []

        def create_doc(i):
            try:
                doc = doc_service.create(name=f"Document {i}")
                results.append(doc.id)
            except Exception as e:
                errors.append((i, e))

        threads = [
            threading.Thread(target=create_doc, args=(i,))
            for i in range(num_docs)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == num_docs
        assert len(set(results)) == num_docs  # All unique IDs

    def test_rapid_create_delete_cycles(self, doc_service: DocumentService):
        """Rapid create-delete cycles should not cause issues."""
        num_cycles = 30
        results = []
        errors = []

        def create_and_delete(i):
            try:
                doc = doc_service.create(name=f"Temp Doc {i}")
                results.append(("create", doc.id))
                success = doc_service.delete(doc.id)
                results.append(("delete", success))
            except Exception as e:
                errors.append((i, e))

        threads = [
            threading.Thread(target=create_and_delete, args=(i,))
            for i in range(num_cycles)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        creates = [r for r in results if r[0] == "create"]
        deletes = [r for r in results if r[0] == "delete"]
        assert len(creates) == num_cycles
        assert all(d[1] is True for d in deletes)


class TestConcurrentDocumentUpdates:
    """Test concurrent document update scenarios."""

    def test_concurrent_updates_same_document(self, doc_service: DocumentService):
        """Concurrent updates to same document should serialize correctly."""
        doc = doc_service.create(name="Concurrent Doc")
        num_updates = 30
        results = []
        errors = []

        def update_doc(i):
            try:
                updated = doc_service.update(
                    doc.id,
                    metadata={f"update_{i}": i},
                )
                results.append(updated.version)
            except Exception as e:
                errors.append((i, e))

        threads = [
            threading.Thread(target=update_doc, args=(i,))
            for i in range(num_updates)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        final = doc_service.get(doc.id)
        assert final.version == 1 + num_updates

    def test_concurrent_updates_different_documents(self, doc_service: DocumentService):
        """Concurrent updates to different documents should not interfere."""
        docs = [doc_service.create(name=f"Doc {i}") for i in range(10)]
        results = []
        errors = []

        def update_doc(doc_index):
            try:
                for j in range(5):
                    doc = doc_service.update(
                        docs[doc_index].id,
                        name=f"Updated {doc_index}-{j}",
                    )
                results.append((doc_index, doc.version))
            except Exception as e:
                errors.append((doc_index, e))

        threads = [
            threading.Thread(target=update_doc, args=(i,))
            for i in range(len(docs))
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"

        # Each document should have version 6 (1 + 5 updates)
        for doc in docs:
            final = doc_service.get(doc.id)
            assert final.version == 6

    def test_interleaved_read_write(self, doc_service: DocumentService):
        """Interleaved reads and writes should not corrupt data."""
        doc = doc_service.create(name="Test")
        reads = []
        writes = []
        errors = []

        def reader():
            for _ in range(20):
                try:
                    result = doc_service.get(doc.id)
                    reads.append(result.version if result else None)
                    time.sleep(0.001)
                except Exception as e:
                    errors.append(("read", e))

        def writer():
            for i in range(10):
                try:
                    result = doc_service.update(doc.id, metadata={f"w_{i}": i})
                    writes.append(result.version if result else None)
                    time.sleep(0.002)
                except Exception as e:
                    errors.append(("write", e))

        reader_threads = [threading.Thread(target=reader) for _ in range(3)]
        writer_threads = [threading.Thread(target=writer) for _ in range(2)]

        all_threads = reader_threads + writer_threads
        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()

        assert len(errors) == 0, f"Errors: {errors}"
        # All reads should return valid version numbers
        assert all(r is not None for r in reads)


class TestConcurrentVersioning:
    """Test concurrent version operations."""

    def test_concurrent_version_creation(self, doc_service: DocumentService):
        """Concurrent updates should create versions correctly."""
        doc = doc_service.create(name="Versioned")
        num_updates = 20
        errors = []

        def update_doc(i):
            try:
                doc_service.update(doc.id, metadata={f"v_{i}": i})
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=update_doc, args=(i,))
            for i in range(num_updates)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == num_updates

    def test_concurrent_version_reads(self, doc_service: DocumentService):
        """Concurrent version reads should not cause issues."""
        doc = doc_service.create(name="Doc")
        for i in range(10):
            doc_service.update(doc.id, name=f"Update {i}")

        results = []
        errors = []

        def read_versions():
            try:
                versions = doc_service.get_versions(doc.id)
                results.append(len(versions))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_versions) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(r == 10 for r in results)


class TestConcurrentComments:
    """Test concurrent comment operations."""

    def test_concurrent_comment_adds(self, doc_service: DocumentService):
        """Concurrent comment additions should all succeed."""
        doc = doc_service.create(name="Doc")
        num_comments = 30
        results = []
        errors = []

        def add_comment(i):
            try:
                comment = doc_service.add_comment(
                    doc.id, i * 10, i * 10 + 5, f"Comment {i}"
                )
                results.append(comment.id if comment else None)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=add_comment, args=(i,))
            for i in range(num_comments)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(r is not None for r in results)

        comments = doc_service.get_comments(doc.id)
        assert len(comments) == num_comments

    def test_concurrent_comment_resolution(self, doc_service: DocumentService):
        """Concurrent comment resolutions should work correctly."""
        doc = doc_service.create(name="Doc")
        comments = [
            doc_service.add_comment(doc.id, i * 10, i * 10 + 5, f"Comment {i}")
            for i in range(10)
        ]

        results = []
        errors = []

        def resolve_comment(comment_id):
            try:
                success = doc_service.resolve_comment(doc.id, comment_id)
                results.append(success)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=resolve_comment, args=(c.id,))
            for c in comments
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(results)

        final_comments = doc_service.get_comments(doc.id)
        assert all(c.resolved for c in final_comments)


class TestConcurrentCollaboration:
    """Test concurrent collaboration operations."""

    def test_concurrent_session_joins(self, collab_service: CollaborationService):
        """Concurrent session joins should all succeed."""
        session = collab_service.start_session("doc-123")
        num_users = 30
        results = []
        errors = []

        def join_session(i):
            try:
                presence = collab_service.join_session(
                    session.id, f"user-{i}", f"User {i}"
                )
                results.append(presence.user_id if presence else None)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=join_session, args=(i,))
            for i in range(num_users)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(r is not None for r in results)

        updated = collab_service.get_session(session.id)
        assert len(updated.participants) == num_users

    def test_concurrent_presence_updates(self, collab_service: CollaborationService):
        """Concurrent presence updates should not cause issues."""
        session = collab_service.start_session("doc-123", user_id="user-1")
        num_updates = 50
        errors = []

        def update_presence(i):
            try:
                collab_service.update_presence(
                    session.id, "user-1", cursor_position=i * 10
                )
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=update_presence, args=(i,))
            for i in range(num_updates)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_concurrent_join_leave_cycles(self, collab_service: CollaborationService):
        """Concurrent join-leave cycles should not cause issues."""
        session = collab_service.start_session("doc-123")
        num_users = 20
        results = []
        errors = []

        def join_and_leave(i):
            try:
                user_id = f"user-{i}"
                collab_service.join_session(session.id, user_id)
                results.append(("join", user_id))
                time.sleep(0.01)
                collab_service.leave_session(session.id, user_id)
                results.append(("leave", user_id))
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=join_and_leave, args=(i,))
            for i in range(num_users)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestThreadPoolExecutor:
    """Test using ThreadPoolExecutor for concurrent operations."""

    def test_executor_document_operations(self, doc_service: DocumentService):
        """Test document operations with ThreadPoolExecutor."""
        def create_and_update(i):
            doc = doc_service.create(name=f"Executor Doc {i}")
            for j in range(3):
                doc = doc_service.update(doc.id, metadata={f"key_{j}": j})
            return doc.id, doc.version

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_and_update, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]

        assert len(results) == 20
        assert all(version == 4 for _, version in results)  # 1 + 3 updates

    def test_executor_mixed_operations(self, doc_service: DocumentService):
        """Test mixed operations with ThreadPoolExecutor."""
        # Create some initial documents
        docs = [doc_service.create(name=f"Base Doc {i}") for i in range(5)]

        operations = []

        def update_op(doc_id, value):
            return doc_service.update(doc_id, metadata={"value": value})

        def read_op(doc_id):
            return doc_service.get(doc_id)

        def comment_op(doc_id, text):
            return doc_service.add_comment(doc_id, 0, 10, text)

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for i in range(50):
                doc_id = docs[i % len(docs)].id
                if i % 3 == 0:
                    futures.append(executor.submit(update_op, doc_id, i))
                elif i % 3 == 1:
                    futures.append(executor.submit(read_op, doc_id))
                else:
                    futures.append(executor.submit(comment_op, doc_id, f"Comment {i}"))

            results = [f.result() for f in as_completed(futures)]

        # All operations should succeed (no None except for some edge cases)
        assert len(results) == 50


class TestStressScenarios:
    """Stress test scenarios for edge cases."""

    def test_high_contention_single_document(self, doc_service: DocumentService):
        """High contention on single document should not deadlock."""
        doc = doc_service.create(name="Contention Test")
        results = Queue()
        errors = Queue()
        stop_flag = threading.Event()

        def worker(worker_id):
            ops = 0
            while not stop_flag.is_set() and ops < 10:
                try:
                    doc_service.update(doc.id, metadata={f"worker_{worker_id}": ops})
                    ops += 1
                except Exception as e:
                    errors.put((worker_id, e))
                    break
            results.put((worker_id, ops))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()

        # Let threads run
        time.sleep(1)
        stop_flag.set()

        for t in threads:
            t.join(timeout=5)

        # Check for deadlocks (threads should have completed)
        assert all(not t.is_alive() for t in threads)

        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())

        all_errors = []
        while not errors.empty():
            all_errors.append(errors.get())

        assert len(all_errors) == 0, f"Errors: {all_errors}"

    def test_burst_traffic(self, doc_service: DocumentService):
        """Handle burst of traffic without failures."""
        results = []
        errors = []
        barrier = threading.Barrier(50)

        def burst_create(i):
            try:
                barrier.wait(timeout=5)  # All threads start at same time
                doc = doc_service.create(name=f"Burst Doc {i}")
                results.append(doc.id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=burst_create, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 50
        assert len(set(results)) == 50
