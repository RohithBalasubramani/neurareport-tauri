"""Tests for Document Q&A feedback and regenerate functionality."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from backend.app.schemas.docqa import (
    AskRequest,
    AskResponse,
    ChatMessage,
    Citation,
    DocQASession,
    DocumentReference,
    FeedbackRequest,
    FeedbackType,
    MessageFeedback,
    MessageRole,
    RegenerateRequest,
)
from backend.app.services.docqa.service import DocumentQAService


class TestFeedbackSchemas:
    """Test feedback-related schemas."""

    def test_feedback_type_enum(self):
        """Test FeedbackType enum values."""
        assert FeedbackType.HELPFUL.value == "helpful"
        assert FeedbackType.NOT_HELPFUL.value == "not_helpful"

    def test_message_feedback_model(self):
        """Test MessageFeedback model."""
        feedback = MessageFeedback(
            feedback_type=FeedbackType.HELPFUL,
            comment="Great answer!"
        )
        assert feedback.feedback_type == FeedbackType.HELPFUL
        assert feedback.comment == "Great answer!"
        assert feedback.timestamp is not None

    def test_chat_message_with_feedback(self):
        """Test ChatMessage model with feedback field."""
        feedback = MessageFeedback(
            feedback_type=FeedbackType.NOT_HELPFUL,
        )
        message = ChatMessage(
            id="msg-123",
            role=MessageRole.ASSISTANT,
            content="Test response",
            feedback=feedback,
        )
        assert message.feedback is not None
        assert message.feedback.feedback_type == FeedbackType.NOT_HELPFUL

    def test_chat_message_without_feedback(self):
        """Test ChatMessage model without feedback field."""
        message = ChatMessage(
            id="msg-123",
            role=MessageRole.ASSISTANT,
            content="Test response",
        )
        assert message.feedback is None

    def test_feedback_request_model(self):
        """Test FeedbackRequest model."""
        request = FeedbackRequest(
            feedback_type=FeedbackType.HELPFUL,
            comment="Useful information"
        )
        assert request.feedback_type == FeedbackType.HELPFUL
        assert request.comment == "Useful information"

    def test_regenerate_request_model(self):
        """Test RegenerateRequest model."""
        request = RegenerateRequest(
            include_citations=False,
            max_response_length=1500
        )
        assert request.include_citations is False
        assert request.max_response_length == 1500

    def test_regenerate_request_defaults(self):
        """Test RegenerateRequest default values."""
        request = RegenerateRequest()
        assert request.include_citations is True
        assert request.max_response_length == 2000


class TestDocQAServiceFeedback:
    """Test feedback functionality in DocumentQAService."""

    @pytest.fixture
    def mock_state_store(self):
        """Create a mock state store."""
        mock_store = MagicMock()
        mock_store._lock = MagicMock()
        mock_store._lock.__enter__ = MagicMock(return_value=None)
        mock_store._lock.__exit__ = MagicMock(return_value=None)
        return mock_store

    @pytest.fixture
    def sample_session(self):
        """Create a sample session with messages."""
        return {
            "id": "session-123",
            "name": "Test Session",
            "documents": [
                {
                    "id": "doc-1",
                    "name": "test.txt",
                    "content_preview": "Test content...",
                    "full_content": "Test content for document",
                    "page_count": 1,
                    "added_at": datetime.utcnow().isoformat(),
                }
            ],
            "messages": [
                {
                    "id": "msg-user-1",
                    "role": "user",
                    "content": "What is in the document?",
                    "citations": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {},
                    "feedback": None,
                },
                {
                    "id": "msg-assistant-1",
                    "role": "assistant",
                    "content": "The document contains test content.",
                    "citations": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"confidence": 0.9},
                    "feedback": None,
                },
            ],
            "context_window": 10,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def test_submit_feedback_helpful(self, mock_state_store, sample_session):
        """Test submitting helpful feedback."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {
                "docqa_sessions": {"session-123": sample_session}
            }

            service = DocumentQAService()
            request = FeedbackRequest(feedback_type=FeedbackType.HELPFUL)

            result = service.submit_feedback("session-123", "msg-assistant-1", request)

            assert result is not None
            assert result.feedback is not None
            assert result.feedback.feedback_type == FeedbackType.HELPFUL

    def test_submit_feedback_not_helpful(self, mock_state_store, sample_session):
        """Test submitting not helpful feedback."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {
                "docqa_sessions": {"session-123": sample_session}
            }

            service = DocumentQAService()
            request = FeedbackRequest(
                feedback_type=FeedbackType.NOT_HELPFUL,
                comment="Answer was not accurate"
            )

            result = service.submit_feedback("session-123", "msg-assistant-1", request)

            assert result is not None
            assert result.feedback is not None
            assert result.feedback.feedback_type == FeedbackType.NOT_HELPFUL
            assert result.feedback.comment == "Answer was not accurate"

    def test_submit_feedback_session_not_found(self, mock_state_store):
        """Test submitting feedback for non-existent session."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {"docqa_sessions": {}}

            service = DocumentQAService()
            request = FeedbackRequest(feedback_type=FeedbackType.HELPFUL)

            result = service.submit_feedback("nonexistent", "msg-1", request)

            assert result is None

    def test_submit_feedback_message_not_found(self, mock_state_store, sample_session):
        """Test submitting feedback for non-existent message."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {
                "docqa_sessions": {"session-123": sample_session}
            }

            service = DocumentQAService()
            request = FeedbackRequest(feedback_type=FeedbackType.HELPFUL)

            result = service.submit_feedback("session-123", "nonexistent-msg", request)

            assert result is None


class TestDocQAServiceRegenerate:
    """Test regenerate functionality in DocumentQAService."""

    @pytest.fixture
    def mock_state_store(self):
        """Create a mock state store."""
        mock_store = MagicMock()
        mock_store._lock = MagicMock()
        mock_store._lock.__enter__ = MagicMock(return_value=None)
        mock_store._lock.__exit__ = MagicMock(return_value=None)
        return mock_store

    @pytest.fixture
    def sample_session_with_docs(self):
        """Create a sample session with documents and messages."""
        return {
            "id": "session-456",
            "name": "Test Session with Docs",
            "documents": [
                {
                    "id": "doc-1",
                    "name": "test.txt",
                    "content_preview": "Test content...",
                    "full_content": "This is the full content of the test document.",
                    "page_count": 1,
                    "added_at": datetime.utcnow().isoformat(),
                }
            ],
            "messages": [
                {
                    "id": "msg-user-1",
                    "role": "user",
                    "content": "What is in the document?",
                    "citations": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {},
                    "feedback": None,
                },
                {
                    "id": "msg-assistant-1",
                    "role": "assistant",
                    "content": "The document contains test content.",
                    "citations": [],
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"confidence": 0.9},
                    "feedback": None,
                },
            ],
            "context_window": 10,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def test_regenerate_session_not_found(self, mock_state_store):
        """Test regenerating response for non-existent session."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {"docqa_sessions": {}}

            service = DocumentQAService()
            request = RegenerateRequest()

            result = service.regenerate_response("nonexistent", "msg-1", request)

            assert result is None

    def test_regenerate_message_not_found(self, mock_state_store, sample_session_with_docs):
        """Test regenerating response for non-existent message."""
        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {
                "docqa_sessions": {"session-456": sample_session_with_docs}
            }

            service = DocumentQAService()
            request = RegenerateRequest()

            result = service.regenerate_response("session-456", "nonexistent-msg", request)

            assert result is None

    def test_regenerate_with_mock_llm(self, mock_state_store, sample_session_with_docs):
        """Test regenerating response with mocked LLM."""
        mock_llm_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"answer": "Regenerated answer.", "citations": [], "confidence": 0.85, "follow_up_questions": []}'
                    }
                }
            ],
            "usage": {"total_tokens": 100},
        }

        with patch("backend.app.services.docqa.service._state_store", return_value=mock_state_store):
            mock_state_store._read_state.return_value = {
                "docqa_sessions": {"session-456": sample_session_with_docs}
            }

            service = DocumentQAService()
            mock_client = MagicMock()
            mock_client.complete.return_value = mock_llm_response
            service._llm_client = mock_client

            request = RegenerateRequest(include_citations=False)
            result = service.regenerate_response("session-456", "msg-assistant-1", request)

            assert result is not None
            assert result.message.content == "Regenerated answer."
            assert result.message.metadata.get("regenerated") is True
            assert result.message.feedback is None  # Feedback should be cleared


class TestDocQAAPIEndpoints:
    """Test API endpoint integration."""

    def test_feedback_request_validation(self):
        """Test feedback request validation."""
        # Valid request
        valid_request = FeedbackRequest(feedback_type=FeedbackType.HELPFUL)
        assert valid_request.feedback_type == FeedbackType.HELPFUL

        # Invalid feedback type should raise error
        with pytest.raises(ValueError):
            FeedbackRequest(feedback_type="invalid")

    def test_regenerate_request_validation(self):
        """Test regenerate request validation."""
        # Valid request
        valid_request = RegenerateRequest(max_response_length=2000)
        assert valid_request.max_response_length == 2000

        # Invalid max_response_length (too low)
        with pytest.raises(ValueError):
            RegenerateRequest(max_response_length=50)

        # Invalid max_response_length (too high)
        with pytest.raises(ValueError):
            RegenerateRequest(max_response_length=20000)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
