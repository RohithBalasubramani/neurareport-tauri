"""Learned user preferences with context awareness."""
from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.repositories.state import store as state_store_module

logger = logging.getLogger("neura.memory.preferences")

# ---------------------------------------------------------------------------
# State store accessor (docqa pattern)
# ---------------------------------------------------------------------------

def _state_store():
    return state_store_module.state_store


# ---------------------------------------------------------------------------
# Known preference keys
# ---------------------------------------------------------------------------

PREFERENCE_KEYS: List[str] = [
    "analysis_depth",
    "chart_style",
    "report_format",
    "response_length",
    "visualization_type",
    "domain_focus",
]

# Mapping of feedback patterns to inferred preferences
_FEEDBACK_INFERENCE_MAP: Dict[str, Dict[str, str]] = {
    "detailed": {"key": "analysis_depth", "value": "comprehensive"},
    "brief": {"key": "analysis_depth", "value": "concise"},
    "concise": {"key": "analysis_depth", "value": "concise"},
    "chart": {"key": "chart_style", "value": "chart-heavy"},
    "table": {"key": "chart_style", "value": "tabular"},
    "technical": {"key": "report_format", "value": "technical"},
    "summary": {"key": "report_format", "value": "executive-summary"},
    "short": {"key": "response_length", "value": "short"},
    "long": {"key": "response_length", "value": "long"},
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class UserPreference:
    """A single learned or explicitly set user preference."""

    key: str
    value: str
    confidence: float = 0.5
    source: str = "inferred"  # "inferred" | "explicit"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserPreference:
        ts = data.get("updated_at")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return cls(
            key=data["key"],
            value=data.get("value", ""),
            confidence=data.get("confidence", 0.5),
            source=data.get("source", "inferred"),
            updated_at=ts,
        )


# ---------------------------------------------------------------------------
# Natural-language fragments for prompt context
# ---------------------------------------------------------------------------

_PREF_TEMPLATES: Dict[str, str] = {
    "analysis_depth": "{value} analysis",
    "chart_style": "{value} charts",
    "report_format": "{value} format",
    "response_length": "{value} responses",
    "visualization_type": "{value} visualizations",
    "domain_focus": "focus on {value}",
}


# ---------------------------------------------------------------------------
# UserPreferences
# ---------------------------------------------------------------------------

class UserPreferences:
    """Manages learned and explicit user preferences per user."""

    def __init__(self) -> None:
        # { user_id: { preference_key: UserPreference } }
        self._prefs: Dict[str, Dict[str, UserPreference]] = {}
        self._load()

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, user_id: str, key: str) -> Optional[UserPreference]:
        """Return a preference by key, or None if not set."""
        return self._prefs.get(user_id, {}).get(key)

    def set_explicit(self, user_id: str, key: str, value: str) -> UserPreference:
        """Explicitly set a preference with full confidence."""
        if user_id not in self._prefs:
            self._prefs[user_id] = {}

        pref = UserPreference(
            key=key,
            value=value,
            confidence=1.0,
            source="explicit",
            updated_at=datetime.now(timezone.utc),
        )
        self._prefs[user_id][key] = pref
        logger.info(
            "User preference set explicitly",
            extra={"event": "preference_set", "user_id": user_id, "key": key, "value": value},
        )
        self._persist()
        return pref

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def infer_from_feedback(self, user_id: str, feedback_entries: List[Any]) -> None:
        """Analyse feedback patterns and infer preferences.

        Each feedback entry is expected to have ``rating`` (e.g. "thumbs_up") and
        ``comment`` (str) attributes or dict keys.
        """
        if user_id not in self._prefs:
            self._prefs[user_id] = {}

        keyword_counts: Dict[str, int] = {}

        for entry in feedback_entries:
            # Support both dict and object access
            if isinstance(entry, dict):
                rating = entry.get("rating", "")
                comment = entry.get("comment", "")
            else:
                rating = getattr(entry, "rating", "")
                comment = getattr(entry, "comment", "")

            # Only consider positive feedback for inference
            if rating not in ("thumbs_up", "positive", "good"):
                continue

            comment_lower = str(comment).lower()
            for keyword, mapping in _FEEDBACK_INFERENCE_MAP.items():
                if keyword in comment_lower:
                    compound_key = f"{mapping['key']}:{mapping['value']}"
                    keyword_counts[compound_key] = keyword_counts.get(compound_key, 0) + 1

        # Apply inferences that appear at least twice
        for compound_key, count in keyword_counts.items():
            if count < 2:
                continue
            pref_key, pref_value = compound_key.split(":", 1)
            existing = self._prefs[user_id].get(pref_key)
            # Do not override explicit preferences
            if existing is not None and existing.source == "explicit":
                continue
            confidence = min(0.3 + 0.1 * count, 0.9)
            self._prefs[user_id][pref_key] = UserPreference(
                key=pref_key,
                value=pref_value,
                confidence=confidence,
                source="inferred",
                updated_at=datetime.now(timezone.utc),
            )
            logger.info(
                "Inferred user preference from feedback",
                extra={
                    "event": "preference_inferred",
                    "user_id": user_id,
                    "key": pref_key,
                    "value": pref_value,
                    "confidence": confidence,
                },
            )

        self._persist()

    def infer_from_choice(self, user_id: str, key: str, chosen_value: str) -> UserPreference:
        """Increment confidence on a preference based on user choice."""
        if user_id not in self._prefs:
            self._prefs[user_id] = {}

        existing = self._prefs[user_id].get(key)
        now = datetime.now(timezone.utc)

        if existing is not None and existing.value == chosen_value:
            # Boost confidence (cap at 0.95 for inferred)
            new_confidence = min(existing.confidence + 0.1, 0.95)
            existing.confidence = new_confidence
            existing.updated_at = now
            self._persist()
            return existing

        # New or different value — start with moderate confidence
        pref = UserPreference(
            key=key,
            value=chosen_value,
            confidence=0.5,
            source="inferred",
            updated_at=now,
        )
        self._prefs[user_id][key] = pref
        self._persist()
        return pref

    # ------------------------------------------------------------------
    # Prompt context
    # ------------------------------------------------------------------

    def to_prompt_context(self, user_id: str) -> str:
        """Return a natural-language summary of user preferences for prompt injection.

        Returns empty string if no preferences are stored for the user.
        """
        user_prefs = self._prefs.get(user_id, {})
        if not user_prefs:
            return ""

        # Only include preferences with reasonable confidence
        fragments: List[str] = []
        for key in PREFERENCE_KEYS:
            pref = user_prefs.get(key)
            if pref is None or pref.confidence < 0.3:
                continue
            template = _PREF_TEMPLATES.get(key, "{value}")
            fragments.append(template.format(value=pref.value))

        if not fragments:
            return ""

        return "User prefers " + ", ".join(fragments) + "."

    # ------------------------------------------------------------------
    # Persistence (state store pattern from docqa)
    # ------------------------------------------------------------------

    def _persist(self) -> None:
        """Write user preferences to state store."""
        serialised: Dict[str, Dict[str, Any]] = {}
        for user_id, prefs in self._prefs.items():
            serialised[user_id] = {key: p.to_dict() for key, p in prefs.items()}

        store = _state_store()
        with store._lock:
            state = store._read_state() or {}
            if not isinstance(state, dict):
                state = {}
            state["user_preferences"] = serialised
            store._write_state(state)

    def _load(self) -> None:
        """Load user preferences from state store."""
        try:
            store = _state_store()
            with store._lock:
                state = store._read_state() or {}
                data = state.get("user_preferences", {}) if isinstance(state, dict) else {}
            if isinstance(data, dict):
                for user_id, prefs_raw in data.items():
                    if isinstance(prefs_raw, dict):
                        self._prefs[user_id] = {
                            key: UserPreference.from_dict(val)
                            for key, val in prefs_raw.items()
                            if isinstance(val, dict)
                        }
        except Exception:
            logger.warning("Failed to load user preferences, starting fresh", extra={"event": "load_failed"})
            self._prefs = {}


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_instance: Optional[UserPreferences] = None
_lock = threading.Lock()


def get_user_preferences() -> UserPreferences:
    """Return the module-level UserPreferences singleton (lazy-init, thread-safe)."""
    global _instance
    with _lock:
        if _instance is None:
            _instance = UserPreferences()
    return _instance
