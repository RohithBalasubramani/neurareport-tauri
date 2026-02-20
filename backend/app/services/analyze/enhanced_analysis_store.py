# mypy: ignore-errors
"""
Persistence layer for enhanced analysis results and collaboration artifacts.

Stores JSON payloads under the configured state directory so analysis data
survives process restarts.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

from backend.app.services.config import get_settings
from backend.app.schemas.analyze.enhanced_analysis import EnhancedAnalysisResult


class EnhancedAnalysisStore:
    """File-backed store for enhanced analysis artifacts."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.results_dir = base_dir / "results"
        self.context_dir = base_dir / "context"
        self.comments_dir = base_dir / "comments"
        self.versions_dir = base_dir / "versions"
        self.shares_dir = base_dir / "shares"
        self._lock = threading.Lock()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.comments_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.shares_dir.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, payload: Any) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        data = json.dumps(payload, ensure_ascii=True, default=str)
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path.write_text(data, encoding="utf-8")
            tmp_path.replace(path)

    def _read_json(self, path: Path, default: Any) -> Any:
        try:
            if not path.exists():
                return default
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            return default

    def _result_path(self, analysis_id: str) -> Path:
        return self.results_dir / f"{analysis_id}.json"

    def _context_path(self, analysis_id: str) -> Path:
        return self.context_dir / f"{analysis_id}.json"

    def _comments_path(self, analysis_id: str) -> Path:
        return self.comments_dir / f"{analysis_id}.json"

    def _versions_path(self, analysis_id: str) -> Path:
        return self.versions_dir / f"{analysis_id}.json"

    def _share_path(self, share_id: str) -> Path:
        return self.shares_dir / f"{share_id}.json"

    # ---------------------------------------------------------------------
    # Results
    # ---------------------------------------------------------------------
    def save_result(self, result: EnhancedAnalysisResult) -> None:
        if hasattr(result, "model_dump"):
            payload = result.model_dump(mode="json")
        else:
            payload = json.loads(result.json())
        self._write_json(self._result_path(result.analysis_id), payload)

    def load_result(self, analysis_id: str) -> Optional[EnhancedAnalysisResult]:
        payload = self._read_json(self._result_path(analysis_id), default=None)
        if not payload:
            return None
        try:
            if hasattr(EnhancedAnalysisResult, "model_validate"):
                return EnhancedAnalysisResult.model_validate(payload)
            return EnhancedAnalysisResult.parse_obj(payload)
        except Exception:
            return None

    def save_context(self, analysis_id: str, text_content: str) -> None:
        if not analysis_id:
            return
        payload = {"analysis_id": analysis_id, "text": text_content or ""}
        self._write_json(self._context_path(analysis_id), payload)

    def load_context(self, analysis_id: str) -> str:
        payload = self._read_json(self._context_path(analysis_id), default=None)
        if isinstance(payload, dict):
            return str(payload.get("text") or "")
        return ""

    # ---------------------------------------------------------------------
    # Comments, versions, shares
    # ---------------------------------------------------------------------
    def save_comments(self, analysis_id: str, payload: list[dict[str, Any]]) -> None:
        self._write_json(self._comments_path(analysis_id), payload)

    def load_comments(self, analysis_id: str) -> list[dict[str, Any]]:
        return self._read_json(self._comments_path(analysis_id), default=[])

    def save_versions(self, analysis_id: str, payload: list[dict[str, Any]]) -> None:
        self._write_json(self._versions_path(analysis_id), payload)

    def load_versions(self, analysis_id: str) -> list[dict[str, Any]]:
        return self._read_json(self._versions_path(analysis_id), default=[])

    def save_share(self, payload: dict[str, Any]) -> None:
        share_id = str(payload.get("id") or "")
        if not share_id:
            return
        self._write_json(self._share_path(share_id), payload)

    def load_share(self, share_id: str) -> Optional[dict[str, Any]]:
        return self._read_json(self._share_path(share_id), default=None)

    def list_shares_for_analysis(self, analysis_id: str) -> list[dict[str, Any]]:
        shares: list[dict[str, Any]] = []
        try:
            for share_file in self.shares_dir.glob("*.json"):
                payload = self._read_json(share_file, default=None)
                if payload and payload.get("analysis_id") == analysis_id:
                    shares.append(payload)
        except Exception:
            return []
        return shares


_STORE: Optional[EnhancedAnalysisStore] = None


def get_analysis_store() -> EnhancedAnalysisStore:
    """Return singleton analysis store."""
    global _STORE
    if _STORE is None:
        settings = get_settings()
        base_dir = settings.state_dir / "analysis_v2"
        _STORE = EnhancedAnalysisStore(base_dir)
    return _STORE
