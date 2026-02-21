"""
Desktop sidecar entry point for Tauri.

Accepts --port to run on a dynamically chosen port.
Configures environment for single-user desktop mode:
  - SQLite database (no PostgreSQL needed)
  - No Redis/Dramatiq (background tasks disabled)
  - Anonymous API access (no login)
  - Files stored in OS app-data directory
"""
import argparse
import os
import platform
import stat
import sys
from pathlib import Path


def get_app_data_dir():
    """Get OS-appropriate app data directory."""
    home = Path.home()
    if platform.system() == "Darwin":
        return home / "Library" / "Application Support" / "com.neurareport.desktop"
    elif platform.system() == "Windows":
        return Path(os.environ.get("APPDATA", home / "AppData" / "Roaming")) / "NeuraReport"
    else:
        return home / ".local" / "share" / "neurareport"


def main():
    parser = argparse.ArgumentParser(description="NeuraReport desktop backend")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    args = parser.parse_args()

    # Resolve data directory
    data_dir = get_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    (data_dir / "uploads_excel").mkdir(exist_ok=True)
    (data_dir / "state").mkdir(exist_ok=True)

    # Logs directory (writable location outside frozen bundle)
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Ensure existing DB files are writable (previous installations may
    # have left them read-only, e.g. when installed to Program Files).
    state_dir = data_dir / "state"
    for f in state_dir.iterdir():
        if f.is_file():
            try:
                mode = f.stat().st_mode
                if not (mode & stat.S_IWRITE):
                    f.chmod(mode | stat.S_IWRITE)
            except OSError:
                pass

    # Desktop-mode environment defaults
    os.environ.setdefault("NEURA_DEBUG", "true")
    os.environ.setdefault("NEURA_ALLOW_ANON_API", "true")
    os.environ.setdefault("NEURA_JWT_SECRET", "desktop-local-secret")
    os.environ.setdefault("NEURA_REDIS_URL", "")
    os.environ.setdefault("NEURA_AGENT_WORKER_DISABLED", "true")
    os.environ.setdefault("NEURA_RECOVERY_DAEMON_DISABLED", "false")
    os.environ.setdefault("NEURA_SCHEDULER_DISABLED", "false")
    os.environ.setdefault("NEURA_METRICS_ENABLED", "false")
    os.environ.setdefault("NEURA_ALLOWED_HOSTS_ALL", "true")
    os.environ.setdefault("UPLOAD_ROOT", str(data_dir / "uploads"))
    os.environ.setdefault("EXCEL_UPLOAD_ROOT", str(data_dir / "uploads_excel"))
    os.environ.setdefault("NEURA_STATE_DIR", str(data_dir / "state"))
    os.environ.setdefault("NEURA_ERROR_LOG", str(logs_dir / "backend_errors.log"))
    os.environ.setdefault("NEURA_LLM_LOG", str(logs_dir / "llm.log"))
    os.environ.setdefault(
        "NEURA_DATABASE_URL",
        f"sqlite+aiosqlite:///{data_dir / 'state' / 'neurareport.db'}",
    )

    # Direct import avoids string-based lookup issues with PyInstaller
    from backend.api import app  # noqa: E402
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
