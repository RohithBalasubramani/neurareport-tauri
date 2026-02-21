from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import shutil
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, Mapping, Optional, Sequence

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, Session, SQLModel, create_engine, select

from backend.app.utils.fs import write_json_atomic
from backend.app.utils.job_status import normalize_job_status as _normalize_job_status

logger = logging.getLogger("neura.state.store")

# Configuration constants
STATE_VERSION = 2
MAX_BACKUP_COUNT = 5
MAX_ACTIVITY_LOG_SIZE = 500
MAX_RUN_HISTORY = max(int(os.getenv("NR_RUN_HISTORY_LIMIT", "200") or "200"), 25)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _compute_checksum(data: dict) -> str:
    """Compute SHA256 checksum of state data."""
    content = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _normalize_mapping_keys(values: Optional[Iterable[str]]) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in values:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _normalize_email_list(values: Optional[Iterable[str]]) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in values:
        text = str(raw or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _json_roundtrip(value: dict) -> dict:
    if not isinstance(value, dict):
        return {}
    try:
        return json.loads(json.dumps(value, default=str))
    except Exception:
        return {}


class _StateSnapshot(SQLModel, table=True):
    __tablename__ = "state_snapshot"

    id: int = Field(default=1, primary_key=True)
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    version: int = Field(default=STATE_VERSION, index=True)
    checksum: str = Field(default="")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class _StateBackup(SQLModel, table=True):
    __tablename__ = "state_backups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    size_bytes: int = Field(default=0)


class StateStore:
    """
    File-backed store that keeps connection credentials (encrypted), template metadata,
    and the last-used selection for report generation.
    """

    _STATE_FILENAME = "state.json"
    _KEY_FILENAME = ".secret"

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        base = Path(
            os.getenv("NEURA_STATE_DIR")
            or (base_dir if base_dir is not None else Path(__file__).resolve().parents[3] / "state")
        )
        base.mkdir(parents=True, exist_ok=True)
        self._base_dir = base
        self._state_path = self._base_dir / self._STATE_FILENAME
        self._key_path = self._base_dir / self._KEY_FILENAME
        self._fernet: Optional[Fernet] = None
        self._lock = threading.RLock()
        self._cache: Optional[dict] = None
        self._cache_mtime: float = 0.0
        self._cache_enabled = os.getenv("NEURA_STATE_CACHE_ENABLED", "true").lower() in {"1", "true", "yes"}
        self._backups_enabled = os.getenv("NEURA_STATE_BACKUPS_ENABLED", "true").lower() in {"1", "true", "yes"}
        self._backup_interval_seconds = max(
            int(os.getenv("NEURA_STATE_BACKUP_INTERVAL_SECONDS", "60") or "60"),
            0,
        )
        self._last_backup_at = 0.0

    # ------------------------------------------------------------------
    # key management / encryption helpers
    # ------------------------------------------------------------------
    def _normalize_key(self, raw: str) -> bytes:
        key_bytes = raw.encode("utf-8")
        try:
            # raw may already be a fernet key
            Fernet(key_bytes)
            return key_bytes
        except ValueError:
            digest = hashlib.sha256(key_bytes).digest()
            return base64.urlsafe_b64encode(digest)

    def _ensure_key(self) -> Fernet:
        if self._fernet is not None:
            return self._fernet

        key_env = os.getenv("NEURA_STATE_SECRET")
        if key_env:
            key = self._normalize_key(key_env)
        elif self._key_path.exists():
            key = self._key_path.read_text(encoding="utf-8").strip().encode("utf-8")
        else:
            key = Fernet.generate_key()
            self._key_path.write_text(key.decode("utf-8"), encoding="utf-8")
            try:
                os.chmod(self._key_path, 0o600)
            except OSError:
                pass

        self._fernet = Fernet(key)
        return self._fernet

    def _encrypt(self, payload: dict) -> str:
        token = self._ensure_key().encrypt(json.dumps(payload).encode("utf-8"))
        return token.decode("utf-8")

    def _decrypt(self, token: str) -> dict:
        if not token:
            return {}
        try:
            data = self._ensure_key().decrypt(token.encode("utf-8"))
            return json.loads(data.decode("utf-8"))
        except (InvalidToken, json.JSONDecodeError, ValueError):
            return {}

    # ------------------------------------------------------------------
    # state IO helpers
    # ------------------------------------------------------------------
    def _default_state(self) -> dict:
        return {
            "connections": {},
            "templates": {},
            "last_used": {},
            "schedules": {},
            "jobs": {},
            "saved_charts": {},
            "runs": {},
            "activity_log": [],
            "favorites": {"templates": [], "connections": [], "documents": [], "spreadsheets": [], "dashboards": []},
            "user_preferences": {},
            "notifications": [],
            # AI Features
            "saved_queries": {},
            "query_history": [],
            "enrichment_sources": {},
            "enrichment_cache": {},
            "virtual_schemas": {},
            "docqa_sessions": {},
            "synthesis_sessions": {},
            "summaries": {},
            # Phase 1-10 Features
            "documents": {},
            "spreadsheets": {},
            "dashboards": {},
            "dashboard_widgets": {},
            "connectors": {},
            "connector_credentials": {},  # Encrypted credentials
            "workflows": {},
            "workflow_executions": {},
            "brand_kits": {},
            "themes": {},
            "library": {"documents": {}, "collections": {}, "tags": {}},
            "export_jobs": {},
            "docai_results": {},
            # Job system enhancements (state-of-the-art patterns)
            "idempotency_keys": {},  # {key: {job_id, response, request_hash, created_at, expires_at}}
            "dead_letter_jobs": {},  # {job_id: {original_job, failure_history, moved_at}}
        }

    # All collections that MUST be dicts keyed by "id".
    # If any is stored as a list (legacy migration / corruption), it's auto-normalized.
    _DICT_KEYED_COLLECTIONS = (
        "connections", "templates", "schedules", "jobs", "saved_charts", "runs",
        "saved_queries", "enrichment_sources", "enrichment_cache",
        "virtual_schemas", "docqa_sessions", "synthesis_sessions", "summaries",
        "documents", "spreadsheets", "dashboards", "dashboard_widgets",
        "connectors", "connector_credentials", "workflows", "workflow_executions",
        "brand_kits", "themes", "export_jobs", "docai_results",
        "idempotency_keys", "dead_letter_jobs",
    )

    def _apply_defaults(self, state: dict) -> dict:
        # Dict-keyed collections: setdefault + normalize list→dict
        for key in self._DICT_KEYED_COLLECTIONS:
            state.setdefault(key, {})
            if isinstance(state.get(key), list):
                state[key] = {
                    item["id"]: item for item in state[key]
                    if isinstance(item, dict) and "id" in item
                }
        state.setdefault("last_used", {})
        # List-typed collections (order matters, not keyed by id)
        state.setdefault("activity_log", [])
        state.setdefault("notifications", [])
        state.setdefault("query_history", [])
        # Nested dict structures (not id-keyed)
        state.setdefault("favorites", {"templates": [], "connections": [], "documents": [], "spreadsheets": [], "dashboards": []})
        state.setdefault("user_preferences", {})
        state.setdefault("library", {"documents": {}, "collections": {}, "tags": {}})
        return state

    def _read_state(self) -> dict:
        if self._cache_enabled and self._cache is not None:
            if not self._state_path.exists():
                return self._cache
            try:
                mtime = self._state_path.stat().st_mtime
            except OSError:
                return self._cache
            if mtime == self._cache_mtime:
                return self._cache

        if not self._state_path.exists():
            state = self._default_state()
            if self._cache_enabled:
                self._cache = state
                self._cache_mtime = 0.0
            return state
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
        except Exception:
            state = self._default_state()
            if self._cache_enabled:
                self._cache = state
                self._cache_mtime = 0.0
            return state
        if not isinstance(raw, dict):
            state = self._default_state()
            if self._cache_enabled:
                self._cache = state
                self._cache_mtime = 0.0
            return state
        state = self._apply_defaults(raw)
        if self._cache_enabled:
            self._cache = state
            try:
                self._cache_mtime = self._state_path.stat().st_mtime
            except OSError:
                self._cache_mtime = time.time()
        return state

    def _write_state(self, state: dict) -> None:
        # Create backup before write
        self._create_backup()
        # Add metadata
        state["_metadata"] = {
            "version": STATE_VERSION,
            "updated_at": _now_iso(),
            "checksum": _compute_checksum(state),
        }
        write_json_atomic(self._state_path, state, ensure_ascii=False, indent=2, step="state_store")
        if self._cache_enabled:
            self._cache = state
            try:
                self._cache_mtime = self._state_path.stat().st_mtime
            except OSError:
                self._cache_mtime = time.time()

    def _create_backup(self) -> None:
        """Create a backup of the current state file."""
        if not self._backups_enabled or self._backup_interval_seconds <= 0:
            return
        if not self._state_path.exists():
            return

        now = time.time()
        if self._last_backup_at and (now - self._last_backup_at) < self._backup_interval_seconds:
            return

        backup_dir = self._base_dir / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"state_{timestamp}.json"

        try:
            shutil.copy2(self._state_path, backup_path)
            self._last_backup_at = now
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

        # Clean up old backups
        self._cleanup_old_backups(backup_dir)

    def _cleanup_old_backups(self, backup_dir: Path) -> None:
        """Remove old backup files, keeping only MAX_BACKUP_COUNT."""
        try:
            backups = sorted(
                backup_dir.glob("state_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            for old_backup in backups[MAX_BACKUP_COUNT:]:
                try:
                    old_backup.unlink()
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")

    def restore_from_backup(self, backup_name: Optional[str] = None) -> bool:
        """Restore state from a backup file."""
        backup_dir = self._base_dir / "backups"
        if not backup_dir.exists():
            return False

        with self._lock:
            try:
                if backup_name:
                    # Prevent path traversal
                    safe_name = Path(backup_name).name  # strips directory components
                    if safe_name != backup_name or '..' in backup_name:
                        raise ValueError("Invalid backup name")
                    backup_path = backup_dir / safe_name
                else:
                    backups = sorted(
                        backup_dir.glob("state_*.json"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )
                    if not backups:
                        return False
                    backup_path = backups[0]

                if not backup_path.exists():
                    return False

                backup_data = json.loads(backup_path.read_text(encoding="utf-8"))
                if not isinstance(backup_data, dict):
                    return False

                shutil.copy2(backup_path, self._state_path)
                logger.info(f"Restored state from backup: {backup_path.name}")
                return True

            except Exception as e:
                logger.error(f"Failed to restore from backup: {e}")
                return False

    def list_backups(self) -> list[dict]:
        """List available backup files."""
        backup_dir = self._base_dir / "backups"
        if not backup_dir.exists():
            return []

        backups = []
        for backup_path in backup_dir.glob("state_*.json"):
            try:
                stat = backup_path.stat()
                backups.append({
                    "name": backup_path.name,
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                })
            except Exception:
                pass

        return sorted(backups, key=lambda b: b["created_at"], reverse=True)

    @contextmanager
    def transaction(self) -> Generator[dict, None, None]:
        """Context manager for atomic state transactions."""
        with self._lock:
            state = self._read_state()
            try:
                yield state
                # Sanitize non-JSON-serializable values (datetime, set, etc.)
                # before writing.  Uses the existing _json_roundtrip helper
                # which applies default=str during serialization.
                sanitized = _json_roundtrip(state)
                if sanitized:
                    state.clear()
                    state.update(sanitized)
                self._write_state(state)
            except Exception as e:
                logger.error(f"Transaction failed: {e}")
                raise

    def validate_state(self) -> tuple[bool, list[str]]:
        """Validate state file integrity."""
        errors = []
        with self._lock:
            try:
                state = self._read_state()
            except Exception as e:
                return False, [f"Failed to read state: {e}"]

            required = ["connections", "templates", "schedules", "jobs"]
            for section in required:
                if section not in state:
                    errors.append(f"Missing section: {section}")

        return len(errors) == 0, errors

    def get_stats(self) -> dict:
        """Get state store statistics."""
        with self._lock:
            state = self._read_state()
            return {
                "connections_count": len(state.get("connections", {})),
                "templates_count": len(state.get("templates", {})),
                "schedules_count": len(state.get("schedules", {})),
                "jobs_count": len(state.get("jobs", {})),
                "backups_count": len(self.list_backups()),
                "state_file_exists": self._state_path.exists(),
            }

    # ------------------------------------------------------------------
    # connection helpers
    # ------------------------------------------------------------------
    def list_connections(self) -> list[dict]:
        with self._lock:
            state = self._read_state()
            return [self._sanitize_connection(rec) for rec in state["connections"].values()]

    def get_connection_record(self, conn_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            return state["connections"].get(conn_id)

    def get_latest_connection(self) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            if not state["connections"]:
                return None
            records = list(state["connections"].values())
            records.sort(key=lambda rec: rec.get("updated_at") or "", reverse=True)
            best = records[0]
            return {
                "id": best.get("id"),
                "database_path": best.get("database_path"),
                "name": best.get("name"),
                "db_type": best.get("db_type"),
            }

    def get_connection_secrets(self, conn_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            rec = state["connections"].get(conn_id)
            if not rec:
                return None
            secrets = self._decrypt(rec.get("secret") or "")
            fallback = {
                "database_path": rec.get("database_path"),
                "db_type": rec.get("db_type"),
                "name": rec.get("name"),
            }
            if not secrets:
                return fallback if fallback.get("database_path") else None
            secrets["database_path"] = rec.get("database_path")
            secrets["db_type"] = rec.get("db_type")
            secrets["name"] = rec.get("name")
            return secrets

    def upsert_connection(
        self,
        *,
        conn_id: Optional[str],
        name: str,
        db_type: str,
        database_path: str,
        secret_payload: Optional[dict],
        status: Optional[str] = None,
        latency_ms: Optional[float] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> dict:
        conn_id = conn_id or str(uuid.uuid4())
        now = _now_iso()
        previous_path: Optional[str] = None
        new_path: Optional[str] = None
        with self._lock:
            state = self._read_state()
            record = state["connections"].get(conn_id, {})
            previous_path = record.get("database_path")
            created_at = record.get("created_at", now)
            # determine secret (reuse previous unless new payload supplied)
            if secret_payload is not None:
                secret_value = self._encrypt(secret_payload)
            else:
                secret_value = record.get("secret") or ""
            if database_path:
                db_path_value = str(database_path)
            else:
                db_path_value = str(record.get("database_path") or "")
            new_path = db_path_value
            record.update(
                {
                    "id": conn_id,
                    "name": name,
                    "db_type": db_type,
                    "database_path": db_path_value,
                    "secret": secret_value,
                    "updated_at": now,
                    "created_at": created_at,
                    "status": status or record.get("status") or "unknown",
                    "last_connected_at": record.get("last_connected_at"),
                    "last_latency_ms": record.get("last_latency_ms"),
                    "tags": sorted(set(tags or record.get("tags") or [])),
                }
            )
            state["connections"][conn_id] = record
            self._write_state(state)
            sanitized = self._sanitize_connection(record)
        if previous_path and new_path and str(previous_path) != str(new_path):
            try:
                from backend.app.repositories.dataframes import dataframe_store

                dataframe_store.invalidate_connection(conn_id)
            except Exception:
                pass
        return sanitized

    def record_connection_ping(
        self,
        conn_id: str,
        *,
        status: str,
        detail: Optional[str],
        latency_ms: Optional[float],
    ) -> None:
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = state["connections"].get(conn_id)
            if not record:
                return
            record["status"] = status
            record["last_connected_at"] = now
            record["last_latency_ms"] = latency_ms
            record["last_detail"] = detail
            record["updated_at"] = now
            state["connections"][conn_id] = record
            self._write_state(state)

    def delete_connection(self, conn_id: str) -> bool:
        with self._lock:
            state = self._read_state()
            if conn_id not in state["connections"]:
                return False
            del state["connections"][conn_id]
            if state.get("last_used", {}).get("connection_id") == conn_id:
                state["last_used"]["connection_id"] = None
            schedules = state.get("schedules") or {}
            schedule_ids = [sid for sid, rec in schedules.items() if rec.get("connection_id") == conn_id]
            for sid in schedule_ids:
                schedules.pop(sid, None)
            state["schedules"] = schedules
            jobs = state.get("jobs") or {}
            job_ids = [jid for jid, rec in jobs.items() if rec.get("connection_id") == conn_id]
            for jid in job_ids:
                jobs.pop(jid, None)
            state["jobs"] = jobs
            runs = state.get("runs") or {}
            run_ids = [rid for rid, rec in runs.items() if rec.get("connection_id") == conn_id]
            for rid in run_ids:
                runs.pop(rid, None)
            state["runs"] = runs
            self._write_state(state)
        try:
            from backend.app.repositories.dataframes import dataframe_store

            dataframe_store.invalidate_connection(conn_id)
        except Exception:
            pass
        return True

    def _sanitize_connection(self, rec: Dict[str, Any]) -> dict:
        return {
            "id": rec.get("id"),
            "name": rec.get("name"),
            "db_type": rec.get("db_type"),
            "status": rec.get("status") or "unknown",
            "lastConnected": rec.get("last_connected_at"),
            "lastLatencyMs": rec.get("last_latency_ms"),
            "hasCredentials": bool(rec.get("secret")),
            "summary": self._summarize_path(rec.get("database_path")),
            "tags": list(rec.get("tags") or []),
            "createdAt": rec.get("created_at"),
            "updatedAt": rec.get("updated_at"),
            "details": rec.get("last_detail"),
        }

    def _summarize_path(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        try:
            p = Path(path)
            if p.name:
                return p.name
            return str(p)
        except Exception:
            return path

    # ------------------------------------------------------------------
    # template helpers
    # ------------------------------------------------------------------
    def list_templates(self) -> list[dict]:
        with self._lock:
            state = self._read_state()
            return [self._sanitize_template(rec) for rec in state["templates"].values()]

    def get_template_record(self, template_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            return state["templates"].get(template_id)

    def upsert_template(
        self,
        template_id: str,
        *,
        name: str,
        status: str,
        artifacts: Optional[dict] = None,
        tags: Optional[Iterable[str]] = None,
        connection_id: Optional[str] = None,
        mapping_keys: Optional[Iterable[str]] = None,
        template_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict:
        tid = template_id
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = state["templates"].get(tid, {})
            created_at = record.get("created_at", now)
            existing_artifacts = record.get("artifacts") or {}
            merged_artifacts = {**existing_artifacts, **(artifacts or {})}
            kind = template_type or record.get("kind") or "pdf"
            record.update(
                {
                    "id": tid,
                    "name": name,
                    "status": status,
                    "description": description if description is not None else record.get("description"),
                    "artifacts": {k: v for k, v in merged_artifacts.items() if v},
                    "updated_at": now,
                    "created_at": created_at,
                    "tags": sorted(set(tags or record.get("tags") or [])),
                    "last_connection_id": connection_id or record.get("last_connection_id"),
                    "kind": kind,
                }
            )
            if mapping_keys is not None:
                record["mapping_keys"] = _normalize_mapping_keys(mapping_keys)
            elif "mapping_keys" not in record:
                record["mapping_keys"] = []
            state["templates"][tid] = record
            self._write_state(state)
            return self._sanitize_template(record)

    def record_template_run(self, template_id: str, connection_id: Optional[str]) -> None:
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = state["templates"].get(template_id)
            if not record:
                return
            record["last_run_at"] = now
            if connection_id:
                record["last_connection_id"] = connection_id
            record["updated_at"] = now
            state["templates"][template_id] = record
            self._write_state(state)

    def delete_template(self, template_id: str) -> bool:
        with self._lock:
            state = self._read_state()
            removed = state["templates"].pop(template_id, None)
            if removed is None:
                return False
            last_used = state.get("last_used") or {}
            if last_used.get("template_id") == template_id:
                last_used["template_id"] = None
                last_used["updated_at"] = _now_iso()
                state["last_used"] = last_used
            saved_charts = state.get("saved_charts") or {}
            drop_ids = [sid for sid, rec in saved_charts.items() if rec.get("template_id") == template_id]
            for sid in drop_ids:
                saved_charts.pop(sid, None)
            schedules = state.get("schedules") or {}
            schedule_ids = [sid for sid, rec in schedules.items() if rec.get("template_id") == template_id]
            for sid in schedule_ids:
                schedules.pop(sid, None)
            state["schedules"] = schedules
            jobs = state.get("jobs") or {}
            job_ids = [jid for jid, rec in jobs.items() if rec.get("template_id") == template_id]
            for jid in job_ids:
                jobs.pop(jid, None)
            state["jobs"] = jobs
            runs = state.get("runs") or {}
            run_ids = [rid for rid, rec in runs.items() if rec.get("template_id") == template_id]
            for rid in run_ids:
                runs.pop(rid, None)
            state["runs"] = runs
            self._write_state(state)
            return True

    def update_template_generator(
        self,
        template_id: str,
        *,
        dialect: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        invalid: Optional[bool] = None,
        needs_user_fix: Optional[Iterable[Any]] = None,
        summary: Optional[Mapping[str, Any]] = None,
        dry_run: Optional[Any] = None,
        cached: Optional[bool] = None,
    ) -> Optional[dict]:
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = state["templates"].get(template_id)
            if not record:
                return None
            generator = dict(record.get("generator") or {})
            if dialect is not None:
                generator["dialect"] = dialect
            if params is not None:
                generator["params"] = dict(params)
            if invalid is not None:
                generator["invalid"] = bool(invalid)
            if needs_user_fix is not None:
                cleaned = []
                for item in needs_user_fix:
                    text = str(item).strip()
                    if text:
                        cleaned.append(text)
                generator["needs_user_fix"] = cleaned
            if summary is not None:
                generator["summary"] = dict(summary)
            if dry_run is not None:
                generator["dry_run"] = dry_run
            if cached is not None:
                generator["cached"] = bool(cached)
            generator["updated_at"] = now
            record["generator"] = generator
            record["updated_at"] = now
            state["templates"][template_id] = record
            self._write_state(state)
            return self._sanitize_template(record)

    def _sanitize_template(self, rec: Dict[str, Any]) -> dict:
        artifacts = rec.get("artifacts") or {}
        mapping_keys = rec.get("mapping_keys") or []
        generator_raw = rec.get("generator") or {}
        generator_meta: Optional[dict] = None
        if generator_raw:
            generator_meta = {
                "dialect": generator_raw.get("dialect"),
                "invalid": generator_raw.get("invalid"),
                "needsUserFix": list(generator_raw.get("needs_user_fix") or []),
                "params": generator_raw.get("params"),
                "summary": generator_raw.get("summary"),
                "dryRun": generator_raw.get("dry_run"),
                "cached": generator_raw.get("cached"),
                "updatedAt": generator_raw.get("updated_at"),
            }
            if generator_meta["needsUserFix"] is None:
                generator_meta["needsUserFix"] = []
            generator_meta = {
                key: value
                for key, value in generator_meta.items()
                if value is not None or key in {"invalid", "needsUserFix"}
            }
        return {
            "id": rec.get("id"),
            "name": rec.get("name"),
            "description": rec.get("description"),
            "status": rec.get("status"),
            "kind": rec.get("kind") or "pdf",
            "tags": list(rec.get("tags") or []),
            "createdAt": rec.get("created_at"),
            "updatedAt": rec.get("updated_at"),
            "lastRunAt": rec.get("last_run_at"),
            "lastConnectionId": rec.get("last_connection_id"),
            "mappingKeys": list(mapping_keys),
            "artifacts": {k: v for k, v in artifacts.items() if v},
            "generator": generator_meta,
        }

    def _sanitize_saved_chart(self, rec: Optional[dict]) -> Optional[dict]:
        if not rec:
            return None
        spec = rec.get("spec") or {}
        sanitized_spec = json.loads(json.dumps(spec))
        return {
            "id": rec.get("id"),
            "template_id": rec.get("template_id"),
            "name": rec.get("name"),
            "spec": sanitized_spec,
            "created_at": rec.get("created_at"),
            "updated_at": rec.get("updated_at"),
        }

    def list_saved_charts(self, template_id: str) -> list[dict]:
        with self._lock:
            state = self._read_state()
            charts = [
                self._sanitize_saved_chart(rec)
                for rec in state.get("saved_charts", {}).values()
                if rec and rec.get("template_id") == template_id
            ]
            return [rec for rec in charts if rec]

    def get_saved_chart(self, chart_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            rec = (state.get("saved_charts") or {}).get(chart_id)
            return self._sanitize_saved_chart(rec)

    def create_saved_chart(self, template_id: str, name: str, spec: Mapping[str, Any]) -> dict:
        now = _now_iso()
        chart_id = str(uuid.uuid4())
        spec_payload = json.loads(json.dumps(spec))
        with self._lock:
            state = self._read_state()
            record = {
                "id": chart_id,
                "template_id": template_id,
                "name": name,
                "spec": spec_payload,
                "created_at": now,
                "updated_at": now,
            }
            state.setdefault("saved_charts", {})
            state["saved_charts"][chart_id] = record
            self._write_state(state)
            return self._sanitize_saved_chart(record)

    def update_saved_chart(
        self,
        chart_id: str,
        *,
        name: Optional[str] = None,
        spec: Optional[Mapping[str, Any]] = None,
    ) -> Optional[dict]:
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = (state.get("saved_charts") or {}).get(chart_id)
            if not record:
                return None
            if name is not None:
                record["name"] = name
            if spec is not None:
                record["spec"] = json.loads(json.dumps(spec))
            record["updated_at"] = now
            state["saved_charts"][chart_id] = record
            self._write_state(state)
            return self._sanitize_saved_chart(record)

    def delete_saved_chart(self, chart_id: str) -> bool:
        with self._lock:
            state = self._read_state()
            saved = state.get("saved_charts") or {}
            removed = saved.pop(chart_id, None)
            if not removed:
                return False
            self._write_state(state)
            return True

    def _sanitize_schedule(self, rec: Optional[dict]) -> Optional[dict]:
        if not rec:
            return None
        sanitized = dict(rec)
        sanitized["email_recipients"] = _normalize_email_list(rec.get("email_recipients"))
        sanitized["email_subject"] = rec.get("email_subject")
        sanitized["email_message"] = rec.get("email_message")
        key_values = rec.get("key_values")
        sanitized["key_values"] = dict(key_values or {})
        batches = rec.get("batch_ids")
        if isinstance(batches, (list, tuple)):
            sanitized["batch_ids"] = [str(b) for b in batches if str(b).strip()]
        else:
            sanitized["batch_ids"] = []
        sanitized["last_run_artifacts"] = dict(rec.get("last_run_artifacts") or {})
        return sanitized

    def list_schedules(self) -> list[dict]:
        with self._lock:
            state = self._read_state()
            return [self._sanitize_schedule(rec) for rec in state["schedules"].values() if rec]

    def get_schedule(self, schedule_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            rec = state["schedules"].get(schedule_id)
            return self._sanitize_schedule(rec)

    def create_schedule(
        self,
        *,
        name: Optional[str],
        template_id: str,
        template_name: str,
        template_kind: str,
        connection_id: Optional[str],
        connection_name: Optional[str],
        start_date: str,
        end_date: str,
        key_values: Optional[Mapping[str, Any]],
        batch_ids: Optional[Iterable[str]],
        docx: bool,
        xlsx: bool,
        email_recipients: Optional[Iterable[str]],
        email_subject: Optional[str],
        email_message: Optional[str],
        frequency: str,
        interval_minutes: int,
        next_run_at: str,
        first_run_at: str,
        active: bool = True,
    ) -> dict:
        schedule_id = str(uuid.uuid4())
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            record = {
                "id": schedule_id,
                "name": (name or "").strip() or template_name,
                "template_id": template_id,
                "template_name": template_name,
                "template_kind": template_kind,
                "connection_id": connection_id,
                "connection_name": connection_name,
                "start_date": start_date,
                "end_date": end_date,
                "key_values": dict(key_values or {}),
                "batch_ids": [str(b) for b in (batch_ids or []) if str(b).strip()],
                "docx": bool(docx),
                "xlsx": bool(xlsx),
                "email_recipients": _normalize_email_list(email_recipients),
                "email_subject": (email_subject or "").strip() or None,
                "email_message": (email_message or "").strip() or None,
                "frequency": frequency,
                "interval_minutes": max(int(interval_minutes or 0), 1),
                "next_run_at": next_run_at,
                "first_run_at": first_run_at,
                "last_run_at": None,
                "last_run_status": None,
                "last_run_error": None,
                "last_run_artifacts": {},
                "active": bool(active),
                "created_at": now,
                "updated_at": now,
            }
            state["schedules"][schedule_id] = record
            self._write_state(state)
            return self._sanitize_schedule(record)

    def delete_schedule(self, schedule_id: str) -> bool:
        with self._lock:
            state = self._read_state()
            removed = state["schedules"].pop(schedule_id, None)
            if not removed:
                return False
            self._write_state(state)
            return True

    def update_schedule(self, schedule_id: str, **changes: Any) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            record = state["schedules"].get(schedule_id)
            if not record:
                return None
            for key, value in changes.items():
                if key == "email_recipients":
                    record[key] = _normalize_email_list(value)
                elif key in {"email_subject", "email_message"}:
                    record[key] = (value or "").strip() or None
                elif key == "key_values":
                    record[key] = dict(value or {})
                elif key == "batch_ids":
                    record[key] = [str(b) for b in (value or []) if str(b).strip()]
                else:
                    record[key] = value
            record["updated_at"] = _now_iso()
            state["schedules"][schedule_id] = record
            self._write_state(state)
            return self._sanitize_schedule(record)

    def record_schedule_run(
        self,
        schedule_id: str,
        *,
        started_at: str,
        finished_at: str,
        status: str,
        next_run_at: Optional[str],
        artifacts: Optional[Mapping[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            record = state["schedules"].get(schedule_id)
            if not record:
                return None
            record["last_run_at"] = finished_at
            record["last_run_status"] = status
            record["last_run_error"] = error
            record["last_run_artifacts"] = dict(artifacts or {})
            if next_run_at:
                record["next_run_at"] = next_run_at
            record["updated_at"] = _now_iso()
            state["schedules"][schedule_id] = record
            self._write_state(state)
            return self._sanitize_schedule(record)

    # ------------------------------------------------------------------
    # report run history helpers
    # ------------------------------------------------------------------
    def _sanitize_report_run(self, rec: Optional[dict]) -> Optional[dict]:
        if not rec:
            return None
        return {
            "id": rec.get("id"),
            "templateId": rec.get("template_id"),
            "templateName": rec.get("template_name"),
            "templateKind": rec.get("template_kind") or "pdf",
            "connectionId": rec.get("connection_id"),
            "connectionName": rec.get("connection_name"),
            "startDate": rec.get("start_date"),
            "endDate": rec.get("end_date"),
            "batchIds": list(rec.get("batch_ids") or []),
            "keyValues": dict(rec.get("key_values") or {}),
            "status": rec.get("status") or "succeeded",
            "artifacts": dict(rec.get("artifacts") or {}),
            "scheduleId": rec.get("schedule_id"),
            "scheduleName": rec.get("schedule_name"),
            "createdAt": rec.get("created_at"),
        }

    def record_report_run(
        self,
        run_id: str,
        *,
        template_id: str,
        template_name: Optional[str],
        template_kind: str,
        connection_id: Optional[str],
        connection_name: Optional[str],
        start_date: str,
        end_date: str,
        batch_ids: Optional[Iterable[str]],
        key_values: Optional[Mapping[str, Any]],
        status: str,
        artifacts: Optional[Mapping[str, Any]] = None,
        schedule_id: Optional[str] = None,
        schedule_name: Optional[str] = None,
    ) -> Optional[dict]:
        if not run_id or not template_id:
            return None
        now = _now_iso()
        record = {
            "id": run_id,
            "template_id": template_id,
            "template_name": template_name or template_id,
            "template_kind": template_kind or "pdf",
            "connection_id": connection_id,
            "connection_name": connection_name,
            "start_date": start_date,
            "end_date": end_date,
            "batch_ids": [str(b) for b in (batch_ids or []) if str(b).strip()],
            "key_values": dict(key_values or {}),
            "status": status or "succeeded",
            "artifacts": dict(artifacts or {}),
            "schedule_id": schedule_id,
            "schedule_name": schedule_name,
            "created_at": now,
        }
        with self._lock:
            state = self._read_state()
            runs = state.get("runs") or {}
            runs[run_id] = record
            if len(runs) > MAX_RUN_HISTORY:
                ordered = sorted(runs.values(), key=lambda item: item.get("created_at") or "", reverse=True)
                keep_ids = {item.get("id") for item in ordered[:MAX_RUN_HISTORY] if item.get("id")}
                runs = {rid: rec for rid, rec in runs.items() if rid in keep_ids}
            state["runs"] = runs
            self._write_state(state)
            return self._sanitize_report_run(record)

    def list_report_runs(
        self,
        *,
        template_id: Optional[str] = None,
        connection_id: Optional[str] = None,
        schedule_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        with self._lock:
            state = self._read_state()
            runs = list((state.get("runs") or {}).values())
            runs.sort(key=lambda rec: rec.get("created_at") or "", reverse=True)
            filtered: list[dict] = []
            for rec in runs:
                if template_id and rec.get("template_id") != template_id:
                    continue
                if connection_id and rec.get("connection_id") != connection_id:
                    continue
                if schedule_id and rec.get("schedule_id") != schedule_id:
                    continue
                sanitized = self._sanitize_report_run(rec)
                if sanitized:
                    filtered.append(sanitized)
                if limit and len(filtered) >= limit:
                    break
            return filtered

    def get_report_run(self, run_id: str) -> Optional[dict]:
        if not run_id:
            return None
        with self._lock:
            state = self._read_state()
            rec = (state.get("runs") or {}).get(run_id)
            return self._sanitize_report_run(rec)

    # ------------------------------------------------------------------
    # last-used helpers
    # ------------------------------------------------------------------
    # Jobs helpers
    # ------------------------------------------------------------------
    def _sanitize_job_step(self, step: Optional[dict]) -> Optional[dict]:
        if not step:
            return None
        return {
            "id": step.get("id"),
            "name": step.get("name"),
            "label": step.get("label") or step.get("name"),
            "status": _normalize_job_status(step.get("status")),
            "progress": step.get("progress"),
            "createdAt": step.get("created_at"),
            "startedAt": step.get("started_at"),
            "finishedAt": step.get("finished_at"),
            "error": step.get("error"),
        }

    def _sanitize_job(self, rec: Optional[dict]) -> Optional[dict]:
        if not rec:
            return None
        steps_raw = rec.get("steps") or []
        steps: list[dict] = []
        for step in steps_raw:
            sanitized = self._sanitize_job_step(step)
            if sanitized:
                steps.append(sanitized)
        return {
            "id": rec.get("id"),
            "type": rec.get("type") or "run_report",
            "status": _normalize_job_status(rec.get("status")),
            "templateId": rec.get("template_id"),
            "templateName": rec.get("template_name"),
            "templateKind": rec.get("template_kind") or "pdf",
            "connectionId": rec.get("connection_id"),
            "scheduleId": rec.get("schedule_id"),
            "correlationId": rec.get("correlation_id"),
            "progress": rec.get("progress") or 0,
            "error": rec.get("error"),
            "result": dict(rec.get("result") or {}),
            "createdAt": rec.get("created_at"),
            "queuedAt": rec.get("queued_at"),
            "startedAt": rec.get("started_at"),
            "finishedAt": rec.get("finished_at"),
            "updatedAt": rec.get("updated_at"),
            "steps": steps,
            # Retry and recovery fields
            "retryCount": rec.get("retry_count") or 0,
            "maxRetries": rec.get("max_retries") or 3,
            "retryAt": rec.get("retry_at"),
            "failureReason": rec.get("failure_reason"),
            "lastHeartbeatAt": rec.get("last_heartbeat_at"),
            "workerId": rec.get("worker_id"),
            # Webhook fields
            "webhookUrl": rec.get("webhook_url"),
            "notificationSentAt": rec.get("notification_sent_at"),
        }

    def create_job(
        self,
        *,
        job_type: str,
        template_id: Optional[str] = None,
        connection_id: Optional[str] = None,
        template_name: Optional[str] = None,
        template_kind: Optional[str] = None,
        schedule_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        steps: Optional[Iterable[Mapping[str, Any]]] = None,
        meta: Optional[Mapping[str, Any]] = None,
        # New retry configuration parameters
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[int] = None,
        # New webhook parameters
        webhook_url: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        # Priority (for future queue ordering)
        priority: int = 0,
    ) -> dict:
        job_id = str(uuid.uuid4())
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            templates = state.get("templates") or {}
            tpl_record = templates.get(template_id) or {}
            tpl_name = template_name or tpl_record.get("name") or template_id
            tpl_kind = template_kind or tpl_record.get("kind") or "pdf"
            step_records: list[dict] = []
            for raw in steps or []:
                name_raw = raw.get("name") if isinstance(raw, Mapping) else None
                name = str(name_raw or "").strip()
                if not name:
                    continue
                step_id = str(raw.get("id") or uuid.uuid4())
                label_raw = raw.get("label") if isinstance(raw, Mapping) else None
                label = str(label_raw or "").strip() or name
                status_raw = raw.get("status") if isinstance(raw, Mapping) else None
                status = (str(status_raw or "") or "queued").strip().lower() or "queued"
                progress_raw = raw.get("progress") if isinstance(raw, Mapping) else None
                try:
                    progress_val = float(progress_raw)
                except (TypeError, ValueError):
                    progress_val = 0.0
                step_records.append(
                    {
                        "id": step_id,
                        "name": name,
                        "label": label,
                        "status": status,
                        "progress": max(0.0, min(progress_val, 100.0)),
                        "created_at": now,
                        "started_at": None,
                        "finished_at": None,
                        "error": None,
                    }
                )
            jobs = state.get("jobs") or {}
            record = {
                "id": job_id,
                "type": str(job_type or "run_report"),
                "template_id": template_id,
                "template_name": tpl_name,
                "template_kind": tpl_kind,
                "connection_id": connection_id,
                "schedule_id": schedule_id,
                "correlation_id": correlation_id,
                "status": "queued",
                "progress": 0.0,
                "error": None,
                "result": {},
                "steps": step_records,
                "created_at": now,
                "queued_at": now,
                "started_at": None,
                "finished_at": None,
                "updated_at": now,
                "meta": dict(meta or {}),
                # Retry configuration
                "retry_count": 0,
                "max_retries": max_retries if max_retries is not None else self.DEFAULT_MAX_RETRIES,
                "retry_backoff_seconds": retry_backoff_seconds if retry_backoff_seconds is not None else self.DEFAULT_RETRY_BACKOFF_SECONDS,
                "retry_at": None,
                "failure_reason": None,
                # Heartbeat tracking
                "last_heartbeat_at": None,
                "worker_id": None,
                # Webhook configuration
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret,
                "notification_sent_at": None,
                # Priority
                "priority": max(-10, min(10, priority)),
            }
            jobs[job_id] = record
            state["jobs"] = jobs
            self._write_state(state)
            sanitized = self._sanitize_job(record)
            assert sanitized is not None
            return sanitized

    def list_jobs(
        self,
        *,
        statuses: Optional[Iterable[str]] = None,
        types: Optional[Iterable[str]] = None,
        limit: int = 50,
        active_only: bool = False,
    ) -> list[dict]:
        with self._lock:
            state = self._read_state()
            jobs = list((state.get("jobs") or {}).values())
            # newest first
            jobs.sort(key=lambda rec: rec.get("created_at") or "", reverse=True)
            status_filter = {str(s).strip().lower() for s in (statuses or []) if str(s).strip()}
            type_filter = {str(t).strip() for t in (types or []) if str(t).strip()}
            out: list[dict] = []
            for rec in jobs:
                status_raw = rec.get("status") or ""
                status_norm = str(status_raw).strip().lower()
                if active_only and status_norm in {"succeeded", "failed", "cancelled"}:
                    continue
                if status_filter and status_norm not in status_filter:
                    continue
                type_raw = rec.get("type") or ""
                if type_filter and str(type_raw) not in type_filter:
                    continue
                sanitized = self._sanitize_job(rec)
                if sanitized:
                    out.append(sanitized)
                if limit and len(out) >= limit:
                    break
            return out

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            rec = (state.get("jobs") or {}).get(job_id)
            return self._sanitize_job(rec)

    def get_job_meta(self, job_id: str) -> dict:
        with self._lock:
            state = self._read_state()
            rec = (state.get("jobs") or {}).get(job_id) or {}
            meta = rec.get("meta") or {}
            return dict(meta)

    def _update_job_record(self, job_id: str, mutator) -> Optional[dict]:
        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            record = jobs.get(job_id)
            if not record:
                return None
            changed = mutator(record)
            if not changed:
                # still touch updated_at for visibility
                record["updated_at"] = _now_iso()
            jobs[job_id] = record
            state["jobs"] = jobs
            self._write_state(state)
            return self._sanitize_job(record)

    def record_job_start(self, job_id: str) -> Optional[dict]:
        def mutator(rec: dict) -> bool:
            now = _now_iso()
            updated = False
            if not rec.get("started_at"):
                rec["started_at"] = now
                updated = True
            if rec.get("status") != "running":
                rec["status"] = "running"
                updated = True
            if rec.get("progress") is None:
                rec["progress"] = 0.0
            rec["updated_at"] = now
            return updated

        return self._update_job_record(job_id, mutator)

    def record_job_progress(self, job_id: str, progress: float) -> Optional[dict]:
        try:
            value = float(progress)
        except (TypeError, ValueError):
            value = 0.0
        clamped = max(0.0, min(value, 100.0))

        def mutator(rec: dict) -> bool:
            now = _now_iso()
            prev = rec.get("progress")
            if prev is not None and float(prev) == clamped:
                rec["updated_at"] = now
                return False
            rec["progress"] = clamped
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def record_job_completion(
        self,
        job_id: str,
        *,
        status: str,
        error: Optional[str] = None,
        result: Optional[Mapping[str, Any]] = None,
    ) -> Optional[dict]:
        status_norm = (status or "").strip().lower()
        if status_norm not in {"succeeded", "failed", "cancelled"}:
            status_norm = "failed"

        def mutator(rec: dict) -> bool:
            now = _now_iso()
            current_status = str(rec.get("status") or "").strip().lower()
            if current_status == "cancelled" and status_norm != "cancelled":
                rec["updated_at"] = now
                return False
            changed = False
            if rec.get("status") != status_norm:
                rec["status"] = status_norm
                changed = True
            if not rec.get("finished_at"):
                rec["finished_at"] = now
                changed = True
            if status_norm == "succeeded" and (rec.get("progress") or 0) < 100:
                rec["progress"] = 100.0
                changed = True
            if error is not None:
                rec["error"] = str(error)
                changed = True
            if result is not None:
                rec["result"] = dict(result)
                changed = True
            rec["updated_at"] = now
            return changed

        return self._update_job_record(job_id, mutator)

    def record_job_step(
        self,
        job_id: str,
        name: str,
        *,
        status: Optional[str] = None,
        error: Optional[str] = None,
        progress: Optional[float] = None,
        label: Optional[str] = None,
    ) -> Optional[dict]:
        step_name = (name or "").strip()
        if not step_name:
            return None
        status_norm = (status or "").strip().lower() if status is not None else None

        def mutator(rec: dict) -> bool:
            now = _now_iso()
            steps = list(rec.get("steps") or [])
            target = None
            for step in steps:
                if step.get("name") == step_name:
                    target = step
                    break
            if target is None:
                target = {
                    "id": str(uuid.uuid4()),
                    "name": step_name,
                    "label": label or step_name,
                    "status": status_norm or "queued",
                    "progress": 0.0,
                    "created_at": now,
                    "started_at": None,
                    "finished_at": None,
                    "error": None,
                }
                steps.append(target)
            else:
                if label is not None:
                    target["label"] = label
                if status_norm is not None:
                    previous_status = str(target.get("status") or "").strip().lower()
                    target["status"] = status_norm
                    if status_norm == "running" and not target.get("started_at"):
                        target["started_at"] = now
                    if status_norm in {"succeeded", "failed", "cancelled"} and not target.get(
                        "finished_at"
                    ):
                        target["finished_at"] = now
                if error is not None:
                    target["error"] = str(error)
                if progress is not None:
                    try:
                        value = float(progress)
                    except (TypeError, ValueError):
                        value = 0.0
                    target["progress"] = max(0.0, min(value, 100.0))
            rec["steps"] = steps
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def cancel_job(self, job_id: str) -> Optional[dict]:
        return self.record_job_completion(job_id, status="cancelled", error="Cancelled by user", result=None)

    def update_job(self, job_id: str, **updates: Any) -> Optional[dict]:
        """Apply arbitrary field updates to a job record."""
        if not updates:
            return self.get_job(job_id)

        def mutator(rec: dict) -> bool:
            now = _now_iso()
            for key, value in updates.items():
                rec[key] = value
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def delete_job(self, job_id: str) -> bool:
        """Permanently remove a job record. Returns True if deleted."""
        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            if job_id not in jobs:
                return False
            del jobs[job_id]
            state["jobs"] = jobs
            self._write_state(state)
            return True

    # ------------------------------------------------------------------
    # Job retry and recovery helpers
    # ------------------------------------------------------------------
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_BACKOFF_SECONDS = 30
    DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 120

    def update_job_heartbeat(self, job_id: str, worker_id: Optional[str] = None) -> Optional[dict]:
        """Update the job's heartbeat timestamp to indicate worker is alive."""
        def mutator(rec: dict) -> bool:
            now = _now_iso()
            rec["last_heartbeat_at"] = now
            if worker_id:
                rec["worker_id"] = worker_id
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def mark_job_for_retry(
        self,
        job_id: str,
        *,
        reason: str,
        retry_at: Optional[str] = None,
        is_retriable: bool = True,
    ) -> Optional[dict]:
        """
        Mark a failed job for retry. Calculates backoff if retry_at not provided.
        Sets status to 'pending_retry' if retriable and under max retries.
        """
        import random

        def mutator(rec: dict) -> bool:
            now = _now_iso()
            retry_count = int(rec.get("retry_count") or 0)
            max_retries = int(rec.get("max_retries") or self.DEFAULT_MAX_RETRIES)

            # Check if we can retry
            if not is_retriable or retry_count >= max_retries:
                rec["status"] = "failed"
                rec["error"] = f"{reason} (max retries exceeded)" if retry_count >= max_retries else reason
                rec["finished_at"] = now
                rec["updated_at"] = now
                return True

            # Calculate retry time with exponential backoff + jitter
            base_backoff = int(rec.get("retry_backoff_seconds") or self.DEFAULT_RETRY_BACKOFF_SECONDS)
            backoff = base_backoff * (2 ** retry_count)  # 30s, 60s, 120s, 240s
            jitter = random.uniform(0, backoff * 0.2)    # ±20% jitter
            delay = backoff + jitter

            if retry_at:
                computed_retry_at = retry_at
            else:
                retry_time = datetime.now(timezone.utc) + timedelta(seconds=delay)
                computed_retry_at = retry_time.isoformat()

            rec["status"] = "pending_retry"
            rec["retry_count"] = retry_count + 1
            rec["retry_at"] = computed_retry_at
            rec["failure_reason"] = reason
            rec["started_at"] = None  # Reset for next attempt
            rec["last_heartbeat_at"] = None
            rec["worker_id"] = None
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def find_stale_running_jobs(
        self,
        heartbeat_timeout_seconds: Optional[int] = None,
    ) -> list[dict]:
        """
        Find jobs in 'running' state whose heartbeat has expired.
        These are likely orphaned due to worker crash.
        """
        timeout = heartbeat_timeout_seconds or self.DEFAULT_HEARTBEAT_TIMEOUT_SECONDS
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout)
        cutoff_iso = cutoff.isoformat()

        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            stale: list[dict] = []

            for job in jobs.values():
                status = str(job.get("status") or "").strip().lower()
                if status != "running":
                    continue

                # Check heartbeat
                heartbeat = job.get("last_heartbeat_at")
                if heartbeat is None:
                    # No heartbeat ever recorded - check started_at
                    started = job.get("started_at")
                    if started and started < cutoff_iso:
                        stale.append(dict(job))
                elif heartbeat < cutoff_iso:
                    stale.append(dict(job))

            return stale

    def find_jobs_ready_for_retry(self) -> list[dict]:
        """
        Find jobs in 'pending_retry' state whose retry_at time has passed.
        These are ready to be re-queued.
        """
        now_iso = _now_iso()

        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            ready: list[dict] = []

            for job in jobs.values():
                status = str(job.get("status") or "").strip().lower()
                if status != "pending_retry":
                    continue

                retry_at = job.get("retry_at")
                if retry_at and retry_at <= now_iso:
                    ready.append(dict(job))

            return ready

    def requeue_job_for_retry(self, job_id: str) -> Optional[dict]:
        """
        Move a job from 'pending_retry' back to 'queued' state.
        Called when retry_at time has passed.
        """
        def mutator(rec: dict) -> bool:
            now = _now_iso()
            status = str(rec.get("status") or "").strip().lower()
            if status != "pending_retry":
                return False

            rec["status"] = "queued"
            rec["queued_at"] = now
            rec["retry_at"] = None
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def update_job_webhook(
        self,
        job_id: str,
        *,
        webhook_url: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> Optional[dict]:
        """Update job's webhook configuration."""
        def mutator(rec: dict) -> bool:
            now = _now_iso()
            if webhook_url is not None:
                rec["webhook_url"] = webhook_url
            if webhook_secret is not None:
                rec["webhook_secret"] = webhook_secret
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def mark_webhook_sent(self, job_id: str) -> Optional[dict]:
        """Mark that webhook notification was sent for this job."""
        def mutator(rec: dict) -> bool:
            now = _now_iso()
            rec["notification_sent_at"] = now
            rec["updated_at"] = now
            return True

        return self._update_job_record(job_id, mutator)

    def get_jobs_pending_webhook(self) -> list[dict]:
        """
        Find completed jobs that have a webhook_url but no notification_sent_at.
        These need webhook delivery.
        """
        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            pending: list[dict] = []

            for job in jobs.values():
                status = str(job.get("status") or "").strip().lower()
                if status not in {"succeeded", "failed", "cancelled"}:
                    continue

                webhook_url = job.get("webhook_url")
                if not webhook_url:
                    continue

                if job.get("notification_sent_at"):
                    continue

                pending.append(dict(job))

            return pending

    # ------------------------------------------------------------------
    # Idempotency key management (state-of-the-art pattern)
    # ------------------------------------------------------------------
    IDEMPOTENCY_KEY_TTL_HOURS = 24

    def check_idempotency_key(
        self,
        key: str,
        request_hash: str,
    ) -> tuple[bool, Optional[dict]]:
        """
        Check if an idempotency key exists and is valid.

        Returns:
            (exists, cached_response) where:
            - exists=True, cached_response=dict: Key found, return cached response
            - exists=True, cached_response=None: Key found but hash mismatch (error)
            - exists=False, cached_response=None: Key not found, proceed with request
        """
        if not key:
            return False, None

        with self._lock:
            state = self._read_state()
            keys = state.get("idempotency_keys") or {}
            record = keys.get(key)

            if not record:
                return False, None

            # Check if expired
            expires_at = record.get("expires_at")
            if expires_at:
                try:
                    exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                    if exp_dt < datetime.now(timezone.utc):
                        # Expired, remove it
                        del keys[key]
                        state["idempotency_keys"] = keys
                        self._write_state(state)
                        return False, None
                except (ValueError, TypeError):
                    pass

            # Check hash match
            stored_hash = record.get("request_hash")
            if stored_hash != request_hash:
                # Hash mismatch - key reused for different request
                return True, None

            return True, record.get("response")

    def store_idempotency_key(
        self,
        key: str,
        job_id: str,
        request_hash: str,
        response: dict,
    ) -> dict:
        """
        Store an idempotency key with its cached response.
        Keys expire after IDEMPOTENCY_KEY_TTL_HOURS hours.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=self.IDEMPOTENCY_KEY_TTL_HOURS)

        record = {
            "key": key,
            "job_id": job_id,
            "request_hash": request_hash,
            "response": response,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }

        with self._lock:
            state = self._read_state()
            keys = state.get("idempotency_keys") or {}
            keys[key] = record
            state["idempotency_keys"] = keys
            self._write_state(state)
            return record

    def clean_expired_idempotency_keys(self) -> int:
        """
        Remove expired idempotency keys.
        Called by recovery daemon periodically.

        Returns:
            Number of keys removed.
        """
        now = datetime.now(timezone.utc)
        removed = 0

        with self._lock:
            state = self._read_state()
            keys = state.get("idempotency_keys") or {}

            for key_id in list(keys.keys()):
                record = keys[key_id]
                expires_at = record.get("expires_at")
                if not expires_at:
                    continue
                try:
                    exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                    if exp_dt < now:
                        del keys[key_id]
                        removed += 1
                except (ValueError, TypeError):
                    pass

            if removed > 0:
                state["idempotency_keys"] = keys
                self._write_state(state)

        return removed

    # ------------------------------------------------------------------
    # Dead Letter Queue management (state-of-the-art pattern)
    # ------------------------------------------------------------------
    def move_job_to_dlq(
        self,
        job_id: str,
        failure_history: Optional[list[dict]] = None,
    ) -> Optional[dict]:
        """
        Move a permanently failed job to the Dead Letter Queue.
        Preserves the original job state and failure history for debugging.

        Returns:
            The DLQ record, or None if job not found.
        """
        now = _now_iso()

        with self._lock:
            state = self._read_state()
            jobs = state.get("jobs") or {}
            dlq = state.get("dead_letter_jobs") or {}

            job = jobs.get(job_id)
            if not job:
                return None

            # Build failure history if not provided
            if failure_history is None:
                failure_history = [{
                    "attempt": job.get("retry_count", 0),
                    "error": job.get("error") or "Unknown error",
                    "timestamp": now,
                    "category": "unknown",
                }]

            dlq_record = {
                "id": job_id,
                "original_job": dict(job),
                "failure_history": failure_history,
                "moved_at": now,
                "requeued_at": None,
                "requeue_count": 0,
            }

            dlq[job_id] = dlq_record

            # Update original job to mark it as moved to DLQ
            job["dead_letter_at"] = now
            job["status"] = "failed"
            jobs[job_id] = job

            state["jobs"] = jobs
            state["dead_letter_jobs"] = dlq
            self._write_state(state)

            return dlq_record

    def list_dead_letter_jobs(self, limit: int = 50) -> list[dict]:
        """List jobs in the Dead Letter Queue, newest first."""
        with self._lock:
            state = self._read_state()
            dlq = list((state.get("dead_letter_jobs") or {}).values())
            dlq.sort(key=lambda r: r.get("moved_at") or "", reverse=True)
            return dlq[:limit]

    def get_dead_letter_job(self, job_id: str) -> Optional[dict]:
        """Get a specific DLQ job by ID."""
        with self._lock:
            state = self._read_state()
            return (state.get("dead_letter_jobs") or {}).get(job_id)

    def requeue_from_dlq(self, job_id: str) -> Optional[dict]:
        """
        Requeue a job from the Dead Letter Queue.
        Creates a new job record with reset retry count.

        Returns:
            The new job record, or None if DLQ job not found.
        """
        now = _now_iso()

        with self._lock:
            state = self._read_state()
            dlq = state.get("dead_letter_jobs") or {}

            dlq_record = dlq.get(job_id)
            if not dlq_record:
                return None

            original_job = dlq_record.get("original_job") or {}

            # Create new job from original
            new_job_id = str(uuid.uuid4())
            new_job = dict(original_job)
            new_job["id"] = new_job_id
            new_job["status"] = "queued"
            new_job["progress"] = 0.0
            new_job["error"] = None
            new_job["result"] = {}
            new_job["created_at"] = now
            new_job["queued_at"] = now
            new_job["started_at"] = None
            new_job["finished_at"] = None
            new_job["updated_at"] = now
            new_job["retry_count"] = 0
            new_job["retry_at"] = None
            new_job["failure_reason"] = None
            new_job["last_heartbeat_at"] = None
            new_job["worker_id"] = None
            new_job["dead_letter_at"] = None
            new_job["meta"] = dict(original_job.get("meta") or {})
            new_job["meta"]["requeued_from_dlq"] = job_id
            new_job["meta"]["dlq_requeue_count"] = dlq_record.get("requeue_count", 0) + 1

            # Reset steps
            for step in new_job.get("steps") or []:
                step["status"] = "queued"
                step["progress"] = 0.0
                step["started_at"] = None
                step["finished_at"] = None
                step["error"] = None

            # Update DLQ record
            dlq_record["requeued_at"] = now
            dlq_record["requeue_count"] = dlq_record.get("requeue_count", 0) + 1

            # Save changes
            jobs = state.get("jobs") or {}
            jobs[new_job_id] = new_job
            state["jobs"] = jobs
            dlq[job_id] = dlq_record
            state["dead_letter_jobs"] = dlq
            self._write_state(state)

            return self._sanitize_job(new_job)

    def delete_from_dlq(self, job_id: str) -> bool:
        """
        Permanently delete a job from the Dead Letter Queue.

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            state = self._read_state()
            dlq = state.get("dead_letter_jobs") or {}

            if job_id not in dlq:
                return False

            del dlq[job_id]
            state["dead_letter_jobs"] = dlq
            self._write_state(state)
            return True

    def get_dlq_stats(self) -> dict:
        """Get statistics about the Dead Letter Queue."""
        with self._lock:
            state = self._read_state()
            dlq = state.get("dead_letter_jobs") or {}

            total = len(dlq)
            requeued = sum(1 for r in dlq.values() if r.get("requeued_at"))

            return {
                "total": total,
                "pending": total - requeued,
                "requeued": requeued,
            }

    # ------------------------------------------------------------------
    # last-used helpers
    # ------------------------------------------------------------------
    def get_last_used(self) -> dict:
        with self._lock:
            state = self._read_state()
            data = state.get("last_used") or {}
            return {
                "connection_id": data.get("connection_id"),
                "template_id": data.get("template_id"),
                "updated_at": data.get("updated_at"),
            }

    def set_last_used(self, connection_id: Optional[str], template_id: Optional[str]) -> dict:
        now = _now_iso()
        with self._lock:
            state = self._read_state()
            state["last_used"] = {
                "connection_id": connection_id,
                "template_id": template_id,
                "updated_at": now,
            }
            self._write_state(state)
            return state["last_used"]

    # ------------------------------------------------------------------
    # activity log helpers
    # ------------------------------------------------------------------
    def log_activity(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        entity_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> dict:
        """Log an activity event."""
        now = _now_iso()
        activity_id = str(uuid.uuid4())
        entry = {
            "id": activity_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "entity_name": entity_name,
            "details": dict(details or {}),
            "user_id": user_id,
            "timestamp": now,
        }
        with self._lock:
            state = self._read_state()
            log = state.get("activity_log") or []
            log.insert(0, entry)
            # Keep only last 500 entries
            if len(log) > 500:
                log = log[:500]
            state["activity_log"] = log
            self._write_state(state)
            return entry

    def get_activity_log(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> list[dict]:
        """Get activity log with optional filtering."""
        with self._lock:
            state = self._read_state()
            log = state.get("activity_log") or []

            # Filter
            if entity_type:
                log = [e for e in log if e.get("entity_type") == entity_type]
            if action:
                log = [e for e in log if e.get("action") == action]

            # Paginate
            return log[offset : offset + limit]

    def clear_activity_log(self) -> int:
        """Clear all activity log entries. Returns count of entries cleared."""
        with self._lock:
            state = self._read_state()
            count = len(state.get("activity_log") or [])
            state["activity_log"] = []
            self._write_state(state)
            return count

    # ------------------------------------------------------------------
    # favorites helpers
    # ------------------------------------------------------------------
    def get_favorites(self) -> dict:
        """Get all favorites."""
        with self._lock:
            state = self._read_state()
            favorites = state.get("favorites") or {"templates": [], "connections": []}
            return {
                "templates": list(favorites.get("templates") or []),
                "connections": list(favorites.get("connections") or []),
            }

    def add_favorite(self, entity_type: str, entity_id: str) -> bool:
        """Add an item to favorites. Returns True if added, False if already exists."""
        if entity_type not in ("templates", "connections"):
            return False
        with self._lock:
            state = self._read_state()
            favorites = state.get("favorites") or {"templates": [], "connections": []}
            items = list(favorites.get(entity_type) or [])
            if entity_id in items:
                return False
            items.append(entity_id)
            favorites[entity_type] = items
            state["favorites"] = favorites
            self._write_state(state)
            return True

    def remove_favorite(self, entity_type: str, entity_id: str) -> bool:
        """Remove an item from favorites. Returns True if removed, False if not found."""
        if entity_type not in ("templates", "connections"):
            return False
        with self._lock:
            state = self._read_state()
            favorites = state.get("favorites") or {"templates": [], "connections": []}
            items = list(favorites.get(entity_type) or [])
            if entity_id not in items:
                return False
            items.remove(entity_id)
            favorites[entity_type] = items
            state["favorites"] = favorites
            self._write_state(state)
            return True

    def is_favorite(self, entity_type: str, entity_id: str) -> bool:
        """Check if an item is a favorite."""
        if entity_type not in ("templates", "connections"):
            return False
        with self._lock:
            state = self._read_state()
            favorites = state.get("favorites") or {"templates": [], "connections": []}
            items = favorites.get(entity_type) or []
            return entity_id in items

    # ------------------------------------------------------------------
    # user preferences helpers
    # ------------------------------------------------------------------
    def get_user_preferences(self) -> dict:
        """Get user preferences."""
        with self._lock:
            state = self._read_state()
            return dict(state.get("user_preferences") or {})

    def set_user_preference(self, key: str, value: Any) -> dict:
        """Set a single user preference."""
        with self._lock:
            state = self._read_state()
            prefs = dict(state.get("user_preferences") or {})
            prefs[key] = value
            prefs["updated_at"] = _now_iso()
            state["user_preferences"] = prefs
            self._write_state(state)
            return prefs

    def update_user_preferences(self, updates: Dict[str, Any]) -> dict:
        """Update multiple user preferences."""
        with self._lock:
            state = self._read_state()
            prefs = dict(state.get("user_preferences") or {})
            prefs.update(updates)
            prefs["updated_at"] = _now_iso()
            state["user_preferences"] = prefs
            self._write_state(state)
            return prefs

    # ------------------------------------------------------------------
    # notifications helpers
    # ------------------------------------------------------------------
    MAX_NOTIFICATIONS = 100

    def add_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info",
        link: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> dict:
        """Add a notification. Returns the created notification."""
        notif = {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "type": notification_type,  # info, success, warning, error
            "link": link,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "read": False,
            "created_at": _now_iso(),
        }
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            notifications.insert(0, notif)
            # Trim to max size
            state["notifications"] = notifications[: self.MAX_NOTIFICATIONS]
            self._write_state(state)
        return notif

    def get_notifications(
        self,
        limit: int = 50,
        unread_only: bool = False,
    ) -> list:
        """Get notifications, optionally filtered to unread only."""
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            if unread_only:
                notifications = [n for n in notifications if not n.get("read")]
            return notifications[:limit]

    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a single notification as read. Returns True if found."""
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            found = False
            for n in notifications:
                if n.get("id") == notification_id:
                    n["read"] = True
                    found = True
                    break
            if found:
                state["notifications"] = notifications
                self._write_state(state)
            return found

    def mark_all_notifications_read(self) -> int:
        """Mark all notifications as read. Returns count of notifications marked."""
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            count = 0
            for n in notifications:
                if not n.get("read"):
                    n["read"] = True
                    count += 1
            state["notifications"] = notifications
            self._write_state(state)
            return count

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification. Returns True if found and deleted."""
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            original_count = len(notifications)
            notifications = [n for n in notifications if n.get("id") != notification_id]
            if len(notifications) < original_count:
                state["notifications"] = notifications
                self._write_state(state)
                return True
            return False

    def clear_notifications(self) -> int:
        """Clear all notifications. Returns count of notifications cleared."""
        with self._lock:
            state = self._read_state()
            count = len(state.get("notifications") or [])
            state["notifications"] = []
            self._write_state(state)
            return count

    def get_unread_count(self) -> int:
        """Get count of unread notifications."""
        with self._lock:
            state = self._read_state()
            notifications = list(state.get("notifications") or [])
            return sum(1 for n in notifications if not n.get("read"))

    # ------------------------------------------------------------------
    # NL2SQL: Saved Queries
    # ------------------------------------------------------------------
    def save_query(self, query: dict) -> str:
        """Save a query. Returns the query ID."""
        with self._lock:
            state = self._read_state()
            query_id = query.get("id") or str(uuid.uuid4())[:8]
            query["id"] = query_id
            state.setdefault("saved_queries", {})[query_id] = query
            self._write_state(state)
            return query_id

    def list_saved_queries(self) -> list[dict]:
        """List all saved queries."""
        with self._lock:
            state = self._read_state()
            queries = list((state.get("saved_queries") or {}).values())
            return sorted(queries, key=lambda q: q.get("created_at", ""), reverse=True)

    def get_saved_query(self, query_id: str) -> Optional[dict]:
        """Get a saved query by ID."""
        with self._lock:
            state = self._read_state()
            return (state.get("saved_queries") or {}).get(query_id)

    def update_saved_query(self, query_id: str, updates: dict) -> Optional[dict]:
        """Update a saved query."""
        with self._lock:
            state = self._read_state()
            queries = state.get("saved_queries") or {}
            if query_id not in queries:
                return None
            queries[query_id].update(updates)
            queries[query_id]["updated_at"] = _now_iso()
            self._write_state(state)
            return queries[query_id]

    def delete_saved_query(self, query_id: str) -> bool:
        """Delete a saved query. Returns True if deleted."""
        with self._lock:
            state = self._read_state()
            queries = state.get("saved_queries") or {}
            if query_id not in queries:
                return False
            del queries[query_id]
            self._write_state(state)
            return True

    def increment_query_run_count(self, query_id: str) -> None:
        """Increment the run count for a saved query."""
        with self._lock:
            state = self._read_state()
            queries = state.get("saved_queries") or {}
            if query_id in queries:
                queries[query_id]["run_count"] = queries[query_id].get("run_count", 0) + 1
                queries[query_id]["last_run_at"] = _now_iso()
                self._write_state(state)

    # ------------------------------------------------------------------
    # NL2SQL: Query History
    # ------------------------------------------------------------------
    MAX_QUERY_HISTORY = 200

    def add_query_history(self, entry: dict) -> None:
        """Add an entry to query history."""
        with self._lock:
            state = self._read_state()
            history = list(state.get("query_history") or [])
            history.insert(0, entry)
            # Trim to max size
            state["query_history"] = history[: self.MAX_QUERY_HISTORY]
            self._write_state(state)

    def get_query_history(self, limit: int = 50) -> list[dict]:
        """Get query history entries."""
        with self._lock:
            state = self._read_state()
            history = list(state.get("query_history") or [])
            return history[:limit]

    def clear_query_history(self) -> int:
        """Clear all query history. Returns count cleared."""
        with self._lock:
            state = self._read_state()
            count = len(state.get("query_history") or [])
            state["query_history"] = []
            self._write_state(state)
            return count

    def delete_query_history_entry(self, entry_id: str) -> bool:
        """Delete a single query history entry by ID."""
        if not entry_id:
            return False
        with self._lock:
            state = self._read_state()
            history = list(state.get("query_history") or [])
            if not history:
                return False
            filtered = [h for h in history if h.get("id") != entry_id]
            if len(filtered) == len(history):
                return False
            state["query_history"] = filtered
            self._write_state(state)
            return True


class SQLiteStateStore(StateStore):
    """SQLite-backed state store with JSON persistence and schema versioning."""

    def __init__(self, base_dir: Optional[Path] = None, db_path: Optional[Path] = None) -> None:
        super().__init__(base_dir=base_dir)
        db_override = db_path or os.getenv("NEURA_STATE_DB_PATH")
        if db_override:
            self._db_path = Path(db_override).expanduser()
        else:
            self._db_path = self._base_dir / "state.sqlite3"
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(
            f"sqlite:///{self._db_path}",
            connect_args={"check_same_thread": False},
        )
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        SQLModel.metadata.create_all(self._engine)
        with Session(self._engine) as session:
            snapshot = session.get(_StateSnapshot, 1)
            if snapshot is not None:
                return
            state = self._load_initial_state()
            meta = {
                "version": STATE_VERSION,
                "updated_at": _now_iso(),
                "checksum": _compute_checksum(state),
            }
            state["_metadata"] = meta
            snapshot = _StateSnapshot(
                id=1,
                data=_json_roundtrip(state),
                version=STATE_VERSION,
                checksum=meta["checksum"],
                updated_at=datetime.now(timezone.utc),
            )
            session.add(snapshot)
            session.commit()

            if self._state_path.exists():
                migrated_path = self._state_path.with_name(self._state_path.name + ".migrated")
                try:
                    if not migrated_path.exists():
                        self._state_path.replace(migrated_path)
                except Exception:
                    pass

    def _load_initial_state(self) -> dict:
        if self._state_path.exists():
            try:
                raw = json.loads(self._state_path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    return self._apply_defaults(raw)
            except Exception:
                pass
        return self._default_state()

    def _snapshot_mtime(self) -> Optional[float]:
        try:
            with Session(self._engine) as session:
                stmt = select(_StateSnapshot.updated_at).where(_StateSnapshot.id == 1)
                updated_at = session.exec(stmt).first()
                if updated_at is None:
                    return None
                return updated_at.timestamp()
        except Exception:
            return None

    def _read_state(self) -> dict:
        if self._cache_enabled and self._cache is not None:
            latest = self._snapshot_mtime()
            if latest is None or latest == self._cache_mtime:
                return self._cache

        with Session(self._engine) as session:
            snapshot = session.get(_StateSnapshot, 1)
            if snapshot is None:
                state = self._default_state()
            else:
                state = snapshot.data if isinstance(snapshot.data, dict) else {}

        state = self._apply_defaults(state)
        if self._cache_enabled:
            self._cache = state
            self._cache_mtime = self._snapshot_mtime() or time.time()
        return state

    def _write_state(self, state: dict) -> None:
        self._create_backup()
        meta = {
            "version": STATE_VERSION,
            "updated_at": _now_iso(),
            "checksum": _compute_checksum(state),
        }
        state["_metadata"] = meta
        sanitized = _json_roundtrip(state)
        now = datetime.now(timezone.utc)
        with Session(self._engine) as session:
            with session.begin():
                snapshot = session.get(_StateSnapshot, 1)
                if snapshot is None:
                    snapshot = _StateSnapshot(
                        id=1,
                        data=sanitized,
                        version=STATE_VERSION,
                        checksum=meta["checksum"],
                        updated_at=now,
                    )
                    session.add(snapshot)
                else:
                    snapshot.data = sanitized
                    snapshot.version = STATE_VERSION
                    snapshot.checksum = meta["checksum"]
                    snapshot.updated_at = now

        if self._cache_enabled:
            self._cache = state
            self._cache_mtime = now.timestamp()

    def _create_backup(self) -> None:
        if not self._backups_enabled or self._backup_interval_seconds <= 0:
            return

        now = time.time()
        if self._last_backup_at and (now - self._last_backup_at) < self._backup_interval_seconds:
            return

        with Session(self._engine) as session:
            snapshot = session.get(_StateSnapshot, 1)
            if snapshot is None:
                return
            backup_state = snapshot.data if isinstance(snapshot.data, dict) else {}
            backup_state = _json_roundtrip(backup_state)
            created_at = datetime.now(timezone.utc)
            name = f"state_{created_at.strftime('%Y%m%d_%H%M%S')}"
            size_bytes = len(json.dumps(backup_state, sort_keys=True, default=str).encode("utf-8"))
            backup = _StateBackup(
                name=name,
                created_at=created_at,
                data=backup_state,
                size_bytes=size_bytes,
            )
            session.add(backup)
            session.commit()
            self._last_backup_at = now

            backups = session.exec(
                select(_StateBackup).order_by(_StateBackup.created_at.desc())
            ).all()
            for old_backup in backups[MAX_BACKUP_COUNT:]:
                session.delete(old_backup)
            session.commit()

    def list_backups(self) -> list[dict]:
        with Session(self._engine) as session:
            backups = session.exec(
                select(_StateBackup).order_by(_StateBackup.created_at.desc())
            ).all()
        results = []
        for backup in backups:
            results.append(
                {
                    "name": backup.name,
                    "size_bytes": backup.size_bytes,
                    "created_at": backup.created_at.astimezone(timezone.utc).isoformat(),
                }
            )
        return results

    def restore_from_backup(self, backup_name: Optional[str] = None) -> bool:
        with Session(self._engine) as session:
            if backup_name:
                stmt = select(_StateBackup).where(_StateBackup.name == backup_name)
            else:
                stmt = select(_StateBackup).order_by(_StateBackup.created_at.desc())
            backup = session.exec(stmt).first()
            if backup is None:
                return False
            state = backup.data if isinstance(backup.data, dict) else {}
            meta = {
                "version": STATE_VERSION,
                "updated_at": _now_iso(),
                "checksum": _compute_checksum(state),
            }
            state["_metadata"] = meta
            sanitized = _json_roundtrip(state)
            snapshot = session.get(_StateSnapshot, 1)
            if snapshot is None:
                snapshot = _StateSnapshot(
                    id=1,
                    data=sanitized,
                    version=STATE_VERSION,
                    checksum=meta["checksum"],
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(snapshot)
            else:
                snapshot.data = sanitized
                snapshot.version = STATE_VERSION
                snapshot.checksum = meta["checksum"]
                snapshot.updated_at = datetime.now(timezone.utc)
            session.commit()
            if self._cache_enabled:
                self._cache = state
                self._cache_mtime = snapshot.updated_at.timestamp()
            return True

    def get_stats(self) -> dict:
        with self._lock:
            state = self._read_state()
            return {
                "connections_count": len(state.get("connections", {})),
                "templates_count": len(state.get("templates", {})),
                "schedules_count": len(state.get("schedules", {})),
                "jobs_count": len(state.get("jobs", {})),
                "backups_count": len(self.list_backups()),
                "state_file_exists": self._db_path.exists(),
            }


def _build_state_store() -> StateStore:
    backend = os.getenv("NEURA_STATE_BACKEND", "sqlite").strip().lower()
    if backend not in {"sqlite", "file"}:
        logger.warning("state_backend_unknown", extra={"backend": backend})
        backend = "sqlite"
    if backend == "file":
        store = StateStore()
        setattr(store, "backend_name", "file")
        return store
    try:
        store = SQLiteStateStore()
        setattr(store, "backend_name", "sqlite")
        return store
    except Exception as exc:
        logger.error("state_store_sqlite_failed", extra={"error": str(exc)})
        store = StateStore()
        setattr(store, "backend_name", "file")
        setattr(store, "backend_fallback", True)
        return store


class StateStoreProxy:
    def __init__(self, store: StateStore) -> None:
        self._store = store

    def set(self, store: StateStore) -> None:
        self._store = store

    def get(self) -> StateStore:
        return self._store

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401 - proxy
        return getattr(self._store, name)


state_store = StateStoreProxy(_build_state_store())


def set_state_store(store: StateStore) -> None:
    """Swap the underlying global state store (primarily for tests)."""
    state_store.set(store)
