from __future__ import annotations

from typing import Optional

from backend.app.utils.errors import DomainError


class TemplateImportError(DomainError):
    def __init__(self, *, code: str, message: str, status_code: int = 400, detail: Optional[str] = None) -> None:
        super().__init__(code=code, message=message, status_code=status_code, detail=detail)


class TemplateZipInvalidError(TemplateImportError):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(code="invalid_zip", message="Invalid zip file", detail=detail, status_code=400)


class TemplateLockedError(TemplateImportError):
    def __init__(self) -> None:
        super().__init__(code="template_locked", message="Template is busy", status_code=409)


class TemplateTooLargeError(TemplateImportError):
    def __init__(self, max_bytes: int) -> None:
        super().__init__(
            code="upload_too_large",
            message=f"Upload exceeds limit of {max_bytes} bytes",
            status_code=413,
        )


class TemplateExtractionError(TemplateImportError):
    def __init__(self, detail: Optional[str] = None) -> None:
        super().__init__(code="import_failed", message="Failed to extract zip", detail=detail, status_code=400)
