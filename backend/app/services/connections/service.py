from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from backend.app.repositories.connections.repository import ConnectionRepository
from backend.app.schemas.connections import ConnectionResponse, ConnectionTestRequest, ConnectionUpsertRequest
from backend.app.utils.errors import AppError

logger = logging.getLogger(__name__)


# Supported database types and their default ports
SUPPORTED_DB_TYPES = {
    "sqlite": {"port": None, "requires_auth": False},
    "postgresql": {"port": 5432, "requires_auth": True},
    "mysql": {"port": 3306, "requires_auth": True},
    "mssql": {"port": 1433, "requires_auth": True},
    "mariadb": {"port": 3306, "requires_auth": True},
}


def _parse_db_url(db_url: str) -> dict:
    """Parse a database URL into components."""
    if not db_url:
        return {}

    # Handle SQLite special case
    if db_url.startswith("sqlite"):
        match = re.match(r"sqlite(?:3)?:///(.+)", db_url)
        if match:
            return {"db_type": "sqlite", "database": match.group(1)}
        return {"db_type": "sqlite", "database": db_url}

    try:
        parsed = urlparse(db_url)
        db_type = parsed.scheme.lower()
        # Normalize postgres -> postgresql
        if db_type == "postgres":
            db_type = "postgresql"
        return {
            "db_type": db_type,
            "host": parsed.hostname or "localhost",
            "port": parsed.port,
            "database": parsed.path.lstrip("/") if parsed.path else "",
            "username": parsed.username,
            "password": parsed.password,
        }
    except Exception:
        return {}


class ConnectionService:
    def __init__(self, repo: ConnectionRepository | None = None):
        self.repo = repo or ConnectionRepository()

    def list(self, correlation_id: str | None = None):
        """List all connections via the repository."""
        return self.repo.list()

    def _resolve_and_verify(
        self,
        *,
        connection_id: str | None,
        db_url: str | None,
        db_path: str | None,
        db_type: str | None = None,
        verify: bool = True,
    ) -> Path | str:
        """Resolve and optionally verify a database connection.

        For SQLite, returns a Path. For other databases, returns the connection URL.
        """
        # Determine database type from URL or explicit parameter
        parsed = _parse_db_url(db_url) if db_url else {}
        detected_type = db_type or parsed.get("db_type") or "sqlite"

        if detected_type == "sqlite":
            # SQLite: verify file path
            try:
                path = self.repo.resolve_path(connection_id=connection_id, db_url=db_url, db_path=db_path)
                if verify:
                    self.repo.verify(path)
                return path
            except Exception as exc:
                raise AppError(
                    code="invalid_database",
                    message="Invalid or unreachable database",
                    detail=None,
                    status_code=400,
                )
        else:
            # Other databases: validate URL format and test connection
            if not db_url:
                raise AppError(
                    code="invalid_database",
                    message="Database URL is required for non-SQLite databases",
                    status_code=400,
                )
            if verify:
                self._verify_network_database(db_url, detected_type)
            return db_url

    def _verify_network_database(self, db_url: str, db_type: str) -> None:
        """Verify a network database connection."""
        parsed = _parse_db_url(db_url)
        host = parsed.get("host", "localhost")
        port = parsed.get("port")

        if not port:
            port = SUPPORTED_DB_TYPES.get(db_type, {}).get("port", 5432)

        # Basic connectivity check using socket
        import socket
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            if result != 0:
                raise AppError(
                    code="connection_failed",
                    message=f"Cannot connect to {db_type} at {host}:{port}",
                    status_code=503,
                )
        except socket.error as exc:
            raise AppError(
                code="connection_failed",
                message=f"Network error connecting to {db_type}",
                detail=None,
                status_code=503,
            )
        finally:
            if sock:
                sock.close()

    def test(self, payload: ConnectionTestRequest, correlation_id: str | None = None) -> dict:
        started = time.time()

        # Parse the URL to determine database type
        parsed = _parse_db_url(payload.db_url) if payload.db_url else {}
        db_type = payload.db_type or parsed.get("db_type") or "sqlite"

        if db_type not in SUPPORTED_DB_TYPES:
            raise AppError(
                code="unsupported_database",
                message=f"Database type '{db_type}' is not supported. Supported: {', '.join(SUPPORTED_DB_TYPES.keys())}",
                status_code=400,
            )

        # Resolve and verify the connection
        connection_ref = self._resolve_and_verify(
            connection_id=None,
            db_url=payload.db_url,
            db_path=payload.database,
            db_type=db_type,
            verify=True,
        )

        latency_ms = int((time.time() - started) * 1000)

        # Build connection config
        if db_type == "sqlite":
            resolved = Path(connection_ref).resolve()
            cfg = {
                "db_type": db_type,
                "database": str(resolved),
                "db_url": payload.db_url,
                "name": resolved.name,
                "status": "connected",
                "latency_ms": latency_ms,
            }
            display_name = resolved.name
            normalized = {"db_type": db_type, "database": str(resolved)}
        else:
            cfg = {
                "db_type": db_type,
                "database": parsed.get("database", ""),
                "host": parsed.get("host", "localhost"),
                "port": parsed.get("port") or SUPPORTED_DB_TYPES[db_type]["port"],
                "db_url": payload.db_url,
                "name": f"{db_type}://{parsed.get('host', 'localhost')}/{parsed.get('database', '')}",
                "status": "connected",
                "latency_ms": latency_ms,
            }
            display_name = f"{parsed.get('host', 'localhost')}:{parsed.get('database', '')}"
            normalized = {"db_type": db_type, "host": parsed.get("host"), "database": parsed.get("database")}

        connection_id = self.repo.save(cfg)
        self.repo.record_ping(connection_id, status="connected", detail="Connected", latency_ms=latency_ms)

        return {
            "ok": True,
            "details": f"Connected ({display_name})",
            "latency_ms": latency_ms,
            "connection_id": connection_id,
            "normalized": normalized,
            "correlation_id": correlation_id,
        }

    def upsert(self, payload: ConnectionUpsertRequest, correlation_id: str | None = None) -> ConnectionResponse:
        # Parse to determine type
        parsed = _parse_db_url(payload.db_url) if payload.db_url else {}
        db_type = payload.db_type or parsed.get("db_type") or "sqlite"

        connection_ref = self._resolve_and_verify(
            connection_id=payload.id,
            db_url=payload.db_url,
            db_path=payload.database,
            db_type=db_type,
            verify=False,
        )

        if db_type == "sqlite":
            db_path_str = str(connection_ref)
            name = payload.name or Path(connection_ref).name
        else:
            db_path_str = payload.db_url or str(connection_ref)
            name = payload.name or f"{db_type}://{parsed.get('host', 'localhost')}/{parsed.get('database', '')}"

        record = self.repo.upsert(
            conn_id=payload.id,
            name=name,
            db_type=db_type,
            database_path=db_path_str,
            secret_payload={"db_url": payload.db_url, "database": db_path_str},
            status=payload.status,
            latency_ms=payload.latency_ms,
            tags=payload.tags,
        )
        if payload.status:
            self.repo.record_ping(record["id"], status=payload.status, detail=None, latency_ms=payload.latency_ms)
        return ConnectionResponse(
            id=record["id"],
            name=record["name"],
            db_type=record["db_type"],
            database_path=Path(db_path_str) if db_type == "sqlite" else None,
            status=record.get("status") or "unknown",
            latency_ms=record.get("latency_ms"),
        )

    def delete(self, connection_id: str) -> None:
        if not self.repo.delete(connection_id):
            raise AppError(code="connection_not_found", message="Connection not found", status_code=404)

    def _execute_health_query(self, db_path: str, db_type: str) -> tuple[bool, str]:
        """Execute a simple query to verify database is actually working.

        Returns:
            Tuple of (success, message)
        """
        if db_type == "sqlite":
            import sqlite3
            conn = None
            try:
                conn = sqlite3.connect(db_path, timeout=5)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True, "Query executed successfully"
            except sqlite3.Error as e:
                logger.warning("sqlite_connection_test_failed", extra={"error": str(e)})
                return False, "SQLite connection test failed"
            finally:
                if conn:
                    conn.close()
        elif db_type in ("postgresql", "postgres"):
            from sqlalchemy import create_engine, text as sa_text
            engine = None
            try:
                engine = create_engine(db_path, connect_args={"connect_timeout": 5})
                with engine.connect() as conn:
                    conn.execute(sa_text("SELECT 1"))
                return True, "Query executed successfully"
            except Exception as e:
                logger.warning("postgres_connection_test_failed", extra={"error": str(e)})
                return False, "PostgreSQL connection test failed"
            finally:
                if engine:
                    engine.dispose()
        else:
            return True, "Port accessible"

    def healthcheck(self, connection_id: str, correlation_id: str | None = None) -> dict:
        """Verify a saved connection is still accessible and can execute queries."""
        secrets = self.repo.get_secrets(connection_id)
        if not secrets:
            raise AppError(code="connection_not_found", message="Connection not found", status_code=404)

        db_path = secrets.get("database_path") or secrets.get("database")
        db_url = secrets.get("db_url")
        if not db_path and not db_url:
            raise AppError(
                code="invalid_connection",
                message="Connection has no database path or URL",
                status_code=400,
            )

        # Determine database type
        parsed = _parse_db_url(db_url) if db_url else {}
        db_type = parsed.get("db_type") or "sqlite"

        started = time.time()

        # First check file/network accessibility
        try:
            if db_type == "sqlite":
                self.repo.verify(Path(db_path))
            else:
                self._verify_network_database(db_url, db_type)
        except Exception as exc:
            latency_ms = int((time.time() - started) * 1000)
            self.repo.record_ping(connection_id, status="error", detail=str(exc), latency_ms=latency_ms)
            raise AppError(
                code="connection_failed",
                message="Database connection failed",
                detail=None,
                status_code=503,
            )

        # Then execute a test query to verify database is actually working
        success, message = self._execute_health_query(db_path or db_url, db_type)
        latency_ms = int((time.time() - started) * 1000)

        if not success:
            self.repo.record_ping(connection_id, status="error", detail=message, latency_ms=latency_ms)
            raise AppError(
                code="connection_failed",
                message="Database query failed",
                detail=message,
                status_code=503,
            )

        self.repo.record_ping(connection_id, status="connected", detail="Health check passed", latency_ms=latency_ms)
        return {
            "status": "connected",
            "latency_ms": latency_ms,
            "connection_id": connection_id,
            "correlation_id": correlation_id,
        }
