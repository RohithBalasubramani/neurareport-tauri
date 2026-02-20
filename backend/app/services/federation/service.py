"""Service layer for Cross-Database Federation feature."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.app.utils.errors import AppError
from backend.app.utils.sql_safety import get_write_operation, is_select_or_with
from backend.app.repositories.state import store as state_store_module
from backend.app.services.llm.client import get_llm_client
from backend.app.services.utils.llm import extract_json_array_from_llm_response
from backend.app.repositories.connections.schema import get_connection_schema

from backend.app.schemas.federation import (
    VirtualSchema,
    VirtualSchemaCreate,
    JoinSuggestion,
    TableReference,
    JoinCondition,
    FederatedQueryRequest,
)

logger = logging.getLogger("neura.domain.federation")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _state_store():
    return state_store_module.state_store


class FederationService:
    """Service for cross-database federation operations."""

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client

    def _get_connection_schema(self, connection_id: str) -> Dict[str, Any]:
        """Get schema for a connection."""
        return get_connection_schema(connection_id, include_row_counts=False, sample_rows=3)

    def create_virtual_schema(
        self,
        request: VirtualSchemaCreate,
        correlation_id: Optional[str] = None,
    ) -> VirtualSchema:
        """Create a new virtual schema."""
        logger.info(f"Creating virtual schema: {request.name}", extra={"correlation_id": correlation_id})

        schema_id = str(uuid.uuid4())[:8]
        now = _now_iso()

        # Gather tables from all connections
        tables: List[TableReference] = []
        for conn_id in request.connection_ids:
            try:
                schema = self._get_connection_schema(conn_id)
                for table in schema.get("tables", []):
                    tables.append(TableReference(
                        connection_id=conn_id,
                        table_name=table["name"],
                        alias=f"{conn_id[:4]}_{table['name']}"
                    ))
            except Exception as exc:
                logger.warning(f"Failed to get schema for {conn_id}: {exc}")

        virtual_schema = VirtualSchema(
            id=schema_id,
            name=request.name,
            description=request.description,
            connections=request.connection_ids,
            tables=tables,
            joins=[],
            created_at=now,
            updated_at=now,
        )

        # Persist
        store = _state_store()
        with store.transaction() as state:
            state.setdefault("virtual_schemas", {})[schema_id] = virtual_schema.model_dump()

        return virtual_schema

    def suggest_joins(
        self,
        connection_ids: List[str],
        correlation_id: Optional[str] = None,
    ) -> List[JoinSuggestion]:
        """Suggest joins between tables in different connections using AI."""
        logger.info(f"Suggesting joins for {len(connection_ids)} connections", extra={"correlation_id": correlation_id})

        # Gather schemas
        schemas = {}
        for conn_id in connection_ids:
            try:
                schemas[conn_id] = self._get_connection_schema(conn_id)
            except Exception as exc:
                logger.warning(f"Failed to get schema for {conn_id}: {exc}")

        if len(schemas) < 2:
            return []

        # Build prompt for LLM
        schema_desc = []
        for conn_id, schema in schemas.items():
            tables_desc = []
            for table in schema.get("tables", []):
                cols = [f"{c['name']} ({c.get('type', 'TEXT')})" for c in table.get("columns", [])]
                tables_desc.append(f"  - {table['name']}: {', '.join(cols)}")
            schema_desc.append(f"Connection {conn_id}:\n" + "\n".join(tables_desc))

        prompt = f"""Analyze these database schemas and suggest joins between tables from different connections.

{chr(10).join(schema_desc)}

For each potential join, consider:
1. Column names that might match (like 'customer_id', 'user_id', 'id')
2. Data types compatibility
3. Business logic relationships

Return a JSON array of join suggestions:
[
  {{
    "left_connection_id": "conn1",
    "left_table": "table1",
    "left_column": "column1",
    "right_connection_id": "conn2",
    "right_table": "table2",
    "right_column": "column2",
    "confidence": 0.9,
    "reason": "Both columns appear to be customer identifiers"
  }}
]

Return ONLY the JSON array."""

        try:
            client = self._get_llm_client()
            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                description="join_suggestion",
                temperature=0.0,
            )

            content = response["choices"][0]["message"]["content"]
            suggestions_data = extract_json_array_from_llm_response(content, default=[])
            if suggestions_data:
                return [JoinSuggestion(**s) for s in suggestions_data]

        except Exception as exc:
            logger.error(f"Join suggestion failed: {exc}")

        return []

    def list_virtual_schemas(self) -> List[VirtualSchema]:
        """List all virtual schemas."""
        store = _state_store()
        with store.transaction() as state:
            schemas = state.get("virtual_schemas", {})
            return [VirtualSchema(**s) for s in schemas.values()]

    def get_virtual_schema(self, schema_id: str) -> Optional[VirtualSchema]:
        """Get a virtual schema by ID."""
        store = _state_store()
        with store.transaction() as state:
            schema = state.get("virtual_schemas", {}).get(schema_id)
            return VirtualSchema(**schema) if schema else None

    def delete_virtual_schema(self, schema_id: str) -> bool:
        """Delete a virtual schema."""
        store = _state_store()
        with store.transaction() as state:
            schemas = state.get("virtual_schemas", {})
            if schema_id not in schemas:
                return False
            del schemas[schema_id]
        return True

    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL query using improved parsing.

        Handles:
        - Simple table names: FROM users
        - Quoted identifiers: FROM "users", FROM `users`, FROM [users]
        - Schema-qualified names: FROM schema.table
        - Comma-separated tables: FROM a, b, c
        - Various JOIN types: LEFT JOIN, RIGHT JOIN, INNER JOIN, etc.
        - CTEs: WITH cte AS (...) SELECT ... FROM cte
        """
        import re

        # Normalize whitespace
        sql_normalized = " ".join(sql.split())

        # Identifier pattern: handles unquoted, double-quoted, backtick-quoted, and bracket-quoted
        # Also handles schema.table notation
        ident = r'(?:' \
                r'(?:[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)' \
                r'|"[^"]+"(?:\."[^"]+")?'  \
                r'|`[^`]+`(?:\.`[^`]+`)?'  \
                r'|\[[^\]]+\](?:\.\[[^\]]+\])?' \
                r')'

        # Pattern for table lists (comma-separated with optional aliases)
        table_list_pattern = rf'{ident}(?:\s+(?:AS\s+)?[a-zA-Z_][a-zA-Z0-9_]*)?(?:\s*,\s*{ident}(?:\s+(?:AS\s+)?[a-zA-Z_][a-zA-Z0-9_]*)?)*'

        # SQL keyword patterns that precede table names
        patterns = [
            rf'\bFROM\s+({table_list_pattern})',
            rf'\b(?:LEFT|RIGHT|INNER|OUTER|CROSS|FULL)?\s*JOIN\s+({ident})',
            rf'\bJOIN\s+({ident})',
            rf'\bINTO\s+({ident})',
            rf'\bUPDATE\s+({ident})',
        ]

        # Also extract CTE names to exclude them from final results
        cte_pattern = rf'\bWITH\s+({ident})\s+AS\s*\('
        cte_names = set()
        for match in re.findall(cte_pattern, sql_normalized, re.IGNORECASE):
            cte_names.add(self._clean_identifier(match).lower())

        tables = set()
        sql_keywords = {
            'SELECT', 'WHERE', 'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS',
            'HAVING', 'GROUP', 'ORDER', 'BY', 'LIMIT', 'OFFSET', 'UNION',
            'INTERSECT', 'EXCEPT', 'AS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
            'NULL', 'TRUE', 'FALSE', 'IS', 'LIKE', 'BETWEEN', 'ALL', 'ANY',
            'LEFT', 'RIGHT', 'INNER', 'OUTER', 'CROSS', 'FULL', 'NATURAL',
        }

        for pattern in patterns:
            matches = re.findall(pattern, sql_normalized, re.IGNORECASE)
            for match in matches:
                # Handle comma-separated table names
                # Split carefully to handle schema.table notation
                parts = re.split(r'\s*,\s*', match)
                for part in parts:
                    # Extract just the table name (remove alias)
                    tokens = part.strip().split()
                    if tokens:
                        table_ref = tokens[0]
                        # Skip AS keyword if present
                        if table_ref.upper() == 'AS' and len(tokens) > 1:
                            continue

                        table_name = self._clean_identifier(table_ref)

                        # Skip SQL keywords and CTEs
                        if table_name.upper() not in sql_keywords and table_name.lower() not in cte_names:
                            tables.add(table_name.lower())

        return list(tables)

    def _clean_identifier(self, ident: str) -> str:
        """Remove quotes from identifier and extract table name from schema.table."""
        # Remove various quote styles
        cleaned = ident.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        elif cleaned.startswith('`') and cleaned.endswith('`'):
            cleaned = cleaned[1:-1]
        elif cleaned.startswith('[') and cleaned.endswith(']'):
            cleaned = cleaned[1:-1]

        # Handle schema.table notation - extract just the table name
        if '.' in cleaned:
            # Could be schema.table or "schema"."table"
            parts = cleaned.split('.')
            cleaned = parts[-1]
            # Clean the table part if it's still quoted
            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]
            elif cleaned.startswith('`') and cleaned.endswith('`'):
                cleaned = cleaned[1:-1]
            elif cleaned.startswith('[') and cleaned.endswith(']'):
                cleaned = cleaned[1:-1]

        return cleaned

    def _map_tables_to_connections(
        self, table_names: List[str], schema: VirtualSchema
    ) -> Dict[str, List[str]]:
        """Map table names to their respective connections."""
        connection_tables: Dict[str, List[str]] = {}

        for table_name in table_names:
            for table_ref in schema.tables:
                # Match by table name or alias
                if (
                    table_ref.table_name.lower() == table_name.lower()
                    or table_ref.alias.lower() == table_name.lower()
                ):
                    conn_id = table_ref.connection_id
                    if conn_id not in connection_tables:
                        connection_tables[conn_id] = []
                    connection_tables[conn_id].append(table_ref.table_name)
                    break

        return connection_tables

    def _execute_on_connection(
        self,
        connection_id: str,
        sql: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute SQL on a specific connection."""
        from backend.app.repositories.connections.db_connection import execute_query
        return execute_query(connection_id=connection_id, sql=sql, limit=limit)

    def _merge_results(
        self,
        results: List[Dict[str, Any]],
        join_keys: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Merge results from multiple connections."""
        if not results:
            return {"columns": [], "rows": [], "row_count": 0}

        if len(results) == 1:
            return results[0]

        # For simple merge (no join), concatenate results
        if not join_keys:
            all_columns = []
            seen_cols = set()
            for r in results:
                for col in r.get("columns", []):
                    if col not in seen_cols:
                        all_columns.append(col)
                        seen_cols.add(col)

            all_rows = []
            for r in results:
                for row in r.get("rows", []):
                    # Extend row with nulls for missing columns
                    extended_row = []
                    for col in all_columns:
                        try:
                            idx = r.get("columns", []).index(col)
                            extended_row.append(row[idx])
                        except (ValueError, IndexError):
                            extended_row.append(None)
                    all_rows.append(extended_row)

            return {
                "columns": all_columns,
                "rows": all_rows,
                "row_count": len(all_rows),
                "merge_type": "union",
            }

        # Client-side join on specified keys
        if len(results) == 2:
            left = results[0]
            right = results[1]

            left_cols = left.get("columns", [])
            right_cols = right.get("columns", [])

            # Find join key indices
            left_key_idx = None
            right_key_idx = None
            for key in join_keys:
                if key in left_cols:
                    left_key_idx = left_cols.index(key)
                if key in right_cols:
                    right_key_idx = right_cols.index(key)

            if left_key_idx is None or right_key_idx is None:
                # Can't find join keys, return concatenated
                return self._merge_results(results, None)

            # Build right side lookup
            right_lookup: Dict[Any, List[List[Any]]] = {}
            for row in right.get("rows", []):
                key_val = row[right_key_idx]
                if key_val not in right_lookup:
                    right_lookup[key_val] = []
                right_lookup[key_val].append(row)

            # Build merged columns (left cols + right cols without join key)
            merged_cols = list(left_cols) + [
                c for i, c in enumerate(right_cols) if i != right_key_idx
            ]

            # Perform join
            merged_rows = []
            for left_row in left.get("rows", []):
                key_val = left_row[left_key_idx]
                if key_val in right_lookup:
                    for right_row in right_lookup[key_val]:
                        new_row = list(left_row) + [
                            v for i, v in enumerate(right_row) if i != right_key_idx
                        ]
                        merged_rows.append(new_row)

            return {
                "columns": merged_cols,
                "rows": merged_rows,
                "row_count": len(merged_rows),
                "merge_type": "join",
                "join_key": join_keys[0],
            }

        return self._merge_results(results, None)

    def execute_query(
        self,
        request: FederatedQueryRequest,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a federated query across multiple databases.

        This method:
        1. Parses the SQL to identify referenced tables
        2. Maps tables to their respective connections
        3. Routes queries to appropriate connections
        4. Merges results client-side if needed
        """
        logger.info(
            f"Executing federated query on schema {request.virtual_schema_id}",
            extra={"correlation_id": correlation_id}
        )

        # Get the virtual schema
        schema = self.get_virtual_schema(request.virtual_schema_id)
        if not schema:
            raise AppError(
                code="schema_not_found",
                message=f"Virtual schema {request.virtual_schema_id} not found",
                status_code=404,
            )

        if not schema.connections:
            raise AppError(
                code="no_connections",
                message="Virtual schema has no connections",
                status_code=400,
            )

        if not is_select_or_with(request.sql):
            raise AppError(
                code="invalid_query",
                message="Only SELECT queries are allowed",
                status_code=400,
            )

        write_op = get_write_operation(request.sql)
        if write_op:
            raise AppError(
                code="dangerous_query",
                message=f"Query contains prohibited operation: {write_op}",
                status_code=400,
            )

        try:
            # Extract table names from SQL
            table_names = self._extract_table_names(request.sql)
            logger.debug(f"Extracted tables from SQL: {table_names}")

            # Map tables to connections
            connection_tables = self._map_tables_to_connections(table_names, schema)
            logger.debug(f"Table-to-connection mapping: {connection_tables}")

            # If no tables found or all tables in one connection, execute directly
            if len(connection_tables) <= 1:
                target_connection = (
                    list(connection_tables.keys())[0]
                    if connection_tables
                    else schema.connections[0]
                )
                result = self._execute_on_connection(
                    connection_id=target_connection,
                    sql=request.sql,
                    limit=request.limit,
                )
                return {
                    "columns": result.get("columns", []),
                    "rows": result.get("rows", []),
                    "row_count": len(result.get("rows", [])),
                    "schema_id": request.virtual_schema_id,
                    "executed_on": [target_connection],
                    "routing": "single",
                }

            # Multi-connection query: need to split and merge
            logger.info(
                f"Federated query spans {len(connection_tables)} connections",
                extra={"connections": list(connection_tables.keys())}
            )

            # Try to get join keys from schema joins
            join_keys = []
            for join in schema.joins:
                if hasattr(join, "conditions"):
                    for cond in join.conditions:
                        join_keys.extend([cond.left_column, cond.right_column])

            # Execute on each connection
            results = []
            executed_on = []
            for conn_id, tables in connection_tables.items():
                # For each connection, try to execute a query for its tables
                # This is a simplified approach - a more sophisticated implementation
                # would rewrite the SQL for each connection
                try:
                    # Execute the original query on this connection
                    # It will fail for tables it doesn't have, but that's handled
                    result = self._execute_on_connection(
                        connection_id=conn_id,
                        sql=request.sql,
                        limit=request.limit,
                    )
                    results.append(result)
                    executed_on.append(conn_id)
                except Exception as exc:
                    logger.warning(f"Query on {conn_id} failed: {exc}")
                    # Try simpler query for just the tables in this connection
                    for table in tables:
                        try:
                            quoted = '"' + table.replace('"', '""') + '"'
                            simple_sql = f"SELECT * FROM {quoted}"
                            if request.limit:
                                simple_sql += f" LIMIT {request.limit}"
                            result = self._execute_on_connection(
                                connection_id=conn_id,
                                sql=simple_sql,
                                limit=request.limit,
                            )
                            results.append(result)
                            executed_on.append(conn_id)
                        except Exception as inner_exc:
                            logger.warning(f"Simple query on {conn_id}.{table} failed: {inner_exc}")

            if not results:
                raise AppError(
                    code="query_failed",
                    message="Could not execute query on any connection",
                    status_code=500,
                )

            # Merge results
            merged = self._merge_results(results, join_keys if join_keys else None)

            return {
                "columns": merged.get("columns", []),
                "rows": merged.get("rows", [])[:request.limit] if request.limit else merged.get("rows", []),
                "row_count": len(merged.get("rows", [])),
                "schema_id": request.virtual_schema_id,
                "executed_on": executed_on,
                "routing": "federated",
                "merge_type": merged.get("merge_type", "unknown"),
            }

        except AppError:
            raise
        except Exception as exc:
            logger.error(f"Federated query failed: {exc}")
            raise AppError(
                code="query_failed",
                message="Query execution failed",
                status_code=500,
            )
