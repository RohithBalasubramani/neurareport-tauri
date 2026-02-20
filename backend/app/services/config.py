from __future__ import annotations

from functools import lru_cache
import json
import logging
import os
from pathlib import Path
from typing import Any, List, Optional

try:
    # Pydantic v2+
    from pydantic_settings import BaseSettings, SettingsConfigDict

    _V2_SETTINGS = True
except ImportError:  # pragma: no cover - fallback for Pydantic v1
    from pydantic import BaseSettings

    SettingsConfigDict = None
    _V2_SETTINGS = False
from pydantic import Field, SecretStr, field_validator


logger = logging.getLogger("neura.config")


def _default_uploads_root() -> Path:
    return Path(__file__).resolve().parents[2] / "uploads"


def _default_excel_uploads_root() -> Path:
    return Path(__file__).resolve().parents[2] / "uploads_excel"


def _default_state_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "state"


def _load_version_info() -> dict[str, Any]:
    version_path = Path(__file__).resolve().parents[1] / "version.json"
    if not version_path.exists():
        return {"version": "dev", "commit": "unknown"}
    try:
        return json.loads(version_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("version_info_load_failed", extra={"event": "version_info_load_failed", "error": str(exc)})
        return {"version": "dev", "commit": "unknown"}


class Settings(BaseSettings):
    api_title: str = "NeuraReport API"
    api_version: str = "4.0"
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"], validation_alias="NEURA_CORS_ORIGINS")
    api_key: Optional[str] = Field(default=None, validation_alias="NEURA_API_KEY")
    allow_anonymous_api: bool = Field(default=False, validation_alias="NEURA_ALLOW_ANON_API")
    jwt_secret: SecretStr = Field(default="change-me", validation_alias="NEURA_JWT_SECRET")
    jwt_lifetime_seconds: int = Field(default=3600, validation_alias="NEURA_JWT_LIFETIME_SECONDS")

    uploads_dir: Path = Field(default_factory=_default_uploads_root, validation_alias="UPLOAD_ROOT")
    excel_uploads_dir: Path = Field(default_factory=_default_excel_uploads_root, validation_alias="EXCEL_UPLOAD_ROOT")
    state_dir: Path = Field(default_factory=_default_state_dir, validation_alias="NEURA_STATE_DIR")

    max_upload_bytes: int = Field(default=50 * 1024 * 1024, validation_alias="NEURA_MAX_UPLOAD_BYTES")
    max_verify_pdf_bytes: int = Field(default=50 * 1024 * 1024, validation_alias="NEURA_MAX_VERIFY_PDF_BYTES")
    max_zip_entries: int = Field(default=2000, validation_alias="NEURA_MAX_ZIP_ENTRIES")
    max_zip_uncompressed_bytes: int = Field(default=200 * 1024 * 1024, validation_alias="NEURA_MAX_ZIP_UNCOMPRESSED_BYTES")

    template_import_max_concurrency: int = Field(default=4, validation_alias="NEURA_TEMPLATE_IMPORT_MAX_CONCURRENCY")

    # Claude Code CLI configuration (no API key needed - uses authenticated CLI)
    claude_code_model: str = Field(default="sonnet", validation_alias="CLAUDE_CODE_MODEL")

    artifact_warn_bytes: int = Field(default=5 * 1024 * 1024, validation_alias="ARTIFACT_WARN_BYTES")
    artifact_warn_render_ms: int = Field(default=2000, validation_alias="ARTIFACT_WARN_RENDER_MS")
    version: str = Field(default="dev", validation_alias="NEURA_VERSION")
    commit: str = Field(default="unknown", validation_alias="NEURA_COMMIT")

    # Rate limiting configuration
    rate_limit_enabled: bool = Field(default=True, validation_alias="NEURA_RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, validation_alias="NEURA_RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, validation_alias="NEURA_RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_burst: int = Field(default=20, validation_alias="NEURA_RATE_LIMIT_BURST")

    # Security configuration
    trusted_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"], validation_alias="NEURA_TRUSTED_HOSTS")
    allowed_hosts_all: bool = Field(default=False, validation_alias="NEURA_ALLOWED_HOSTS_ALL")  # Set to True only for local development

    # Request timeout
    request_timeout_seconds: int = Field(default=300, validation_alias="NEURA_REQUEST_TIMEOUT_SECONDS")

    # Idempotency configuration
    idempotency_enabled: bool = Field(default=True, validation_alias="NEURA_IDEMPOTENCY_ENABLED")
    idempotency_ttl_seconds: int = Field(default=86400, validation_alias="NEURA_IDEMPOTENCY_TTL_SECONDS")

    # Task queue (Dramatiq + Redis)
    redis_url: str = Field(default="redis://localhost:6379/0", env="NEURA_REDIS_URL")
    worker_processes: int = Field(default=4, env="NEURA_WORKER_PROCESSES")
    worker_threads: int = Field(default=8, env="NEURA_WORKER_THREADS")
    task_result_ttl_ms: int = Field(default=1_800_000, env="NEURA_TASK_RESULT_TTL_MS")

    # Embeddings / vector search (pgvector is the system-of-record in Postgres)
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="NEURA_EMBEDDING_MODEL")
    embedding_dim: int = Field(default=384, env="NEURA_EMBEDDING_DIM")

    # Database configuration (PostgreSQL)
    database_url: str = Field(
        default="sqlite+aiosqlite:///backend/state/neurareport.db",
        env="NEURA_DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="NEURA_DB_POOL_SIZE")
    database_pool_max_overflow: int = Field(default=20, env="NEURA_DB_POOL_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="NEURA_DB_POOL_TIMEOUT")
    database_echo: bool = Field(default=False, env="NEURA_DB_ECHO")

    # Content Security Policy configuration
    csp_connect_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:*", "ws://localhost:*"],
        validation_alias="NEURA_CSP_CONNECT_ORIGINS"
    )

    # Analysis cache configuration
    analysis_cache_max_items: int = Field(default=100, validation_alias="NEURA_ANALYSIS_CACHE_MAX_ITEMS")
    analysis_cache_ttl_seconds: int = Field(default=3600, validation_alias="NEURA_ANALYSIS_CACHE_TTL_SECONDS")  # 1 hour
    analysis_max_concurrency: int = Field(default=4, validation_alias="NEURA_ANALYSIS_MAX_CONCURRENCY")

    # Observability
    otlp_endpoint: Optional[str] = Field(default=None, env="NEURA_OTLP_ENDPOINT")
    metrics_enabled: bool = Field(default=True, env="NEURA_METRICS_ENABLED")
    app_name: str = Field(default="neurareport-backend", env="NEURA_APP_NAME")

    # Debug/development mode - defaults to False for safety.
    # Set NEURA_DEBUG=true explicitly for local development.
    debug_mode: bool = Field(default=False, validation_alias="NEURA_DEBUG")

    # File/path safety overrides (use only in trusted environments)
    allow_unsafe_pdf_paths: bool = Field(default=False, validation_alias="NEURA_ALLOW_UNSAFE_PDF_PATHS")

    # UX Governance configuration
    # Set to True when frontend is fully compliant with governance headers
    # Default is False to allow development without strict UX headers
    ux_governance_strict: bool = Field(default=False, validation_alias="NEURA_UX_GOVERNANCE_STRICT")

    @field_validator("embedding_dim")
    @classmethod
    def _validate_embedding_dim(cls, v: int) -> int:
        if v <= 0 or v > 8192:
            raise ValueError("embedding_dim must be between 1 and 8192")
        return v

    @property
    def uploads_root(self) -> Path:
        return self.uploads_dir

    @property
    def excel_uploads_root(self) -> Path:
        return self.excel_uploads_dir

    if _V2_SETTINGS:
        # Pydantic Settings v2 - use absolute path to backend/.env
        _env_file = Path(__file__).resolve().parents[2] / ".env"
        model_config = SettingsConfigDict(env_file=str(_env_file), extra="ignore", populate_by_name=True)
    else:  # pragma: no cover - Pydantic v1 fallback
        class Config:
            env_file = str(Path(__file__).resolve().parents[2] / ".env")
            extra = "ignore"


def _apply_runtime_defaults(settings: Settings) -> Settings:
    # Claude Code CLI is the only LLM provider - no API key validation needed
    # The CLI handles authentication via its own session

    jwt_val = settings.jwt_secret.get_secret_value()
    if jwt_val.strip().lower() in {"", "change-me"}:
        if settings.debug_mode:
            logger.warning(
                "jwt_secret_default",
                extra={"event": "jwt_secret_default"},
            )
        else:
            raise RuntimeError(
                "NEURA_JWT_SECRET must be set to a strong secret in production "
                "(debug_mode is off). Set NEURA_DEBUG=true to bypass for local development."
            )

    if not os.getenv("NEURA_VERSION") or not os.getenv("NEURA_COMMIT"):
        version_info = _load_version_info()
        if not os.getenv("NEURA_VERSION"):
            settings.version = str(version_info.get("version", settings.version))
        if not os.getenv("NEURA_COMMIT"):
            settings.commit = str(version_info.get("commit", settings.commit))

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.excel_uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.state_dir.mkdir(parents=True, exist_ok=True)
    return settings


@lru_cache
def get_settings() -> Settings:
    return _apply_runtime_defaults(Settings())


def log_settings(target_logger: logging.Logger, settings: Settings) -> None:
    target_logger.info(
        "app_config",
        extra={
            "event": "app_config",
            "version": settings.version,
            "commit": settings.commit,
            "llm_provider": "claude_code",
            "claude_model": settings.claude_code_model,
            "uploads_root": str(settings.uploads_root),
            "excel_uploads_root": str(settings.excel_uploads_root),
            "artifact_warn_bytes": settings.artifact_warn_bytes,
            "artifact_warn_render_ms": settings.artifact_warn_render_ms,
        },
    )
