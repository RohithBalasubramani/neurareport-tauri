"""Document Q&A API Route Tests.

Comprehensive tests for DocQA session management, document handling,
question-answer flows, feedback, and chat history endpoints.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes.docqa import router, get_service
from backend.app.services.docqa.service import DocumentQAService
from backend.app.services.security import require_api_key


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def state_dict():
    """Shared mutable dict backing the mock state store."""
    return {"docqa_sessions": {}}


@pytest.fixture
def mock_service(state_dict):
    """Create a real DocumentQAService backed by an in-memory mock state store.

    The mock replaces `state_store_module.state_store` so the service can
    create/read/update/delete sessions without touching the filesystem.
    """
    svc = DocumentQAService()

    mock_store = MagicMock()
    # _lock must be usable as a context manager
    mock_store._lock = MagicMock()
    mock_store._read_state.side_effect = lambda: state_dict
    mock_store._write_state.side_effect = lambda s: state_dict.update(s)

    with patch("backend.app.services.docqa.service.state_store_module") as mock_module:
        mock_module.state_store = mock_store
        yield svc


@pytest.fixture
def client(mock_service):
    """TestClient with the docqa router mounted and dependencies overridden."""
    app = FastAPI()
    app.include_router(router, prefix="/docqa")

    # Bypass the API key requirement
    app.dependency_overrides[require_api_key] = lambda: None
    # Return the mock-backed service instead of creating a new one
    app.dependency_overrides[get_service] = lambda: mock_service

    return TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_session(client, name="Test Session"):
    """Helper: create a session and return the JSON body."""
    resp = client.post("/docqa/sessions", json={"name": name})
    assert resp.status_code == 200
    return resp.json()


def _add_document(client, session_id, name="report.pdf", content=None):
    """Helper: add a document to a session and return the JSON body."""
    if content is None:
        content = "A" * 100  # satisfies min_length=10
    resp = client.post(
        f"/docqa/sessions/{session_id}/documents",
        json={"name": name, "content": content},
    )
    assert resp.status_code == 200
    return resp.json()


LLM_RESPONSE_PAYLOAD = {
    "choices": [
        {
            "message": {
                "content": json.dumps(
                    {
                        "answer": "The answer is 42.",
                        "citations": [
                            {
                                "document_id": "doc-1",
                                "document_name": "report.pdf",
                                "quote": "The answer is 42.",
                                "relevance_score": 0.95,
                            }
                        ],
                        "confidence": 0.9,
                        "follow_up_questions": ["What is 43?"],
                    }
                )
            }
        }
    ],
    "usage": {"total_tokens": 150},
}


# ===================================================================
# 1. Session CRUD
# ===================================================================

class TestCreateSession:
    """POST /docqa/sessions"""

    def test_create_session_success(self, client):
        body = _create_session(client, "My Q&A Session")
        assert body["status"] == "ok"
        assert body["session"]["name"] == "My Q&A Session"
        assert "id" in body["session"]
        assert "correlation_id" in body

    def test_create_session_returns_empty_lists(self, client):
        body = _create_session(client)
        session = body["session"]
        assert session["documents"] == []
        assert session["messages"] == []

    def test_create_session_name_too_short(self, client):
        resp = client.post("/docqa/sessions", json={"name": ""})
        assert resp.status_code == 422

    def test_create_session_name_too_long(self, client):
        resp = client.post("/docqa/sessions", json={"name": "x" * 201})
        assert resp.status_code == 422

    def test_create_session_missing_name(self, client):
        resp = client.post("/docqa/sessions", json={})
        assert resp.status_code == 422

    def test_create_session_name_max_boundary(self, client):
        resp = client.post("/docqa/sessions", json={"name": "x" * 200})
        assert resp.status_code == 200
        assert resp.json()["session"]["name"] == "x" * 200

    def test_create_session_name_min_boundary(self, client):
        resp = client.post("/docqa/sessions", json={"name": "A"})
        assert resp.status_code == 200


class TestListSessions:
    """GET /docqa/sessions"""

    def test_list_sessions_empty(self, client):
        resp = client.get("/docqa/sessions")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["sessions"] == []

    def test_list_sessions_returns_created(self, client):
        _create_session(client, "Session A")
        _create_session(client, "Session B")

        resp = client.get("/docqa/sessions")
        body = resp.json()
        names = [s["name"] for s in body["sessions"]]
        assert "Session A" in names
        assert "Session B" in names
        assert len(body["sessions"]) == 2


class TestGetSession:
    """GET /docqa/sessions/{session_id}"""

    def test_get_session_success(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.get(f"/docqa/sessions/{session_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["session"]["id"] == session_id

    def test_get_session_not_found(self, client):
        resp = client.get("/docqa/sessions/nonexistent-id")
        assert resp.status_code == 404

    def test_get_session_contains_documents_after_add(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, name="my_doc.pdf")

        resp = client.get(f"/docqa/sessions/{session_id}")
        session = resp.json()["session"]
        assert len(session["documents"]) == 1
        assert session["documents"][0]["name"] == "my_doc.pdf"


class TestDeleteSession:
    """DELETE /docqa/sessions/{session_id}"""

    def test_delete_session_success(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.delete(f"/docqa/sessions/{session_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["deleted"] is True

        # Verify it's gone
        resp = client.get(f"/docqa/sessions/{session_id}")
        assert resp.status_code == 404

    def test_delete_session_not_found(self, client):
        resp = client.delete("/docqa/sessions/nonexistent-id")
        assert resp.status_code == 404

    def test_delete_session_double_delete(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp1 = client.delete(f"/docqa/sessions/{session_id}")
        assert resp1.status_code == 200

        resp2 = client.delete(f"/docqa/sessions/{session_id}")
        assert resp2.status_code == 404

    def test_delete_session_removes_from_list(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.get("/docqa/sessions")
        assert len(resp.json()["sessions"]) == 0


# ===================================================================
# 2. Documents
# ===================================================================

class TestAddDocument:
    """POST /docqa/sessions/{session_id}/documents"""

    def test_add_document_success(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        body = _add_document(client, session_id, name="report.pdf", content="A" * 100)
        assert body["status"] == "ok"
        doc = body["document"]
        assert doc["name"] == "report.pdf"
        assert "id" in doc
        assert "added_at" in doc

    def test_add_document_with_page_count(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "doc.pdf", "content": "A" * 50, "page_count": 5},
        )
        assert resp.status_code == 200
        assert resp.json()["document"]["page_count"] == 5

    def test_add_document_session_not_found(self, client):
        resp = client.post(
            "/docqa/sessions/nonexistent-id/documents",
            json={"name": "doc.pdf", "content": "A" * 50},
        )
        assert resp.status_code == 404

    def test_add_document_name_too_long(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "x" * 201, "content": "A" * 50},
        )
        assert resp.status_code == 422

    def test_add_document_name_empty(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "", "content": "A" * 50},
        )
        assert resp.status_code == 422

    def test_add_document_content_too_short(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "doc.pdf", "content": "short"},
        )
        assert resp.status_code == 422

    def test_add_document_content_missing(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "doc.pdf"},
        )
        assert resp.status_code == 422

    def test_add_multiple_documents(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        _add_document(client, session_id, name="doc1.pdf")
        _add_document(client, session_id, name="doc2.pdf")

        resp = client.get(f"/docqa/sessions/{session_id}")
        docs = resp.json()["session"]["documents"]
        assert len(docs) == 2

    def test_add_document_content_preview_truncated(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        long_content = "B" * 1000
        body = _add_document(client, session_id, content=long_content)
        preview = body["document"]["content_preview"]
        # The service truncates preview to 500 chars + "..."
        assert len(preview) <= 504
        assert preview.endswith("...")


class TestRemoveDocument:
    """DELETE /docqa/sessions/{session_id}/documents/{document_id}"""

    def test_remove_document_success(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        doc_body = _add_document(client, session_id)
        document_id = doc_body["document"]["id"]

        resp = client.delete(f"/docqa/sessions/{session_id}/documents/{document_id}")
        assert resp.status_code == 200
        assert resp.json()["removed"] is True

        # Verify document is removed
        resp = client.get(f"/docqa/sessions/{session_id}")
        assert len(resp.json()["session"]["documents"]) == 0

    def test_remove_document_session_not_found(self, client):
        resp = client.delete("/docqa/sessions/nonexistent/documents/some-doc")
        assert resp.status_code == 404

    def test_remove_document_document_not_found(self, client):
        """Removing a non-existent document ID still returns True (service
        filters the list; if the session exists, the removal is considered
        successful even if the doc was not present)."""
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.delete(f"/docqa/sessions/{session_id}/documents/nonexistent-doc")
        # The service returns True when session exists even if doc_id is absent
        assert resp.status_code == 200

    def test_remove_document_double_remove(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        doc_body = _add_document(client, session_id)
        document_id = doc_body["document"]["id"]

        resp1 = client.delete(f"/docqa/sessions/{session_id}/documents/{document_id}")
        assert resp1.status_code == 200

        # Second removal also succeeds (session still exists, doc already gone)
        resp2 = client.delete(f"/docqa/sessions/{session_id}/documents/{document_id}")
        assert resp2.status_code == 200


# ===================================================================
# 3. Ask questions (LLM interaction)
# ===================================================================

class TestAskQuestion:
    """POST /docqa/sessions/{session_id}/ask"""

    def test_ask_success_with_documents(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="The answer to everything is 42. " * 5)

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is the answer?"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert "response" in body
        assert body["response"]["message"]["role"] == "assistant"
        assert body["response"]["message"]["content"] == "The answer is 42."
        assert body["response"]["processing_time_ms"] >= 0
        assert body["response"]["tokens_used"] == 150

    def test_ask_includes_citations(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Important data here. " * 10)

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "Tell me about the data", "include_citations": True},
        )
        assert resp.status_code == 200
        citations = resp.json()["response"]["message"]["citations"]
        assert len(citations) == 1
        assert citations[0]["document_name"] == "report.pdf"
        assert citations[0]["relevance_score"] == 0.95

    def test_ask_no_documents_returns_message(self, client):
        """When no documents are added, the service returns a helpful message
        without calling the LLM."""
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is in the document?"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "No documents" in body["response"]["message"]["content"]

    def test_ask_session_not_found(self, client):
        resp = client.post(
            "/docqa/sessions/nonexistent/ask",
            json={"question": "Hello there?"},
        )
        assert resp.status_code == 404

    def test_ask_question_too_short(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "Hi"},  # min_length=3 but "Hi" is 2 chars
        )
        assert resp.status_code == 422

    def test_ask_question_too_long(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "x" * 2001},
        )
        assert resp.status_code == 422

    def test_ask_question_min_boundary(self, client, mock_service):
        """3-character question should be accepted."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some content here for testing.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "Why"},
        )
        assert resp.status_code == 200

    def test_ask_question_max_boundary(self, client, mock_service):
        """2000-character question should be accepted."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some content here for testing.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "x" * 2000},
        )
        assert resp.status_code == 200

    def test_ask_max_response_length_too_low(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is this?", "max_response_length": 50},
        )
        assert resp.status_code == 422

    def test_ask_max_response_length_too_high(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is this?", "max_response_length": 10001},
        )
        assert resp.status_code == 422

    def test_ask_llm_error_returns_error_message(self, client, mock_service):
        """When the LLM call raises, the service catches it and returns an
        error response rather than a 500."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some content here for testing.")

        mock_llm = MagicMock()
        mock_llm.complete.side_effect = RuntimeError("LLM unavailable")
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is in the document?"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "error" in body["response"]["message"]["content"].lower()

    def test_ask_adds_messages_to_history(self, client, mock_service):
        """Asking a question should add both the user and assistant messages
        to the session's message history."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="The sky is blue. " * 10)

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What color is the sky?"},
        )

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        messages = resp.json()["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"


# ===================================================================
# 4. Feedback
# ===================================================================

class TestSubmitFeedback:
    """POST /docqa/sessions/{session_id}/messages/{message_id}/feedback"""

    def _create_session_with_message(self, client, mock_service):
        """Helper: create a session, add a doc, ask a question, return IDs."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Test document content here.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        ask_resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is this about?"},
        )
        message_id = ask_resp.json()["response"]["message"]["id"]
        return session_id, message_id

    def test_feedback_helpful(self, client, mock_service):
        session_id, message_id = self._create_session_with_message(client, mock_service)

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/feedback",
            json={"feedback_type": "helpful"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["message"]["feedback"]["feedback_type"] == "helpful"

    def test_feedback_not_helpful_with_comment(self, client, mock_service):
        session_id, message_id = self._create_session_with_message(client, mock_service)

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/feedback",
            json={
                "feedback_type": "not_helpful",
                "comment": "The answer was incorrect",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"]["feedback"]["feedback_type"] == "not_helpful"
        assert body["message"]["feedback"]["comment"] == "The answer was incorrect"

    def test_feedback_invalid_type(self, client, mock_service):
        session_id, message_id = self._create_session_with_message(client, mock_service)

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/feedback",
            json={"feedback_type": "invalid_value"},
        )
        assert resp.status_code == 422

    def test_feedback_session_not_found(self, client):
        resp = client.post(
            "/docqa/sessions/nonexistent/messages/msg-1/feedback",
            json={"feedback_type": "helpful"},
        )
        assert resp.status_code == 404

    def test_feedback_message_not_found(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/nonexistent-msg/feedback",
            json={"feedback_type": "helpful"},
        )
        assert resp.status_code == 404

    def test_feedback_missing_feedback_type(self, client, mock_service):
        session_id, message_id = self._create_session_with_message(client, mock_service)

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/feedback",
            json={},
        )
        assert resp.status_code == 422


# ===================================================================
# 5. Regenerate response
# ===================================================================

class TestRegenerateResponse:
    """POST /docqa/sessions/{session_id}/messages/{message_id}/regenerate"""

    def _setup_session_for_regenerate(self, client, mock_service):
        """Helper: create a session with a doc, ask a question, return IDs."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Test document content here repeated. " * 5)

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        ask_resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is this about?"},
        )
        message_id = ask_resp.json()["response"]["message"]["id"]
        return session_id, message_id

    def test_regenerate_success(self, client, mock_service):
        session_id, message_id = self._setup_session_for_regenerate(client, mock_service)

        regen_payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "answer": "A completely new regenerated answer.",
                                "citations": [],
                                "confidence": 0.85,
                                "follow_up_questions": [],
                            }
                        )
                    }
                }
            ],
            "usage": {"total_tokens": 200},
        }
        mock_service._llm_client.complete.return_value = regen_payload

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/regenerate",
            json={},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["response"]["message"]["content"] == "A completely new regenerated answer."
        assert body["response"]["message"]["metadata"]["regenerated"] is True

    def test_regenerate_session_not_found(self, client):
        resp = client.post(
            "/docqa/sessions/nonexistent/messages/msg-1/regenerate",
            json={},
        )
        assert resp.status_code == 404

    def test_regenerate_message_not_found(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some document content here.")

        # The session exists but has no messages yet
        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/nonexistent-msg/regenerate",
            json={},
        )
        assert resp.status_code == 404

    def test_regenerate_llm_failure_returns_500(self, client, mock_service):
        """When the LLM fails during regeneration, the service raises
        RuntimeError which the route converts to a 500."""
        session_id, message_id = self._setup_session_for_regenerate(client, mock_service)

        mock_service._llm_client.complete.side_effect = RuntimeError("LLM down")

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/regenerate",
            json={},
        )
        assert resp.status_code == 500

    def test_regenerate_max_response_length_validation(self, client, mock_service):
        session_id, message_id = self._setup_session_for_regenerate(client, mock_service)

        # max_response_length below minimum
        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/regenerate",
            json={"max_response_length": 10},
        )
        assert resp.status_code == 422

        # max_response_length above maximum
        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/regenerate",
            json={"max_response_length": 99999},
        )
        assert resp.status_code == 422


# ===================================================================
# 6. Chat history
# ===================================================================

class TestGetChatHistory:
    """GET /docqa/sessions/{session_id}/history"""

    def test_get_history_empty(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["messages"] == []
        assert body["count"] == 0

    def test_get_history_after_ask(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some lengthy content here for testing purposes.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "Tell me about this"},
        )

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        body = resp.json()
        assert body["count"] == 2  # user + assistant
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][1]["role"] == "assistant"

    def test_get_history_with_limit(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some lengthy content here for testing purposes.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        # Ask multiple questions to build up history
        for i in range(3):
            client.post(
                f"/docqa/sessions/{session_id}/ask",
                json={"question": f"Question number {i + 1} here?"},
            )

        # Without limit, all messages should be present
        resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert resp.json()["count"] == 6  # 3 user + 3 assistant

        # With limit=2, only last 2 messages
        resp = client.get(f"/docqa/sessions/{session_id}/history?limit=2")
        assert resp.json()["count"] == 2

    def test_get_history_session_not_found(self, client):
        resp = client.get("/docqa/sessions/nonexistent/history")
        assert resp.status_code == 404

    def test_get_history_default_limit(self, client, mock_service):
        """Default limit is 50; verify we get back all messages when count < 50."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some lengthy content here for testing purposes.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is in the document?"},
        )

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        body = resp.json()
        # default limit=50 allows all messages to be returned
        assert body["count"] == 2


class TestClearChatHistory:
    """DELETE /docqa/sessions/{session_id}/history"""

    def test_clear_history_success(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Some lengthy content here for testing purposes.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is this document about?"},
        )

        # Confirm history exists
        resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert resp.json()["count"] > 0

        # Clear history
        resp = client.delete(f"/docqa/sessions/{session_id}/history")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["cleared"] is True

        # Confirm history is empty
        resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert resp.json()["count"] == 0

    def test_clear_history_session_not_found(self, client):
        resp = client.delete("/docqa/sessions/nonexistent/history")
        assert resp.status_code == 404

    def test_clear_history_already_empty(self, client):
        """Clearing history on a session with no messages should still succeed."""
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.delete(f"/docqa/sessions/{session_id}/history")
        assert resp.status_code == 200
        assert resp.json()["cleared"] is True


# ===================================================================
# 7. Response structure
# ===================================================================

class TestResponseStructure:
    """Verify that all endpoints include the expected top-level keys."""

    def test_create_session_has_correlation_id(self, client):
        body = _create_session(client)
        assert "correlation_id" in body

    def test_list_sessions_has_correlation_id(self, client):
        resp = client.get("/docqa/sessions")
        assert "correlation_id" in resp.json()

    def test_delete_session_has_correlation_id(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        resp = client.delete(f"/docqa/sessions/{session_id}")
        assert "correlation_id" in resp.json()

    def test_ask_response_has_processing_time(self, client, mock_service):
        created = _create_session(client)
        session_id = created["session"]["id"]
        _add_document(client, session_id, content="Content for testing purposes here.")

        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What is the content?"},
        )
        body = resp.json()
        assert "processing_time_ms" in body["response"]
        assert isinstance(body["response"]["processing_time_ms"], int)

    def test_history_response_has_count(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        body = resp.json()
        assert "count" in body
        assert "messages" in body


# ===================================================================
# 8. Edge cases and integration-like scenarios
# ===================================================================

class TestEdgeCases:
    """Miscellaneous edge cases and integration-like scenarios."""

    def test_ask_on_deleted_session(self, client):
        """Asking a question after the session was deleted returns 404."""
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "Can you answer this?"},
        )
        assert resp.status_code == 404

    def test_add_document_after_session_deleted(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.post(
            f"/docqa/sessions/{session_id}/documents",
            json={"name": "doc.pdf", "content": "A" * 50},
        )
        assert resp.status_code == 404

    def test_history_after_session_deleted(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert resp.status_code == 404

    def test_clear_history_after_session_deleted(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.delete(f"/docqa/sessions/{session_id}/history")
        assert resp.status_code == 404

    def test_feedback_after_session_deleted(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/some-msg/feedback",
            json={"feedback_type": "helpful"},
        )
        assert resp.status_code == 404

    def test_regenerate_after_session_deleted(self, client):
        created = _create_session(client)
        session_id = created["session"]["id"]
        client.delete(f"/docqa/sessions/{session_id}")

        resp = client.post(
            f"/docqa/sessions/{session_id}/messages/some-msg/regenerate",
            json={},
        )
        assert resp.status_code == 404

    def test_multiple_sessions_isolated(self, client, mock_service):
        """Documents added to one session do not appear in another."""
        s1 = _create_session(client, "Session 1")["session"]["id"]
        s2 = _create_session(client, "Session 2")["session"]["id"]

        _add_document(client, s1, name="doc_s1.pdf")

        resp = client.get(f"/docqa/sessions/{s2}")
        assert len(resp.json()["session"]["documents"]) == 0

        resp = client.get(f"/docqa/sessions/{s1}")
        assert len(resp.json()["session"]["documents"]) == 1

    def test_full_workflow(self, client, mock_service):
        """End-to-end: create session -> add doc -> ask -> feedback -> history -> clear."""
        # Create
        body = _create_session(client, "Full Workflow")
        session_id = body["session"]["id"]

        # Add document
        _add_document(client, session_id, name="report.pdf", content="Revenue grew 20% in Q4. " * 10)

        # Ask
        mock_llm = MagicMock()
        mock_llm.complete.return_value = LLM_RESPONSE_PAYLOAD
        mock_service._llm_client = mock_llm

        ask_resp = client.post(
            f"/docqa/sessions/{session_id}/ask",
            json={"question": "What was the revenue growth?"},
        )
        assert ask_resp.status_code == 200
        message_id = ask_resp.json()["response"]["message"]["id"]

        # Feedback
        fb_resp = client.post(
            f"/docqa/sessions/{session_id}/messages/{message_id}/feedback",
            json={"feedback_type": "helpful", "comment": "Great answer!"},
        )
        assert fb_resp.status_code == 200

        # History
        hist_resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert hist_resp.json()["count"] == 2

        # Clear history
        clear_resp = client.delete(f"/docqa/sessions/{session_id}/history")
        assert clear_resp.status_code == 200

        # Verify cleared
        hist_resp = client.get(f"/docqa/sessions/{session_id}/history")
        assert hist_resp.json()["count"] == 0

        # Delete session
        del_resp = client.delete(f"/docqa/sessions/{session_id}")
        assert del_resp.status_code == 200

        # Confirm gone
        get_resp = client.get(f"/docqa/sessions/{session_id}")
        assert get_resp.status_code == 404


# =============================================================================
# SECURITY TESTS
# =============================================================================


class TestDocQAPagination:
    """Pagination parameter constraints on list endpoints."""

    def test_list_sessions_limit_too_high(self, client):
        resp = client.get("/docqa/sessions?limit=999")
        assert resp.status_code == 422

    def test_list_sessions_limit_zero(self, client):
        resp = client.get("/docqa/sessions?limit=0")
        assert resp.status_code == 422

    def test_list_sessions_default_limit_works(self, client):
        resp = client.get("/docqa/sessions")
        assert resp.status_code == 200
