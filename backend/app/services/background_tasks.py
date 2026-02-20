from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncIterable, Callable, Iterable, Optional

from backend.app.repositories.state import state_store

logger = logging.getLogger("neura.background_tasks")

_DEFAULT_TASK_WORKERS = os.cpu_count() or 4
_TASK_WORKERS = max(int(os.getenv("NR_TASK_WORKERS", str(_DEFAULT_TASK_WORKERS)) or _DEFAULT_TASK_WORKERS), 1)
_TASK_EXECUTOR = ThreadPoolExecutor(max_workers=_TASK_WORKERS)

# Limit concurrent LLM-intensive jobs (verify, mapping) to prevent OOM.
# Each LLM job can consume 500MB+ of memory; running too many in parallel
# (e.g. 5 template verifications) can exhaust available RAM and crash the server.
_MAX_LLM_CONCURRENT = max(int(os.getenv("NR_MAX_LLM_CONCURRENT", "2")), 1)
_LLM_SEMAPHORE = threading.Semaphore(_MAX_LLM_CONCURRENT)

_BACKGROUND_TASKS: set[asyncio.Task] = set()
_BACKGROUND_LOCK = threading.Lock()


def _track_task(task: asyncio.Task) -> None:
    with _BACKGROUND_LOCK:
        _BACKGROUND_TASKS.add(task)

    def _done(_task: asyncio.Task) -> None:
        with _BACKGROUND_LOCK:
            _BACKGROUND_TASKS.discard(_task)

    task.add_done_callback(_done)


def _is_cancelled(job_id: str) -> bool:
    job = state_store.get_job(job_id) or {}
    status = str(job.get("status") or "").strip().lower()
    return status == "cancelled"


def _normalize_step_status(status: Optional[str]) -> Optional[str]:
    if not status:
        return None
    value = str(status).strip().lower()
    if value in {"started", "running", "in_progress"}:
        return "running"
    if value in {"complete", "completed", "done", "success"}:
        return "succeeded"
    if value in {"error", "failed"}:
        return "failed"
    if value in {"skipped"}:
        return "succeeded"
    if value in {"cancelled", "canceled"}:
        return "cancelled"
    return value


def _apply_event(
    job_id: str,
    event: dict,
    *,
    result_builder: Optional[Callable[[dict], dict]] = None,
) -> bool:
    event_type = str(event.get("event") or "").strip().lower()
    if event_type == "stage":
        stage = str(event.get("stage") or event.get("label") or "stage").strip()
        label = str(event.get("label") or event.get("detail") or stage).strip()
        status = _normalize_step_status(event.get("status"))
        progress = event.get("progress")
        state_store.record_job_step(
            job_id,
            stage,
            label=label,
            status=status,
            progress=progress if isinstance(progress, (int, float)) else None,
        )
        if isinstance(progress, (int, float)):
            state_store.record_job_progress(job_id, float(progress))
        return False

    if event_type == "error":
        detail = event.get("detail") or event.get("message") or "Task failed"
        state_store.record_job_completion(job_id, status="failed", error=str(detail))
        return True

    if event_type == "result":
        result_payload = result_builder(event) if result_builder else dict(event)
        state_store.record_job_completion(job_id, status="succeeded", result=result_payload)
        return True

    return False


def iter_ndjson_events(chunks: Iterable[bytes]) -> Iterable[dict]:
    buffer = ""
    for chunk in chunks:
        try:
            text = chunk.decode("utf-8")
        except Exception:
            continue
        buffer += text
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                yield payload


async def iter_ndjson_events_async(chunks: AsyncIterable[bytes]) -> AsyncIterable[dict]:
    buffer = ""
    try:
        async for chunk in chunks:
            try:
                text = chunk.decode("utf-8")
            except Exception:
                continue
            buffer += text
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    yield payload
    finally:
        close_fn = getattr(chunks, "aclose", None)
        if callable(close_fn):
            with contextlib.suppress(Exception):
                await close_fn()


def run_event_stream(
    job_id: str,
    events: Iterable[dict],
    *,
    result_builder: Optional[Callable[[dict], dict]] = None,
) -> None:
    if _is_cancelled(job_id):
        return
    state_store.record_job_start(job_id)
    completed = False
    for event in events:
        if _is_cancelled(job_id):
            state_store.record_job_completion(job_id, status="cancelled", error="Cancelled by user")
            close_fn = getattr(events, "close", None)
            if callable(close_fn):
                with contextlib.suppress(Exception):
                    close_fn()
            return
        completed = _apply_event(job_id, event, result_builder=result_builder)
        if completed:
            break
    if completed:
        close_fn = getattr(events, "close", None)
        if callable(close_fn):
            with contextlib.suppress(Exception):
                close_fn()
    if not completed:
        state_store.record_job_completion(job_id, status="failed", error="Task finished without result")


async def run_event_stream_async(
    job_id: str,
    events: AsyncIterable[dict],
    *,
    result_builder: Optional[Callable[[dict], dict]] = None,
) -> None:
    if _is_cancelled(job_id):
        return
    state_store.record_job_start(job_id)
    completed = False
    async for event in events:
        if _is_cancelled(job_id):
            state_store.record_job_completion(job_id, status="cancelled", error="Cancelled by user")
            close_fn = getattr(events, "aclose", None)
            if callable(close_fn):
                with contextlib.suppress(Exception):
                    await close_fn()
            return
        completed = _apply_event(job_id, event, result_builder=result_builder)
        if completed:
            break
    if completed:
        close_fn = getattr(events, "aclose", None)
        if callable(close_fn):
            with contextlib.suppress(Exception):
                await close_fn()
    if not completed:
        state_store.record_job_completion(job_id, status="failed", error="Task finished without result")


# Job types that involve heavy LLM calls and should be concurrency-limited.
_LLM_JOB_TYPES = {"verify_template", "verify_excel", "mapping_approve"}


async def enqueue_background_job(
    *,
    job_type: str,
    template_id: Optional[str] = None,
    connection_id: Optional[str] = None,
    template_name: Optional[str] = None,
    template_kind: Optional[str] = None,
    steps: Optional[Iterable[dict]] = None,
    meta: Optional[dict] = None,
    runner: Callable[[str], None],
) -> dict:
    job = state_store.create_job(
        job_type=job_type,
        template_id=template_id,
        connection_id=connection_id,
        template_name=template_name,
        template_kind=template_kind,
        steps=steps,
        meta=meta,
    )

    use_llm_semaphore = job_type in _LLM_JOB_TYPES

    async def _schedule() -> None:
        def _run() -> None:
            acquired = False
            try:
                if use_llm_semaphore:
                    logger.info(
                        "llm_semaphore_wait",
                        extra={"event": "llm_semaphore_wait", "job_id": job["id"], "job_type": job_type},
                    )
                    _LLM_SEMAPHORE.acquire()
                    acquired = True
                result = runner(job["id"])
                if asyncio.iscoroutine(result):
                    asyncio.run(result)
            except Exception as exc:
                logger.exception(
                    "background_task_failed",
                    extra={"event": "background_task_failed", "job_id": job.get("id"), "error": str(exc)},
                )
                state_store.record_job_completion(job["id"], status="failed", error="Background task failed")
            finally:
                if acquired:
                    _LLM_SEMAPHORE.release()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(_TASK_EXECUTOR, _run)

    task = asyncio.create_task(_schedule())
    _track_task(task)
    return job


def mark_incomplete_jobs_failed(
    *,
    reason: str = "Server restarted before job completed",
    skip_types: Optional[set[str]] = None,
) -> int:
    """
    Mark queued/running jobs as failed (used during startup recovery).
    Returns number of jobs updated.
    """
    skipped = {str(t or "").strip().lower() for t in (skip_types or set())}
    jobs = state_store.list_jobs(statuses=["queued", "running"], limit=0)
    updated = 0
    for job in jobs:
        job_id = job.get("id")
        if not job_id:
            continue
        job_type = str(job.get("type") or "").strip().lower()
        if job_type in skipped:
            continue
        state_store.record_job_completion(job_id, status="failed", error=reason)
        updated += 1
    return updated
