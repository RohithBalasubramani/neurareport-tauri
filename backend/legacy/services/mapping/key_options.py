from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import Request

from backend.app.repositories.connections.db_connection import verify_sqlite
from backend.app.repositories.dataframes import sqlite_shim as sqlite3
from backend.app.services.mapping.HeaderMapping import approval_errors
from backend.app.repositories.state import state_store
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.mapping_utils import load_mapping_keys
from backend.legacy.utils.template_utils import template_dir
from backend.legacy.services.mapping.helpers import (
    build_mapping_lookup,
    execute_token_query,
    execute_token_query_df,
    extract_contract_metadata,
    http_error,
    normalize_tokens_request,
    resolve_token_binding,
    write_debug_log,
)

logger = logging.getLogger(__name__)


def mapping_key_options(
    template_id: str,
    request: Request,
    connection_id: str | None = None,
    tokens: str | None = None,
    limit: int = 50,
    start_date: str | None = None,
    end_date: str | None = None,
    *,
    kind: str = "pdf",
    debug: bool = False,
):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.info(
        "mapping_key_options_start",
        extra={
            "event": "mapping_key_options_start",
            "template_id": template_id,
            "connection_id": connection_id,
            "tokens": tokens,
            "limit": limit,
            "start_date": start_date,
            "end_date": end_date,
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )

    def _resolve_connection_id(explicit_id: str | None) -> str | None:
        if explicit_id:
            explicit_id = str(explicit_id).strip()
            if explicit_id:
                return explicit_id
        try:
            record = state_store.get_template_record(template_id) or {}
        except Exception:
            record = {}
        last_conn = record.get("last_connection_id")
        if last_conn:
            return str(last_conn)
        last_used = state_store.get_last_used() or {}
        fallback_conn = last_used.get("connection_id")
        return str(fallback_conn) if fallback_conn else None

    effective_connection_id = _resolve_connection_id(connection_id)

    try:
        template_dir_path = template_dir(template_id, kind=kind)
    except Exception:
        # Template directory doesn't exist on disk — return empty keys
        # rather than a hard 404, since key options are optional.
        logger.info("mapping_key_options_no_dir", extra={"template_id": template_id, "kind": kind})
        return {"keys": {}}

    keys_available = load_mapping_keys(template_dir_path)
    if not keys_available:
        return {"keys": {}}

    token_list = normalize_tokens_request(tokens, keys_available)
    if not token_list:
        return {"keys": {}}

    try:
        limit_value = int(limit)
    except (TypeError, ValueError):
        limit_value = 50
    limit_value = max(1, min(limit_value, 500))

    mapping_path = template_dir_path / "mapping_pdf_labels.json"
    if not mapping_path.exists():
        return {"keys": {}}
    try:
        mapping_doc = json.loads(mapping_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception("Failed to read mapping file")
        raise http_error(500, "mapping_load_failed", "Failed to read mapping file")

    if not isinstance(mapping_doc, list):
        raise http_error(500, "mapping_invalid", "Approved mapping is not in the expected format.")
    mapping_lookup = build_mapping_lookup(mapping_doc)

    contract_filters_required: dict[str, str] = {}
    contract_filters_optional: dict[str, str] = {}
    contract_date_columns: dict[str, str] = {}
    contract_join: dict[str, Any] = {}
    contract_path = template_dir_path / "contract.json"
    if contract_path.exists():
        try:
            contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
        except Exception:
            contract_data = {}
        (
            contract_filters_required,
            contract_filters_optional,
            contract_date_columns,
        ) = extract_contract_metadata(contract_data)
        if isinstance(contract_data, dict):
            join_section = contract_data.get("join")
            if isinstance(join_section, dict):
                contract_join = join_section

    db_path = db_path_from_payload_or_default(effective_connection_id)
    verify_sqlite(db_path)

    options: dict[str, list[str]] = {}
    debug_payload: dict[str, Any] = {
        "template_id": template_id,
        "connection_id": effective_connection_id,
        "db_path": str(db_path),
        "tokens_available": keys_available,
        "token_details": {},
    }

    # Optional local fallback DB for templates that ship auxiliary lookup tables
    # (e.g., runtime_machine_keys.db) alongside their artifacts.
    fallback_db_path = template_dir_path / "runtime_machine_keys.db"

    # DataFrame pipeline is the only mode
    _use_df = True

    with sqlite3.connect(str(db_path)) as con:
        con.row_factory = sqlite3.Row
        for token in token_list:
            table_clean, column_clean, binding_source = resolve_token_binding(
                token,
                mapping_lookup,
                contract_filters_required,
                contract_filters_optional,
            )
            if not table_clean or not column_clean:
                options[token] = []
                continue
            date_column_name = contract_date_columns.get(table_clean.lower())

            def _schema_machine_columns(connection):
                parent_table = str(contract_join.get("parent_table") or "").strip() or "neuract__RUNHOURS"
                if _use_df:
                    try:
                        from backend.legacy.utils.connection_utils import get_loader_for_ref
                        loader = get_loader_for_ref(db_path)
                        df = loader.frame(parent_table)
                        columns = [str(c) for c in df.columns]
                    except Exception:
                        return [], {"error": "DataFrame schema query failed", "table": parent_table}
                else:
                    try:
                        safe_table = parent_table.replace("'", "''")
                        pragma_rows = list(
                            connection.execute(f"PRAGMA table_info('{safe_table}')")
                        )
                        columns = [row[1] for row in pragma_rows if len(row) > 1]
                    except Exception as exc:  # pragma: no cover - defensive
                        return [], {"error": "Schema query failed", "table": parent_table}

                filtered = [col for col in columns if "hrs" in str(col or "").lower()]
                filtered.sort()
                limited = filtered[:limit_value]
                return limited, {
                    "table": parent_table,
                    "column_source": "schema_columns",
                    "row_count": len(limited),
                }

            # Primary logic: derive machine names from runtime schema columns containing "HRS".
            if token == "machine_name":
                rows, token_debug = _schema_machine_columns(con)
                if binding_source:
                    token_debug["binding_source"] = binding_source
                options[token] = rows
                debug_payload["token_details"][token] = token_debug
                continue

            def _run_query(connection, *, mark_fallback: bool = False, query_db_path=db_path):
                if _use_df:
                    rows_inner, debug_inner = execute_token_query_df(
                        query_db_path,
                        token=token,
                        table_clean=table_clean,
                        column_clean=column_clean,
                        date_column_name=date_column_name,
                        start_date=start_date,
                        end_date=end_date,
                        limit_value=limit_value,
                    )
                else:
                    rows_inner, debug_inner = execute_token_query(
                        connection,
                        token=token,
                        table_clean=table_clean,
                        column_clean=column_clean,
                        date_column_name=date_column_name,
                        start_date=start_date,
                        end_date=end_date,
                        limit_value=limit_value,
                    )
                if mark_fallback:
                    debug_inner["fallback_db"] = str(fallback_db_path)
                return rows_inner, debug_inner

            rows, token_debug = _run_query(con)

            def _fallback_schema_columns(con_ref):
                fallback_table = str(contract_join.get("parent_table") or "").strip()
                if not fallback_table:
                    fallback_table = "neuract__RUNHOURS"
                try:
                    safe_fallback_table = fallback_table.replace("'", "''")
                    pragma_rows = list(
                        con_ref.execute(f"PRAGMA table_info('{safe_fallback_table}')")
                    )
                    columns = [row[1] for row in pragma_rows if len(row) > 1]
                except Exception as exc:  # pragma: no cover - defensive
                    return [], {"fallback_error": "Fallback schema query failed", "fallback_table": fallback_table}

                filtered = [col for col in columns if "hrs" in str(col or "").lower()]
                filtered.sort()
                return filtered[:limit_value], {"fallback_table": fallback_table}

            needs_fallback = (
                not rows
                and fallback_db_path.exists()
                and isinstance(token_debug.get("error"), str)
                and "no such table" in token_debug["error"].lower()
            )
            if needs_fallback:
                with sqlite3.connect(str(fallback_db_path)) as fallback_con:
                    fallback_con.row_factory = sqlite3.Row
                    rows, token_debug = _run_query(fallback_con, mark_fallback=True, query_db_path=fallback_db_path)
            elif not rows and isinstance(token_debug.get("error"), str):
                err_text = token_debug.get("error", "").lower()
                if "no such table" in err_text or "no such column" in err_text:
                    fallback_rows, fallback_meta = _fallback_schema_columns(con)
                    if fallback_rows:
                        rows = fallback_rows
                        token_debug["fallback_used"] = True
                        token_debug["fallback_source"] = "schema_columns"
                        token_debug["row_count"] = len(rows)
                    token_debug.update(fallback_meta)

            if binding_source:
                token_debug["binding_source"] = binding_source
            options[token] = rows
            if token_debug.get("error"):
                logger.warning(
                    "mapping_key_query_failed",
                    extra={
                        "event": "mapping_key_query_failed",
                        "template_id": template_id,
                        "token": token,
                        "table": table_clean,
                        "column": column_clean,
                        "db_path": str(db_path),
                        "error": token_debug["error"],
                        "correlation_id": correlation_id,
                    },
                )
            debug_payload["token_details"][token] = token_debug

    logger.info(
        "mapping_key_options_complete",
        extra={
            "event": "mapping_key_options_complete",
            "template_id": template_id,
            "tokens": token_list,
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )
    response: dict[str, Any] = {"keys": options}
    write_debug_log(template_id, kind=kind, event="mapping_key_options", payload=debug_payload)
    if debug:
        response["debug"] = debug_payload
    return response