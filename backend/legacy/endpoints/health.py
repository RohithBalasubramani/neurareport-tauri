from __future__ import annotations

import os

from fastapi import APIRouter, Request

from backend.legacy.core.config import SETTINGS, UPLOAD_ROOT
from backend.legacy.utils.health_utils import check_clock, check_external_head, check_fs_writable, health_response

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/healthz")
def healthz(request: Request):
    checks: dict[str, tuple[bool, str]] = {}
    checks["fs_write"] = check_fs_writable(UPLOAD_ROOT.resolve())
    checks["clock"] = check_clock()
    external_url = os.getenv("NEURA_HEALTH_EXTERNAL_HEAD")
    if external_url:
        checks["external"] = check_external_head(external_url, SETTINGS.openai_api_key or None)
    return health_response(request, checks)


@router.get("/readyz")
def readyz(request: Request):
    checks: dict[str, tuple[bool, str]] = {}
    checks["fs_write"] = check_fs_writable(UPLOAD_ROOT.resolve())
    checks["clock"] = check_clock()
    checks["openai_key"] = (
        bool(SETTINGS.openai_api_key),
        "configured" if SETTINGS.openai_api_key else "missing",
    )
    external_url = os.getenv("NEURA_HEALTH_EXTERNAL_HEAD") or "https://api.openai.com/v1/models"
    checks["external"] = check_external_head(external_url, SETTINGS.openai_api_key or None)
    return health_response(request, checks)
