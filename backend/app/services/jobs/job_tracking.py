from __future__ import annotations

import importlib
import logging
from typing import Any, Iterable, Mapping, Optional

from backend.app.repositories.state import state_store as state_store_module
from backend.app.schemas.generate.reports import RunPayload
from backend.app.utils.email_utils import normalize_email_targets

logger = logging.getLogger("backend.legacy.services.report_service")


def _state_store():
    try:
        api_mod = importlib.import_module("backend.api")
        return getattr(api_mod, "state_store", state_store_module)
    except Exception:
        return state_store_module


DEFAULT_JOB_STEP_PROGRESS = {
    "dataLoad": 5.0,
    "contractCheck": 15.0,
    "renderPdf": 60.0,
    "renderDocx": 75.0,
    "renderXlsx": 85.0,
    "finalize": 95.0,
    "email": 100.0,
}


def _build_job_steps(payload: RunPayload, *, kind: str) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = [
        {"name": "dataLoad", "label": "Load database"},
        {"name": "contractCheck", "label": "Prepare contract"},
        {"name": "renderPdf", "label": "Render PDF"},
    ]
    docx_requested = bool(payload.docx)
    if docx_requested:
        steps.append({"name": "renderDocx", "label": "Render DOCX"})
    if kind == "excel" or bool(payload.xlsx):
        steps.append({"name": "renderXlsx", "label": "Render XLSX"})
    steps.append({"name": "finalize", "label": "Finalize artifacts"})
    if normalize_email_targets(payload.email_recipients):
        steps.append({"name": "email", "label": "Send email"})
    return steps


def _step_progress_from_steps(steps: Iterable[Mapping[str, Any]]) -> dict[str, float]:
    progress: dict[str, float] = {}
    for step in steps:
        name = str(step.get("name") or "").strip()
        if not name:
            continue
        progress[name] = DEFAULT_JOB_STEP_PROGRESS.get(name, 0.0)
    return progress


class JobRunTracker:
    def __init__(
        self,
        job_id: str | None,
        *,
        correlation_id: str | None = None,
        step_progress: Optional[Mapping[str, float]] = None,
    ) -> None:
        self.job_id = job_id
        self.correlation_id = correlation_id
        self.step_progress = {k: float(v) for k, v in (step_progress or {}).items()}
        self._step_names = set(self.step_progress.keys()) if self.step_progress else None

    def _should_track(self, name: str) -> bool:
        if not name:
            return False
        if self._step_names is None:
            return True
        return name in self._step_names

    def has_step(self, name: str) -> bool:
        return self._should_track(name)

    def start(self) -> None:
        if not self.job_id:
            return
        try:
            _state_store().record_job_start(self.job_id)
        except Exception:
            logger.exception(
                "job_start_record_failed",
                extra={
                    "event": "job_start_record_failed",
                    "job_id": self.job_id,
                    "correlation_id": self.correlation_id,
                },
            )

    def progress(self, value: float) -> None:
        if not self.job_id:
            return
        try:
            _state_store().record_job_progress(self.job_id, value)
        except Exception:
            logger.exception(
                "job_progress_record_failed",
                extra={
                    "event": "job_progress_record_failed",
                    "job_id": self.job_id,
                    "correlation_id": self.correlation_id,
                },
            )

    def _record_step(
        self,
        name: str,
        status: str,
        *,
        error: Optional[str] = None,
        progress: Optional[float] = None,
        label: Optional[str] = None,
    ) -> None:
        if not self.job_id or not self._should_track(name):
            return
        try:
            _state_store().record_job_step(
                self.job_id,
                name,
                status=status,
                error=error,
                progress=progress,
                label=label,
            )
        except Exception:
            logger.exception(
                "job_step_record_failed",
                extra={
                    "event": "job_step_record_failed",
                    "job_id": self.job_id,
                    "step": name,
                    "correlation_id": self.correlation_id,
                },
            )

    def step_running(self, name: str, *, label: Optional[str] = None) -> None:
        self._record_step(name, "running", label=label)

    def step_succeeded(self, name: str, *, progress: Optional[float] = None) -> None:
        progress_value = progress if progress is not None else self.step_progress.get(name)
        self._record_step(name, "succeeded")
        if progress_value is not None:
            self.progress(progress_value)

    def step_failed(self, name: str, error: str) -> None:
        self._record_step(name, "failed", error=str(error))

    def succeed(self, result: Optional[Mapping[str, Any]]) -> None:
        if not self.job_id:
            return
        self.progress(100.0)
        try:
            _state_store().record_job_completion(self.job_id, status="succeeded", error=None, result=result)
        except Exception:
            logger.exception(
                "job_completion_record_failed",
                extra={
                    "event": "job_completion_record_failed",
                    "job_id": self.job_id,
                    "correlation_id": self.correlation_id,
                },
            )

    def fail(self, error: str, *, status: str = "failed") -> None:
        if not self.job_id:
            return
        try:
            _state_store().record_job_completion(self.job_id, status=status, error=str(error), result=None)
        except Exception:
            logger.exception(
                "job_completion_record_failed",
                extra={
                    "event": "job_completion_record_failed",
                    "job_id": self.job_id,
                    "correlation_id": self.correlation_id,
                },
            )
