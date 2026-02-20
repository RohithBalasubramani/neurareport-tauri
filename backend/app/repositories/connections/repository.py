from __future__ import annotations

from pathlib import Path

from backend.app.repositories.connections.db_connection import resolve_db_path, save_connection, verify_sqlite
from backend.app.repositories.state import state_store


class ConnectionRepository:
    def resolve_path(self, *, connection_id: str | None, db_url: str | None, db_path: str | None) -> Path:
        return resolve_db_path(connection_id=connection_id, db_url=db_url, db_path=db_path)

    def verify(self, path: Path) -> None:
        verify_sqlite(path)

    def save(self, payload: dict) -> str:
        return save_connection(payload)

    def upsert(self, **kwargs) -> dict:
        return state_store.upsert_connection(**kwargs)

    def list(self) -> list[dict]:
        return state_store.list_connections()

    def get_secrets(self, connection_id: str) -> dict | None:
        return state_store.get_connection_secrets(connection_id)

    def delete(self, connection_id: str) -> bool:
        return state_store.delete_connection(connection_id)

    def record_ping(self, connection_id: str, status: str, detail: str | None, latency_ms: float | None) -> None:
        state_store.record_connection_ping(connection_id, status=status, detail=detail, latency_ms=latency_ms)
