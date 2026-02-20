"""
Document Service Tests - Testing DocumentService CRUD operations.
"""

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock
import threading
import time

import pytest


from backend.app.services.documents.service import (
    Document,
    DocumentService,
    DocumentVersion,
    DocumentComment,
    DocumentContent,
    _utcnow,
)


@pytest.fixture
def doc_service(tmp_path: Path) -> DocumentService:
    """Create a document service with temporary storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


@pytest.fixture
def sample_content() -> dict:
    """Sample TipTap document content."""
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello, world!"}],
            }
        ],
    }


class TestDocumentCreate:
    """Test document creation."""

    def test_create_document_minimal(self, doc_service: DocumentService):
        """Create document with minimal fields."""
        doc = doc_service.create(name="Test Document")
        assert doc.id is not None
        assert doc.name == "Test Document"
        assert doc.version == 1
        # Content may be DocumentContent model or dict
        content = doc.content if isinstance(doc.content, dict) else doc.content.model_dump()
        assert content["type"] == "doc"

    def test_create_document_with_content(
        self, doc_service: DocumentService, sample_content: dict
    ):
        """Create document with content."""
        doc = doc_service.create(
            name="With Content",
            content=DocumentContent(**sample_content),
        )
        content = doc.content if isinstance(doc.content, dict) else doc.content.model_dump()
        assert content["content"][0]["type"] == "paragraph"

    def test_create_document_with_owner(self, doc_service: DocumentService):
        """Create document with owner ID."""
        doc = doc_service.create(name="Owned Doc", owner_id="user-123")
        assert doc.owner_id == "user-123"

    def test_create_document_as_template(self, doc_service: DocumentService):
        """Create document as template."""
        doc = doc_service.create(name="Template", is_template=True)
        assert doc.is_template is True

    def test_create_document_with_metadata(self, doc_service: DocumentService):
        """Create document with metadata."""
        doc = doc_service.create(
            name="With Metadata",
            metadata={"category": "report", "priority": "high"},
        )
        assert doc.metadata["category"] == "report"
        assert doc.metadata["priority"] == "high"

    def test_create_document_generates_unique_ids(self, doc_service: DocumentService):
        """Each document should have unique ID."""
        docs = [doc_service.create(name=f"Doc {i}") for i in range(10)]
        ids = [d.id for d in docs]
        assert len(set(ids)) == 10

    def test_create_document_persists_to_disk(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Created document should be saved to disk."""
        doc = doc_service.create(name="Persisted")
        doc_path = tmp_path / "documents" / doc.id / "document.json"
        assert doc_path.exists()
        with open(doc_path) as f:
            data = json.load(f)
        assert data["name"] == "Persisted"

    def test_create_document_timestamps_set(self, doc_service: DocumentService):
        """Created document should have timestamps."""
        doc = doc_service.create(name="Timestamped")
        assert doc.created_at is not None
        assert doc.updated_at is not None
        assert doc.created_at == doc.updated_at

    def test_create_document_with_none_content(self, doc_service: DocumentService):
        """Create document with None content should use default."""
        doc = doc_service.create(name="No Content", content=None)
        content = doc.content if isinstance(doc.content, dict) else doc.content.model_dump()
        assert content == {"type": "doc", "content": []}

    def test_create_document_with_unicode_name(self, doc_service: DocumentService):
        """Create document with unicode name."""
        doc = doc_service.create(name="日本語ドキュメント")
        assert doc.name == "日本語ドキュメント"

    def test_create_document_with_special_characters(self, doc_service: DocumentService):
        """Create document with special characters in content."""
        content = {
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Special: <>&\"'"}]}
            ],
        }
        doc = doc_service.create(name="Special", content=DocumentContent(**content))
        assert "<>&" in str(doc.content)


class TestDocumentGet:
    """Test document retrieval."""

    def test_get_existing_document(self, doc_service: DocumentService):
        """Get existing document by ID."""
        created = doc_service.create(name="To Retrieve")
        retrieved = doc_service.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "To Retrieve"

    def test_get_nonexistent_document(self, doc_service: DocumentService):
        """Get nonexistent document returns None."""
        result = doc_service.get(str(uuid.uuid4()))
        assert result is None

    def test_get_with_invalid_id(self, doc_service: DocumentService):
        """Get with invalid ID format returns None."""
        result = doc_service.get("not-a-valid-uuid")
        assert result is None

    def test_get_with_empty_id(self, doc_service: DocumentService):
        """Get with empty ID returns None."""
        result = doc_service.get("")
        assert result is None

    def test_get_preserves_all_fields(self, doc_service: DocumentService):
        """Retrieved document should have all original fields."""
        created = doc_service.create(
            name="Full Fields",
            owner_id="user-123",
            is_template=True,
            metadata={"key": "value"},
        )
        retrieved = doc_service.get(created.id)
        assert retrieved.owner_id == "user-123"
        assert retrieved.is_template is True
        assert retrieved.metadata["key"] == "value"

    def test_get_after_file_deleted(self, doc_service: DocumentService, tmp_path: Path):
        """Get after file deleted returns None."""
        doc = doc_service.create(name="To Delete")
        doc_path = tmp_path / "documents" / doc.id / "document.json"
        doc_path.unlink()
        result = doc_service.get(doc.id)
        assert result is None


class TestDocumentUpdate:
    """Test document updates."""

    def test_update_document_name(self, doc_service: DocumentService):
        """Update document name."""
        doc = doc_service.create(name="Original Name")
        updated = doc_service.update(doc.id, name="New Name")
        assert updated is not None
        assert updated.name == "New Name"

    def test_update_document_content(
        self, doc_service: DocumentService, sample_content: dict
    ):
        """Update document content."""
        doc = doc_service.create(name="Doc")
        updated = doc_service.update(
            doc.id, content=DocumentContent(**sample_content)
        )
        content = updated.content if isinstance(updated.content, dict) else updated.content.model_dump()
        assert content["content"][0]["type"] == "paragraph"

    def test_update_document_metadata(self, doc_service: DocumentService):
        """Update document metadata merges with existing."""
        doc = doc_service.create(name="Doc", metadata={"a": 1})
        updated = doc_service.update(doc.id, metadata={"b": 2})
        assert updated.metadata["a"] == 1
        assert updated.metadata["b"] == 2

    def test_update_increments_version(self, doc_service: DocumentService):
        """Update should increment version number."""
        doc = doc_service.create(name="Doc")
        assert doc.version == 1
        updated = doc_service.update(doc.id, name="Updated")
        assert updated.version == 2

    def test_update_creates_version_snapshot(self, doc_service: DocumentService):
        """Update should create version snapshot."""
        doc = doc_service.create(name="Doc")
        doc_service.update(doc.id, name="Updated")
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 1
        assert versions[0].version == 1

    def test_update_without_version_snapshot(self, doc_service: DocumentService):
        """Update with create_version=False should not create snapshot."""
        doc = doc_service.create(name="Doc")
        doc_service.update(doc.id, name="Updated", create_version=False)
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 0

    def test_update_nonexistent_document(self, doc_service: DocumentService):
        """Update nonexistent document returns None."""
        result = doc_service.update(str(uuid.uuid4()), name="New Name")
        assert result is None

    def test_update_updates_timestamp(self, doc_service: DocumentService):
        """Update should change updated_at timestamp."""
        doc = doc_service.create(name="Doc")
        original_updated = doc.updated_at
        time.sleep(0.01)  # Ensure time passes
        updated = doc_service.update(doc.id, name="Updated")
        assert updated.updated_at != original_updated

    def test_update_preserves_created_at(self, doc_service: DocumentService):
        """Update should not change created_at timestamp."""
        doc = doc_service.create(name="Doc")
        original_created = doc.created_at
        updated = doc_service.update(doc.id, name="Updated")
        assert updated.created_at == original_created

    def test_update_persists_changes(self, doc_service: DocumentService):
        """Updates should be persisted to disk."""
        doc = doc_service.create(name="Doc")
        doc_service.update(doc.id, name="Updated")
        retrieved = doc_service.get(doc.id)
        assert retrieved.name == "Updated"

    def test_multiple_updates(self, doc_service: DocumentService):
        """Multiple updates should work correctly."""
        doc = doc_service.create(name="Doc")
        for i in range(5):
            doc = doc_service.update(doc.id, name=f"Update {i}")
        assert doc.version == 6
        assert doc.name == "Update 4"
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 5


class TestDocumentDelete:
    """Test document deletion."""

    def test_delete_existing_document(self, doc_service: DocumentService):
        """Delete existing document returns True."""
        doc = doc_service.create(name="To Delete")
        result = doc_service.delete(doc.id)
        assert result is True

    def test_delete_removes_from_disk(
        self, doc_service: DocumentService, tmp_path: Path
    ):
        """Delete should remove file from disk."""
        doc = doc_service.create(name="To Delete")
        doc_path = tmp_path / "documents" / doc.id / "document.json"
        assert doc_path.exists()
        doc_service.delete(doc.id)
        assert not doc_path.exists()

    def test_delete_nonexistent_document(self, doc_service: DocumentService):
        """Delete nonexistent document returns False."""
        result = doc_service.delete(str(uuid.uuid4()))
        assert result is False

    def test_delete_with_invalid_id(self, doc_service: DocumentService):
        """Delete with invalid ID returns False."""
        result = doc_service.delete("not-a-uuid")
        assert result is False

    def test_delete_removes_versions(self, doc_service: DocumentService, tmp_path: Path):
        """Delete should also remove version snapshots."""
        doc = doc_service.create(name="Doc")
        doc_service.update(doc.id, name="Updated")
        versions_dir = tmp_path / "documents" / doc.id / "versions"
        assert versions_dir.exists()
        doc_service.delete(doc.id)
        assert not versions_dir.exists()

    def test_delete_removes_comments(self, doc_service: DocumentService, tmp_path: Path):
        """Delete should also remove comments."""
        doc = doc_service.create(name="Doc")
        doc_service.add_comment(doc.id, 0, 10, "Comment")
        comments_dir = tmp_path / "documents" / doc.id / "comments"
        assert comments_dir.exists()
        doc_service.delete(doc.id)
        assert not comments_dir.exists()

    def test_deleted_document_not_retrievable(self, doc_service: DocumentService):
        """Deleted document should not be retrievable."""
        doc = doc_service.create(name="Doc")
        doc_service.delete(doc.id)
        result = doc_service.get(doc.id)
        assert result is None


class TestDocumentList:
    """Test document listing."""

    def test_list_empty(self, doc_service: DocumentService):
        """List with no documents returns empty list."""
        docs, total = doc_service.list_documents()
        assert docs == []
        assert total == 0

    def test_list_all_documents(self, doc_service: DocumentService):
        """List returns all documents."""
        for i in range(5):
            doc_service.create(name=f"Doc {i}")
        docs, total = doc_service.list_documents()
        assert len(docs) == 5
        assert total == 5

    def test_list_filter_by_owner(self, doc_service: DocumentService):
        """List can filter by owner_id."""
        doc_service.create(name="User1 Doc", owner_id="user-1")
        doc_service.create(name="User2 Doc", owner_id="user-2")
        doc_service.create(name="User1 Doc 2", owner_id="user-1")

        docs, total = doc_service.list_documents(owner_id="user-1")
        assert len(docs) == 2
        assert total == 2
        assert all(d.owner_id == "user-1" for d in docs)

    def test_list_filter_by_is_template(self, doc_service: DocumentService):
        """List can filter by is_template."""
        doc_service.create(name="Regular", is_template=False)
        doc_service.create(name="Template", is_template=True)
        doc_service.create(name="Regular 2", is_template=False)

        docs, total = doc_service.list_documents(is_template=True)
        assert len(docs) == 1
        assert docs[0].name == "Template"

    def test_list_filter_by_tags(self, doc_service: DocumentService):
        """List can filter by tags."""
        doc_service.create(name="Doc 1")
        d1 = doc_service.get(doc_service.create(name="Tagged").id)
        # Manually add tags since create doesn't support it directly
        d1.tags = ["important"]
        doc_service._save_document(d1)

        # List with tag filter - documents with any matching tag
        docs, total = doc_service.list_documents(tags=["important"])
        assert len(docs) == 1
        assert docs[0].name == "Tagged"

    def test_list_with_limit(self, doc_service: DocumentService):
        """List respects limit parameter."""
        for i in range(10):
            doc_service.create(name=f"Doc {i}")
        docs, total = doc_service.list_documents(limit=5)
        assert len(docs) == 5
        assert total == 10

    def test_list_with_offset(self, doc_service: DocumentService):
        """List respects offset parameter."""
        for i in range(10):
            doc_service.create(name=f"Doc {i}")
        docs, total = doc_service.list_documents(offset=5)
        assert len(docs) == 5
        assert total == 10

    def test_list_with_limit_and_offset(self, doc_service: DocumentService):
        """List respects both limit and offset."""
        for i in range(20):
            doc_service.create(name=f"Doc {i}")
        docs, total = doc_service.list_documents(limit=5, offset=10)
        assert len(docs) == 5
        assert total == 20

    def test_list_sorted_by_updated_at(self, doc_service: DocumentService):
        """List should be sorted by updated_at descending."""
        d1 = doc_service.create(name="First")
        time.sleep(0.01)
        d2 = doc_service.create(name="Second")
        time.sleep(0.01)
        d3 = doc_service.create(name="Third")

        docs, total = doc_service.list_documents()
        assert docs[0].name == "Third"
        assert docs[1].name == "Second"
        assert docs[2].name == "First"


class TestDocumentVersions:
    """Test document version management."""

    def test_get_versions_empty(self, doc_service: DocumentService):
        """New document has no versions."""
        doc = doc_service.create(name="Doc")
        versions = doc_service.get_versions(doc.id)
        assert versions == []

    def test_get_versions_after_update(self, doc_service: DocumentService):
        """Update creates version snapshot."""
        doc = doc_service.create(name="Doc")
        doc_service.update(doc.id, name="Updated")
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 1
        assert versions[0].version == 1

    def test_version_preserves_content(self, doc_service: DocumentService):
        """Version snapshot preserves original content."""
        original_content = {"type": "doc", "content": [{"type": "text", "text": "Original"}]}
        doc = doc_service.create(name="Doc", content=DocumentContent(**original_content))
        doc_service.update(
            doc.id,
            content=DocumentContent(type="doc", content=[{"type": "text", "text": "Updated"}]),
        )
        versions = doc_service.get_versions(doc.id)
        # Content may be coerced to DocumentContent model
        vc = versions[0].content if isinstance(versions[0].content, dict) else versions[0].content.model_dump()
        assert vc == original_content

    def test_multiple_versions(self, doc_service: DocumentService):
        """Multiple updates create multiple versions."""
        doc = doc_service.create(name="Doc")
        for i in range(5):
            doc_service.update(doc.id, name=f"Update {i}")
        versions = doc_service.get_versions(doc.id)
        assert len(versions) == 5

    def test_versions_sorted_descending(self, doc_service: DocumentService):
        """Versions should be sorted by version number descending."""
        doc = doc_service.create(name="Doc")
        for i in range(3):
            doc_service.update(doc.id, name=f"Update {i}")
        versions = doc_service.get_versions(doc.id)
        assert versions[0].version == 3
        assert versions[1].version == 2
        assert versions[2].version == 1

    def test_get_versions_nonexistent_document(self, doc_service: DocumentService):
        """Get versions for nonexistent document returns empty list."""
        versions = doc_service.get_versions(str(uuid.uuid4()))
        assert versions == []


class TestDocumentComments:
    """Test document comment operations."""

    def test_add_comment(self, doc_service: DocumentService):
        """Add comment to document."""
        doc = doc_service.create(name="Doc")
        comment = doc_service.add_comment(
            doc.id,
            selection_start=0,
            selection_end=10,
            text="This is a comment",
        )
        assert comment is not None
        assert comment.text == "This is a comment"
        assert comment.selection_start == 0
        assert comment.selection_end == 10

    def test_add_comment_with_author(self, doc_service: DocumentService):
        """Add comment with author information."""
        doc = doc_service.create(name="Doc")
        comment = doc_service.add_comment(
            doc.id,
            selection_start=0,
            selection_end=10,
            text="Review needed",
            author_id="user-123",
            author_name="John Doe",
        )
        assert comment.author_id == "user-123"
        assert comment.author_name == "John Doe"

    def test_add_comment_to_nonexistent_document(self, doc_service: DocumentService):
        """Add comment to nonexistent document returns None."""
        result = doc_service.add_comment(
            str(uuid.uuid4()), 0, 10, "Comment"
        )
        assert result is None

    def test_get_comments_empty(self, doc_service: DocumentService):
        """Document with no comments returns empty list."""
        doc = doc_service.create(name="Doc")
        comments = doc_service.get_comments(doc.id)
        assert comments == []

    def test_get_comments(self, doc_service: DocumentService):
        """Get all comments for document."""
        doc = doc_service.create(name="Doc")
        doc_service.add_comment(doc.id, 0, 10, "First")
        doc_service.add_comment(doc.id, 20, 30, "Second")
        comments = doc_service.get_comments(doc.id)
        assert len(comments) == 2

    def test_comments_sorted_by_created_at(self, doc_service: DocumentService):
        """Comments should be sorted by created_at ascending."""
        doc = doc_service.create(name="Doc")
        doc_service.add_comment(doc.id, 0, 10, "First")
        time.sleep(0.01)
        doc_service.add_comment(doc.id, 20, 30, "Second")
        comments = doc_service.get_comments(doc.id)
        assert comments[0].text == "First"
        assert comments[1].text == "Second"

    def test_resolve_comment(self, doc_service: DocumentService):
        """Resolve a comment."""
        doc = doc_service.create(name="Doc")
        comment = doc_service.add_comment(doc.id, 0, 10, "Comment")
        result = doc_service.resolve_comment(doc.id, comment.id)
        assert result is True
        comments = doc_service.get_comments(doc.id)
        assert comments[0].resolved is True

    def test_resolve_nonexistent_comment(self, doc_service: DocumentService):
        """Resolve nonexistent comment returns False."""
        doc = doc_service.create(name="Doc")
        result = doc_service.resolve_comment(doc.id, str(uuid.uuid4()))
        assert result is False

    def test_get_comments_nonexistent_document(self, doc_service: DocumentService):
        """Get comments for nonexistent document returns empty list."""
        comments = doc_service.get_comments(str(uuid.uuid4()))
        assert comments == []


class TestDocumentServiceHelpers:
    """Test internal helper methods."""

    def test_normalize_content_none(self, doc_service: DocumentService):
        """_normalize_content handles None."""
        result = doc_service._normalize_content(None)
        assert result == {"type": "doc", "content": []}

    def test_normalize_content_dict(self, doc_service: DocumentService):
        """_normalize_content handles dict."""
        content = {"type": "doc", "content": [{"type": "text"}]}
        result = doc_service._normalize_content(content)
        assert result == content

    def test_normalize_content_model(self, doc_service: DocumentService):
        """_normalize_content handles DocumentContent model."""
        content = DocumentContent(type="doc", content=[])
        result = doc_service._normalize_content(content)
        assert result == {"type": "doc", "content": []}

    def test_normalize_id_valid(self, doc_service: DocumentService):
        """_normalize_id handles valid UUID."""
        valid_uuid = str(uuid.uuid4())
        result = doc_service._normalize_id(valid_uuid)
        assert result == valid_uuid

    def test_normalize_id_invalid(self, doc_service: DocumentService):
        """_normalize_id returns None for invalid UUID."""
        result = doc_service._normalize_id("not-a-uuid")
        assert result is None

    def test_normalize_id_empty(self, doc_service: DocumentService):
        """_normalize_id returns None for empty string."""
        result = doc_service._normalize_id("")
        assert result is None


class TestDocumentServiceConcurrency:
    """Test thread safety of document service."""

    def test_concurrent_creates(self, doc_service: DocumentService):
        """Concurrent creates should all succeed."""
        results = []
        errors = []

        def create_doc(i):
            try:
                doc = doc_service.create(name=f"Doc {i}")
                results.append(doc.id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_doc, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10
        assert len(set(results)) == 10  # All unique IDs

    def test_concurrent_updates_same_document(self, doc_service: DocumentService):
        """Concurrent updates to same document should not corrupt data."""
        doc = doc_service.create(name="Concurrent Doc")
        results = []
        errors = []

        def update_doc(i):
            try:
                updated = doc_service.update(doc.id, metadata={f"key_{i}": i})
                results.append(updated.version)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=update_doc, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        final = doc_service.get(doc.id)
        assert final.version == 11  # 1 initial + 10 updates

    def test_concurrent_reads(self, doc_service: DocumentService):
        """Concurrent reads should not cause issues."""
        doc = doc_service.create(name="Read Me")
        results = []
        errors = []

        def read_doc():
            try:
                retrieved = doc_service.get(doc.id)
                results.append(retrieved.name)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_doc) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(r == "Read Me" for r in results)
