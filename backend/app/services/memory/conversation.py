"""Per-user session context with prompt injection for conversation memory."""
from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import store as state_store_module

logger = logging.getLogger("neura.memory.conversation")

# ---------------------------------------------------------------------------
# State store accessor (docqa pattern)
# ---------------------------------------------------------------------------

def _state_store():
    return state_store_module.state_store


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class MemoryEntry:
    """A single conversation turn stored in memory."""

    role: str
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "metadata": self.metadata,
            "relevance_score": self.relevance_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryEntry:
        ts = data.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=ts,
            session_id=data.get("session_id", ""),
            metadata=data.get("metadata", {}),
            relevance_score=data.get("relevance_score", 1.0),
        )


# ---------------------------------------------------------------------------
# ConversationMemory
# ---------------------------------------------------------------------------

class ConversationMemory:
    """Manages per-user conversation sessions with prompt injection."""

    MAX_HISTORY = 100
    MAX_CONTEXT_TOKENS = 4000

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # _sessions layout: { user_id: { session_id: { "name": ..., "created_at": ..., "entries": [...] } } }
        self._load()

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def create_session(self, user_id: str, name: str = "") -> str:
        """Create a new conversation session for a user. Returns session_id."""
        session_id = str(uuid.uuid4())
        if user_id not in self._sessions:
            self._sessions[user_id] = {}

        session_name = name or f"Session {len(self._sessions[user_id]) + 1}"
        self._sessions[user_id][session_id] = {
            "name": session_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "entries": [],
        }
        logger.info(
            "Created conversation session",
            extra={"event": "session_created", "user_id": user_id, "session_id": session_id},
        )
        self._persist()
        return session_id

    def get_session(self, user_id: str, session_id: str) -> List[MemoryEntry]:
        """Return all entries for a specific session."""
        user_sessions = self._sessions.get(user_id, {})
        session = user_sessions.get(session_id)
        if session is None:
            return []
        return [MemoryEntry.from_dict(e) for e in session.get("entries", [])]

    def list_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a user with summary metadata."""
        user_sessions = self._sessions.get(user_id, {})
        result: List[Dict[str, Any]] = []
        for sid, data in user_sessions.items():
            result.append({
                "session_id": sid,
                "name": data.get("name", ""),
                "created_at": data.get("created_at", ""),
                "entry_count": len(data.get("entries", [])),
            })
        return result

    # ------------------------------------------------------------------
    # Memory operations
    # ------------------------------------------------------------------

    def add_entry(self, user_id: str, session_id: str, entry: MemoryEntry) -> None:
        """Append an entry to a session, trimming to MAX_HISTORY."""
        user_sessions = self._sessions.get(user_id, {})
        session = user_sessions.get(session_id)
        if session is None:
            logger.warning(
                "Session not found for add_entry",
                extra={"event": "session_not_found", "user_id": user_id, "session_id": session_id},
            )
            return

        entry.session_id = session_id
        session["entries"].append(entry.to_dict())

        # Trim oldest entries if over limit
        if len(session["entries"]) > self.MAX_HISTORY:
            session["entries"] = session["entries"][-self.MAX_HISTORY:]

        self._persist()

    def get_context(
        self,
        user_id: str,
        session_id: str,
        current_query: str,
        max_entries: int = 10,
    ) -> List[MemoryEntry]:
        """Return the most recent entries with optional keyword relevance scoring."""
        entries = self.get_session(user_id, session_id)
        if not entries:
            return []

        # Simple keyword overlap scoring
        query_tokens = set(current_query.lower().split())
        if query_tokens:
            for entry in entries:
                content_tokens = set(entry.content.lower().split())
                overlap = len(query_tokens & content_tokens)
                # Blend recency (base 0.5) with keyword relevance
                entry.relevance_score = 0.5 + (0.5 * min(overlap / max(len(query_tokens), 1), 1.0))

        # Sort by relevance (descending), then take most recent among top-scored
        scored = sorted(entries, key=lambda e: e.relevance_score, reverse=True)
        top = scored[:max_entries]
        # Re-sort by timestamp so context reads chronologically
        top.sort(key=lambda e: e.timestamp)
        return top

    # ------------------------------------------------------------------
    # Prompt injection
    # ------------------------------------------------------------------

    def inject_context(
        self,
        messages: List[Dict[str, Any]],
        user_id: str,
        session_id: str,
        current_query: str,
    ) -> List[Dict[str, Any]]:
        """Prepend a system message with relevant history, entity context, and user preferences."""
        context_entries = self.get_context(user_id, session_id, current_query)

        parts: List[str] = []

        # Conversation history
        if context_entries:
            history_lines = []
            for entry in context_entries:
                role_label = "User" if entry.role == "user" else "Assistant"
                history_lines.append(f"{role_label}: {entry.content}")
            parts.append("## Conversation History\n" + "\n".join(history_lines))

        # Entity context (lazy import to avoid circular dependencies)
        try:
            from backend.app.services.memory.entity_tracker import get_entity_tracker
            entity_ctx = get_entity_tracker().to_context_string(user_id, limit=5)
            if entity_ctx:
                parts.append("## Entity Context\n" + entity_ctx)
        except Exception:
            logger.debug("Entity tracker unavailable for context injection", extra={"event": "entity_tracker_skip"})

        # User preferences
        try:
            from backend.app.services.memory.preferences import get_user_preferences
            pref_ctx = get_user_preferences().to_prompt_context(user_id)
            if pref_ctx:
                parts.append("## User Preferences\n" + pref_ctx)
        except Exception:
            logger.debug("User preferences unavailable for context injection", extra={"event": "preferences_skip"})

        if not parts:
            return messages

        system_content = "\n\n".join(parts)
        context_message = {"role": "system", "content": system_content}

        return [context_message] + list(messages)

    # ------------------------------------------------------------------
    # Persistence (state store pattern from docqa)
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write conversation memory to state store."""
        store = _state_store()
        with store._lock:
            state = store._read_state() or {}
            if not isinstance(state, dict):
                state = {}
            state["conversation_memory"] = self._sessions
            store._write_state(state)

    def _load(self) -> None:
        """Load conversation memory from state store."""
        try:
            store = _state_store()
            with store._lock:
                state = store._read_state() or {}
                data = state.get("conversation_memory", {}) if isinstance(state, dict) else {}
            if isinstance(data, dict):
                self._sessions = data
        except Exception:
            logger.warning("Failed to load conversation memory, starting fresh", extra={"event": "load_failed"})
            self._sessions = {}


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_instance: Optional[ConversationMemory] = None
_lock = threading.Lock()


def get_conversation_memory() -> ConversationMemory:
    """Return the module-level ConversationMemory singleton (lazy-init, thread-safe)."""
    global _instance
    with _lock:
        if _instance is None:
            _instance = ConversationMemory()
    return _instance
