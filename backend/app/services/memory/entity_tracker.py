"""Entity mention tracking and resolution across conversations."""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import store as state_store_module

logger = logging.getLogger("neura.memory.entity_tracker")

# ---------------------------------------------------------------------------
# State store accessor (docqa pattern)
# ---------------------------------------------------------------------------

def _state_store():
    return state_store_module.state_store


# ---------------------------------------------------------------------------
# Anaphoric reference tokens that should resolve to the most recent entity
# ---------------------------------------------------------------------------

_ANAPHORIC_TOKENS = frozenset({
    "it", "its", "that", "that one", "the same", "the same one",
    "this", "this one", "those", "them", "these",
})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class TrackedEntity:
    """An entity mention tracked across conversation sessions."""

    name: str
    entity_type: str
    first_mentioned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_mentioned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mention_count: int = 1
    aliases: List[str] = field(default_factory=list)
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entity_type": self.entity_type,
            "first_mentioned": self.first_mentioned.isoformat(),
            "last_mentioned": self.last_mentioned.isoformat(),
            "mention_count": self.mention_count,
            "aliases": list(self.aliases),
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TrackedEntity:
        first = data.get("first_mentioned")
        last = data.get("last_mentioned")
        if isinstance(first, str):
            first = datetime.fromisoformat(first)
        elif first is None:
            first = datetime.now(timezone.utc)
        if isinstance(last, str):
            last = datetime.fromisoformat(last)
        elif last is None:
            last = datetime.now(timezone.utc)
        return cls(
            name=data["name"],
            entity_type=data.get("entity_type", "unknown"),
            first_mentioned=first,
            last_mentioned=last,
            mention_count=data.get("mention_count", 1),
            aliases=data.get("aliases", []),
            context=data.get("context", ""),
        )


# ---------------------------------------------------------------------------
# EntityTracker
# ---------------------------------------------------------------------------

class EntityTracker:
    """Tracks entity mentions per user and resolves anaphoric references."""

    def __init__(self) -> None:
        # { user_id: { normalised_entity_name: TrackedEntity } }
        self._entities: Dict[str, Dict[str, TrackedEntity]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Tracking
    # ------------------------------------------------------------------

    def track_mention(
        self,
        user_id: str,
        session_id: str,
        entity_name: str,
        entity_type: str = "unknown",
    ) -> TrackedEntity:
        """Create or update a tracked entity for a user."""
        if user_id not in self._entities:
            self._entities[user_id] = {}

        key = entity_name.lower().strip()
        now = datetime.now(timezone.utc)

        existing = self._entities[user_id].get(key)
        if existing is not None:
            existing.mention_count += 1
            existing.last_mentioned = now
            if entity_type != "unknown":
                existing.entity_type = entity_type
            logger.debug(
                "Updated entity mention",
                extra={"event": "entity_updated", "user_id": user_id, "entity": key, "count": existing.mention_count},
            )
            self._persist()
            return existing

        entity = TrackedEntity(
            name=entity_name,
            entity_type=entity_type,
            first_mentioned=now,
            last_mentioned=now,
            mention_count=1,
            context=session_id,
        )
        self._entities[user_id][key] = entity
        logger.info(
            "Tracked new entity",
            extra={"event": "entity_tracked", "user_id": user_id, "entity": key, "type": entity_type},
        )
        self._persist()
        return entity

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve_reference(self, user_id: str, reference: str) -> Optional[TrackedEntity]:
        """Resolve anaphoric references ('it', 'that one', etc.) to the most recently mentioned entity.

        Also checks entity aliases for direct name matches.
        """
        user_entities = self._entities.get(user_id, {})
        if not user_entities:
            return None

        ref_lower = reference.lower().strip()

        # If the reference is an anaphoric token, return the most recently mentioned entity
        if ref_lower in _ANAPHORIC_TOKENS:
            return self._most_recent(user_entities)

        # Direct key match
        if ref_lower in user_entities:
            return user_entities[ref_lower]

        # Alias match
        for entity in user_entities.values():
            for alias in entity.aliases:
                if alias.lower().strip() == ref_lower:
                    return entity

        # Substring / partial match as a fallback
        for key, entity in user_entities.items():
            if ref_lower in key or key in ref_lower:
                return entity

        return None

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    def get_recent_entities(self, user_id: str, limit: int = 10) -> List[TrackedEntity]:
        """Return tracked entities sorted by last_mentioned descending."""
        user_entities = self._entities.get(user_id, {})
        sorted_entities = sorted(
            user_entities.values(),
            key=lambda e: e.last_mentioned,
            reverse=True,
        )
        return sorted_entities[:limit]

    def to_context_string(self, user_id: str, limit: int = 5) -> str:
        """Format recent entities for prompt injection.

        Returns a string like: 'Recently discussed: Pump-01 (pump), TRF-02 (transformer), ...'
        Returns empty string if no entities are tracked.
        """
        recent = self.get_recent_entities(user_id, limit=limit)
        if not recent:
            return ""
        items = [f"{e.name} ({e.entity_type})" for e in recent]
        return "Recently discussed: " + ", ".join(items)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _most_recent(entities: Dict[str, TrackedEntity]) -> Optional[TrackedEntity]:
        if not entities:
            return None
        return max(entities.values(), key=lambda e: e.last_mentioned)

    # ------------------------------------------------------------------
    # Persistence (state store pattern from docqa)
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write entity tracker state to the state store."""
        serialised: Dict[str, Dict[str, Any]] = {}
        for user_id, entities in self._entities.items():
            serialised[user_id] = {key: ent.to_dict() for key, ent in entities.items()}

        store = _state_store()
        with store._lock:
            state = store._read_state() or {}
            if not isinstance(state, dict):
                state = {}
            state["entity_tracker"] = serialised
            store._write_state(state)

    def _load(self) -> None:
        """Load entity tracker state from the state store."""
        try:
            store = _state_store()
            with store._lock:
                state = store._read_state() or {}
                data = state.get("entity_tracker", {}) if isinstance(state, dict) else {}
            if isinstance(data, dict):
                for user_id, entities_raw in data.items():
                    if isinstance(entities_raw, dict):
                        self._entities[user_id] = {
                            key: TrackedEntity.from_dict(val)
                            for key, val in entities_raw.items()
                            if isinstance(val, dict)
                        }
        except Exception:
            logger.warning("Failed to load entity tracker, starting fresh", extra={"event": "load_failed"})
            self._entities = {}


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_instance: Optional[EntityTracker] = None
_lock = threading.Lock()


def get_entity_tracker() -> EntityTracker:
    """Return the module-level EntityTracker singleton (lazy-init, thread-safe)."""
    global _instance
    with _lock:
        if _instance is None:
            _instance = EntityTracker()
    return _instance
