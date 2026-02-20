"""
Logger Integration API Routes.

Provides endpoints for auto-discovering Logger databases and querying
Logger-specific data (devices, schemas, jobs, storage targets).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.services.security import require_api_key

logger = logging.getLogger("neura.api.logger")

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/discover")
async def discover_logger():
    """Auto-discover Logger databases on the local network."""
    from backend.app.services.logger.discovery import discover_logger_databases

    try:
        databases = discover_logger_databases()
        return {"status": "ok", "databases": databases}
    except Exception as exc:
        logger.exception("Logger discovery failed")
        raise HTTPException(status_code=500, detail="Logger discovery failed")


@router.get("/{connection_id}/devices")
async def list_devices(connection_id: str):
    """List all PLC devices from a Logger database."""
    from backend.app.services.logger.query_service import get_devices

    try:
        devices = get_devices(connection_id)
        return {"status": "ok", "devices": devices}
    except Exception as exc:
        logger.exception("Failed to list devices for %s", connection_id)
        raise HTTPException(status_code=500, detail="Failed to list devices")


@router.get("/{connection_id}/devices/{device_id}")
async def get_device(connection_id: str, device_id: str):
    """Get a single device with its protocol configuration."""
    from backend.app.services.logger.query_service import get_device_with_config

    try:
        device = get_device_with_config(connection_id, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return {"status": "ok", "device": device}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get device %s", device_id)
        raise HTTPException(status_code=500, detail="Failed to get device")


@router.get("/{connection_id}/schemas")
async def list_schemas(connection_id: str):
    """List all device schemas with their fields."""
    from backend.app.services.logger.query_service import get_schemas

    try:
        schemas = get_schemas(connection_id)
        return {"status": "ok", "schemas": schemas}
    except Exception as exc:
        logger.exception("Failed to list schemas for %s", connection_id)
        raise HTTPException(status_code=500, detail="Failed to list schemas")


@router.get("/{connection_id}/jobs")
async def list_jobs(connection_id: str):
    """List all logging jobs with their status."""
    from backend.app.services.logger.query_service import get_jobs

    try:
        jobs = get_jobs(connection_id)
        return {"status": "ok", "jobs": jobs}
    except Exception as exc:
        logger.exception("Failed to list jobs for %s", connection_id)
        raise HTTPException(status_code=500, detail="Failed to list jobs")


@router.get("/{connection_id}/jobs/{job_id}/runs")
async def list_job_runs(
    connection_id: str,
    job_id: str,
    limit: int = Query(50, ge=1, le=500),
):
    """Get execution history for a specific logging job."""
    from backend.app.services.logger.query_service import get_job_runs

    try:
        runs = get_job_runs(connection_id, job_id, limit=limit)
        return {"status": "ok", "runs": runs}
    except Exception as exc:
        logger.exception("Failed to get runs for job %s", job_id)
        raise HTTPException(status_code=500, detail="Failed to get job runs")


@router.get("/{connection_id}/storage-targets")
async def list_storage_targets(connection_id: str):
    """List all storage targets (external databases where data is logged)."""
    from backend.app.services.logger.query_service import get_storage_targets

    try:
        targets = get_storage_targets(connection_id)
        return {"status": "ok", "storage_targets": targets}
    except Exception as exc:
        logger.exception("Failed to list storage targets for %s", connection_id)
        raise HTTPException(status_code=500, detail="Failed to list storage targets")


@router.get("/{connection_id}/device-tables")
async def list_device_tables(connection_id: str):
    """List all device tables (logical tables bound to schema + device + storage)."""
    from backend.app.services.logger.query_service import get_device_tables

    try:
        tables = get_device_tables(connection_id)
        return {"status": "ok", "device_tables": tables}
    except Exception as exc:
        logger.exception("Failed to list device tables for %s", connection_id)
        raise HTTPException(status_code=500, detail="Failed to list device tables")


@router.get("/{connection_id}/device-tables/{table_id}/mappings")
async def list_field_mappings(connection_id: str, table_id: str):
    """Get field mappings for a specific device table."""
    from backend.app.services.logger.query_service import get_field_mappings

    try:
        mappings = get_field_mappings(connection_id, table_id)
        return {"status": "ok", "mappings": mappings}
    except Exception as exc:
        logger.exception("Failed to get mappings for table %s", table_id)
        raise HTTPException(status_code=500, detail="Failed to get field mappings")
