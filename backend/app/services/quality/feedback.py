from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("neura.quality.feedback")


class FeedbackType(str, Enum):
    """Supported feedback signal types."""

    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    STAR_RATING = "star_rating"
    CORRECTION = "correction"
    QUALITY_FLAG = "quality_flag"


class FeedbackEntry(BaseModel):
    """A single piece of user feedback."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str  # e.g. "docqa", "widget", "agent", "report"
    entity_id: str
    feedback_type: FeedbackType
    rating: Optional[float] = None  # 1-5 for star ratings
    correction_text: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    user_id: Optional[str] = None


class FeedbackCollector:
    """Thread-safe collector for user feedback with state-store persistence.

    Feedback entries are keyed by ``"<source>:<entity_id>"`` so that
    consumers can query all feedback related to a specific generated
    artifact.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, List[FeedbackEntry]] = {}
        self._lock = threading.Lock()
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(self, entry: FeedbackEntry) -> FeedbackEntry:
        """Record a new feedback entry (thread-safe).

        Returns the entry (with its generated ``id`` populated).
        """
        key = f"{entry.source}:{entry.entity_id}"
        with self._lock:
            self._entries.setdefault(key, []).append(entry)
            self._persist()
        logger.info(
            "feedback_submitted",
            extra={
                "event": "feedback_submitted",
                "feedback_id": entry.id,
                "source": entry.source,
                "entity_id": entry.entity_id,
                "feedback_type": entry.feedback_type.value,
            },
        )
        return entry

    def get_feedback(
        self, source: str, entity_id: str
    ) -> List[FeedbackEntry]:
        """Return all feedback for a specific source + entity."""
        key = f"{source}:{entity_id}"
        with self._lock:
            return list(self._entries.get(key, []))

    def list_feedback(
        self, source: Optional[str] = None, limit: int = 100
    ) -> List[FeedbackEntry]:
        """Return recent feedback entries, optionally filtered by source.

        Results are sorted newest-first and capped at *limit*.
        """
        with self._lock:
            all_entries: List[FeedbackEntry] = []
            for entries in self._entries.values():
                for entry in entries:
                    if source is None or entry.source == source:
                        all_entries.append(entry)

        # Sort newest first
        all_entries.sort(key=lambda e: e.created_at, reverse=True)
        return all_entries[:limit]

    # ------------------------------------------------------------------
    # Reward mapping
    # ------------------------------------------------------------------

    def to_reward(self, entry: FeedbackEntry) -> float:
        """Convert a feedback entry into a scalar reward signal.

        Mapping
        -------
        THUMBS_UP    ->  +1.0
        THUMBS_DOWN  ->  -1.0
        STAR_RATING  ->  (rating - 3) / 2.0   (maps 1-5 to -1.0 .. +1.0)
        CORRECTION   ->  -0.5
        QUALITY_FLAG ->  -0.3
        """
        if entry.feedback_type == FeedbackType.THUMBS_UP:
            return 1.0
        if entry.feedback_type == FeedbackType.THUMBS_DOWN:
            return -1.0
        if entry.feedback_type == FeedbackType.STAR_RATING:
            rating = entry.rating if entry.rating is not None else 3.0
            return (rating - 3.0) / 2.0
        if entry.feedback_type == FeedbackType.CORRECTION:
            return -0.5
        if entry.feedback_type == FeedbackType.QUALITY_FLAG:
            return -0.3
        return 0.0

    def aggregate_rewards(self, source: str, entity_id: str) -> float:
        """Average reward across all feedback for the given entity."""
        entries = self.get_feedback(source, entity_id)
        if not entries:
            return 0.0
        return sum(self.to_reward(e) for e in entries) / len(entries)

    # ------------------------------------------------------------------
    # Persistence (follows docqa/service.py state-store pattern)
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write current entries to the state store."""
        try:
            from backend.app.repositories.state import store as state_store_module

            store = state_store_module.state_store
            with store._lock:
                state = store._read_state() or {}
                if not isinstance(state, dict):
                    state = {}
                data: Dict[str, List[dict]] = {
                    k: [e.model_dump(mode="json") for e in v]
                    for k, v in self._entries.items()
                }
                state["quality_feedback"] = data
                store._write_state(state)
        except Exception as exc:
            logger.warning(
                "feedback_persist_failed",
                extra={"event": "feedback_persist_failed", "error": str(exc)},
            )

    def _load(self) -> None:
        """Restore entries from the state store on startup."""
        try:
            from backend.app.repositories.state import store as state_store_module

            store = state_store_module.state_store
            with store._lock:
                state = store._read_state() or {}
            if not isinstance(state, dict):
                return
            raw: Dict[str, list] = state.get("quality_feedback", {})
            if not isinstance(raw, dict):
                return
            for key, entries in raw.items():
                if not isinstance(entries, list):
                    continue
                self._entries[key] = [
                    FeedbackEntry(**e) for e in entries
                ]
        except Exception as exc:
            logger.warning(
                "feedback_load_failed",
                extra={"event": "feedback_load_failed", "error": str(exc)},
            )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_collector: Optional[FeedbackCollector] = None
_collector_lock = threading.Lock()


def get_feedback_collector() -> FeedbackCollector:
    """Return the process-wide :class:`FeedbackCollector` singleton."""
    global _collector
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = FeedbackCollector()
    return _collector
