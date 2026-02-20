"""Service for Document Q&A Chat using AI."""
from __future__ import annotations

import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from backend.app.services.llm.client import get_llm_client
from backend.app.services.utils.llm import extract_json_from_llm_response
from backend.app.repositories.state import store as state_store_module

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

logger = logging.getLogger("neura.domain.docqa")


def _state_store():
    return state_store_module.state_store


class DocumentQAService:
    """Service for document-based Q&A chat."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def _read_sessions(self) -> Dict[str, Any]:
        store = _state_store()
        # Use the StateStore's low-level primitives so tests can patch _read_state/_write_state.
        with store._lock:
            state = store._read_state() or {}
            sessions = state.get("docqa_sessions", {}) if isinstance(state, dict) else {}
            return dict(sessions or {})

    def _update_sessions(self, updater: Callable[[Dict[str, Any]], None]) -> None:
        store = _state_store()
        with store._lock:
            state = store._read_state() or {}
            if not isinstance(state, dict):
                state = {}
            sessions = state.get("docqa_sessions", {})
            if not isinstance(sessions, dict):
                sessions = {}
            updater(sessions)
            state["docqa_sessions"] = sessions
            store._write_state(state)

    def create_session(
        self,
        name: str,
        correlation_id: Optional[str] = None,
    ) -> DocQASession:
        """Create a new Q&A session."""
        logger.info("Creating DocQA session", extra={"correlation_id": correlation_id})

        session = DocQASession(
            id=str(uuid.uuid4()),
            name=name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._update_sessions(lambda sessions: sessions.__setitem__(session.id, session.model_dump(mode="json")))

        return session

    def get_session(self, session_id: str) -> Optional[DocQASession]:
        """Get a Q&A session by ID."""
        sessions = self._read_sessions()
        session_data = sessions.get(session_id)

        if session_data:
            return DocQASession(**session_data)
        return None

    def list_sessions(self) -> List[DocQASession]:
        """List all Q&A sessions."""
        sessions = self._read_sessions()
        return [DocQASession(**data) for data in sessions.values()]

    def add_document(
        self,
        session_id: str,
        name: str,
        content: str,
        page_count: Optional[int] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[DocumentReference]:
        """Add a document to a Q&A session."""
        logger.info(
            f"Adding document to DocQA session {session_id}",
            extra={"correlation_id": correlation_id},
        )

        session = self.get_session(session_id)
        if not session:
            return None

        document = DocumentReference(
            id=str(uuid.uuid4()),
            name=name,
            content_preview=content[:500] + "..." if len(content) > 500 else content,
            full_content=content[:100000],  # Limit stored content
            page_count=page_count,
            added_at=datetime.now(timezone.utc),
        )

        session.documents.append(document)
        session.updated_at = datetime.now(timezone.utc)

        self._update_sessions(lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json")))

        return document

    def remove_document(self, session_id: str, document_id: str) -> bool:
        """Remove a document from a session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.documents = [d for d in session.documents if d.id != document_id]
        session.updated_at = datetime.now(timezone.utc)

        self._update_sessions(lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json")))

        return True

    def ask(
        self,
        session_id: str,
        request: AskRequest,
        correlation_id: Optional[str] = None,
    ) -> Optional[AskResponse]:
        """Ask a question about the documents in a session."""
        start_time = time.time()
        logger.info(
            f"Processing question in session {session_id}",
            extra={"correlation_id": correlation_id},
        )

        session = self.get_session(session_id)
        if not session:
            return None

        if not session.documents:
            # Return a helpful message if no documents
            no_docs_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content="No documents have been added to this session yet. Please add documents first.",
                citations=[],
                timestamp=datetime.now(timezone.utc),
            )
            return AskResponse(
                message=no_docs_message,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        # Add user message to history
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            role=MessageRole.USER,
            content=request.question,
            timestamp=datetime.now(timezone.utc),
        )
        session.messages.append(user_message)

        # Build context from documents with total budget limit
        # Limit total context to prevent memory explosion with many documents
        MAX_TOTAL_CONTEXT = 50000  # ~50KB total context budget
        MAX_PER_DOC = 15000  # Max per document

        doc_context = []
        total_chars = 0
        for doc in session.documents:
            remaining_budget = MAX_TOTAL_CONTEXT - total_chars
            if remaining_budget <= 0:
                doc_context.append(f"[Document: {doc.name} (ID: {doc.id})]\n(Skipped due to context limit)")
                continue
            # Take the lesser of per-doc limit or remaining budget
            chunk_size = min(MAX_PER_DOC, remaining_budget)
            content_chunk = doc.full_content[:chunk_size]
            doc_context.append(f"[Document: {doc.name} (ID: {doc.id})]\n{content_chunk}")
            total_chars += len(content_chunk)

        # Build conversation history (last N messages)
        window = max(1, session.context_window)
        history_messages = session.messages[-(window * 2):-1]  # Exclude current message
        history_text = ""
        if history_messages:
            history_parts = []
            for msg in history_messages:
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                history_parts.append(f"{role}: {msg.content}")
            history_text = f"\nPREVIOUS CONVERSATION:\n" + "\n".join(history_parts)

        citation_instruction = ""
        if request.include_citations:
            citation_instruction = """
For each statement, provide citations in this format:
Include a "citations" array in your response with:
- document_id: The document ID
- document_name: The document name
- quote: The relevant quote from the document
- relevance_score: How relevant (0-1)
"""

        prompt = f"""You are a helpful document Q&A assistant. Answer questions based ONLY on the provided documents.

DOCUMENTS:
{chr(10).join(doc_context)}
{history_text}

CURRENT QUESTION: {request.question}

INSTRUCTIONS:
1. Answer based ONLY on information in the documents
2. If the information is not in the documents, say so clearly
3. Be concise but thorough (max {request.max_response_length} characters)
4. Reference specific documents when appropriate
{citation_instruction}

Return a JSON object:
{{
  "answer": "Your comprehensive answer here",
  "citations": [
    {{
      "document_id": "doc_id",
      "document_name": "doc_name",
      "quote": "relevant quote",
      "relevance_score": 0.9
    }}
  ],
  "confidence": 0.9,
  "follow_up_questions": ["Suggested follow-up 1", "Suggested follow-up 2"]
}}

Return ONLY the JSON object."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="docqa_answer",
                temperature=0.2,
            )

            content = response["choices"][0]["message"]["content"]
            response_data = extract_json_from_llm_response(content, default=None)

            if response_data is not None:

                # Build citations
                citations = []
                for cit in response_data.get("citations", []):
                    citations.append(Citation(
                        document_id=cit.get("document_id", ""),
                        document_name=cit.get("document_name", ""),
                        quote=cit.get("quote", ""),
                        relevance_score=cit.get("relevance_score", 1.0),
                    ))

                # Create assistant message
                assistant_message = ChatMessage(
                    id=str(uuid.uuid4()),
                    role=MessageRole.ASSISTANT,
                    content=response_data.get("answer", "I couldn't generate an answer."),
                    citations=citations,
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "confidence": response_data.get("confidence", 0.8),
                        "follow_up_questions": response_data.get("follow_up_questions", []),
                    },
                )

                # Add to session history
                session.messages.append(assistant_message)
                session.updated_at = datetime.now(timezone.utc)

                self._update_sessions(
                    lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json"))
                )

                processing_time = int((time.time() - start_time) * 1000)

                return AskResponse(
                    message=assistant_message,
                    processing_time_ms=processing_time,
                    tokens_used=response.get("usage", {}).get("total_tokens"),
                )

        except Exception as exc:
            logger.error(f"DocQA failed: {exc}")

            error_message = ChatMessage(
                id=str(uuid.uuid4()),
                role=MessageRole.ASSISTANT,
                content=f"I encountered an error processing your question. Please try again.",
                timestamp=datetime.now(timezone.utc),
            )

            return AskResponse(
                message=error_message,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        return None

    def submit_feedback(
        self,
        session_id: str,
        message_id: str,
        request: FeedbackRequest,
        correlation_id: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """Submit feedback for a message."""
        logger.info(
            "docqa_feedback_recorded",
            extra={
                "correlation_id": correlation_id,
                "session_id": session_id,
                "message_id": message_id,
                "feedback_type": request.feedback_type,
            },
        )

        session = self.get_session(session_id)
        if not session:
            return None

        target = next((msg for msg in session.messages if msg.id == message_id), None)
        if not target:
            return None

        feedback = MessageFeedback(
            feedback_type=request.feedback_type,
            timestamp=datetime.now(timezone.utc),
            comment=request.comment,
        )
        target.feedback = feedback
        meta = dict(target.metadata or {})
        meta["feedback"] = feedback.model_dump(mode="json")
        target.metadata = meta
        session.updated_at = datetime.now(timezone.utc)

        self._update_sessions(lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json")))

        return target

    def regenerate_response(
        self,
        session_id: str,
        message_id: str,
        request: RegenerateRequest,
        correlation_id: Optional[str] = None,
    ) -> Optional[AskResponse]:
        """Regenerate the assistant response for a given message."""
        start_time = time.time()

        session = self.get_session(session_id)
        if not session:
            return None

        message_index = None
        for idx, msg in enumerate(session.messages):
            if msg.id == message_id:
                message_index = idx
                break
        if message_index is None:
            return None

        question_message = None
        question_index = None
        for idx in range(message_index - 1, -1, -1):
            candidate = session.messages[idx]
            if candidate.role == MessageRole.USER:
                question_message = candidate
                question_index = idx
                break
        if not question_message:
            return None

        question = question_message.content

        if not session.documents:
            return None

        # Build context from documents with total budget limit
        MAX_TOTAL_CONTEXT = 50000  # ~50KB total context budget
        MAX_PER_DOC = 15000  # Max per document

        doc_context = []
        total_chars = 0
        for doc in session.documents:
            remaining_budget = MAX_TOTAL_CONTEXT - total_chars
            if remaining_budget <= 0:
                doc_context.append(f"[Document: {doc.name} (ID: {doc.id})]\n(Skipped due to context limit)")
                continue
            chunk_size = min(MAX_PER_DOC, remaining_budget)
            content_chunk = doc.full_content[:chunk_size]
            doc_context.append(f"[Document: {doc.name} (ID: {doc.id})]\n{content_chunk}")
            total_chars += len(content_chunk)

        history_window = session.context_window * 2
        history_start = max(0, (question_index or 0) - history_window)
        history_messages = session.messages[history_start:question_index]
        history_text = ""
        if history_messages:
            history_parts = []
            for msg in history_messages:
                role = "User" if msg.role == MessageRole.USER else "Assistant"
                history_parts.append(f"{role}: {msg.content}")
            history_text = "\nPREVIOUS CONVERSATION:\n" + "\n".join(history_parts)

        citation_instruction = ""
        if request.include_citations:
            citation_instruction = """
For each statement, provide citations in this format:
Include a "citations" array in your response with:
- document_id: The document ID
- document_name: The document name
- quote: The relevant quote from the document
- relevance_score: How relevant (0-1)
"""

        prompt = f"""You are a helpful document Q&A assistant. Answer questions based ONLY on the provided documents.

DOCUMENTS:
{chr(10).join(doc_context)}
{history_text}

CURRENT QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on information in the documents
2. If the information is not in the documents, say so clearly
3. Be concise but thorough (max {request.max_response_length} characters)
4. Reference specific documents when appropriate
5. Provide a DIFFERENT perspective or additional details compared to previous answers
{citation_instruction}

Return a JSON object:
{{
  "answer": "Your comprehensive answer here",
  "citations": [
    {{
      "document_id": "doc_id",
      "document_name": "doc_name",
      "quote": "relevant quote",
      "relevance_score": 0.9
    }}
  ],
  "confidence": 0.9,
  "follow_up_questions": ["Suggested follow-up 1", "Suggested follow-up 2"]
}}

Return ONLY the JSON object."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="docqa_regenerate",
                temperature=0.5,
            )

            content = response["choices"][0]["message"]["content"]
            response_data = extract_json_from_llm_response(content, default=None)

            if response_data is None:
                raise ValueError("No JSON payload returned from LLM")

            citations = []
            for cit in response_data.get("citations", []):
                citations.append(Citation(
                    document_id=cit.get("document_id", ""),
                    document_name=cit.get("document_name", ""),
                    quote=cit.get("quote", ""),
                    relevance_score=cit.get("relevance_score", 1.0),
                ))

            assistant_message = ChatMessage(
                id=message_id,
                role=MessageRole.ASSISTANT,
                content=response_data.get("answer", "I couldn't generate an answer."),
                citations=citations,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "confidence": response_data.get("confidence", 0.8),
                    "follow_up_questions": response_data.get("follow_up_questions", []),
                    "regenerated": True,
                },
                feedback=None,
            )

            session.messages[message_index] = assistant_message
            session.updated_at = datetime.now(timezone.utc)

            self._update_sessions(
                lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json"))
            )

            processing_time = int((time.time() - start_time) * 1000)

            return AskResponse(
                message=assistant_message,
                processing_time_ms=processing_time,
                tokens_used=response.get("usage", {}).get("total_tokens"),
            )

        except Exception as exc:
            logger.error(f"DocQA regenerate failed: {exc}")
            raise RuntimeError("Failed to regenerate response") from exc

    def get_chat_history(
        self,
        session_id: str,
        limit: int = 50,
    ) -> List[ChatMessage]:
        """Get chat history for a session."""
        session = self.get_session(session_id)
        if not session:
            return []

        return session.messages[-limit:] if limit else session.messages

    def clear_history(self, session_id: str) -> bool:
        """Clear chat history for a session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.messages = []
        session.updated_at = datetime.now(timezone.utc)

        self._update_sessions(lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json")))

        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a Q&A session."""
        deleted = False

        def _updater(sessions: Dict[str, Any]) -> None:
            nonlocal deleted
            if session_id in sessions:
                del sessions[session_id]
                deleted = True

        self._update_sessions(_updater)
        return deleted
