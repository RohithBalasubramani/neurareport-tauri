"""
Logger Query Service.

Encapsulates SQL queries for Logger-specific data. Since Logger databases have
a known schema, we can write targeted queries for devices, schemas, jobs, etc.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.app.repositories.dataframes.store import get_dataframe_store, ensure_connection_loaded
from backend.app.repositories.connections.db_connection import resolve_connection_ref

logger = logging.getLogger("neura.logger.query")


def _ensure_loaded(connection_id: str) -> None:
    """Ensure the connection's DataFrames are loaded."""
    ref = resolve_connection_ref(connection_id)
    ensure_connection_loaded(
        connection_id,
        db_path=ref["db_path"],
        db_type=ref["db_type"],
        connection_url=ref["connection_url"],
    )


def _query(connection_id: str, sql: str) -> list[dict[str, Any]]:
    """Execute a query and return results as list of dicts."""
    _ensure_loaded(connection_id)
    store = get_dataframe_store()
    return store.execute_query_to_dicts(connection_id, sql)


def get_devices(connection_id: str) -> list[dict[str, Any]]:
    """Get all PLC devices with their configuration."""
    return _query(connection_id, """
        SELECT
            d.id, d.name, d.protocol, d.status, d.latency_ms,
            d.auto_reconnect, d.last_error, d.created_at, d.updated_at
        FROM app_devices d
        ORDER BY d.name
    """)


def get_device_with_config(connection_id: str, device_id: str) -> dict[str, Any] | None:
    """Get a single device with its protocol-specific configuration."""
    devices = _query(connection_id, f"""
        SELECT
            d.id, d.name, d.protocol, d.status, d.latency_ms,
            d.auto_reconnect, d.last_error
        FROM app_devices d
        WHERE CAST(d.id AS VARCHAR) = '{device_id}'
    """)
    if not devices:
        return None
    device = devices[0]

    if device.get("protocol") == "modbus":
        configs = _query(connection_id, f"""
            SELECT host, port, unit_id, timeout_ms, retries
            FROM app_modbus_configs
            WHERE CAST(device_id AS VARCHAR) = '{device_id}'
        """)
        if configs:
            device["config"] = configs[0]
    elif device.get("protocol") == "opcua":
        configs = _query(connection_id, f"""
            SELECT endpoint, auth_type, security_policy, security_mode
            FROM app_opcua_configs
            WHERE CAST(device_id AS VARCHAR) = '{device_id}'
        """)
        if configs:
            device["config"] = configs[0]

    return device


def get_schemas(connection_id: str) -> list[dict[str, Any]]:
    """Get all schemas with their fields."""
    schemas = _query(connection_id, """
        SELECT id, name, description, created_at, updated_at
        FROM app_schemas
        ORDER BY name
    """)

    for schema in schemas:
        schema_id = schema["id"]
        fields = _query(connection_id, f"""
            SELECT key, field_type, unit, scale, description
            FROM app_schema_fields
            WHERE CAST(schema_id AS VARCHAR) = CAST('{schema_id}' AS VARCHAR)
            ORDER BY key
        """)
        schema["fields"] = fields

    return schemas


def get_jobs(connection_id: str) -> list[dict[str, Any]]:
    """Get all logging jobs with status."""
    return _query(connection_id, """
        SELECT
            id, name, job_type, interval_ms, enabled, status,
            batch_size, created_at, updated_at
        FROM app_jobs
        ORDER BY name
    """)


def get_job_runs(connection_id: str, job_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Get execution history for a specific job."""
    return _query(connection_id, f"""
        SELECT
            id, started_at, stopped_at, duration_ms,
            rows_written, reads_count, read_errors, write_errors,
            avg_latency_ms, p95_latency_ms
        FROM app_job_runs
        WHERE CAST(job_id AS VARCHAR) = '{job_id}'
        ORDER BY started_at DESC
        LIMIT {int(limit)}
    """)


def get_storage_targets(connection_id: str) -> list[dict[str, Any]]:
    """Get all storage targets (external databases where data is logged)."""
    return _query(connection_id, """
        SELECT
            id, name, provider, connection_string,
            is_default, status, last_error
        FROM app_storage_targets
        ORDER BY name
    """)


def get_device_tables(connection_id: str) -> list[dict[str, Any]]:
    """Get all device tables (logical tables bound to schema + device + storage)."""
    return _query(connection_id, """
        SELECT
            dt.id, dt.name, dt.status, dt.mapping_health,
            dt.last_migrated_at
        FROM app_device_tables dt
        ORDER BY dt.name
    """)


def get_field_mappings(connection_id: str, device_table_id: str) -> list[dict[str, Any]]:
    """Get field mappings for a specific device table."""
    return _query(connection_id, f"""
        SELECT
            field_key, protocol, address, data_type,
            scale, deadband, byte_order, poll_interval_ms
        FROM app_field_mappings
        WHERE CAST(device_table_id AS VARCHAR) = '{device_table_id}'
        ORDER BY field_key
    """)
