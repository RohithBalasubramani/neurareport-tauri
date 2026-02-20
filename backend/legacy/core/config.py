from __future__ import annotations

from pathlib import Path

from backend.app.services.config import get_settings

SETTINGS = get_settings()
APP_VERSION = SETTINGS.version
APP_COMMIT = SETTINGS.commit

UPLOAD_ROOT: Path = SETTINGS.uploads_root
EXCEL_UPLOAD_ROOT: Path = SETTINGS.excel_uploads_root


def get_settings():
    return SETTINGS
