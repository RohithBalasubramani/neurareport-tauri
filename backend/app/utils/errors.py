from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class AppError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int = 400, detail: str | None = None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


@dataclass
class DomainError(AppError):
    """
    Base domain error to keep HTTP concerns at the edge while providing typed failures.
    """

    code: str
    message: str
    status_code: int = 400
    detail: Optional[str] = None

    def __post_init__(self) -> None:
        super().__init__(code=self.code, message=self.message, status_code=self.status_code, detail=self.detail)
