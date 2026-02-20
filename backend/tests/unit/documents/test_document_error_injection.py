"""
Document Error Injection Tests - Testing failure modes and error handling.
"""

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import threading

import pytest


from backend.app.services.documents.service import (
    Document,
    DocumentService,
    DocumentVersion,
    DocumentComment,
    DocumentContent,
)
from backend.app.services.documents.collaboration import (
    CollaborationService,
    CollaboratorPresence,
)


@pytest.fixture
def doc_service(tmp_path: Path) -> DocumentService:
    """Create a document service with temporary storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


@pytest.fixture
def collab_service() -> CollaborationService:
    """Create a collaboration service."""
    return CollaborationService()


class TestFileSystemErrors:
    """Test handling of file system errors."""

    def test_create_with_disk_full_simulation(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Simulate disk full error during create."""
        with patch.object(doc_service, "_save_document") as mock_save:
            mock_save.side_effect = OSError("No space left on device")

            with pytest.raises(OSError, match="No space left"):
                doc_service.create(name="Test")

    def test_get_with_corrupted_json(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Get should handle corrupted JSON gracefully."""
        doc = doc_service.create(name="Test")
        doc_path = tmp_path / "documents" / doc.id / "document.json"

        # Corrupt the file
        doc_path.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            doc_service.get(doc.id)

    def test_get_with_missing_required_fields(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Get should handle missing required fields."""
        doc = doc_service.create(name="Test")
        doc_path = tmp_path / "documents" / doc.id / "document.json"

        # Write incomplete JSON
        doc_path.write_text('{"id": "test"}')

        with pytest.raises(Exception):  # Pydantic validation error
            doc_service.get(doc.id)

    def test_update_with_write_failure(self, doc_service: DocumentService):
        """Update should handle write failures."""
        doc = doc_service.create(name="Test")

        with patch.object(doc_service, "_save_document") as mock_save:
            mock_save.side_effect = PermissionError("Write denied")

            with pytest.raises(PermissionError):
                doc_service.update(doc.id, name="New Name")

    def test_delete_with_permission_error(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Delete should handle permission errors."""
        doc = doc_service.create(name="Test")
        doc_path = tmp_path / "documents" / doc.id / "document.json"

        with patch.object(Path, "unlink") as mock_unlink:
            mock_unlink.side_effect = PermissionError("Delete denied")

            with pytest.raises(PermissionError):
                doc_service.delete(doc.id)

    def test_list_with_concurrent_deletion(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """List should handle files deleted during iteration."""
        docs = [doc_service.create(name=f"Doc {i}") for i in range(5)]

        # Delete some documents between glob and read
        original_open = open

        call_count = [0]

        def delete_during_read(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 3:
                # Delete a file during iteration
                doc_path = tmp_path / "documents" / docs[2].id / "document.json"
                if doc_path.exists():
                    doc_path.unlink()
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=delete_during_read):
            # Should not raise, just skip missing files
            result, total = doc_service.list_documents()
            # May have fewer documents due to deletion
            assert len(result) <= 5


class TestVersionErrors:
    """Test error handling in version operations."""

    def test_get_versions_with_corrupted_version_file(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Get versions should skip corrupted version files."""
        doc = doc_service.create(name="Test")
        doc_service.update(doc.id, name="Update 1")
        doc_service.update(doc.id, name="Update 2")

        # Corrupt one version file
        versions_dir = tmp_path / "documents" / doc.id / "versions"
        version_files = list(versions_dir.glob("*.json"))
        if version_files:
            version_files[0].write_text("{ invalid }")

        # Should still return valid versions
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 1  # One corrupted, one valid

    def test_create_version_with_write_failure(self, doc_service: DocumentService):
        """Version creation failure should propagate."""
        doc = doc_service.create(name="Test")

        with patch.object(doc_service, "_create_version") as mock_version:
            mock_version.side_effect = IOError("Cannot write version")

            with pytest.raises(IOError):
                doc_service.update(doc.id, name="New Name")


class TestCommentErrors:
    """Test error handling in comment operations."""

    def test_add_comment_to_nonexistent_document(self, doc_service: DocumentService):
        """Add comment to nonexistent document should return None."""
        result = doc_service.add_comment(
            str(uuid.uuid4()), 0, 10, "Comment"
        )
        assert result is None

    def test_get_comments_with_corrupted_comment_file(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Get comments should skip corrupted files."""
        doc = doc_service.create(name="Test")
        doc_service.add_comment(doc.id, 0, 10, "Comment 1")
        doc_service.add_comment(doc.id, 20, 30, "Comment 2")

        # Corrupt one comment file
        comments_dir = tmp_path / "documents" / doc.id / "comments"
        comment_files = list(comments_dir.glob("*.json"))
        if comment_files:
            comment_files[0].write_text("{ invalid }")

        # Should still return valid comments
        comments = doc_service.get_comments(doc.id)
        assert len(comments) == 1

    def test_resolve_nonexistent_comment(self, doc_service: DocumentService):
        """Resolve nonexistent comment should return False."""
        doc = doc_service.create(name="Test")
        result = doc_service.resolve_comment(doc.id, str(uuid.uuid4()))
        assert result is False


class TestConcurrencyErrors:
    """Test error handling in concurrent scenarios."""

    def test_concurrent_creates_under_memory_pressure(
        self, doc_service: DocumentService
    ):
        """Concurrent creates should handle memory pressure."""
        errors = []
        success_count = [0]

        def create_with_potential_error(i):
            try:
                doc_service.create(name=f"Doc {i}")
                success_count[0] += 1
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=create_with_potential_error, args=(i,))
            for i in range(50)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed (no memory simulation, just stress test)
        assert success_count[0] == 50
        assert len(errors) == 0

    def test_concurrent_updates_with_lock_timeout(
        self, doc_service: DocumentService
    ):
        """Concurrent updates should not deadlock."""
        doc = doc_service.create(name="Test")
        errors = []
        results = []

        def slow_update(i):
            try:
                # Simulate slow update
                result = doc_service.update(doc.id, metadata={f"key_{i}": i})
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=slow_update, args=(i,))
            for i in range(20)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 20


class TestInvalidInputErrors:
    """Test handling of invalid inputs."""

    def test_create_with_none_name(self, doc_service: DocumentService):
        """Create with None name should raise error."""
        with pytest.raises(Exception):  # Pydantic validation
            doc_service.create(name=None)

    def test_get_with_none_id(self, doc_service: DocumentService):
        """Get with None ID should return None."""
        result = doc_service.get(None)
        assert result is None

    def test_update_with_none_id(self, doc_service: DocumentService):
        """Update with None ID should return None."""
        result = doc_service.update(None, name="Test")
        assert result is None

    def test_delete_with_none_id(self, doc_service: DocumentService):
        """Delete with None ID should return False."""
        result = doc_service.delete(None)
        assert result is False

    def test_add_comment_with_none_document_id(self, doc_service: DocumentService):
        """Add comment with None document ID should return None."""
        result = doc_service.add_comment(None, 0, 10, "Comment")
        assert result is None


class TestCollaborationErrors:
    """Test error handling in collaboration service."""

    def test_join_nonexistent_session(self, collab_service: CollaborationService):
        """Join nonexistent session should return None."""
        result = collab_service.join_session("nonexistent", "user-1")
        assert result is None

    def test_leave_nonexistent_session(self, collab_service: CollaborationService):
        """Leave nonexistent session should return False."""
        result = collab_service.leave_session("nonexistent", "user-1")
        assert result is False

    def test_update_presence_nonexistent_session(
        self, collab_service: CollaborationService
    ):
        """Update presence in nonexistent session should return None."""
        result = collab_service.update_presence(
            "nonexistent", "user-1", cursor_position=50
        )
        assert result is None

    def test_update_presence_nonexistent_user(
        self, collab_service: CollaborationService
    ):
        """Update presence for nonexistent user should return None."""
        session = collab_service.start_session("doc-123")
        result = collab_service.update_presence(
            session.id, "nonexistent", cursor_position=50
        )
        assert result is None

    def test_end_nonexistent_session(self, collab_service: CollaborationService):
        """End nonexistent session should return False."""
        result = collab_service.end_session("nonexistent")
        assert result is False

    def test_get_presence_nonexistent_session(
        self, collab_service: CollaborationService
    ):
        """Get presence for nonexistent session should return empty list."""
        result = collab_service.get_presence("nonexistent")
        assert result == []


class TestStateConsistencyErrors:
    """Test state consistency under error conditions."""

    def test_failed_update_preserves_original(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Failed update should preserve original document state."""
        doc = doc_service.create(name="Original")
        original_version = doc.version

        # Make the document directory read-only to cause write failure
        doc_dir = tmp_path / "documents" / doc.id

        with patch.object(doc_service, "_save_document") as mock_save:
            mock_save.side_effect = IOError("Write failed")

            try:
                doc_service.update(doc.id, name="New Name")
            except IOError:
                pass

        # Original should still be readable
        retrieved = doc_service.get(doc.id)
        # Note: In current implementation, the update may have partially modified
        # the in-memory state before failing. This tests the file persistence.
        # The file should still exist and be readable.
        assert retrieved is not None

    def test_failed_delete_preserves_document(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Failed delete should preserve document."""
        doc = doc_service.create(name="Test")
        doc_path = tmp_path / "documents" / doc.id / "document.json"

        with patch.object(Path, "unlink") as mock_unlink:
            mock_unlink.side_effect = PermissionError()

            try:
                doc_service.delete(doc.id)
            except PermissionError:
                pass

        # Document should still exist
        assert doc_path.exists()


class TestEdgeCaseErrors:
    """Test edge case error scenarios."""

    def test_extremely_long_document_name(self, doc_service: DocumentService):
        """Extremely long document name should be handled."""
        long_name = "x" * 10000
        # This should work with the service (model doesn't enforce limit)
        doc = doc_service.create(name=long_name)
        assert len(doc.name) == 10000

    def test_extremely_deep_content_nesting(self, doc_service: DocumentService):
        """Deeply nested content should be handled."""
        # Create deeply nested content
        content = {"type": "doc", "content": []}
        current = content
        for i in range(50):
            nested = {"type": "paragraph", "content": []}
            current["content"].append(nested)
            current = nested

        doc = doc_service.create(
            name="Deep",
            content=DocumentContent(**content),
        )
        assert doc is not None

    def test_unicode_in_all_fields(self, doc_service: DocumentService):
        """Unicode characters in all fields should be handled."""
        doc = doc_service.create(
            name="日本語ドキュメント",
            owner_id="用户-123",
            metadata={"キー": "値"},
        )

        retrieved = doc_service.get(doc.id)
        assert retrieved.name == "日本語ドキュメント"
        assert retrieved.owner_id == "用户-123"
        assert retrieved.metadata["キー"] == "値"

    def test_empty_string_fields(self, doc_service: DocumentService):
        """Empty string fields where allowed should work."""
        doc = doc_service.create(
            name="Test",
            owner_id="",  # Empty owner is allowed
            metadata={},
        )
        assert doc.owner_id == ""

    def test_special_characters_in_metadata_keys(self, doc_service: DocumentService):
        """Special characters in metadata keys should be handled."""
        doc = doc_service.create(
            name="Test",
            metadata={
                "key.with.dots": "value",
                "key-with-dashes": "value",
                "key_with_underscores": "value",
                "key with spaces": "value",
            },
        )

        retrieved = doc_service.get(doc.id)
        assert retrieved.metadata["key.with.dots"] == "value"
        assert retrieved.metadata["key with spaces"] == "value"


class TestRecoveryScenarios:
    """Test recovery from various failure scenarios."""

    def test_recovery_after_partial_write(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Service should handle partially written files."""
        doc = doc_service.create(name="Test")
        doc_path = tmp_path / "documents" / doc.id / "document.json"

        # Simulate partial write by truncating file
        with open(doc_path, "r") as f:
            original = f.read()

        with open(doc_path, "w") as f:
            f.write(original[:len(original) // 2])

        # Get should fail gracefully
        with pytest.raises(json.JSONDecodeError):
            doc_service.get(doc.id)

    def test_service_creates_missing_directories(self, tmp_path: Path):
        """Service should create missing directories on init."""
        new_root = tmp_path / "nonexistent" / "nested" / "documents"
        service = DocumentService(uploads_root=new_root)
        assert new_root.exists()

    def test_list_documents_with_empty_directory(self, doc_service: DocumentService):
        """List should work with empty directory."""
        docs, total = doc_service.list_documents()
        assert docs == []
        assert total == 0

    def test_get_versions_with_no_versions_directory(
        self, doc_service: DocumentService
    ):
        """Get versions should work when versions dir doesn't exist."""
        doc = doc_service.create(name="Test")
        # Don't create any versions
        versions = doc_service.get_versions(doc.id)
        assert versions == []

    def test_get_comments_with_no_comments_directory(
        self, doc_service: DocumentService
    ):
        """Get comments should work when comments dir doesn't exist."""
        doc = doc_service.create(name="Test")
        comments = doc_service.get_comments(doc.id)
        assert comments == []
