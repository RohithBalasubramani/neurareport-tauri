from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.services.config import get_settings
from backend.app.services.security import require_api_key
from backend.app.services.job_status import (
    normalize_job_status as _normalize_job_status,
    STATUS_SUCCEEDED,
    STATUS_FAILED,
    STATUS_RUNNING,
    STATUS_QUEUED,
)
import backend.app.services.state_access as state_access

router = APIRouter(dependencies=[Depends(require_api_key)])


def _parse_iso(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _get_date_bucket(date_str: Optional[str], bucket: str = "day") -> Optional[str]:
    """Convert date string to bucket key (day, week, month)."""
    dt = _parse_iso(date_str)
    if not dt:
        return None
    if bucket == "day":
        return dt.strftime("%Y-%m-%d")
    elif bucket == "week":
        # Get start of week (Monday)
        start = dt - timedelta(days=dt.weekday())
        return start.strftime("%Y-%m-%d")
    elif bucket == "month":
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")


@router.get("/dashboard")
async def get_dashboard_analytics() -> Dict[str, Any]:
    """Get comprehensive dashboard analytics."""

    # Get all data from state store
    connections = state_access.list_connections()
    templates = state_access.list_templates()
    jobs = state_access.list_jobs()
    schedules = state_access.list_schedules()

    # Calculate time boundaries
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    # Job statistics - use canonical status constants
    total_jobs = len(jobs)
    completed_jobs = [j for j in jobs if _normalize_job_status(j.get("status")) == STATUS_SUCCEEDED]
    failed_jobs = [j for j in jobs if _normalize_job_status(j.get("status")) == STATUS_FAILED]
    running_jobs = [j for j in jobs if _normalize_job_status(j.get("status")) == STATUS_RUNNING]
    pending_jobs = [j for j in jobs if _normalize_job_status(j.get("status")) == STATUS_QUEUED]

    # Helper: state_access.list_jobs() returns camelCase keys from _sanitize_job.
    # Support both camelCase and snake_case for robustness.
    def _job_created(j: dict) -> str | None:
        return j.get("createdAt") or j.get("created_at")

    def _job_template_id(j: dict) -> str | None:
        return j.get("templateId") or j.get("template_id")

    def _job_template_name(j: dict) -> str | None:
        return j.get("templateName") or j.get("template_name")

    def _job_finished(j: dict) -> str | None:
        return j.get("finishedAt") or j.get("finished_at") or j.get("completedAt") or j.get("completed_at")

    # Jobs by time period
    def count_jobs_after(job_list: list, after: datetime) -> int:
        count = 0
        for j in job_list:
            created = _parse_iso(_job_created(j))
            if created and created >= after:
                count += 1
        return count

    jobs_today = count_jobs_after(jobs, today_start)
    jobs_this_week = count_jobs_after(jobs, week_start)
    jobs_this_month = count_jobs_after(jobs, month_start)

    # Success rate
    finished_jobs = len(completed_jobs) + len(failed_jobs)
    success_rate = (len(completed_jobs) / finished_jobs * 100) if finished_jobs > 0 else 0

    # Template statistics
    pdf_templates = [t for t in templates if t.get("kind") == "pdf"]
    excel_templates = [t for t in templates if t.get("kind") == "excel"]
    approved_templates = [t for t in templates if t.get("status") == "approved"]

    # Most used templates (by job count)
    template_usage: dict[str, int] = {}
    for job in jobs:
        tid = _job_template_id(job)
        if tid:
            template_usage[tid] = template_usage.get(tid, 0) + 1

    top_templates = []
    for tid, count in sorted(template_usage.items(), key=lambda x: -x[1])[:5]:
        template = next((t for t in templates if t.get("id") == tid), None)
        if template:
            top_templates.append({
                "id": tid,
                "name": template.get("name", tid[:12]),
                "kind": template.get("kind", "pdf"),
                "runCount": count,
            })

    # Connection statistics
    active_connections = [c for c in connections if c.get("status") == "connected"]
    avg_latency = 0
    latencies = [c.get("lastLatencyMs") for c in connections if c.get("lastLatencyMs")]
    if latencies:
        avg_latency = sum(latencies) / len(latencies)

    # Schedule statistics
    active_schedules = [s for s in schedules if s.get("active")]

    # Jobs trend (last 7 days)
    jobs_trend = []
    for i in range(6, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_str = day.strftime("%Y-%m-%d")

        day_jobs = [
            j for j in jobs
            if (created := _parse_iso(_job_created(j))) and day <= created < day_end
        ]
        day_completed = len([j for j in day_jobs if _normalize_job_status(j.get("status")) == STATUS_SUCCEEDED])
        day_failed = len([j for j in day_jobs if _normalize_job_status(j.get("status")) == STATUS_FAILED])

        jobs_trend.append({
            "date": day_str,
            "label": day.strftime("%a"),
            "total": len(day_jobs),
            "completed": day_completed,
            "failed": day_failed,
        })

    # Recent activity (last 10 jobs)
    recent_jobs = sorted(jobs, key=lambda j: _job_created(j) or "", reverse=True)[:10]
    recent_activity = []
    for job in recent_jobs:
        recent_activity.append({
            "id": job.get("id"),
            "type": "job",
            "action": f"Report {_normalize_job_status(job.get('status'))}",
            "template": _job_template_name(job) or (_job_template_id(job) or "")[:12],
            "timestamp": _job_finished(job) or _job_created(job),
            "status": _normalize_job_status(job.get("status")),
        })

    return {
        "summary": {
            "totalConnections": len(connections),
            "activeConnections": len(active_connections),
            "totalTemplates": len(templates),
            "approvedTemplates": len(approved_templates),
            "pdfTemplates": len(pdf_templates),
            "excelTemplates": len(excel_templates),
            "totalJobs": total_jobs,
            "activeJobs": len(running_jobs) + len(pending_jobs),
            "completedJobs": len(completed_jobs),
            "failedJobs": len(failed_jobs),
            "totalSchedules": len(schedules),
            "activeSchedules": len(active_schedules),
        },
        "metrics": {
            "successRate": round(success_rate, 1),
            "avgConnectionLatency": round(avg_latency, 1),
            "jobsToday": jobs_today,
            "jobsThisWeek": jobs_this_week,
            "jobsThisMonth": jobs_this_month,
        },
        "topTemplates": top_templates,
        "jobsTrend": jobs_trend,
        "recentActivity": recent_activity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/usage")
async def get_usage_statistics(
    period: str = Query("week", pattern="^(day|week|month)$"),
) -> Dict[str, Any]:
    """Get detailed usage statistics over time."""

    jobs = state_access.list_jobs()
    templates = state_access.list_templates()

    now = datetime.now(timezone.utc)

    # Determine date range based on period
    if period == "day":
        start_date = now - timedelta(days=1)
        bucket = "hour"
    elif period == "week":
        start_date = now - timedelta(days=7)
        bucket = "day"
    else:  # month
        start_date = now - timedelta(days=30)
        bucket = "day"

    # Filter jobs in date range
    filtered_jobs = []
    for job in jobs:
        created = _parse_iso(job.get("created_at"))
        if created and created >= start_date:
            filtered_jobs.append(job)

    # Group by status
    by_status = {}
    for job in filtered_jobs:
        status = _normalize_job_status(job.get("status"))
        by_status[status] = by_status.get(status, 0) + 1

    # Group by template kind
    by_kind = {"pdf": 0, "excel": 0}
    for job in filtered_jobs:
        kind = job.get("template_kind", "pdf")
        by_kind[kind] = by_kind.get(kind, 0) + 1

    # Group by template
    by_template = {}
    for job in filtered_jobs:
        tid = job.get("template_id", "unknown")
        tname = job.get("template_name") or tid[:12]
        if tid not in by_template:
            by_template[tid] = {"name": tname, "count": 0}
        by_template[tid]["count"] += 1

    template_breakdown = sorted(
        [{"id": k, **v} for k, v in by_template.items()],
        key=lambda x: -x["count"]
    )[:10]

    return {
        "period": period,
        "totalJobs": len(filtered_jobs),
        "byStatus": by_status,
        "byKind": by_kind,
        "templateBreakdown": template_breakdown,
        "startDate": start_date.isoformat(),
        "endDate": now.isoformat(),
    }


@router.get("/reports/history")
async def get_report_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get report generation history with filtering.

    Merges completed report runs (which have artifacts) with in-progress
    jobs so the timeline shows both finished and pending work.
    """

    # Report runs have artifacts, templateName, timestamps
    runs = state_access.list_report_runs(
        template_id=template_id or None,
        limit=0,  # fetch all, we paginate below
    )

    # Also include in-progress / queued jobs that haven't finished yet
    jobs = state_access.list_jobs()
    completed_job_ids: set[str] = set()
    for run in runs:
        # correlation between run id and job id varies; track run ids
        completed_job_ids.add(run.get("id", ""))

    templates = {t.get("id"): t for t in state_access.list_templates()}

    history: list[dict] = []

    # Add completed report runs
    for run in runs:
        entry = {
            "id": run.get("id"),
            "templateId": run.get("templateId"),
            "templateName": run.get("templateName") or "Unknown",
            "templateKind": run.get("templateKind") or "pdf",
            "connectionId": run.get("connectionId"),
            "connectionName": run.get("connectionName"),
            "status": _normalize_job_status(run.get("status")),
            "createdAt": run.get("createdAt"),
            "completedAt": run.get("createdAt"),  # run recorded at completion
            "artifacts": run.get("artifacts"),
            "startDate": run.get("startDate"),
            "endDate": run.get("endDate"),
            "keyValues": run.get("keyValues"),
            "scheduleId": run.get("scheduleId"),
            "scheduleName": run.get("scheduleName"),
            "error": None,
            "source": "run",
        }
        history.append(entry)

    # Add jobs that don't have a corresponding report run entry
    for job in jobs:
        jid = job.get("id", "")
        if jid in completed_job_ids:
            continue
        job_status = _normalize_job_status(job.get("status"))
        tid = job.get("template_id")
        template = templates.get(tid, {})
        entry = {
            "id": jid,
            "templateId": tid,
            "templateName": job.get("template_name") or template.get("name") or (tid[:12] if tid else "Unknown"),
            "templateKind": job.get("template_kind") or template.get("kind") or "pdf",
            "connectionId": job.get("connection_id"),
            "connectionName": None,
            "status": job_status,
            "createdAt": job.get("created_at"),
            "completedAt": job.get("finished_at"),
            "artifacts": None,
            "startDate": None,
            "endDate": None,
            "keyValues": None,
            "scheduleId": job.get("schedule_id"),
            "scheduleName": None,
            "error": job.get("error"),
            "source": "job",
        }
        history.append(entry)

    # Filter
    if status:
        status_norm = _normalize_job_status(status)
        history = [h for h in history if h.get("status") == status_norm]
    if template_id:
        history = [h for h in history if h.get("templateId") == template_id]

    # Sort by createdAt descending
    history.sort(key=lambda h: h.get("createdAt") or "", reverse=True)

    total = len(history)
    paginated = history[offset:offset + limit]

    return {
        "history": paginated,
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + limit < total,
    }


# ------------------------------------------------------------------
# Activity Log Endpoints
# ------------------------------------------------------------------

@router.get("/activity")
async def get_activity_log(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get the activity log with optional filtering."""
    log = state_access.get_activity_log(
        limit=limit,
        offset=offset,
        entity_type=entity_type,
        action=action,
    )
    return {
        "activities": log,
        "limit": limit,
        "offset": offset,
    }


@router.post("/activity")
async def log_activity(payload: LogActivityRequest) -> Dict[str, Any]:
    """Log an activity event."""
    entry = state_access.log_activity(
        action=payload.action,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        entity_name=payload.entity_name,
        details=payload.details,
    )
    return {"activity": entry}


@router.delete("/activity")
async def clear_activity_log(
    x_confirm_destructive: str = Header(None, alias="X-Confirm-Destructive"),
) -> Dict[str, Any]:
    """Clear all activity log entries. Requires X-Confirm-Destructive: true header."""
    if x_confirm_destructive != "true":
        raise HTTPException(
            status_code=400,
            detail="Destructive operation requires header X-Confirm-Destructive: true",
        )
    count = state_access.clear_activity_log()
    return {"cleared": count}


# ------------------------------------------------------------------
# Favorites Endpoints
# ------------------------------------------------------------------

@router.get("/favorites")
async def get_favorites() -> Dict[str, Any]:
    """Get all favorites."""
    favorites = state_access.get_favorites()

    # Enrich with template/connection details
    templates = {t.get("id"): t for t in state_access.list_templates()}
    connections = {c.get("id"): c for c in state_access.list_connections()}

    enriched_templates = []
    for tid in favorites.get("templates", []):
        template = templates.get(tid)
        if template:
            enriched_templates.append({
                "id": tid,
                "name": template.get("name"),
                "kind": template.get("kind"),
                "status": template.get("status"),
            })

    enriched_connections = []
    for cid in favorites.get("connections", []):
        conn = connections.get(cid)
        if conn:
            enriched_connections.append({
                "id": cid,
                "name": conn.get("name"),
                "dbType": conn.get("db_type"),
                "status": conn.get("status"),
            })

    return {
        "templates": enriched_templates,
        "connections": enriched_connections,
    }


@router.post("/favorites/{entity_type}/{entity_id}")
async def add_favorite(entity_type: str, entity_id: str) -> Dict[str, Any]:
    """Add an item to favorites."""
    if entity_type not in ("templates", "connections"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid entity type")

    added = state_access.add_favorite(entity_type, entity_id)

    # Log activity
    state_access.log_activity(
        action="favorite_added",
        entity_type=entity_type.rstrip("s"),  # template or connection
        entity_id=entity_id,
    )

    return {"added": added, "entityType": entity_type, "entityId": entity_id}


@router.delete("/favorites/{entity_type}/{entity_id}")
async def remove_favorite(entity_type: str, entity_id: str) -> Dict[str, Any]:
    """Remove an item from favorites."""
    if entity_type not in ("templates", "connections"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid entity type")

    removed = state_access.remove_favorite(entity_type, entity_id)

    # Log activity
    state_access.log_activity(
        action="favorite_removed",
        entity_type=entity_type.rstrip("s"),
        entity_id=entity_id,
    )

    return {"removed": removed, "entityType": entity_type, "entityId": entity_id}


@router.get("/favorites/{entity_type}/{entity_id}")
async def check_favorite(entity_type: str, entity_id: str) -> Dict[str, Any]:
    """Check if an item is a favorite."""
    if entity_type not in ("templates", "connections"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid entity type")

    is_fav = state_access.is_favorite(entity_type, entity_id)
    return {"isFavorite": is_fav, "entityType": entity_type, "entityId": entity_id}


# ------------------------------------------------------------------
# User Preferences Endpoints
# ------------------------------------------------------------------

class PreferenceValue(BaseModel):
    value: Any


class LogActivityRequest(BaseModel):
    action: str = Field(..., min_length=1, max_length=100)
    entity_type: str = Field(..., min_length=1, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=255)
    entity_name: Optional[str] = Field(None, max_length=255)
    details: Optional[Dict[str, Any]] = None


class CreateNotificationRequest(BaseModel):
    title: str = Field(default="Notification", min_length=1, max_length=255)
    message: str = Field(default="", max_length=2000)
    type: str = Field(default="info", pattern="^(info|success|warning|error)$")
    link: Optional[str] = Field(None, max_length=2000)
    entityType: Optional[str] = Field(None, max_length=50)
    entityId: Optional[str] = Field(None, max_length=255)


class BulkTemplateRequest(BaseModel):
    templateIds: List[str] = Field(..., min_length=1, max_length=500)
    status: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(None, max_length=100)


class BulkJobRequest(BaseModel):
    jobIds: List[str] = Field(..., min_length=1, max_length=500)


MAX_PREFERENCES_SIZE_BYTES = 50_000  # 50KB total


@router.get("/preferences")
async def get_preferences() -> Dict[str, Any]:
    """Get user preferences."""
    prefs = state_access.get_user_preferences()
    return {"preferences": prefs}


@router.put("/preferences")
async def update_preferences(updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update user preferences."""
    import json
    try:
        size = len(json.dumps(updates, default=str).encode("utf-8"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid preference data")
    if size > MAX_PREFERENCES_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Preferences payload too large (max {MAX_PREFERENCES_SIZE_BYTES} bytes)",
        )
    prefs = state_access.update_user_preferences(updates)
    return {"preferences": prefs}


@router.put("/preferences/{key}")
async def set_preference(
    key: str,
    payload: PreferenceValue | None = Body(default=None),
    value: Any = Query(default=None),
) -> Dict[str, Any]:
    """Set a single user preference."""
    import json

    # Size limits to prevent bloated state files
    MAX_KEY_LENGTH = 100
    MAX_VALUE_SIZE_BYTES = 10000  # 10KB per preference value

    # Validate key length
    if len(key) > MAX_KEY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Preference key too long (max {MAX_KEY_LENGTH} characters)"
        )

    if payload is not None and payload.value is not None:
        pref_value = payload.value
    elif value is not None:
        pref_value = value
    else:
        raise HTTPException(status_code=422, detail="Preference value is required.")

    # Validate value size
    try:
        value_json = json.dumps(pref_value, default=str)
        if len(value_json.encode('utf-8')) > MAX_VALUE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"Preference value too large (max {MAX_VALUE_SIZE_BYTES} bytes)"
            )
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail="Invalid preference value")

    prefs = state_access.set_user_preference(key, pref_value)
    return {"preferences": prefs}


# ------------------------------------------------------------------
# Export/Backup Endpoints
# ------------------------------------------------------------------

@router.get("/export/config")
async def export_configuration() -> Dict[str, Any]:
    """Export all configuration (templates, connections, schedules, preferences) as JSON."""
    connections = state_access.list_connections()
    templates = state_access.list_templates()
    schedules = state_access.list_schedules()
    favorites = state_access.get_favorites()
    preferences = state_access.get_user_preferences()

    # Remove sensitive data from connections
    safe_connections = []
    for conn in connections:
        safe_conn = {
            "id": conn.get("id"),
            "name": conn.get("name"),
            "db_type": conn.get("db_type"),
            "summary": conn.get("summary"),
            "tags": conn.get("tags"),
        }
        safe_connections.append(safe_conn)

    return {
        "version": "1.0",
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "data": {
            "connections": safe_connections,
            "templates": templates,
            "schedules": schedules,
            "favorites": favorites,
            "preferences": preferences,
        },
    }


# ------------------------------------------------------------------
# Global Search Endpoint
# ------------------------------------------------------------------

@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    types: Optional[str] = Query(None),  # comma-separated: templates,connections,jobs
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """Search across templates, connections, and jobs."""
    query = q.lower().strip()
    type_filter = set(types.split(",")) if types else {"templates", "connections", "jobs"}

    results = []

    # Search templates
    if "templates" in type_filter:
        templates = state_access.list_templates()
        for t in templates:
            name = (t.get("name") or "").lower()
            tid = (t.get("id") or "").lower()
            template_id = t.get("id")
            if query in name or query in tid:
                results.append({
                    "type": "template",
                    "id": template_id,
                    "name": t.get("name"),
                    "description": f"{t.get('kind', 'pdf').upper()} Template",
                    "url": f"/templates/{template_id}/edit" if template_id else "/templates",
                    "meta": {"kind": t.get("kind"), "status": t.get("status")},
                })

    # Search connections
    if "connections" in type_filter:
        connections = state_access.list_connections()
        for c in connections:
            name = (c.get("name") or "").lower()
            cid = (c.get("id") or "").lower()
            summary = (c.get("summary") or "").lower()
            connection_id = c.get("id")
            if query in name or query in cid or query in summary:
                results.append({
                    "type": "connection",
                    "id": connection_id,
                    "name": c.get("name"),
                    "description": c.get("summary") or c.get("db_type"),
                    "url": f"/connections?selected={connection_id}" if connection_id else "/connections",
                    "meta": {"dbType": c.get("db_type"), "status": c.get("status")},
                })

    # Search jobs
    if "jobs" in type_filter:
        jobs = state_access.list_jobs(limit=100)
        for j in jobs:
            tname = (j.get("templateName") or j.get("template_name") or "").lower()
            jid = (j.get("id") or "").lower()
            job_id = j.get("id")
            if query in tname or query in jid:
                results.append({
                    "type": "job",
                    "id": job_id,
                    "name": j.get("templateName") or j.get("template_name") or (job_id[:12] if job_id else "Job"),
                    "description": f"Job - {_normalize_job_status(j.get('status'))}",
                    "url": f"/jobs?selected={job_id}" if job_id else "/jobs",
                    "meta": {
                        "status": _normalize_job_status(j.get("status")),
                        "createdAt": j.get("createdAt") or j.get("created_at"),
                    },
                })

    # Limit results
    results = results[:limit]

    return {
        "query": q,
        "results": results,
        "total": len(results),
    }


# ------------------------------------------------------------------
# Notification Endpoints
# ------------------------------------------------------------------

@router.get("/notifications")
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
) -> Dict[str, Any]:
    """Get notifications list."""
    notifications = state_access.get_notifications(limit=limit, unread_only=unread_only)
    unread_count = state_access.get_unread_count()
    return {
        "notifications": notifications,
        "unreadCount": unread_count,
        "total": len(notifications),
    }


@router.get("/notifications/unread-count")
async def get_unread_count() -> Dict[str, int]:
    """Get count of unread notifications."""
    return {"unreadCount": state_access.get_unread_count()}


@router.post("/notifications")
async def create_notification(payload: CreateNotificationRequest) -> Dict[str, Any]:
    """Create a new notification."""
    notification = state_access.add_notification(
        title=payload.title,
        message=payload.message,
        notification_type=payload.type,
        link=payload.link,
        entity_type=payload.entityType,
        entity_id=payload.entityId,
    )
    return {"notification": notification}


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str) -> Dict[str, Any]:
    """Mark a notification as read."""
    found = state_access.mark_notification_read(notification_id)
    if not found:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"marked": True, "notificationId": notification_id}


@router.put("/notifications/read-all")
async def mark_all_read() -> Dict[str, Any]:
    """Mark all notifications as read."""
    count = state_access.mark_all_notifications_read()
    return {"markedCount": count}


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str) -> Dict[str, Any]:
    """Delete a notification."""
    found = state_access.delete_notification(notification_id)
    if not found:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"deleted": True, "notificationId": notification_id}


@router.delete("/notifications")
async def clear_all_notifications(
    x_confirm_destructive: str = Header(None, alias="X-Confirm-Destructive"),
) -> Dict[str, Any]:
    """Clear all notifications. Requires X-Confirm-Destructive: true header."""
    if x_confirm_destructive != "true":
        raise HTTPException(
            status_code=400,
            detail="Destructive operation requires header X-Confirm-Destructive: true",
        )
    count = state_access.clear_notifications()
    return {"clearedCount": count}


# ------------------------------------------------------------------
# Bulk Operations Endpoints
# ------------------------------------------------------------------

@router.post("/bulk/templates/delete")
async def bulk_delete_templates(payload: BulkTemplateRequest) -> Dict[str, Any]:
    """Delete multiple templates in bulk."""
    template_ids = payload.templateIds

    deleted = []
    failed = []

    for tid in template_ids:
        try:
            state_access.delete_template(tid)
            deleted.append(tid)
            state_access.log_activity(
                action="template_deleted",
                entity_type="template",
                entity_id=tid,
            )
        except Exception as e:
            failed.append({"id": tid, "error": "Delete failed"})

    return {
        "deleted": deleted,
        "deletedCount": len(deleted),
        "failed": failed,
        "failedCount": len(failed),
    }


@router.post("/bulk/templates/update-status")
async def bulk_update_template_status(payload: BulkTemplateRequest) -> Dict[str, Any]:
    """Update status for multiple templates."""
    template_ids = payload.templateIds
    status = payload.status

    if not status:
        raise HTTPException(status_code=400, detail="Status is required")

    updated = []
    failed = []

    for tid in template_ids:
        try:
            record = state_access.get_template_record(tid)
            if not record:
                failed.append({"id": tid, "error": "Template not found"})
                continue

            state_access.upsert_template(
                tid,
                name=record.get("name") or tid,
                status=status,
                artifacts=record.get("artifacts"),
                tags=record.get("tags"),
                connection_id=record.get("last_connection_id"),
                mapping_keys=record.get("mapping_keys"),
                template_type=record.get("kind"),
                description=record.get("description"),
            )
            updated.append(tid)
            state_access.log_activity(
                action="template_status_updated",
                entity_type="template",
                entity_id=tid,
                details={"status": status},
            )
        except Exception as e:
            failed.append({"id": tid, "error": "Status update failed"})

    return {
        "updated": updated,
        "updatedCount": len(updated),
        "failed": failed,
        "failedCount": len(failed),
    }


@router.post("/bulk/templates/add-tags")
async def bulk_add_tags(payload: BulkTemplateRequest) -> Dict[str, Any]:
    """Add tags to multiple templates."""
    template_ids = payload.templateIds
    tags_to_add = payload.tags or []

    if not tags_to_add:
        raise HTTPException(status_code=400, detail="No tags provided")

    updated = []
    failed = []

    for tid in template_ids:
        try:
            record = state_access.get_template_record(tid)
            if not record:
                failed.append({"id": tid, "error": "Template not found"})
                continue

            existing_tags = list(record.get("tags") or [])
            merged_tags = sorted(set(existing_tags + tags_to_add))

            state_access.upsert_template(
                tid,
                name=record.get("name") or tid,
                status=record.get("status") or "draft",
                artifacts=record.get("artifacts"),
                tags=merged_tags,
                connection_id=record.get("last_connection_id"),
                mapping_keys=record.get("mapping_keys"),
                template_type=record.get("kind"),
                description=record.get("description"),
            )
            updated.append(tid)
        except Exception as e:
            failed.append({"id": tid, "error": "Tag update failed"})

    return {
        "updated": updated,
        "updatedCount": len(updated),
        "failed": failed,
        "failedCount": len(failed),
    }


@router.post("/bulk/jobs/cancel")
async def bulk_cancel_jobs(payload: BulkJobRequest) -> Dict[str, Any]:
    """Cancel multiple jobs."""
    job_ids = payload.jobIds

    cancelled = []
    failed = []

    for jid in job_ids:
        try:
            job = state_access.get_job(jid)
            if not job:
                failed.append({"id": jid, "error": "Job not found"})
                continue

            status = _normalize_job_status(job.get("status"))
            if status in ("succeeded", "failed", "cancelled"):
                failed.append({"id": jid, "error": f"Cannot cancel job with status: {status}"})
                continue

            state_access.update_job(jid, status="cancelled")
            cancelled.append(jid)
            state_access.log_activity(
                action="job_cancelled",
                entity_type="job",
                entity_id=jid,
            )
        except Exception as e:
            failed.append({"id": jid, "error": "Cancel failed"})

    return {
        "cancelled": cancelled,
        "cancelledCount": len(cancelled),
        "failed": failed,
        "failedCount": len(failed),
    }


@router.post("/bulk/jobs/delete")
async def bulk_delete_jobs(payload: BulkJobRequest) -> Dict[str, Any]:
    """Delete multiple jobs from history."""
    job_ids = payload.jobIds

    deleted = []
    failed = []

    for jid in job_ids:
        try:
            state_access.delete_job(jid)
            deleted.append(jid)
        except Exception as e:
            failed.append({"id": jid, "error": "Delete failed"})

    return {
        "deleted": deleted,
        "deletedCount": len(deleted),
        "failed": failed,
        "failedCount": len(failed),
    }


# ------------------------------------------------------------------
# AI Analytics Endpoints
# ------------------------------------------------------------------

from backend.app.schemas.analytics import (
    InsightsRequest,
    InsightsResponse,
    TrendRequest,
    TrendResponse,
    AnomaliesRequest,
    AnomaliesResponse,
    CorrelationsRequest,
    CorrelationsResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from backend.app.services.analytics import (
    insight_service,
    trend_service,
    anomaly_service,
    correlation_service,
    whatif_service,
)


@router.post("/insights", response_model=InsightsResponse)
async def generate_insights(request: InsightsRequest) -> InsightsResponse:
    """Generate automated insights from data.

    Analyzes data series to discover trends, anomalies, distributions,
    and other notable patterns.
    """
    return await insight_service.generate_insights(request)


@router.post("/trends", response_model=TrendResponse)
async def analyze_trends(request: TrendRequest) -> TrendResponse:
    """Analyze trends and generate forecasts.

    Uses linear regression, exponential smoothing, ARIMA, or Prophet
    to detect trends and forecast future values.
    """
    return await trend_service.analyze_trend(request)


@router.post("/anomalies", response_model=AnomaliesResponse)
async def detect_anomalies(request: AnomaliesRequest) -> AnomaliesResponse:
    """Detect anomalies in data.

    Uses statistical methods to identify point anomalies,
    contextual anomalies, and collective anomalies.
    """
    return await anomaly_service.detect_anomalies(request)


@router.post("/correlations", response_model=CorrelationsResponse)
async def analyze_correlations(request: CorrelationsRequest) -> CorrelationsResponse:
    """Analyze correlations between data series.

    Calculates Pearson, Spearman, or Kendall correlation coefficients
    between all pairs of variables.
    """
    return await correlation_service.analyze_correlations(request)


@router.post("/whatif", response_model=WhatIfResponse)
async def what_if_analysis(request: WhatIfRequest) -> WhatIfResponse:
    """Perform what-if scenario analysis.

    Evaluates how changes to input variables might affect
    a target variable based on historical relationships.
    """
    return await whatif_service.analyze_whatif(request)
