from __future__ import annotations

import asyncio
import concurrent.futures
import ctypes
import contextlib
import importlib
import json
import logging
import os
import re
import signal
import subprocess
import time
import threading
import uuid
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

from fastapi import HTTPException, Request

from backend.app.utils.event_bus import Event, EventBus, logging_middleware, metrics_middleware
from backend.app.services.jobs.job_tracking import (
    DEFAULT_JOB_STEP_PROGRESS,
    JobRunTracker,
    _build_job_steps,
    _step_progress_from_steps,
)
from backend.app.services.reports.strategies import build_notification_strategy_registry, build_render_strategy_registry
from backend.app.schemas.generate.reports import RunPayload
from backend.app.services.utils import (
    TemplateLockError,
    acquire_template_lock,
    validate_contract_schema,
    write_artifact_manifest,
)
from backend.app.services.utils.artifacts import load_manifest
from backend.app.repositories.state import state_store
from backend.legacy.core.config import EXCEL_UPLOAD_ROOT, UPLOAD_ROOT
from backend.legacy.utils.connection_utils import db_path_from_payload_or_default
from backend.legacy.utils.email_utils import normalize_email_targets
from backend.legacy.utils.schedule_utils import clean_key_values

logger = logging.getLogger(__name__)
EVENT_BUS = EventBus(middlewares=[logging_middleware(logger), metrics_middleware(logger)])
RENDER_STRATEGIES = build_render_strategy_registry()
NOTIFICATION_STRATEGIES = build_notification_strategy_registry()

_UPLOAD_KIND_PREFIXES: dict[str, str] = {"pdf": "uploads", "excel": "excel-uploads"}
UPLOAD_ROOT_BASE = UPLOAD_ROOT.resolve()
EXCEL_UPLOAD_ROOT_BASE = EXCEL_UPLOAD_ROOT.resolve()

_DEFAULT_JOB_WORKERS = os.cpu_count() or 4
_JOB_MAX_WORKERS = max(int(os.getenv("NEURA_JOB_MAX_WORKERS", str(_DEFAULT_JOB_WORKERS)) or _DEFAULT_JOB_WORKERS), 1)
REPORT_JOB_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=_JOB_MAX_WORKERS,
    thread_name_prefix="nr-job",
)
_JOB_TASKS: set[asyncio.Task] = set()
_JOB_FUTURES: dict[str, concurrent.futures.Future] = {}
_JOB_THREADS: dict[str, int] = {}
_JOB_PROCESSES: dict[str, set[int]] = {}
_JOB_PROCESS_LOCK = threading.RLock()
_SUBPROCESS_JOB_CONTEXT = threading.local()
_ORIGINAL_POPEN = subprocess.Popen


class _TrackingPopen(_ORIGINAL_POPEN):
    """Popen subclass that registers child PIDs with the active job context."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        job_id = getattr(_SUBPROCESS_JOB_CONTEXT, "job_id", None)
        if job_id and self.pid:
            _register_job_process(job_id, self.pid)


# Install once at import time — no reference counting needed.
subprocess.Popen = _TrackingPopen  # type: ignore[misc]


@contextlib.contextmanager
def _track_subprocess(job_id: str):
    """Set thread-local job context so _TrackingPopen records child PIDs."""
    _SUBPROCESS_JOB_CONTEXT.job_id = job_id
    try:
        yield
    finally:
        _SUBPROCESS_JOB_CONTEXT.job_id = None


def _state_store():
    try:
        api_mod = importlib.import_module("backend.api")
        return getattr(api_mod, "state_store", state_store)
    except Exception:
        return state_store


def _is_job_cancelled(job_id: str | None) -> bool:
    if not job_id:
        return False
    try:
        record = _state_store().get_job(job_id) or {}
    except Exception:
        logger.exception("job_status_check_failed", extra={"event": "job_status_check_failed", "job_id": job_id})
        return False
    status = str(record.get("status") or "").lower()
    return status == "cancelled"


def _raise_if_cancelled(job_tracker: "JobRunTracker" | None) -> None:
    if _is_job_cancelled(job_tracker.job_id if job_tracker else None):
        raise _http_error(409, "job_cancelled", "Job was cancelled.")


def _http_error(status_code: int, code: str, message: str, details: str | None = None) -> HTTPException:
    payload: dict[str, Any] = {"status": "error", "code": code, "message": message}
    if details:
        payload["detail"] = details
    return HTTPException(status_code=status_code, detail=payload)


def _track_background_task(task: asyncio.Task) -> None:
    _JOB_TASKS.add(task)

    def _cleanup(t: asyncio.Task) -> None:
        _JOB_TASKS.discard(t)

    task.add_done_callback(_cleanup)


def _track_job_future(job_id: str, future: concurrent.futures.Future) -> None:
    if not job_id or future is None:
        return
    _JOB_FUTURES[job_id] = future

    def _cleanup(_: concurrent.futures.Future) -> None:
        _JOB_FUTURES.pop(job_id, None)

    future.add_done_callback(_cleanup)


def _register_job_thread(job_id: str) -> None:
    if not job_id:
        return
    try:
        _JOB_THREADS[job_id] = threading.get_ident()
    except Exception:
        logger.exception("job_thread_register_failed", extra={"event": "job_thread_register_failed", "job_id": job_id})


def _clear_job_thread(job_id: str) -> None:
    if not job_id:
        return
    _JOB_THREADS.pop(job_id, None)


def _register_job_process(job_id: str, pid: int) -> None:
    if not job_id or not pid:
        return
    with _JOB_PROCESS_LOCK:
        _JOB_PROCESSES.setdefault(job_id, set()).add(pid)


def _clear_job_processes(job_id: str) -> None:
    if not job_id:
        return
    with _JOB_PROCESS_LOCK:
        _JOB_PROCESSES.pop(job_id, None)


def _terminate_pid(pid: int, *, kill_tree: bool = True) -> bool:
    if not pid:
        return False
    try:
        if os.name == "nt" and kill_tree:
            # Use the real Popen to avoid recursive tracking.
            _SUBPROCESS_POPEN(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        os.kill(pid, signal.SIGTERM)
        return True
    except Exception:
        return False


def _kill_job_processes(job_id: str, *, kill_tree: bool = True) -> None:
    if not job_id:
        return
    with _JOB_PROCESS_LOCK:
        pids = list(_JOB_PROCESSES.get(job_id) or [])
    for pid in pids:
        _terminate_pid(pid, kill_tree=kill_tree)
    _clear_job_processes(job_id)


def _inject_thread_cancel(thread_id: int) -> bool:
    """
    Best-effort cancellation for a running thread by injecting CancelledError.
    """
    if not thread_id:
        return False
    try:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread_id), ctypes.py_object(asyncio.CancelledError)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)
            return False
        return res == 1
    except Exception:
        logger.exception(
            "job_force_cancel_injection_failed",
            extra={"event": "job_force_cancel_injection_failed", "thread_id": thread_id},
        )
        return False


def force_cancel_job(job_id: str, *, force: bool = False) -> bool:
    """
    Attempt to cancel a running or queued job. When force=True, injects a CancelledError
    into the worker thread if it is already running and terminates tracked child processes.
    """
    if not job_id:
        return False
    future = _JOB_FUTURES.get(job_id)
    cancelled = False
    if future and not future.done():
        cancelled = future.cancel()
    if force and not cancelled:
        thread_id = _JOB_THREADS.get(job_id)
        if thread_id:
            cancelled = _inject_thread_cancel(thread_id)
        _kill_job_processes(job_id, kill_tree=True)
    return cancelled


def _publish_event_safe(event: Event) -> None:
    try:
        # Try to get the running loop (Python 3.10+ safe approach)
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, schedule the coroutine
            asyncio.run_coroutine_threadsafe(EVENT_BUS.publish(event), loop)
        except RuntimeError:
            # No running loop, create a new one
            asyncio.run(EVENT_BUS.publish(event))
    except Exception:
        logger.exception(
            "event_bus_publish_failed",
            extra={"event": event.name, "correlation_id": event.correlation_id},
        )


def _job_error_message(detail: Any) -> str:
    if isinstance(detail, Mapping):
        message = detail.get("message") or detail.get("detail")
        if message:
            return str(message)
        return json.dumps(detail, ensure_ascii=False)
    return str(detail)


_TEMPLATE_ID_SAFE_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{2,180}$")


def _normalize_template_id(template_id: str) -> str:
    raw = str(template_id or "").strip()
    candidate = raw.replace("\\", "/").split("/")[-1].strip()
    if not candidate or candidate in {".", ".."}:
        raise _http_error(400, "invalid_template_id", "Invalid template_id format")
    normalized = candidate.lower()
    if _TEMPLATE_ID_SAFE_RE.fullmatch(normalized):
        return normalized
    try:
        return str(uuid.UUID(candidate))
    except (ValueError, TypeError):
        raise _http_error(400, "invalid_template_id", "Invalid template_id format")


def _template_dir(
    template_id: str,
    *,
    must_exist: bool = True,
    create: bool = False,
    kind: str = "pdf",
) -> Path:
    normalized_kind = (kind or "pdf").lower()
    if normalized_kind not in _UPLOAD_KIND_PREFIXES:
        raise _http_error(400, "invalid_template_kind", f"Unsupported template kind: {kind}")

    try:
        api_mod = importlib.import_module("backend.api")
        base_dir = getattr(api_mod, "UPLOAD_ROOT_BASE" if normalized_kind == "pdf" else "EXCEL_UPLOAD_ROOT_BASE")
    except Exception:
        base_dir = UPLOAD_ROOT_BASE if normalized_kind == "pdf" else EXCEL_UPLOAD_ROOT_BASE

    tid = _normalize_template_id(template_id)
    base_dir = base_dir.resolve()
    tdir = (base_dir / tid).resolve()
    if base_dir not in tdir.parents:
        raise _http_error(400, "invalid_template_path", "Invalid template_id path")
    if must_exist and not tdir.exists():
        raise _http_error(404, "template_not_found", "template_id not found")
    if create:
        tdir.mkdir(parents=True, exist_ok=True)
    return tdir


def _artifact_url(path: Path | None) -> Optional[str]:
    if path is None:
        return None
    path = Path(path)
    resolved = path.resolve()
    try:
        api_mod = importlib.import_module("backend.api")
        upload_root_base = getattr(api_mod, "UPLOAD_ROOT_BASE", UPLOAD_ROOT_BASE)
        excel_root_base = getattr(api_mod, "EXCEL_UPLOAD_ROOT_BASE", EXCEL_UPLOAD_ROOT_BASE)
    except Exception:
        upload_root_base = UPLOAD_ROOT_BASE
        excel_root_base = EXCEL_UPLOAD_ROOT_BASE
    mapping: dict[Path, str] = {
        upload_root_base: f"/{_UPLOAD_KIND_PREFIXES['pdf']}",
        excel_root_base: f"/{_UPLOAD_KIND_PREFIXES['excel']}",
    }
    for base, prefix in mapping.items():
        try:
            relative = resolved.relative_to(base)
        except ValueError:
            continue
        safe = relative.as_posix()
        return f"{prefix}/{safe}"
    return None


def _manifest_endpoint(template_id: str, kind: str = "pdf") -> str:
    if (kind or "pdf").lower() == "excel":
        return f"/excel/{template_id}/artifacts/manifest"
    return f"/templates/{template_id}/artifacts/manifest"


_EXCEL_SCALE_RE = re.compile(r"--excel-print-scale:\s*([0-9]*\.?[0-9]+)")


def _extract_excel_print_scale_from_html(html_path: Path) -> Optional[float]:
    try:
        html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    match = _EXCEL_SCALE_RE.search(html_text)
    if not match:
        return None
    try:
        value = float(match.group(1))
    except (TypeError, ValueError):
        return None
    if value <= 0 or value > 1.0:
        return None
    return value


def _ensure_contract_files(template_id: str, *, kind: str = "pdf") -> tuple[Path, Path]:
    tdir = _template_dir(template_id, kind=kind)

    template_html_path = tdir / "report_final.html"
    if not template_html_path.exists():
        template_html_path = tdir / "template_p1.html"
    if not template_html_path.exists():
        raise _http_error(
            status_code=404,
            code="template_html_missing",
            message="No template HTML found (report_final.html or template_p1.html).",
        )

    contract_path = tdir / "contract.json"
    if not contract_path.exists():
        raise _http_error(
            status_code=400,
            code="contract_missing",
            message="Missing contract.json. Finish template approval/mapping to create a contract for generation.",
        )
    return template_html_path, contract_path


def _artifact_map_from_paths(
    out_html: Path,
    out_pdf: Path,
    out_docx: Path | None,
    out_xlsx: Path | None,
) -> dict[str, Path]:
    artifacts = {out_html.name: out_html, out_pdf.name: out_pdf}
    if out_docx:
        artifacts[out_docx.name] = out_docx
    if out_xlsx:
        artifacts[out_xlsx.name] = out_xlsx
    return artifacts


def _run_report_internal(
    p: RunPayload,
    *,
    kind: str = "pdf",
    correlation_id: str | None = None,
    job_tracker: JobRunTracker | None = None,
):
    def _ensure_not_cancelled():
        _raise_if_cancelled(job_tracker)

    run_started = time.time()
    logger.info(
        "reports_run_start",
        extra={
            "event": "reports_run_start",
            "template_id": p.template_id,
            "connection_id": p.connection_id,
            "template_kind": kind,
            "correlation_id": correlation_id,
        },
    )
    _ensure_not_cancelled()
    if job_tracker:
        job_tracker.step_running("dataLoad", label="Load database connection")
    db_path = db_path_from_payload_or_default(p.connection_id)
    if not db_path.exists():
        if job_tracker:
            job_tracker.step_failed("dataLoad", "Database not found")
        raise _http_error(400, "db_not_found", "Database not found")
    if job_tracker:
        job_tracker.step_succeeded("dataLoad")

    _ensure_not_cancelled()

    if job_tracker:
        job_tracker.step_running("contractCheck", label="Prepare contract")
    try:
        template_html_path, contract_path = _ensure_contract_files(p.template_id, kind=kind)
    except HTTPException as exc:
        if job_tracker:
            job_tracker.step_failed("contractCheck", _job_error_message(exc.detail))
        raise
    tdir = template_html_path.parent

    try:
        contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.exception("Invalid contract.json")
        if job_tracker:
            job_tracker.step_failed("contractCheck", "Invalid contract.json")
        raise _http_error(500, "invalid_contract", "Invalid contract.json")
    else:
        try:
            api_mod = importlib.import_module("backend.api")
            validate_fn = getattr(api_mod, "validate_contract_schema", validate_contract_schema)
        except Exception:
            validate_fn = validate_contract_schema
        try:
            validate_fn(contract_data)
        except Exception as exc:
            logger.exception("Contract schema validation failed")
            if job_tracker:
                job_tracker.step_failed("contractCheck", "Contract schema validation failed")
            raise _http_error(500, "invalid_contract", "Contract schema validation failed")
    if job_tracker:
        job_tracker.step_succeeded("contractCheck")

    key_values_payload = clean_key_values(p.key_values)

    docx_requested = bool(p.docx)
    xlsx_requested = bool(p.xlsx)
    docx_landscape = kind == "excel"
    docx_enabled = docx_requested or docx_landscape
    xlsx_enabled = xlsx_requested or kind == "excel"
    render_strategy = RENDER_STRATEGIES.resolve("excel" if docx_landscape or xlsx_enabled else "pdf")
    _ensure_not_cancelled()

    ts = str(int(time.time()))
    out_html = tdir / f"filled_{ts}.html"
    out_pdf = tdir / f"filled_{ts}.pdf"
    out_docx = tdir / f"filled_{ts}.docx" if docx_enabled else None
    out_xlsx = tdir / f"filled_{ts}.xlsx" if xlsx_enabled else None
    tmp_html = out_html.with_name(out_html.name + ".tmp")
    tmp_pdf = out_pdf.with_name(out_pdf.name + ".tmp")
    tmp_docx = out_docx.with_name(out_docx.name + ".tmp") if out_docx else None
    tmp_xlsx = out_xlsx.with_name(out_xlsx.name + ".tmp") if out_xlsx else None
    docx_path: Path | None = None
    docx_font_scale: float | None = None
    xlsx_path: Path | None = None

    try:
        lock_ctx = acquire_template_lock(tdir, "reports_run", correlation_id)
    except TemplateLockError:
        raise _http_error(409, "template_locked", "Template is currently processing another request.")

    with lock_ctx:
        try:
            _ensure_not_cancelled()
            initial_artifacts = _artifact_map_from_paths(out_html, out_pdf, out_docx, out_xlsx)
            try:
                write_artifact_manifest(
                    tdir,
                    step="reports_run_started",
                    files=initial_artifacts,
                    inputs=[str(contract_path), str(db_path)],
                    correlation_id=correlation_id,
                )
            except Exception:
                logger.exception(
                    "artifact_manifest_start_failed",
                    extra={
                        "event": "artifact_manifest_start_failed",
                        "template_id": p.template_id,
                        "correlation_id": correlation_id,
                    },
                )
            if job_tracker:
                job_tracker.step_running("renderPdf", label="Render PDF artifacts")
            if kind == "excel":
                from backend.app.services.reports import ReportGenerateExcel as report_generate_module
            else:
                from backend.app.services.reports import ReportGenerate as report_generate_module

            fill_and_print = report_generate_module.fill_and_print

            fill_and_print(
                OBJ=contract_data,
                TEMPLATE_PATH=template_html_path,
                DB_PATH=db_path,
                OUT_HTML=tmp_html,
                OUT_PDF=tmp_pdf,
                START_DATE=p.start_date,
                END_DATE=p.end_date,
                batch_ids=p.batch_ids,
                KEY_VALUES=key_values_payload,
                BRAND_KIT_ID=getattr(p, "brand_kit_id", None),
            )
            _ensure_not_cancelled()
            if tmp_html.exists():
                tmp_html.replace(out_html)
            if tmp_pdf.exists():
                tmp_pdf.replace(out_pdf)
            docx_step_tracked = bool(job_tracker and job_tracker.has_step("renderDocx"))
            if docx_enabled and out_docx and tmp_docx:
                _ensure_not_cancelled()
                if docx_step_tracked:
                    job_tracker.step_running("renderDocx", label="Render DOCX")
                docx_tmp_result: Path | None = None
                docx_error: str | None = None
                try:
                    if docx_landscape:
                        docx_font_scale = _extract_excel_print_scale_from_html(out_html) or docx_font_scale
                    docx_tmp_result = render_strategy.render_docx(
                        out_html,
                        out_pdf if out_pdf and Path(out_pdf).exists() else None,
                        tmp_docx,
                        landscape=docx_landscape,
                        font_scale=docx_font_scale or (0.82 if docx_landscape else None),
                    )
                except Exception as exc:
                    with contextlib.suppress(FileNotFoundError):
                        tmp_docx.unlink(missing_ok=True)
                    docx_error = f"DOCX export failed: {exc}"
                    logger.exception(
                        "docx_export_failed",
                        extra={
                            "event": "docx_export_failed",
                            "template_id": p.template_id,
                            "template_kind": kind,
                            "correlation_id": correlation_id,
                        },
                    )
                else:
                    if docx_tmp_result:
                        docx_tmp_path = Path(docx_tmp_result)
                        if docx_tmp_path != out_docx:
                            docx_tmp_path.replace(out_docx)
                        docx_path = out_docx
                    else:
                        with contextlib.suppress(FileNotFoundError):
                            tmp_docx.unlink(missing_ok=True)
                if docx_step_tracked:
                    if docx_error:
                        job_tracker.step_failed("renderDocx", docx_error)
                    else:
                        job_tracker.step_succeeded("renderDocx")
                if docx_path and not docx_error:
                    _publish_event_safe(
                        Event(
                            name="render.completed",
                            payload={"template_id": p.template_id, "kind": "docx"},
                            correlation_id=correlation_id,
                        )
                    )
            xlsx_step_tracked = bool(job_tracker and job_tracker.has_step("renderXlsx"))
            if xlsx_enabled and out_xlsx and tmp_xlsx:
                _ensure_not_cancelled()
                if xlsx_step_tracked:
                    job_tracker.step_running("renderXlsx", label="Render XLSX")
                xlsx_error: str | None = None
                try:
                    xlsx_tmp_result = render_strategy.render_xlsx(out_html, tmp_xlsx)
                except Exception as exc:
                    with contextlib.suppress(FileNotFoundError):
                        tmp_xlsx.unlink(missing_ok=True)
                    logger.exception(
                        "xlsx_export_failed",
                        extra={
                            "event": "xlsx_export_failed",
                            "template_id": p.template_id,
                            "template_kind": kind,
                            "correlation_id": correlation_id,
                        },
                    )
                    xlsx_error = f"XLSX export failed: {exc}"
                else:
                    if xlsx_tmp_result:
                        xlsx_tmp_path = Path(xlsx_tmp_result)
                        if xlsx_tmp_path != out_xlsx:
                            xlsx_tmp_path.replace(out_xlsx)
                        xlsx_path = out_xlsx
                    else:
                        with contextlib.suppress(FileNotFoundError):
                            tmp_xlsx.unlink(missing_ok=True)
                if xlsx_step_tracked:
                    if xlsx_error:
                        job_tracker.step_failed("renderXlsx", xlsx_error)
                    else:
                        job_tracker.step_succeeded("renderXlsx")
                if xlsx_path and not xlsx_error:
                    _publish_event_safe(
                        Event(
                            name="render.completed",
                            payload={"template_id": p.template_id, "kind": "xlsx"},
                            correlation_id=correlation_id,
                        )
                    )
        except ImportError:
            raise _http_error(
                501,
                "report_module_missing",
                (
                    "Report generation module not found. "
                    "Add .app.services.reports.ReportGenerate.fill_and_print("
                    "OBJ, TEMPLATE_PATH, DB_PATH, OUT_HTML, OUT_PDF, START_DATE, END_DATE, batch_ids=None)."
                ),
            )
        except Exception as exc:
            with contextlib.suppress(FileNotFoundError):
                tmp_html.unlink(missing_ok=True)
            with contextlib.suppress(FileNotFoundError):
                tmp_pdf.unlink(missing_ok=True)
            if tmp_docx is not None:
                with contextlib.suppress(FileNotFoundError):
                    tmp_docx.unlink(missing_ok=True)
            if tmp_xlsx is not None:
                with contextlib.suppress(FileNotFoundError):
                    tmp_xlsx.unlink(missing_ok=True)
            logger.exception("Report generation failed")
            if job_tracker:
                job_tracker.step_failed("renderPdf", "Report generation failed")
            raise _http_error(500, "report_generation_failed", "Report generation failed")
    if job_tracker:
        job_tracker.step_succeeded("renderPdf")

    _ensure_not_cancelled()

    artifact_files = _artifact_map_from_paths(out_html, out_pdf, out_docx, out_xlsx)

    if job_tracker and job_tracker.has_step("finalize"):
        job_tracker.step_running("finalize", label="Finalize artifacts")
    write_artifact_manifest(
        tdir,
        step="reports_run",
        files=artifact_files,
        inputs=[str(contract_path), str(db_path)],
        correlation_id=correlation_id,
    )
    if job_tracker and job_tracker.has_step("finalize"):
        job_tracker.step_succeeded("finalize")

    manifest_data = load_manifest(tdir) or {}
    manifest_url = _manifest_endpoint(p.template_id, kind=kind)
    _state_store().record_template_run(p.template_id, p.connection_id)
    _state_store().set_last_used(p.connection_id, p.template_id)

    logger.info(
        "reports_run_complete",
        extra={
            "event": "reports_run_complete",
            "template_id": p.template_id,
            "html": str(out_html.name),
            "pdf": str(out_pdf.name),
            "docx": str(out_docx.name) if docx_path and out_docx else None,
            "xlsx": str(out_xlsx.name) if xlsx_path and out_xlsx else None,
            "correlation_id": correlation_id,
            "elapsed_ms": int((time.time() - run_started) * 1000),
        },
    )

    run_id = str(uuid.uuid4())
    result = {
        "ok": True,
        "run_id": run_id,
        "template_id": p.template_id,
        "start_date": p.start_date,
        "end_date": p.end_date,
        "html_url": _artifact_url(out_html),
        "pdf_url": _artifact_url(out_pdf),
        "docx_url": _artifact_url(out_docx) if docx_path and out_docx else None,
        "xlsx_url": _artifact_url(out_xlsx) if xlsx_path and out_xlsx else None,
        "manifest_url": manifest_url,
        "manifest_produced_at": manifest_data.get("produced_at"),
        "correlation_id": correlation_id,
    }
    try:
        template_record = _state_store().get_template_record(p.template_id) or {}
        connection_record = _state_store().get_connection_record(p.connection_id) if p.connection_id else {}
        _state_store().record_report_run(
            run_id,
            template_id=p.template_id,
            template_name=template_record.get("name") or p.template_id,
            template_kind=kind,
            connection_id=p.connection_id,
            connection_name=(connection_record or {}).get("name"),
            start_date=p.start_date,
            end_date=p.end_date,
            batch_ids=p.batch_ids,
            key_values=key_values_payload,
            status="succeeded",
            artifacts={
                "html_url": result.get("html_url"),
                "pdf_url": result.get("pdf_url"),
                "docx_url": result.get("docx_url"),
                "xlsx_url": result.get("xlsx_url"),
                "manifest_url": result.get("manifest_url"),
            },
            schedule_id=p.schedule_id,
            schedule_name=p.schedule_name,
        )
    except Exception:
        logger.exception(
            "report_run_history_record_failed",
            extra={
                "event": "report_run_history_record_failed",
                "template_id": p.template_id,
                "correlation_id": correlation_id,
            },
        )
    artifact_paths = {
        "html": out_html if out_html.exists() else None,
        "pdf": out_pdf if out_pdf.exists() else None,
        "docx": docx_path if docx_path and docx_path.exists() else None,
        "xlsx": xlsx_path if xlsx_path and xlsx_path.exists() else None,
    }

    # Post-generation agent hooks (fire-and-forget, non-blocking)
    try:
        _run_post_generation_hooks(run_id, p.template_id, kind, correlation_id)
    except Exception:
        logger.debug("post_generation_hooks_skipped")

    return result, artifact_paths


def _run_post_generation_hooks(
    run_id: str,
    template_id: str,
    kind: str,
    correlation_id: str | None,
) -> None:
    """
    Fire-and-forget post-generation agent hooks.

    Controlled by NEURA_REPORT_AGENT_HOOKS env var (comma-separated list).
    Supported hooks: summarize, insights
    Failures are logged but never block report delivery.
    """
    hooks_raw = os.getenv("NEURA_REPORT_AGENT_HOOKS", "").strip()
    if not hooks_raw:
        return

    hooks = [h.strip().lower() for h in hooks_raw.split(",") if h.strip()]
    if not hooks:
        return

    HOOK_TO_ANALYSIS_TYPE = {
        "summarize": "summarize",
        "insights": "insights",
    }

    for hook in hooks:
        analysis_type = HOOK_TO_ANALYSIS_TYPE.get(hook)
        if not analysis_type:
            logger.warning("Unknown report agent hook: %s (supported: %s)", hook, ", ".join(HOOK_TO_ANALYSIS_TYPE))
            continue

        try:
            import asyncio
            from backend.app.services.agents.agent_service import AgentService

            service = AgentService()

            async def _run_hook(at=analysis_type, rid=run_id):
                try:
                    await service.run_report_analyst(
                        run_id=rid,
                        analysis_type=at,
                        sync=False,  # async — don't block report delivery
                    )
                    logger.info(
                        "report_agent_hook_queued",
                        extra={
                            "event": "report_agent_hook_queued",
                            "hook": at,
                            "run_id": rid,
                        },
                    )
                except Exception as exc:
                    logger.warning(
                        "report_agent_hook_failed",
                        extra={
                            "event": "report_agent_hook_failed",
                            "hook": at,
                            "run_id": rid,
                            "error": str(exc),
                        },
                    )

            # Schedule on the running event loop if available, else ignore
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_run_hook())
            except RuntimeError:
                # No running event loop (synchronous context) — run in thread
                import threading

                def _thread_runner():
                    asyncio.run(_run_hook())

                t = threading.Thread(target=_thread_runner, daemon=True, name=f"agent-hook-{hook}-{run_id[:8]}")
                t.start()

        except Exception as exc:
            logger.warning(
                "report_agent_hook_setup_failed",
                extra={
                    "event": "report_agent_hook_setup_failed",
                    "hook": hook,
                    "run_id": run_id,
                    "error": str(exc),
                },
            )


def _maybe_send_email(
    p: RunPayload,
    artifact_paths: Mapping[str, Optional[Path]],
    run_result: Mapping[str, Any],
    *,
    kind: str,
    correlation_id: str | None,
    job_tracker: JobRunTracker | None = None,
) -> None:
    notification_strategy = NOTIFICATION_STRATEGIES.resolve("email")
    _raise_if_cancelled(job_tracker)
    recipients = normalize_email_targets(p.email_recipients)
    email_step_tracked = bool(job_tracker and job_tracker.has_step("email"))
    if not recipients:
        if email_step_tracked:
            job_tracker.step_succeeded("email")
        return
    if email_step_tracked:
        job_tracker.step_running("email", label="Send notification email")
    attachments: list[Path] = []
    for key in ("pdf", "docx", "xlsx"):
        path = artifact_paths.get(key)
        if isinstance(path, Path) and path.exists():
            attachments.append(path)
    if not attachments:
        fallback = artifact_paths.get("html")
        if isinstance(fallback, Path) and fallback.exists():
            attachments.append(fallback)
    if not attachments:
        return
    template_record = _state_store().get_template_record(p.template_id) or {}
    template_name = template_record.get("name") or p.template_id
    default_subject = f"Report run for {template_name}"
    subject = (p.email_subject or default_subject).strip()
    if not subject:
        subject = default_subject
    if p.email_message:
        body = p.email_message.strip()
    else:
        artifact_lines = []
        for key in ("pdf_url", "docx_url", "xlsx_url", "html_url"):
            url = run_result.get(key)
            if url:
                label = key.replace("_url", "").upper()
                artifact_lines.append(f"{label}: {url}")
        lines = [
            f"Template: {template_name} ({p.template_id})",
            f"Run kind: {kind}",
            f"Range: {p.start_date} -> {p.end_date}",
        ]
        if artifact_lines:
            lines.append("")
            lines.append("Artifacts:")
            lines.extend(artifact_lines)
        lines.append("")
        lines.append("This notification was generated automatically by NeuraReport.")
        body = "\n".join(lines)

    success = notification_strategy.send(
        recipients=recipients,
        subject=subject,
        body=body,
        attachments=attachments,
    )
    if email_step_tracked:
        if success:
            job_tracker.step_succeeded("email")
        else:
            job_tracker.step_failed("email", "Email delivery failed")
    _publish_event_safe(
        Event(
            name="notification.sent" if success else "notification.failed",
            payload={
                "template_id": p.template_id,
                "kind": kind,
                "recipients": len(recipients),
            },
            correlation_id=correlation_id,
        )
    )
    logger.info(
        "report_email_attempt",
        extra={
            "event": "report_email_attempt",
            "template_id": p.template_id,
            "recipients": len(recipients),
            "correlation_id": correlation_id,
            "status": "sent" if success else "skipped",
        },
    )


def _run_report_with_email(
    p: RunPayload,
    *,
    kind: str,
    correlation_id: str | None = None,
    job_tracker: JobRunTracker | None = None,
) -> dict:
    result, artifact_paths = _run_report_internal(p, kind=kind, correlation_id=correlation_id, job_tracker=job_tracker)
    _maybe_send_email(
        p,
        artifact_paths,
        result,
        kind=kind,
        correlation_id=correlation_id,
        job_tracker=job_tracker,
    )
    return result


def _run_report_job_sync(
    job_id: str,
    payload_data: Mapping[str, Any],
    kind: str,
    correlation_id: str,
    step_progress: Mapping[str, float],
) -> None:
    # If job was cancelled before starting, short-circuit.
    if _is_job_cancelled(job_id):
        logger.info("report_job_skipped_cancelled", extra={"event": "report_job_skipped_cancelled", "job_id": job_id})
        return

    # Import retry/webhook services
    try:
        from backend.app.services.jobs.error_classifier import is_retriable_error
        from backend.app.services.jobs.webhook_service import send_job_webhook_sync
    except ImportError:
        is_retriable_error = lambda e: True  # Default to retriable
        send_job_webhook_sync = None

    _register_job_thread(job_id)
    tracker = JobRunTracker(job_id, correlation_id=correlation_id, step_progress=step_progress)
    tracker.start()
    _publish_event_safe(Event(name="job.started", payload={"job_id": job_id, "kind": kind}, correlation_id=correlation_id))

    # Start heartbeat thread to indicate worker is alive
    heartbeat_stop = threading.Event()
    worker_id = f"worker-{threading.get_ident()}"

    def _heartbeat_worker():
        while not heartbeat_stop.is_set():
            try:
                _state_store().update_job_heartbeat(job_id, worker_id=worker_id)
            except Exception:
                logger.debug("heartbeat_update_failed", extra={"job_id": job_id})
            heartbeat_stop.wait(timeout=30)

    heartbeat_thread = threading.Thread(target=_heartbeat_worker, daemon=True, name=f"heartbeat-{job_id[:8]}")
    heartbeat_thread.start()

    @contextlib.contextmanager
    def _patch_subprocess_tracking():
        if not job_id:
            yield
            return
        with _track_subprocess(job_id):
            yield

    job_succeeded = False
    job_error: str | None = None

    try:
        api_mod = importlib.import_module("backend.api")
        run_fn = getattr(api_mod, "_run_report_with_email", _run_report_with_email)
    except Exception:
        run_fn = _run_report_with_email
    try:
        run_payload = RunPayload(**payload_data)
    except Exception as exc:
        tracker.fail("Invalid payload")
        job_error = "Invalid payload"
        logger.exception(
            "report_job_payload_invalid",
            extra={"event": "report_job_payload_invalid", "job_id": job_id},
        )
        # Mark as non-retriable since payload is invalid
        _state_store().record_job_completion(job_id, status="failed", error=job_error)
        return
    try:
        with _patch_subprocess_tracking():
            result = run_fn(run_payload, kind=kind, correlation_id=correlation_id, job_tracker=tracker)
    except HTTPException as exc:
        error_message = _job_error_message(exc.detail)
        error_code = str(exc.detail.get("code") or "").lower() if isinstance(exc.detail, Mapping) else ""
        is_cancelled = error_code == "job_cancelled"
        job_error = error_message
        # Print to stderr so it appears in Tauri desktop logs
        import traceback
        print(f"[REPORT_ERROR] job={job_id} http_error={error_message} code={error_code}", flush=True)
        traceback.print_exc()

        if is_cancelled:
            tracker.fail(error_message, status="cancelled")
            logger.info("report_job_cancelled", extra={
                "event": "report_job_cancelled",
                "job_id": job_id,
                "template_id": run_payload.template_id,
                "correlation_id": correlation_id,
            })
            _publish_event_safe(
                Event(
                    name="job.cancelled",
                    payload={"job_id": job_id, "kind": kind, "status": "cancelled"},
                    correlation_id=correlation_id,
                )
            )
        else:
            # Check if error is retriable
            retriable = is_retriable_error(error_message)
            if retriable:
                # Mark for retry instead of permanent failure
                _state_store().mark_job_for_retry(job_id, reason=error_message, is_retriable=True)
                logger.warning("report_job_marked_for_retry", extra={
                    "event": "report_job_marked_for_retry",
                    "job_id": job_id,
                    "error": error_message,
                    "correlation_id": correlation_id,
                })
                _publish_event_safe(
                    Event(
                        name="job.retry_scheduled",
                        payload={"job_id": job_id, "kind": kind, "error": error_message},
                        correlation_id=correlation_id,
                    )
                )
            else:
                tracker.fail(error_message, status="failed")
                logger.exception("report_job_http_error", extra={
                    "event": "report_job_http_error",
                    "job_id": job_id,
                    "template_id": run_payload.template_id,
                    "correlation_id": correlation_id,
                })
                _publish_event_safe(
                    Event(
                        name="job.failed",
                        payload={"job_id": job_id, "kind": kind, "error": error_message},
                        correlation_id=correlation_id,
                    )
                )
    except (asyncio.CancelledError, KeyboardInterrupt, SystemExit) as exc:
        tracker.fail("Job cancelled", status="cancelled")
        job_error = "Job cancelled"
        logger.info(
            "report_job_force_cancelled",
            extra={
                "event": "report_job_force_cancelled",
                "job_id": job_id,
                "template_id": run_payload.template_id,
                "correlation_id": correlation_id,
                "exc": str(exc),
            },
        )
        _publish_event_safe(
            Event(
                name="job.cancelled",
                payload={"job_id": job_id, "kind": kind, "status": "cancelled"},
                correlation_id=correlation_id,
            )
        )
    except Exception as exc:
        error_str = str(exc)
        job_error = "Report generation failed"
        # Print full traceback to stderr so it appears in Tauri desktop logs
        import traceback
        print(f"[REPORT_ERROR] job={job_id} error={error_str}", flush=True)
        traceback.print_exc()

        # Check if error is retriable
        retriable = is_retriable_error(error_str)
        if retriable:
            # Mark for retry instead of permanent failure
            _state_store().mark_job_for_retry(job_id, reason=error_str, is_retriable=True)
            logger.warning("report_job_marked_for_retry", extra={
                "event": "report_job_marked_for_retry",
                "job_id": job_id,
                "error": error_str,
                "correlation_id": correlation_id,
            })
            _publish_event_safe(
                Event(
                    name="job.retry_scheduled",
                    payload={"job_id": job_id, "kind": kind, "error": error_str},
                    correlation_id=correlation_id,
                )
            )
        else:
            tracker.fail(error_str)
            logger.exception(
                "report_job_failed",
                extra={
                    "event": "report_job_failed",
                    "job_id": job_id,
                    "template_id": run_payload.template_id,
                    "correlation_id": correlation_id,
                },
            )
            _publish_event_safe(
                Event(
                    name="job.failed",
                    payload={"job_id": job_id, "kind": kind, "error": error_str},
                    correlation_id=correlation_id,
                )
            )
    else:
        job_succeeded = True
        tracker.succeed(result)
        _publish_event_safe(
            Event(
                name="job.completed",
                payload={"job_id": job_id, "kind": kind, "status": "succeeded"},
                correlation_id=correlation_id,
            )
        )
    finally:
        # Stop heartbeat thread
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=5)

        _clear_job_thread(job_id)
        _clear_job_processes(job_id)

        # Send webhook notification if job completed (success or permanent failure)
        if send_job_webhook_sync is not None:
            try:
                job_record = _state_store().get_job(job_id)
                if job_record and job_record.get("webhookUrl"):
                    job_status = str(job_record.get("status") or "").lower()
                    # Only send webhook for terminal states (not pending_retry)
                    if job_status in {"succeeded", "failed", "cancelled"}:
                        webhook_result = send_job_webhook_sync(job_record)
                        if webhook_result.success:
                            _state_store().mark_webhook_sent(job_id)
                            logger.info("webhook_sent", extra={"job_id": job_id, "status": job_status})
                        else:
                            logger.warning("webhook_failed", extra={
                                "job_id": job_id,
                                "error": webhook_result.error,
                            })
            except Exception:
                logger.exception("webhook_send_error", extra={"job_id": job_id})


def _schedule_report_job(
    job_id: str,
    payload_data: Mapping[str, Any],
    kind: str,
    correlation_id: str,
    step_progress: Mapping[str, float],
) -> None:
    _publish_event_safe(
        Event(
            name="job.enqueued",
            payload={"job_id": job_id, "kind": kind},
            correlation_id=correlation_id,
        )
    )

    async def runner() -> None:
        try:
            future = asyncio.get_running_loop().run_in_executor(
                REPORT_JOB_EXECUTOR,
                _run_report_job_sync,
                job_id,
                payload_data,
                kind,
                correlation_id,
                step_progress,
            )
            _track_job_future(job_id, future)
            await future
        except Exception:
            logger.exception(
                "report_job_task_failed",
                extra={"event": "report_job_task_failed", "job_id": job_id, "correlation_id": correlation_id},
            )

    task = asyncio.create_task(runner())
    _track_background_task(task)


def _normalize_run_payloads(raw: RunPayload | Sequence[Any]) -> list[RunPayload]:
    """
    Accept a single run payload or a sequence of payloads and normalize to RunPayload instances.
    """
    if isinstance(raw, RunPayload):
        return [raw]
    if isinstance(raw, Mapping) and "runs" in raw:
        return _normalize_run_payloads(raw.get("runs") or [])
    if isinstance(raw, Iterable) and not isinstance(raw, (str, bytes)):
        normalized: list[RunPayload] = []
        for idx, item in enumerate(raw):
            if isinstance(item, RunPayload):
                normalized.append(item)
                continue
            if isinstance(item, Mapping):
                try:
                    normalized.append(RunPayload(**item))
                    continue
                except Exception as exc:
                    logger.exception("Invalid run payload at index %d", idx)
                    raise _http_error(400, "invalid_payload", f"Invalid run payload at index {idx}")
            raise _http_error(400, "invalid_payload", "Payload entries must be run payload objects or mappings")
        if not normalized:
            raise _http_error(400, "invalid_payload", "At least one run payload is required")
        return normalized
    raise _http_error(400, "invalid_payload", "Payload must be a run payload or a list of run payloads")


async def queue_report_job(p: RunPayload | Sequence[Any], request: Request, *, kind: str) -> dict:
    correlation_base = getattr(request.state, "correlation_id", None) or f"job-{uuid.uuid4().hex[:10]}"
    payloads = _normalize_run_payloads(p)
    try:
        api_mod = importlib.import_module("backend.api")
        schedule_fn = getattr(api_mod, "_schedule_report_job", _schedule_report_job)
    except Exception:
        schedule_fn = _schedule_report_job

    scheduled_jobs: list[dict[str, Any]] = []
    for idx, payload in enumerate(payloads):
        correlation_id = correlation_base if len(payloads) == 1 else f"{correlation_base}-{idx + 1}"
        steps = _build_job_steps(payload, kind=kind)
        template_rec = _state_store().get_template_record(payload.template_id) or {}
        payload_data = payload.model_dump()
        job_record = _state_store().create_job(
            job_type="run_report",
            template_id=payload.template_id,
            connection_id=payload.connection_id,
            template_name=template_rec.get("name") or f"Template {payload.template_id[:8]}",
            template_kind=template_rec.get("kind") or kind,
            schedule_id=payload.schedule_id,
            correlation_id=correlation_id,
            steps=steps,
            meta={
                "start_date": payload.start_date,
                "end_date": payload.end_date,
                "docx": bool(payload.docx),
                "xlsx": bool(payload.xlsx),
                "payload": payload_data,
            },
        )
        step_progress = _step_progress_from_steps(steps)
        schedule_fn(job_record["id"], payload_data, kind, correlation_id, step_progress)
        logger.info(
            "job_enqueued",
            extra={
                "event": "job_enqueued",
                "job_id": job_record["id"],
                "template_id": payload.template_id,
                "template_kind": kind,
                "correlation_id": correlation_id,
            },
        )
        scheduled_jobs.append(
            {
                "job_id": job_record["id"],
                "template_id": payload.template_id,
                "correlation_id": correlation_id,
                "kind": kind,
            }
        )

    job_ids = [job["job_id"] for job in scheduled_jobs]
    response: dict[str, Any] = {
        "job_id": job_ids[0],
        "job_ids": job_ids,
        "jobs": scheduled_jobs,
        "count": len(job_ids),
    }
    if len(job_ids) == 1:
        return {"job_id": job_ids[0]}
    return response


def recover_report_jobs(*, max_jobs: int = 50) -> int:
    """
    Attempt to requeue report jobs that were queued/running before a restart.

    Jobs must have a serialized payload stored in job meta to be recoverable.
    Returns the number of jobs requeued.
    """
    recovered = 0
    try:
        api_mod = importlib.import_module("backend.api")
        schedule_fn = getattr(api_mod, "_schedule_report_job", _schedule_report_job)
    except Exception:
        schedule_fn = _schedule_report_job

    jobs = _state_store().list_jobs(statuses=["queued", "running"], types=["run_report"], limit=0)
    for job in jobs:
        if max_jobs and recovered >= max_jobs:
            break
        job_id = job.get("id")
        if not job_id:
            continue
        meta = _state_store().get_job_meta(job_id) or {}
        payload = meta.get("payload")
        if not isinstance(payload, Mapping):
            _state_store().record_job_completion(
                job_id,
                status="failed",
                error="Server restarted before job could resume",
            )
            continue
        try:
            run_payload = RunPayload(**payload)
        except Exception as exc:
            logger.exception("Server restarted; job payload invalid for job %s", job_id)
            _state_store().record_job_completion(
                job_id,
                status="failed",
                error="Server restarted; job payload invalid",
            )
            continue

        kind = str(job.get("templateKind") or meta.get("template_kind") or payload.get("template_kind") or "pdf")
        steps = _build_job_steps(run_payload, kind=kind)
        step_progress = _step_progress_from_steps(steps)
        correlation_id = job.get("correlationId") or payload.get("correlation_id") or f"recovered-{job_id[:8]}"

        _state_store().record_job_completion(
            job_id,
            status="failed",
            error="Server restarted; job requeued",
        )

        template_rec = _state_store().get_template_record(run_payload.template_id) or {}
        new_job = _state_store().create_job(
            job_type="run_report",
            template_id=run_payload.template_id,
            connection_id=run_payload.connection_id,
            template_name=template_rec.get("name") or f"Template {run_payload.template_id[:8]}",
            template_kind=template_rec.get("kind") or kind,
            schedule_id=run_payload.schedule_id,
            correlation_id=correlation_id,
            steps=steps,
            meta={
                "start_date": run_payload.start_date,
                "end_date": run_payload.end_date,
                "docx": bool(run_payload.docx),
                "xlsx": bool(run_payload.xlsx),
                "payload": payload,
                "recovered_from": job_id,
            },
        )
        schedule_fn(new_job["id"], payload, kind, correlation_id, step_progress)
        recovered += 1

    return recovered


def list_report_runs(
    *,
    template_id: str | None = None,
    connection_id: str | None = None,
    schedule_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    return _state_store().list_report_runs(
        template_id=template_id,
        connection_id=connection_id,
        schedule_id=schedule_id,
        limit=limit,
    )


def get_report_run(run_id: str) -> dict | None:
    return _state_store().get_report_run(run_id)


def generate_docx_for_run(run_id: str) -> dict:
    """Generate DOCX on-demand from a completed run's PDF artifact.

    Raises ValueError if the run or PDF doesn't exist,
    RuntimeError if conversion fails.
    """
    store = _state_store()
    run = store.get_report_run(run_id)
    if not run:
        raise ValueError(f"Run {run_id} not found")

    artifacts = run.get("artifacts") or {}
    if artifacts.get("docx_url"):
        return run  # already generated

    pdf_url = artifacts.get("pdf_url")
    if not pdf_url:
        raise ValueError("Run has no PDF artifact to convert")

    # Reverse-map the URL to a filesystem path.
    # PDF URLs look like: /uploads/<template_id>/…/filled_123.pdf
    #                  or: /excel-uploads/<template_id>/…/filled_123.pdf
    try:
        api_mod = importlib.import_module("backend.api")
        upload_root = getattr(api_mod, "UPLOAD_ROOT_BASE", UPLOAD_ROOT_BASE)
        excel_root = getattr(api_mod, "EXCEL_UPLOAD_ROOT_BASE", EXCEL_UPLOAD_ROOT_BASE)
    except Exception:
        upload_root = UPLOAD_ROOT_BASE
        excel_root = EXCEL_UPLOAD_ROOT_BASE

    pdf_path: Path | None = None
    for prefix, root in [("/uploads/", upload_root), ("/excel-uploads/", excel_root)]:
        if pdf_url.startswith(prefix):
            relative = pdf_url[len(prefix):]
            candidate = root / relative
            if candidate.exists():
                pdf_path = candidate
            break

    if not pdf_path or not pdf_path.exists():
        raise ValueError(f"PDF file not found on disk for URL: {pdf_url}")

    docx_path = pdf_path.with_suffix(".docx")

    from backend.app.services.reports.docx_export import pdf_file_to_docx

    logger.info("generate_docx_start", extra={
        "event": "generate_docx_start",
        "run_id": run_id,
        "pdf_path": str(pdf_path),
    })

    result = pdf_file_to_docx(pdf_path, docx_path)
    if not result:
        raise RuntimeError("DOCX conversion failed — check backend logs for details")

    # Build the docx_url the same way _artifact_url does
    docx_url = _artifact_url(docx_path)
    if not docx_url:
        raise RuntimeError("Could not build download URL for generated DOCX")

    updated = store.update_report_run_artifacts(run_id, {"docx_url": docx_url})
    logger.info("generate_docx_complete", extra={
        "event": "generate_docx_complete",
        "run_id": run_id,
        "docx_url": docx_url,
    })
    return updated or run


def scheduler_runner(payload: dict, kind: str, *, job_tracker: JobRunTracker | None = None) -> dict:
    run_payload = RunPayload(**payload)
    correlation_id = payload.get("correlation_id") or f"sched-{payload.get('schedule_id') or uuid.uuid4()}"
    return _run_report_with_email(run_payload, kind=kind, correlation_id=correlation_id, job_tracker=job_tracker)


def run_report(p: RunPayload, request: Request, *, kind: str = "pdf"):
    correlation_id = getattr(request.state, "correlation_id", None)
    return _run_report_with_email(p, kind=kind, correlation_id=correlation_id)
