from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterator

logger = logging.getLogger("neura.env")


def _iter_candidate_paths() -> Iterator[Path]:
    """
    Yield possible .env files from highest to lowest priority.

    Precedence:
    1. NEURA_ENV_FILE (absolute or relative)
    2. Repository root .env (sibling of backend/)
    3. backend/.env (created by scripts/setup.ps1)
    """
    env_override = os.getenv("NEURA_ENV_FILE")
    if env_override:
        yield Path(env_override).expanduser()

    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    yield repo_root / ".env"
    yield backend_dir / ".env"


def _strip_quotes(value: str) -> str:
    if not value:
        return value
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_env_file() -> Path | None:
    """
    Load KEY=VALUE pairs from the first existing candidate .env file.
    Existing environment variables are never overridden.
    """
    for candidate in _iter_candidate_paths():
        try:
            resolved = candidate if candidate.is_absolute() else (Path.cwd() / candidate)
            if not resolved.exists():
                continue
            _apply_env_file(resolved)
            logger.info("loaded_env_file", extra={"event": "loaded_env_file", "path": str(resolved)})
            return resolved
        except PermissionError:
            logger.warning(
                "env_file_permission_denied",
                extra={"event": "env_file_permission_denied", "path": str(candidate)},
            )
        except UnicodeDecodeError as e:
            logger.warning(
                "env_file_encoding_error",
                extra={"event": "env_file_encoding_error", "path": str(candidate), "detail": str(e)},
            )
        except (ValueError, SyntaxError) as e:
            logger.warning(
                "env_file_parse_error",
                extra={"event": "env_file_parse_error", "path": str(candidate), "detail": str(e)},
            )
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception(
                "env_file_load_failed",
                extra={"event": "env_file_load_failed", "path": str(candidate)},
            )
    return None


def _apply_env_file(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        try:
            key, value = line.split("=", 1)
            key = key.strip()
            value = _strip_quotes(value.strip())
            if not key or key.startswith("#"):
                continue
            os.environ.setdefault(key, value)
        except Exception as e:
            logger.warning(
                "env_file_bad_line",
                extra={"event": "env_file_bad_line", "path": str(path), "line": line_num, "detail": str(e)},
            )
