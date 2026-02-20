from __future__ import annotations

from typing import Any

from backend.app.repositories.state import StateStore, set_state_store, state_store as _state_store_proxy

# NOTE: Prefer these explicit service helpers in API code. The underlying proxy
# is kept for compatibility with legacy/service usage and tests.


def _call(method: str, *args: Any, **kwargs: Any) -> Any:
    return getattr(_state_store_proxy, method)(*args, **kwargs)


def get_state_store() -> StateStore:
    return _state_store_proxy.get()


def list_connections() -> list[dict]:
    return _call("list_connections")


def list_templates() -> list[dict]:
    return _call("list_templates")


def list_jobs(*args: Any, **kwargs: Any) -> list[dict]:
    return _call("list_jobs", *args, **kwargs)


def list_schedules() -> list[dict]:
    return _call("list_schedules")


def get_connection_record(conn_id: str) -> dict | None:
    return _call("get_connection_record", conn_id)


def get_connection_secrets(conn_id: str) -> dict | None:
    return _call("get_connection_secrets", conn_id)


def get_latest_connection() -> dict | None:
    return _call("get_latest_connection")


def get_template_record(template_id: str) -> dict | None:
    return _call("get_template_record", template_id)


def upsert_template(*args: Any, **kwargs: Any) -> dict:
    return _call("upsert_template", *args, **kwargs)


def delete_template(template_id: str) -> bool:
    return _call("delete_template", template_id)


def get_job(job_id: str) -> dict | None:
    return _call("get_job", job_id)


def update_job(job_id: str, **updates: Any) -> dict | None:
    return _call("update_job", job_id, **updates)


def delete_job(job_id: str) -> bool:
    return _call("delete_job", job_id)


def create_job(*args: Any, **kwargs: Any) -> dict:
    return _call("create_job", *args, **kwargs)


def record_job_start(job_id: str) -> None:
    _call("record_job_start", job_id)


def record_job_step(*args: Any, **kwargs: Any) -> None:
    _call("record_job_step", *args, **kwargs)


def record_job_completion(*args: Any, **kwargs: Any) -> None:
    _call("record_job_completion", *args, **kwargs)


def record_schedule_run(*args: Any, **kwargs: Any) -> None:
    _call("record_schedule_run", *args, **kwargs)


def list_report_runs(*args: Any, **kwargs: Any) -> list[dict]:
    return _call("list_report_runs", *args, **kwargs)


def get_report_run(run_id: str) -> dict | None:
    return _call("get_report_run", run_id)


def get_activity_log(*args: Any, **kwargs: Any) -> list[dict]:
    return _call("get_activity_log", *args, **kwargs)


def log_activity(*args: Any, **kwargs: Any) -> dict:
    return _call("log_activity", *args, **kwargs)


def clear_activity_log() -> int:
    return _call("clear_activity_log")


def get_favorites() -> dict:
    return _call("get_favorites")


def add_favorite(entity_type: str, entity_id: str) -> bool:
    return _call("add_favorite", entity_type, entity_id)


def remove_favorite(entity_type: str, entity_id: str) -> bool:
    return _call("remove_favorite", entity_type, entity_id)


def is_favorite(entity_type: str, entity_id: str) -> bool:
    return _call("is_favorite", entity_type, entity_id)


def get_user_preferences() -> dict:
    return _call("get_user_preferences")


def update_user_preferences(updates: dict) -> dict:
    return _call("update_user_preferences", updates)


def set_user_preference(key: str, value: Any) -> dict:
    return _call("set_user_preference", key, value)


def get_notifications(*args: Any, **kwargs: Any) -> list[dict]:
    return _call("get_notifications", *args, **kwargs)


def get_unread_count() -> int:
    return _call("get_unread_count")


def add_notification(*args: Any, **kwargs: Any) -> dict:
    return _call("add_notification", *args, **kwargs)


def mark_notification_read(notification_id: str) -> bool:
    return _call("mark_notification_read", notification_id)


def mark_all_notifications_read() -> int:
    return _call("mark_all_notifications_read")


def delete_notification(notification_id: str) -> bool:
    return _call("delete_notification", notification_id)


def clear_notifications() -> int:
    return _call("clear_notifications")


def get_last_used() -> dict:
    return _call("get_last_used")


def set_last_used(*args: Any, **kwargs: Any) -> dict:
    return _call("set_last_used", *args, **kwargs)


def get() -> dict:
    return _call("get")


# =============================================================================
# Idempotency key management
# =============================================================================

def check_idempotency_key(key: str, request_hash: str) -> tuple[bool, dict | None]:
    return _call("check_idempotency_key", key, request_hash)


def store_idempotency_key(key: str, job_id: str, request_hash: str, response: dict) -> dict:
    return _call("store_idempotency_key", key, job_id, request_hash, response)


def clean_expired_idempotency_keys() -> int:
    return _call("clean_expired_idempotency_keys")


# =============================================================================
# Dead Letter Queue management
# =============================================================================

def list_dead_letter_jobs(limit: int = 50) -> list[dict]:
    return _call("list_dead_letter_jobs", limit=limit)


def get_dead_letter_job(job_id: str) -> dict | None:
    return _call("get_dead_letter_job", job_id)


def move_job_to_dlq(job_id: str, failure_history: list[dict] | None = None) -> dict | None:
    return _call("move_job_to_dlq", job_id, failure_history)


def requeue_from_dlq(job_id: str) -> dict | None:
    return _call("requeue_from_dlq", job_id)


def delete_from_dlq(job_id: str) -> bool:
    return _call("delete_from_dlq", job_id)


def get_dlq_stats() -> dict:
    return _call("get_dlq_stats")


state_store = _state_store_proxy


__all__ = [
    "StateStore",
    "set_state_store",
    "state_store",
    "get_state_store",
    "list_connections",
    "list_templates",
    "list_jobs",
    "list_schedules",
    "get_connection_record",
    "get_connection_secrets",
    "get_latest_connection",
    "get_template_record",
    "upsert_template",
    "delete_template",
    "get_job",
    "update_job",
    "delete_job",
    "create_job",
    "record_job_start",
    "record_job_step",
    "record_job_completion",
    "record_schedule_run",
    "list_report_runs",
    "get_report_run",
    "get_activity_log",
    "log_activity",
    "clear_activity_log",
    "get_favorites",
    "add_favorite",
    "remove_favorite",
    "is_favorite",
    "get_user_preferences",
    "update_user_preferences",
    "set_user_preference",
    "get_notifications",
    "get_unread_count",
    "add_notification",
    "mark_notification_read",
    "mark_all_notifications_read",
    "delete_notification",
    "clear_notifications",
    "get_last_used",
    "set_last_used",
    "get",
    # Idempotency key management
    "check_idempotency_key",
    "store_idempotency_key",
    "clean_expired_idempotency_keys",
    # Dead Letter Queue management
    "list_dead_letter_jobs",
    "get_dead_letter_job",
    "move_job_to_dlq",
    "requeue_from_dlq",
    "delete_from_dlq",
    "get_dlq_stats",
]
