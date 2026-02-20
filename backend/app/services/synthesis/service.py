"""Service for Multi-Document Synthesis using AI."""
from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from backend.app.services.llm.client import get_llm_client
from backend.app.services.utils.llm import (
    extract_json_from_llm_response,
    extract_json_array_from_llm_response,
)
from backend.app.repositories.state import store as state_store_module

from backend.app.schemas.synthesis import (
    DocumentType,
    Inconsistency,
    SynthesisDocument,
    SynthesisRequest,
    SynthesisResult,
    SynthesisSession,
)

logger = logging.getLogger("neura.domain.synthesis")


def _state_store():
    return state_store_module.state_store


class DocumentSynthesisService:
    """Service for synthesizing information from multiple documents."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def _read_sessions(self) -> Dict[str, Any]:
        store = _state_store()
        with store.transaction() as state:
            return dict(state.get("synthesis_sessions", {}) or {})

    def _update_sessions(self, updater: Callable[[Dict[str, Any]], None]) -> None:
        store = _state_store()
        with store.transaction() as state:
            sessions = state.get("synthesis_sessions", {})
            if not isinstance(sessions, dict):
                sessions = {}
            updater(sessions)
            state["synthesis_sessions"] = sessions

    def create_session(
        self,
        name: str,
        correlation_id: Optional[str] = None,
    ) -> SynthesisSession:
        """Create a new synthesis session."""
        logger.info("Creating synthesis session", extra={"correlation_id": correlation_id})

        session = SynthesisSession(
            id=str(uuid.uuid4()),
            name=name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self._update_sessions(lambda sessions: sessions.__setitem__(session.id, session.model_dump(mode="json")))

        return session

    def get_session(self, session_id: str) -> Optional[SynthesisSession]:
        """Get a synthesis session by ID."""
        sessions = self._read_sessions()
        session_data = sessions.get(session_id)

        if session_data:
            return SynthesisSession(**session_data)
        return None

    def list_sessions(self) -> List[SynthesisSession]:
        """List all synthesis sessions."""
        sessions = self._read_sessions()
        return [SynthesisSession(**data) for data in sessions.values()]

    def add_document(
        self,
        session_id: str,
        name: str,
        content: str,
        doc_type: DocumentType,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[SynthesisDocument]:
        """Add a document to a synthesis session."""
        logger.info(
            f"Adding document to session {session_id}",
            extra={"correlation_id": correlation_id},
        )

        session = self.get_session(session_id)
        if not session:
            return None

        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        document = SynthesisDocument(
            id=str(uuid.uuid4()),
            name=name,
            doc_type=doc_type,
            content_hash=content_hash,
            extracted_text=content[:50000],  # Limit stored text
            metadata=metadata or {},
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

    def find_inconsistencies(
        self,
        session_id: str,
        correlation_id: Optional[str] = None,
    ) -> List[Inconsistency]:
        """Find inconsistencies between documents in a session."""
        logger.info(
            f"Finding inconsistencies in session {session_id}",
            extra={"correlation_id": correlation_id},
        )

        session = self.get_session(session_id)
        if not session or len(session.documents) < 2:
            return []

        # Build document summaries for comparison
        doc_summaries = []
        for doc in session.documents:
            doc_summaries.append({
                "id": doc.id,
                "name": doc.name,
                "content": doc.extracted_text[:5000] if doc.extracted_text else "",
            })

        prompt = f"""Analyze these documents for inconsistencies, contradictions, or conflicting information.

DOCUMENTS:
{json.dumps(doc_summaries, indent=2)}

Find any:
1. Numerical discrepancies (different values for the same metric)
2. Date/time conflicts
3. Contradictory statements
4. Conflicting facts or claims
5. Missing information in one doc that's present in another

Return a JSON array of inconsistencies:
[
  {{
    "description": "Brief description of the inconsistency",
    "severity": "low|medium|high|critical",
    "documents_involved": ["doc_id_1", "doc_id_2"],
    "field_or_topic": "The field or topic with inconsistency",
    "values": {{"doc_id_1": "value1", "doc_id_2": "value2"}},
    "suggested_resolution": "How to resolve this"
  }}
]

Return ONLY the JSON array. Return [] if no inconsistencies found."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="find_inconsistencies",
                temperature=0.2,
            )

            content = response["choices"][0]["message"]["content"]
            inconsistencies_data = extract_json_array_from_llm_response(content, default=[])

            if inconsistencies_data:
                inconsistencies = []

                for i, item in enumerate(inconsistencies_data):
                    inconsistencies.append(Inconsistency(
                        id=str(uuid.uuid4()),
                        description=item.get("description", ""),
                        severity=item.get("severity", "medium"),
                        documents_involved=item.get("documents_involved", []),
                        field_or_topic=item.get("field_or_topic", ""),
                        values=item.get("values", {}),
                        suggested_resolution=item.get("suggested_resolution"),
                    ))

                # Update session with inconsistencies
                session.inconsistencies = inconsistencies
                session.updated_at = datetime.now(timezone.utc)

                self._update_sessions(
                    lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json"))
                )

                return inconsistencies

        except Exception as exc:
            logger.error(f"Inconsistency detection failed: {exc}")

        return []

    def synthesize(
        self,
        session_id: str,
        request: SynthesisRequest,
        correlation_id: Optional[str] = None,
    ) -> Optional[SynthesisResult]:
        """Synthesize information from all documents in a session."""
        logger.info(
            f"Synthesizing documents in session {session_id}",
            extra={"correlation_id": correlation_id},
        )

        session = self.get_session(session_id)
        if not session or not session.documents:
            return None

        session.status = "processing"

        # Prepare document content for synthesis
        doc_contents = []
        for doc in session.documents:
            doc_contents.append({
                "id": doc.id,
                "name": doc.name,
                "type": doc.doc_type.value,
                "content": doc.extracted_text[:8000] if doc.extracted_text else "",
            })

        focus_str = ""
        if request.focus_topics:
            focus_str = f"\nFOCUS TOPICS: {', '.join(request.focus_topics)}"

        format_instructions = {
            "structured": "Return a structured JSON with sections, key_points, and summary",
            "narrative": "Return a cohesive narrative summary combining all information",
            "comparison": "Return a comparison table/matrix of key points across documents",
        }

        prompt = f"""Synthesize information from these documents into a comprehensive summary.

DOCUMENTS:
{json.dumps(doc_contents, indent=2)}
{focus_str}

OUTPUT FORMAT: {request.output_format}
{format_instructions.get(request.output_format, "")}

MAX LENGTH: {request.max_length} characters

Requirements:
1. Combine information intelligently, avoiding redundancy
2. Highlight key insights and findings
3. Note any patterns or trends across documents
4. {'Include source references for each point' if request.include_sources else 'Do not include source references'}

Return a JSON object:
{{
  "title": "Synthesis title",
  "executive_summary": "2-3 sentence overview",
  "sections": [
    {{
      "heading": "Section heading",
      "content": "Section content",
      "sources": ["doc_id_1", "doc_id_2"]
    }}
  ],
  "key_insights": ["insight 1", "insight 2"],
  "cross_references": [
    {{"topic": "topic", "documents": ["doc1", "doc2"], "finding": "what was found"}}
  ],
  "confidence": 0.9
}}

Return ONLY the JSON object."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="document_synthesis",
                temperature=0.3,
            )

            content = response["choices"][0]["message"]["content"]
            synthesis_data = extract_json_from_llm_response(content, default=None)

            if synthesis_data:
                # Build source references
                source_refs = []
                for doc in session.documents:
                    source_refs.append({
                        "document_id": doc.id,
                        "document_name": doc.name,
                        "document_type": doc.doc_type.value,
                    })

                result = SynthesisResult(
                    session_id=session_id,
                    synthesis=synthesis_data,
                    inconsistencies=session.inconsistencies,
                    source_references=source_refs,
                    confidence=synthesis_data.get("confidence", 0.8),
                    generated_at=datetime.now(timezone.utc),
                )

                # Update session
                session.synthesis_result = synthesis_data
                session.status = "completed"
                session.updated_at = datetime.now(timezone.utc)

                self._update_sessions(
                    lambda sessions: sessions.__setitem__(session_id, session.model_dump(mode="json"))
                )

                return result

        except Exception as exc:
            logger.error(f"Synthesis failed: {exc}")
            session.status = "error"

        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a synthesis session."""
        deleted = False

        def _delete(sessions: Dict[str, Any]) -> None:
            nonlocal deleted
            if session_id in sessions:
                del sessions[session_id]
                deleted = True

        self._update_sessions(_delete)
        return deleted
