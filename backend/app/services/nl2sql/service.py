"""Service layer for Natural Language to SQL feature."""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import re

from backend.app.utils.errors import AppError
from backend.app.utils.sql_safety import get_write_operation, is_select_or_with
from backend.app.repositories.connections.db_connection import resolve_db_path, verify_sqlite
from backend.app.repositories.dataframes import sqlite_shim, ensure_connection_loaded
from backend.app.services.llm.client import get_llm_client
from backend.app.services.llm.text_to_sql import TextToSQL, TableSchema
from backend.app.repositories.state import store as state_store_module

from backend.app.schemas.nl2sql import (
    NL2SQLGenerateRequest,
    NL2SQLExecuteRequest,
    NL2SQLSaveRequest,
    NL2SQLResult,
    QueryExecutionResult,
    SavedQuery,
    QueryHistoryEntry,
)

logger = logging.getLogger("neura.domain.nl2sql")

_TRAILING_SEMICOLONS_RE = re.compile(r";+\s*$")


def _strip_trailing_semicolons(sql: str) -> str:
    # Users commonly paste SQL ending with ';'. That breaks subquery wrapping/pagination.
    return _TRAILING_SEMICOLONS_RE.sub("", (sql or "").strip())


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_store():
    return state_store_module.state_store


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _coerce_value(value: Any) -> Any:
    """Convert bytes and other non-JSON types to serializable formats."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    try:
        if hasattr(value, "item"):
            return value.item()
    except Exception:
        pass
    return value


class NL2SQLService:
    """Service for natural language to SQL operations."""

    def __init__(self):
        self._text_to_sql: Optional[TextToSQL] = None

    def _get_text_to_sql(self) -> TextToSQL:
        """Get or create TextToSQL instance."""
        if self._text_to_sql is None:
            client = get_llm_client()
            self._text_to_sql = TextToSQL(client=client, dialect="sqlite")
        return self._text_to_sql

    def _resolve_connection(self, connection_id: str) -> Path:
        """Resolve and verify a database connection."""
        try:
            db_path = resolve_db_path(connection_id=connection_id, db_url=None, db_path=None)
            verify_sqlite(db_path)
            return db_path
        except Exception as exc:
            logger.warning("Connection validation failed: %s", exc)
            raise AppError(
                code="connection_invalid",
                message="Invalid or unreachable database connection",
                status_code=400,
            )

    def _get_schema_for_connection(self, db_path: Path, tables: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get database schema for SQL generation context using DataFrames."""
        from backend.app.repositories.dataframes.sqlite_loader import get_loader

        loader = get_loader(db_path)
        schema = {}

        table_names = tables if tables else loader.table_names()

        for table_name in table_names:
            if tables and table_name not in tables:
                continue

            columns = []
            for col in loader.pragma_table_info(table_name):
                columns.append({
                    "name": col.get("name"),
                    "type": col.get("type", "TEXT"),
                    "description": "",
                })

            # Get sample values from DataFrame (no direct DB access)
            sample_values = {}
            try:
                frame = loader.frame(table_name)
                if not frame.empty:
                    sample_rows = frame.head(3)
                    for col in columns:
                        col_name = col["name"]
                        if col_name in sample_rows.columns:
                            values = [_coerce_value(v) for v in sample_rows[col_name].tolist()]
                            if values:
                                sample_values[col_name] = values[:3]
            except Exception as e:
                logger.debug("Failed to extract sample values for %s: %s", table_name, e)

            schema[table_name] = {
                "columns": columns,
                "foreign_keys": loader.foreign_keys(table_name),
                "sample_values": sample_values,
            }

        return schema

    def generate_sql(
        self,
        request: NL2SQLGenerateRequest,
        correlation_id: Optional[str] = None,
    ) -> NL2SQLResult:
        """Generate SQL from a natural language question."""
        logger.info(f"Generating SQL for question: {request.question[:100]}...", extra={"correlation_id": correlation_id})

        # Resolve and verify connection
        db_path = self._resolve_connection(request.connection_id)

        # Get schema for context
        schema = self._get_schema_for_connection(db_path, request.tables)
        if not schema:
            raise AppError(
                code="no_tables",
                message="No tables found in the database",
                status_code=400,
            )

        # Set up TextToSQL with schema
        t2sql = self._get_text_to_sql()
        t2sql._schemas.clear()  # Clear previous schemas
        t2sql.add_schemas_from_catalog(schema)

        # Generate SQL
        try:
            result = t2sql.generate_sql(
                question=request.question,
                tables=request.tables,
                context=request.context,
            )
        except Exception as exc:
            logger.error(f"SQL generation failed: {exc}", extra={"correlation_id": correlation_id})
            raise AppError(
                code="generation_failed",
                message="Failed to generate SQL query",
                status_code=500,
            )

        # Record in history
        self._record_history(
            question=request.question,
            sql=result.sql,
            connection_id=request.connection_id,
            confidence=result.confidence,
            success=True,
        )

        return NL2SQLResult(
            sql=result.sql,
            explanation=result.explanation,
            confidence=result.confidence,
            warnings=result.warnings,
            original_question=request.question,
        )

    def execute_query(
        self,
        request: NL2SQLExecuteRequest,
        correlation_id: Optional[str] = None,
    ) -> QueryExecutionResult:
        """Execute a SQL query and return results using DataFrames."""
        logger.info(f"Executing SQL query on connection {request.connection_id}", extra={"correlation_id": correlation_id})

        # Resolve and verify connection
        db_path = self._resolve_connection(request.connection_id)

        # Ensure DataFrames are loaded for this connection
        ensure_connection_loaded(request.connection_id, db_path)

        sql_clean = _strip_trailing_semicolons(request.sql)

        # Validate SQL (read-only safety check)
        if not is_select_or_with(sql_clean):
            raise AppError(
                code="invalid_query",
                message="Only SELECT queries are allowed",
                status_code=400,
            )

        write_op = get_write_operation(sql_clean)
        if write_op:
            raise AppError(
                code="dangerous_query",
                message=f"Query contains prohibited operation: {write_op}",
                status_code=400,
            )

        # Execute query using DataFrame shim
        started = time.time()
        try:
            with sqlite_shim.connect(str(db_path)) as con:
                con.row_factory = sqlite_shim.Row

                total_count = None
                if request.include_total:
                    count_sql = f"SELECT COUNT(*) as cnt FROM ({sql_clean}) AS subq"
                    try:
                        total_count = con.execute(count_sql).fetchone()["cnt"]
                    except Exception:
                        total_count = None

                # Execute with limit and offset
                limited_sql = f"SELECT * FROM ({sql_clean}) AS subq LIMIT {request.limit} OFFSET {request.offset}"
                cur = con.execute(limited_sql)
                rows_raw = cur.fetchall()

                # Get column names from cursor description (reliable across all Row types)
                columns = [desc[0] for desc in cur.description] if cur.description else []
                rows = [{col: _coerce_value(row[i]) for i, col in enumerate(columns)} for row in rows_raw]

        except sqlite_shim.OperationalError as exc:
            execution_time_ms = int((time.time() - started) * 1000)
            logger.error(f"Query execution failed: {exc}", extra={"correlation_id": correlation_id})

            # Record failure in history
            self._update_history_execution(
                sql=request.sql,
                connection_id=request.connection_id,
                success=False,
                error="Query execution failed",
                execution_time_ms=execution_time_ms,
            )

            raise AppError(
                code="execution_failed",
                message="Failed to execute SQL query",
                status_code=400,
            )

        execution_time_ms = int((time.time() - started) * 1000)

        # Record success in history
        self._update_history_execution(
            sql=request.sql,
            connection_id=request.connection_id,
            success=True,
            execution_time_ms=execution_time_ms,
            row_count=len(rows),
        )

        return QueryExecutionResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            total_count=total_count,
            execution_time_ms=execution_time_ms,
            truncated=total_count is not None and total_count > request.limit,
        )

    def explain_query(
        self,
        sql: str,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Get a natural language explanation of a SQL query."""
        t2sql = self._get_text_to_sql()
        return t2sql.explain_sql(sql)

    def save_query(
        self,
        request: NL2SQLSaveRequest,
        correlation_id: Optional[str] = None,
    ) -> SavedQuery:
        """Save a query as a reusable data source."""
        logger.info(f"Saving query: {request.name}", extra={"correlation_id": correlation_id})

        # Verify connection exists
        self._resolve_connection(request.connection_id)

        query_id = str(uuid.uuid4())
        now = _now_iso()

        saved_query = SavedQuery(
            id=query_id,
            name=request.name,
            description=request.description,
            sql=request.sql,
            connection_id=request.connection_id,
            original_question=request.original_question,
            tags=request.tags or [],
            created_at=now,
            updated_at=now,
            run_count=0,
        )

        # Persist to state store
        store = _state_store()
        store.save_query(saved_query.model_dump(mode="json"))

        return saved_query

    def list_saved_queries(
        self,
        connection_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[SavedQuery]:
        """List saved queries, optionally filtered."""
        store = _state_store()
        queries = store.list_saved_queries()

        if connection_id:
            queries = [q for q in queries if q.get("connection_id") == connection_id]

        if tags:
            tag_set = set(tags)
            queries = [q for q in queries if tag_set.intersection(set(q.get("tags", [])))]

        return [SavedQuery(**q) for q in queries]

    def get_saved_query(self, query_id: str) -> Optional[SavedQuery]:
        """Get a saved query by ID."""
        store = _state_store()
        query = store.get_saved_query(query_id)
        return SavedQuery(**query) if query else None

    def delete_saved_query(self, query_id: str) -> bool:
        """Delete a saved query."""
        store = _state_store()
        return store.delete_saved_query(query_id)

    def get_query_history(
        self,
        connection_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[QueryHistoryEntry]:
        """Get query history."""
        store = _state_store()
        history = store.get_query_history(limit=limit)

        if connection_id:
            history = [h for h in history if h.get("connection_id") == connection_id]

        return [QueryHistoryEntry(**h) for h in history]

    def delete_query_history_entry(self, entry_id: str) -> bool:
        """Delete a query history entry by ID."""
        store = _state_store()
        return store.delete_query_history_entry(entry_id)

    def _record_history(
        self,
        question: str,
        sql: str,
        connection_id: str,
        confidence: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Record a query generation in history."""
        store = _state_store()
        entry = {
            "id": str(uuid.uuid4())[:8],
            "question": question,
            "sql": sql,
            "connection_id": connection_id,
            "confidence": confidence,
            "success": success,
            "error": error,
            "created_at": _now_iso(),
        }
        store.add_query_history(entry)

    def _update_history_execution(
        self,
        sql: str,
        connection_id: str,
        success: bool,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        row_count: Optional[int] = None,
    ) -> None:
        """Update history with execution results."""
        # This could be enhanced to update the last matching history entry
        pass  # For now, execution results are returned directly
