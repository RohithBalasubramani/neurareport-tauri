"""Documents API Route Tests.

Comprehensive tests for document CRUD, versioning, comments, collaboration,
PDF operations, and AI writing stub endpoints.
"""
import os
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


from backend.app.api.routes.documents import (
    router,
    get_document_service,
    get_collaboration_service,
    get_pdf_service,
)
from backend.app.api.middleware import limiter
from backend.app.services.documents.service import DocumentService


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def doc_service(tmp_path):
    """Create a document service with temp storage."""
    return DocumentService(uploads_root=tmp_path / "documents")


@pytest.fixture
def collab_service():
    """Mock collaboration service."""
    return MagicMock()


@pytest.fixture
def pdf_service():
    """Mock PDF operations service."""
    return MagicMock()


@pytest.fixture
def client(doc_service, collab_service, pdf_service):
    """Create test client with dependency overrides."""
    app = FastAPI()
    app.include_router(router, prefix="/documents")
    app.dependency_overrides[get_document_service] = lambda: doc_service
    app.dependency_overrides[get_collaboration_service] = lambda: collab_service
    app.dependency_overrides[get_pdf_service] = lambda: pdf_service
    limiter.enabled = False
    yield TestClient(app)
    limiter.enabled = True


@pytest.fixture
def created_doc(client):
    """Helper: create a document and return the JSON response."""
    resp = client.post("/documents", json={"name": "Test Document"})
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture
def created_doc_with_content(client):
    """Helper: create a document with content."""
    payload = {
        "name": "Content Doc",
        "content": {
            "type": "doc",
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Hello world"}]}
            ],
        },
        "metadata": {"category": "report"},
    }
    resp = client.post("/documents", json=payload)
    assert resp.status_code == 200
    return resp.json()


# =============================================================================
# 1. DOCUMENT CRUD (15+ tests)
# =============================================================================


class TestCreateDocument:
    """Test POST /documents."""

    def test_create_document_minimal(self, client):
        """Create document with only required name field."""
        resp = client.post("/documents", json={"name": "My Doc"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "My Doc"
        assert "id" in data
        assert data["version"] == 1
        assert data["is_template"] is False

    def test_create_document_with_content(self, client):
        """Create document with structured TipTap content."""
        payload = {
            "name": "With Content",
            "content": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}
                ],
            },
        }
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"]["type"] == "doc"
        assert len(data["content"]["content"]) == 1

    def test_create_document_with_metadata(self, client):
        """Create document with metadata dict."""
        payload = {
            "name": "Metadata Doc",
            "metadata": {"project": "alpha", "priority": 1},
        }
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["metadata"]["project"] == "alpha"
        assert data["metadata"]["priority"] == 1

    def test_create_document_as_template(self, client):
        """Create document with is_template=True."""
        payload = {"name": "Template", "is_template": True}
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        assert resp.json()["is_template"] is True

    def test_create_document_with_tags_field(self, client):
        """Create document accepts tags field without error."""
        payload = {"name": "Tagged", "tags": ["finance", "Q4"]}
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        # Note: the route's create call does not forward tags to the service,
        # so tags remain at the service default (empty).
        assert isinstance(resp.json()["tags"], list)

    def test_create_document_empty_name_rejected(self, client):
        """Empty name should be rejected (min_length=1)."""
        resp = client.post("/documents", json={"name": ""})
        assert resp.status_code == 422

    def test_create_document_missing_name_rejected(self, client):
        """Missing name field should be rejected."""
        resp = client.post("/documents", json={})
        assert resp.status_code == 422

    def test_create_document_name_too_long(self, client):
        """Name exceeding 255 chars should be rejected."""
        resp = client.post("/documents", json={"name": "A" * 256})
        assert resp.status_code == 422

    def test_create_document_name_max_length(self, client):
        """Name at exactly 255 chars should be accepted."""
        resp = client.post("/documents", json={"name": "A" * 255})
        assert resp.status_code == 200
        assert len(resp.json()["name"]) == 255

    def test_create_document_returns_timestamps(self, client):
        """Created document should have created_at and updated_at."""
        resp = client.post("/documents", json={"name": "Timestamped"})
        data = resp.json()
        assert "created_at" in data
        assert "updated_at" in data


class TestGetDocument:
    """Test GET /documents/{id}."""

    def test_get_existing_document(self, client, created_doc):
        """Get a document by ID returns the document."""
        doc_id = created_doc["id"]
        resp = client.get(f"/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == doc_id
        assert resp.json()["name"] == "Test Document"

    def test_get_nonexistent_document_404(self, client):
        """Getting a nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/documents/{fake_id}")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_get_document_preserves_metadata(self, client, created_doc_with_content):
        """Get preserves metadata set during creation."""
        doc_id = created_doc_with_content["id"]
        resp = client.get(f"/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["metadata"]["category"] == "report"


class TestListDocuments:
    """Test GET /documents."""

    def test_list_empty(self, client):
        """List with no documents returns empty list."""
        resp = client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["documents"] == []
        assert data["total"] == 0

    def test_list_returns_all_documents(self, client):
        """List returns all created documents."""
        for i in range(3):
            client.post("/documents", json={"name": f"Doc {i}"})
        resp = client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["documents"]) == 3

    def test_list_with_limit(self, client):
        """List respects limit parameter."""
        for i in range(5):
            client.post("/documents", json={"name": f"Doc {i}"})
        resp = client.get("/documents?limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["documents"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2

    def test_list_with_offset(self, client):
        """List respects offset parameter."""
        for i in range(5):
            client.post("/documents", json={"name": f"Doc {i}"})
        resp = client.get("/documents?offset=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["documents"]) == 2
        assert data["total"] == 5
        assert data["offset"] == 3

    def test_list_with_limit_and_offset(self, client):
        """List respects both limit and offset."""
        for i in range(10):
            client.post("/documents", json={"name": f"Doc {i}"})
        resp = client.get("/documents?limit=3&offset=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["documents"]) == 3
        assert data["total"] == 10

    def test_list_filter_is_template(self, client):
        """List filters by is_template flag."""
        client.post("/documents", json={"name": "Regular"})
        client.post("/documents", json={"name": "Template", "is_template": True})
        resp = client.get("/documents?is_template=true")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["documents"][0]["is_template"] is True

    def test_list_filter_is_template_false(self, client):
        """List filters non-templates."""
        client.post("/documents", json={"name": "Regular"})
        client.post("/documents", json={"name": "Template", "is_template": True})
        resp = client.get("/documents?is_template=false")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["documents"][0]["is_template"] is False

    def test_list_invalid_limit_rejected(self, client):
        """Limit below 1 or above 500 should be rejected."""
        resp = client.get("/documents?limit=0")
        assert resp.status_code == 422
        resp = client.get("/documents?limit=501")
        assert resp.status_code == 422

    def test_list_negative_offset_rejected(self, client):
        """Negative offset should be rejected."""
        resp = client.get("/documents?offset=-1")
        assert resp.status_code == 422

    def test_list_response_structure(self, client):
        """List response has documents, total, offset, limit fields."""
        resp = client.get("/documents")
        data = resp.json()
        assert "documents" in data
        assert "total" in data
        assert "offset" in data
        assert "limit" in data


class TestUpdateDocument:
    """Test PUT /documents/{id}."""

    def test_update_name(self, client, created_doc):
        """Update document name."""
        doc_id = created_doc["id"]
        resp = client.put(f"/documents/{doc_id}", json={"name": "Renamed"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

    def test_update_content(self, client, created_doc):
        """Update document content."""
        doc_id = created_doc["id"]
        new_content = {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Updated"}]}],
        }
        resp = client.put(f"/documents/{doc_id}", json={"content": new_content})
        assert resp.status_code == 200
        assert resp.json()["content"]["content"][0]["content"][0]["text"] == "Updated"

    def test_update_metadata(self, client, created_doc):
        """Update document metadata."""
        doc_id = created_doc["id"]
        resp = client.put(
            f"/documents/{doc_id}",
            json={"metadata": {"status": "reviewed"}},
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["status"] == "reviewed"

    def test_update_increments_version(self, client, created_doc):
        """Update should increment the version."""
        doc_id = created_doc["id"]
        assert created_doc["version"] == 1
        resp = client.put(f"/documents/{doc_id}", json={"name": "V2"})
        assert resp.status_code == 200
        assert resp.json()["version"] == 2

    def test_update_nonexistent_document_404(self, client):
        """Updating a nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.put(f"/documents/{fake_id}", json={"name": "Ghost"})
        assert resp.status_code == 404

    def test_update_empty_name_rejected(self, client, created_doc):
        """Updating with empty name should fail validation."""
        doc_id = created_doc["id"]
        resp = client.put(f"/documents/{doc_id}", json={"name": ""})
        assert resp.status_code == 422


class TestDeleteDocument:
    """Test DELETE /documents/{id}."""

    def test_delete_existing_document(self, client, created_doc):
        """Delete a document returns success."""
        doc_id = created_doc["id"]
        resp = client.delete(f"/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_delete_makes_document_inaccessible(self, client, created_doc):
        """Deleted document is no longer accessible."""
        doc_id = created_doc["id"]
        client.delete(f"/documents/{doc_id}")
        resp = client.get(f"/documents/{doc_id}")
        assert resp.status_code == 404

    def test_delete_nonexistent_document_404(self, client):
        """Deleting a nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/documents/{fake_id}")
        assert resp.status_code == 404


# =============================================================================
# 2. VERSION HISTORY (5+ tests)
# =============================================================================


class TestVersionHistory:
    """Test GET /documents/{id}/versions and /documents/{id}/versions/{version}."""

    def test_no_versions_for_new_document(self, client, created_doc):
        """Newly created document has no version history."""
        doc_id = created_doc["id"]
        resp = client.get(f"/documents/{doc_id}/versions")
        assert resp.status_code == 200
        assert resp.json()["versions"] == []

    def test_version_created_after_update(self, client, created_doc):
        """Updating a document creates a version snapshot."""
        doc_id = created_doc["id"]
        client.put(f"/documents/{doc_id}", json={"name": "Updated"})
        resp = client.get(f"/documents/{doc_id}/versions")
        assert resp.status_code == 200
        versions = resp.json()["versions"]
        assert len(versions) >= 1
        assert versions[0]["version"] == 1

    def test_multiple_updates_create_multiple_versions(self, client, created_doc):
        """Multiple updates create corresponding version entries."""
        doc_id = created_doc["id"]
        for i in range(3):
            client.put(f"/documents/{doc_id}", json={"name": f"Update {i}"})
        resp = client.get(f"/documents/{doc_id}/versions")
        assert resp.status_code == 200
        versions = resp.json()["versions"]
        assert len(versions) == 3

    def test_get_specific_version(self, client, created_doc):
        """Get a specific version by version number."""
        doc_id = created_doc["id"]
        client.put(f"/documents/{doc_id}", json={"name": "V2"})
        resp = client.get(f"/documents/{doc_id}/versions/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == 1

    def test_get_specific_version_missing_404(self, client, created_doc):
        """Getting a version that does not exist returns 404."""
        doc_id = created_doc["id"]
        resp = client.get(f"/documents/{doc_id}/versions/999")
        assert resp.status_code == 404

    def test_versions_404_for_missing_document(self, client):
        """Version history for nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/documents/{fake_id}/versions")
        assert resp.status_code == 404

    def test_version_contains_expected_fields(self, client, created_doc):
        """Version entry contains expected response fields."""
        doc_id = created_doc["id"]
        client.put(f"/documents/{doc_id}", json={"name": "V2 Name"})
        resp = client.get(f"/documents/{doc_id}/versions/1")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "document_id" in data
        assert "version" in data
        assert "content" in data
        assert "created_at" in data


# =============================================================================
# 3. COMMENTS (8+ tests)
# =============================================================================


class TestComments:
    """Test comment endpoints."""

    def test_add_comment(self, client, created_doc):
        """Add a comment to a document."""
        doc_id = created_doc["id"]
        payload = {"selection_start": 0, "selection_end": 10, "text": "Great intro!"}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["text"] == "Great intro!"
        assert data["selection_start"] == 0
        assert data["selection_end"] == 10
        assert data["resolved"] is False

    def test_add_comment_returns_id(self, client, created_doc):
        """Comment response includes a generated ID."""
        doc_id = created_doc["id"]
        payload = {"selection_start": 0, "selection_end": 5, "text": "Note"}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 200
        assert "id" in resp.json()

    def test_add_comment_to_nonexistent_document_404(self, client):
        """Adding comment to nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        payload = {"selection_start": 0, "selection_end": 5, "text": "Missing doc"}
        resp = client.post(f"/documents/{fake_id}/comments", json=payload)
        assert resp.status_code == 404

    def test_add_comment_empty_text_rejected(self, client, created_doc):
        """Empty comment text should be rejected."""
        doc_id = created_doc["id"]
        payload = {"selection_start": 0, "selection_end": 5, "text": ""}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 422

    def test_add_comment_negative_selection_rejected(self, client, created_doc):
        """Negative selection values should be rejected (ge=0)."""
        doc_id = created_doc["id"]
        payload = {"selection_start": -1, "selection_end": 5, "text": "Bad"}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 422

    def test_list_comments_empty(self, client, created_doc):
        """Document with no comments returns empty list."""
        doc_id = created_doc["id"]
        resp = client.get(f"/documents/{doc_id}/comments")
        assert resp.status_code == 200
        assert resp.json()["comments"] == []

    def test_list_comments_after_adding(self, client, created_doc):
        """List comments returns all added comments."""
        doc_id = created_doc["id"]
        client.post(
            f"/documents/{doc_id}/comments",
            json={"selection_start": 0, "selection_end": 5, "text": "First"},
        )
        client.post(
            f"/documents/{doc_id}/comments",
            json={"selection_start": 10, "selection_end": 20, "text": "Second"},
        )
        resp = client.get(f"/documents/{doc_id}/comments")
        assert resp.status_code == 200
        comments = resp.json()["comments"]
        assert len(comments) == 2

    def test_resolve_comment(self, client, created_doc):
        """Resolve a comment by PATCH."""
        doc_id = created_doc["id"]
        comment_resp = client.post(
            f"/documents/{doc_id}/comments",
            json={"selection_start": 0, "selection_end": 5, "text": "To resolve"},
        )
        comment_id = comment_resp.json()["id"]
        resp = client.patch(f"/documents/{doc_id}/comments/{comment_id}/resolve")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_resolve_comment_marks_resolved(self, client, created_doc):
        """After resolving, the comment is marked as resolved."""
        doc_id = created_doc["id"]
        comment_resp = client.post(
            f"/documents/{doc_id}/comments",
            json={"selection_start": 0, "selection_end": 5, "text": "Will resolve"},
        )
        comment_id = comment_resp.json()["id"]
        client.patch(f"/documents/{doc_id}/comments/{comment_id}/resolve")
        resp = client.get(f"/documents/{doc_id}/comments")
        comments = resp.json()["comments"]
        resolved = [c for c in comments if c["id"] == comment_id]
        assert len(resolved) == 1
        assert resolved[0]["resolved"] is True

    def test_resolve_nonexistent_comment_404(self, client, created_doc):
        """Resolving a nonexistent comment returns 404."""
        doc_id = created_doc["id"]
        fake_comment_id = str(uuid.uuid4())
        resp = client.patch(f"/documents/{doc_id}/comments/{fake_comment_id}/resolve")
        assert resp.status_code == 404

    def test_add_comment_text_too_long(self, client, created_doc):
        """Comment text exceeding max_length=5000 should be rejected."""
        doc_id = created_doc["id"]
        payload = {"selection_start": 0, "selection_end": 5, "text": "X" * 5001}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 422


# =============================================================================
# 4. COLLABORATION (5+ tests)
# =============================================================================


class TestCollaboration:
    """Test collaboration endpoints."""

    def test_start_collaboration_session(self, client, created_doc, collab_service):
        """Start a collaboration session for a document."""
        doc_id = created_doc["id"]
        mock_session = MagicMock()
        mock_session.model_dump.return_value = {
            "id": "session-1",
            "document_id": doc_id,
            "websocket_url": "ws://localhost:8000/ws/collab/" + doc_id,
            "created_at": "2025-01-01T00:00:00Z",
            "participants": [],
            "is_active": True,
        }
        collab_service.start_session.return_value = mock_session
        resp = client.post(f"/documents/{doc_id}/collaborate")
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_id"] == doc_id
        assert data["is_active"] is True

    def test_start_collaboration_missing_doc_404(self, client):
        """Starting collaboration on nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/documents/{fake_id}/collaborate")
        assert resp.status_code == 404

    def test_get_presence_no_session(self, client, created_doc, collab_service):
        """Get presence with no active session returns empty collaborators."""
        doc_id = created_doc["id"]
        collab_service.get_session_by_document.return_value = None
        resp = client.get(f"/documents/{doc_id}/collaborate/presence")
        assert resp.status_code == 200
        assert resp.json()["collaborators"] == []

    def test_get_presence_with_session(self, client, created_doc, collab_service):
        """Get presence with active session returns collaborator list."""
        doc_id = created_doc["id"]
        mock_session = MagicMock()
        mock_session.id = "session-1"
        collab_service.get_session_by_document.return_value = mock_session

        mock_presence = MagicMock()
        mock_presence.model_dump.return_value = {
            "user_id": "user-1",
            "user_name": "Alice",
            "cursor_position": 42,
            "selection_start": None,
            "selection_end": None,
            "color": "#FF0000",
            "last_seen": "2025-01-01T00:00:00Z",
        }
        collab_service.get_presence.return_value = [mock_presence]

        resp = client.get(f"/documents/{doc_id}/collaborate/presence")
        assert resp.status_code == 200
        collabs = resp.json()["collaborators"]
        assert len(collabs) == 1
        assert collabs[0]["user_id"] == "user-1"

    def test_start_collaboration_calls_set_websocket_base_url(
        self, client, created_doc, collab_service
    ):
        """Starting collaboration should set the websocket base URL."""
        doc_id = created_doc["id"]
        mock_session = MagicMock()
        mock_session.model_dump.return_value = {
            "id": "session-2",
            "document_id": doc_id,
            "websocket_url": "ws://testserver/ws/collab/" + doc_id,
            "created_at": "2025-01-01T00:00:00Z",
            "participants": [],
            "is_active": True,
        }
        collab_service.start_session.return_value = mock_session
        client.post(f"/documents/{doc_id}/collaborate")
        collab_service.set_websocket_base_url.assert_called_once()

    def test_get_presence_calls_correct_session_id(
        self, client, created_doc, collab_service
    ):
        """Presence lookup uses the session ID from session-by-document."""
        doc_id = created_doc["id"]
        mock_session = MagicMock()
        mock_session.id = "sess-abc"
        collab_service.get_session_by_document.return_value = mock_session
        collab_service.get_presence.return_value = []
        client.get(f"/documents/{doc_id}/collaborate/presence")
        collab_service.get_presence.assert_called_once_with("sess-abc")


# =============================================================================
# 5. PDF OPERATIONS (12+ tests)
# =============================================================================


class TestPDFReorder:
    """Test POST /documents/{id}/pdf/reorder."""

    def test_reorder_success(self, client, doc_service, pdf_service, tmp_path):
        """Reorder pages in a PDF document."""
        doc = doc_service.create(
            name="PDF Doc", metadata={"pdf_path": str(tmp_path / "test.pdf")}
        )
        pdf_service.reorder_pages.return_value = tmp_path / "reordered.pdf"

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "test.pdf",
        ):
            resp = client.post(
                f"/documents/{doc.id}/pdf/reorder",
                json={"page_order": [2, 0, 1]},
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert "output_path" in resp.json()

    def test_reorder_missing_document_404(self, client):
        """Reorder on nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.post(
            f"/documents/{fake_id}/pdf/reorder",
            json={"page_order": [0, 1]},
        )
        assert resp.status_code == 404

    def test_reorder_empty_page_order_rejected(self, client, created_doc):
        """Empty page_order should be rejected (min_length=1)."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/reorder",
            json={"page_order": []},
        )
        assert resp.status_code == 422

    def test_reorder_service_error_500(self, client, doc_service, pdf_service, tmp_path):
        """Service exception during reorder returns 500."""
        doc = doc_service.create(
            name="PDF Doc", metadata={"pdf_path": str(tmp_path / "test.pdf")}
        )
        pdf_service.reorder_pages.side_effect = RuntimeError("Reorder failed")

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "test.pdf",
        ):
            resp = client.post(
                f"/documents/{doc.id}/pdf/reorder",
                json={"page_order": [0]},
            )
        assert resp.status_code == 500


class TestPDFWatermark:
    """Test POST /documents/{id}/pdf/watermark."""

    def test_watermark_success(self, client, doc_service, pdf_service, tmp_path):
        """Add watermark to a PDF document."""
        doc = doc_service.create(
            name="PDF Doc", metadata={"pdf_path": str(tmp_path / "test.pdf")}
        )
        pdf_service.add_watermark.return_value = tmp_path / "watermarked.pdf"

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "test.pdf",
        ):
            resp = client.post(
                f"/documents/{doc.id}/pdf/watermark",
                json={"text": "CONFIDENTIAL"},
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_watermark_with_options(self, client, doc_service, pdf_service, tmp_path):
        """Add watermark with all configuration options."""
        doc = doc_service.create(
            name="PDF Doc", metadata={"pdf_path": str(tmp_path / "test.pdf")}
        )
        pdf_service.add_watermark.return_value = tmp_path / "watermarked.pdf"

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "test.pdf",
        ):
            resp = client.post(
                f"/documents/{doc.id}/pdf/watermark",
                json={
                    "text": "DRAFT",
                    "position": "diagonal",
                    "font_size": 72,
                    "opacity": 0.5,
                    "color": "#FF0000",
                },
            )
        assert resp.status_code == 200

    def test_watermark_missing_document_404(self, client):
        """Watermark on nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.post(
            f"/documents/{fake_id}/pdf/watermark",
            json={"text": "SECRET"},
        )
        assert resp.status_code == 404

    def test_watermark_empty_text_rejected(self, client, created_doc):
        """Empty watermark text should be rejected."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/watermark",
            json={"text": ""},
        )
        assert resp.status_code == 422

    def test_watermark_invalid_position_rejected(self, client, created_doc):
        """Invalid position value should be rejected."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/watermark",
            json={"text": "DRAFT", "position": "invalid"},
        )
        assert resp.status_code == 422

    def test_watermark_invalid_color_rejected(self, client, created_doc):
        """Invalid color format should be rejected."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/watermark",
            json={"text": "DRAFT", "color": "red"},
        )
        assert resp.status_code == 422


class TestPDFRedact:
    """Test POST /documents/{id}/pdf/redact."""

    def test_redact_success(self, client, doc_service, pdf_service, tmp_path):
        """Redact regions in a PDF document."""
        doc = doc_service.create(
            name="PDF Doc", metadata={"pdf_path": str(tmp_path / "test.pdf")}
        )
        pdf_service.redact_regions.return_value = tmp_path / "redacted.pdf"

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "test.pdf",
        ):
            resp = client.post(
                f"/documents/{doc.id}/pdf/redact",
                json={
                    "regions": [
                        {"page": 0, "x": 10, "y": 20, "width": 100, "height": 50}
                    ]
                },
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_redact_missing_document_404(self, client):
        """Redact on nonexistent document returns 404."""
        fake_id = str(uuid.uuid4())
        resp = client.post(
            f"/documents/{fake_id}/pdf/redact",
            json={"regions": [{"page": 0, "x": 0, "y": 0, "width": 10, "height": 10}]},
        )
        assert resp.status_code == 404

    def test_redact_empty_regions_rejected(self, client, created_doc):
        """Empty regions list should be rejected (min_length=1)."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/redact",
            json={"regions": []},
        )
        assert resp.status_code == 422

    def test_redact_invalid_region_dimensions_rejected(self, client, created_doc):
        """Regions with zero width/height should be rejected (gt=0)."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/pdf/redact",
            json={"regions": [{"page": 0, "x": 0, "y": 0, "width": 0, "height": 10}]},
        )
        assert resp.status_code == 422


class TestPDFMerge:
    """Test POST /documents/merge."""

    def test_merge_success(self, client, doc_service, pdf_service, tmp_path):
        """Merge multiple PDF documents."""
        doc1 = doc_service.create(
            name="PDF 1", metadata={"pdf_path": str(tmp_path / "doc1.pdf")}
        )
        doc2 = doc_service.create(
            name="PDF 2", metadata={"pdf_path": str(tmp_path / "doc2.pdf")}
        )
        mock_result = MagicMock()
        mock_result.output_path = str(tmp_path / "merged.pdf")
        mock_result.page_count = 10
        pdf_service.merge_pdfs.return_value = mock_result

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            side_effect=[tmp_path / "doc1.pdf", tmp_path / "doc2.pdf"],
        ):
            resp = client.post(
                "/documents/merge",
                json={"document_ids": [doc1.id, doc2.id]},
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert resp.json()["page_count"] == 10

    def test_merge_too_few_documents_rejected(self, client):
        """Merge with fewer than 2 document IDs should be rejected."""
        resp = client.post(
            "/documents/merge",
            json={"document_ids": ["single-id"]},
        )
        assert resp.status_code == 422

    def test_merge_nonexistent_document_404(self, client, doc_service, tmp_path):
        """Merge with a nonexistent document returns 404."""
        doc1 = doc_service.create(
            name="Exists", metadata={"pdf_path": str(tmp_path / "d1.pdf")}
        )
        fake_id = str(uuid.uuid4())
        # The loop in merge_pdfs will find doc1 first, call validate_pdf_path
        # on it, then fail with 404 when it cannot find the fake doc.
        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            return_value=tmp_path / "d1.pdf",
        ):
            resp = client.post(
                "/documents/merge",
                json={"document_ids": [doc1.id, fake_id]},
            )
        assert resp.status_code == 404

    def test_merge_service_error_500(self, client, doc_service, pdf_service, tmp_path):
        """Service exception during merge returns 500."""
        doc1 = doc_service.create(
            name="PDF 1", metadata={"pdf_path": str(tmp_path / "d1.pdf")}
        )
        doc2 = doc_service.create(
            name="PDF 2", metadata={"pdf_path": str(tmp_path / "d2.pdf")}
        )
        pdf_service.merge_pdfs.side_effect = RuntimeError("Merge failed")

        with patch(
            "backend.app.api.routes.documents.validate_pdf_path",
            side_effect=[tmp_path / "d1.pdf", tmp_path / "d2.pdf"],
        ):
            resp = client.post(
                "/documents/merge",
                json={"document_ids": [doc1.id, doc2.id]},
            )
        assert resp.status_code == 500


# =============================================================================
# 6. AI WRITING STUBS (10+ tests)
# =============================================================================


class TestAIGrammar:
    """Test POST /documents/{id}/ai/grammar."""

    def test_grammar_returns_stub_response(self, client, created_doc):
        """Grammar check returns stub structure."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/grammar",
            json={"text": "This is a test sentence."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_text"] == "This is a test sentence."
        assert data["result_text"] == "This is a test sentence."
        assert data["metadata"]["operation"] == "grammar_check"

    def test_grammar_returns_suggestions_list(self, client, created_doc):
        """Grammar response includes suggestions key."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/grammar",
            json={"text": "Test text"},
        )
        assert "suggestions" in resp.json()
        assert isinstance(resp.json()["suggestions"], list)


class TestAISummarize:
    """Test POST /documents/{id}/ai/summarize."""

    def test_summarize_returns_stub_response(self, client, created_doc):
        """Summarize returns truncated stub text."""
        doc_id = created_doc["id"]
        long_text = "A" * 500
        resp = client.post(
            f"/documents/{doc_id}/ai/summarize",
            json={"text": long_text},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_text"] == long_text
        assert data["result_text"] == long_text[:200] + "..."
        assert data["metadata"]["operation"] == "summarize"

    def test_summarize_short_text(self, client, created_doc):
        """Summarize with short text still returns stub."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/summarize",
            json={"text": "Short"},
        )
        assert resp.status_code == 200
        assert resp.json()["result_text"] == "Short..."


class TestAIRewrite:
    """Test POST /documents/{id}/ai/rewrite."""

    def test_rewrite_returns_stub_response(self, client, created_doc):
        """Rewrite returns same text as stub."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/rewrite",
            json={"text": "Please rewrite me."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_text"] == "Please rewrite me."
        assert data["result_text"] == "Please rewrite me."
        assert data["metadata"]["operation"] == "rewrite"

    def test_rewrite_with_instruction(self, client, created_doc):
        """Rewrite with instruction param is accepted."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/rewrite",
            json={"text": "Content here", "instruction": "Make it formal"},
        )
        assert resp.status_code == 200


class TestAIExpand:
    """Test POST /documents/{id}/ai/expand."""

    def test_expand_returns_stub_response(self, client, created_doc):
        """Expand returns same text as stub."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/expand",
            json={"text": "Bullet point notes."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_text"] == "Bullet point notes."
        assert data["result_text"] == "Bullet point notes."
        assert data["metadata"]["operation"] == "expand"

    def test_expand_with_options(self, client, created_doc):
        """Expand with options dict is accepted."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/expand",
            json={"text": "Points", "options": {"target_length": "paragraph"}},
        )
        assert resp.status_code == 200


class TestAITranslate:
    """Test POST /documents/{id}/ai/translate."""

    def test_translate_returns_stub_response(self, client, created_doc):
        """Translate returns stub with target_language metadata."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/translate",
            json={"text": "Hello world", "options": {"target_language": "French"}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_text"] == "Hello world"
        assert data["metadata"]["operation"] == "translate"
        assert data["metadata"]["target_language"] == "French"

    def test_translate_default_language(self, client, created_doc):
        """Translate without target_language defaults to Spanish."""
        doc_id = created_doc["id"]
        resp = client.post(
            f"/documents/{doc_id}/ai/translate",
            json={"text": "Hello"},
        )
        assert resp.status_code == 200
        assert resp.json()["metadata"]["target_language"] == "Spanish"


class TestAIValidation:
    """Validation tests for AI endpoints."""

    def test_ai_empty_text_rejected(self, client, created_doc):
        """AI endpoint with empty text should be rejected."""
        doc_id = created_doc["id"]
        for endpoint in ["grammar", "summarize", "rewrite", "expand", "translate"]:
            resp = client.post(
                f"/documents/{doc_id}/ai/{endpoint}",
                json={"text": ""},
            )
            assert resp.status_code == 422, f"Expected 422 for {endpoint} with empty text"

    def test_ai_missing_text_rejected(self, client, created_doc):
        """AI endpoint with missing text field should be rejected."""
        doc_id = created_doc["id"]
        for endpoint in ["grammar", "summarize", "rewrite", "expand", "translate"]:
            resp = client.post(
                f"/documents/{doc_id}/ai/{endpoint}",
                json={},
            )
            assert resp.status_code == 422, f"Expected 422 for {endpoint} with missing text"


# =============================================================================
# 7. EDGE CASES (5+ tests)
# =============================================================================


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_create_with_empty_content_blocks(self, client):
        """Create document with empty content blocks list."""
        payload = {
            "name": "Empty Content",
            "content": {"type": "doc", "content": []},
        }
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        assert resp.json()["content"]["content"] == []

    def test_create_with_large_metadata(self, client):
        """Create document with a large metadata dictionary."""
        big_meta = {f"key_{i}": f"value_{i}" * 20 for i in range(50)}
        payload = {"name": "Big Meta", "metadata": big_meta}
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        meta = resp.json()["metadata"]
        assert len(meta) == 50
        assert meta["key_0"] == "value_0" * 20

    def test_create_with_special_characters_in_name(self, client):
        """Create document with special characters in the name."""
        payload = {"name": "Report <Q4> & Summary \"2025\" / Final"}
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Report <Q4> & Summary \"2025\" / Final"

    def test_create_with_unicode_name(self, client):
        """Create document with unicode characters in name."""
        payload = {"name": "Informe de ventas \u00e9\u00e8\u00ea \u65e5\u672c\u8a9e"}
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        assert "\u65e5\u672c\u8a9e" in resp.json()["name"]

    def test_create_with_nested_metadata(self, client):
        """Create document with nested metadata structures."""
        payload = {
            "name": "Nested Meta",
            "metadata": {
                "author": {"name": "Alice", "email": "alice@example.com"},
                "tags": ["draft", "review"],
                "counts": {"words": 1500, "pages": 5},
            },
        }
        resp = client.post("/documents", json=payload)
        assert resp.status_code == 200
        meta = resp.json()["metadata"]
        assert meta["author"]["name"] == "Alice"
        assert meta["counts"]["pages"] == 5

    def test_update_with_no_changes(self, client, created_doc):
        """Update with empty body still returns document."""
        doc_id = created_doc["id"]
        resp = client.put(f"/documents/{doc_id}", json={})
        assert resp.status_code == 200
        assert resp.json()["id"] == doc_id

    def test_create_multiple_and_list(self, client):
        """Create several documents and verify list count."""
        count = 15
        for i in range(count):
            client.post("/documents", json={"name": f"Bulk Doc {i}"})
        resp = client.get("/documents?limit=500")
        assert resp.status_code == 200
        assert resp.json()["total"] == count

    def test_delete_then_list(self, client):
        """Deleted documents should not appear in list."""
        resp1 = client.post("/documents", json={"name": "Keeper"})
        resp2 = client.post("/documents", json={"name": "Goner"})
        client.delete(f"/documents/{resp2.json()['id']}")
        resp = client.get("/documents")
        assert resp.json()["total"] == 1
        assert resp.json()["documents"][0]["name"] == "Keeper"

    def test_update_after_delete_404(self, client, created_doc):
        """Updating a deleted document returns 404."""
        doc_id = created_doc["id"]
        client.delete(f"/documents/{doc_id}")
        resp = client.put(f"/documents/{doc_id}", json={"name": "Resurrected"})
        assert resp.status_code == 404

    def test_comment_on_deleted_document_404(self, client, created_doc):
        """Adding comment to a deleted document returns 404."""
        doc_id = created_doc["id"]
        client.delete(f"/documents/{doc_id}")
        payload = {"selection_start": 0, "selection_end": 5, "text": "Ghost comment"}
        resp = client.post(f"/documents/{doc_id}/comments", json=payload)
        assert resp.status_code == 404
