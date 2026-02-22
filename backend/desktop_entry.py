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
import subprocess
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


def _clean_stale_locks(data_dir: Path):
    """Remove stale .lock.* files left by previous crashes.

    On Windows, filelock uses lockfile semantics that may leave .lock files
    behind if the process is killed. These stale locks cause subsequent
    report runs to timeout waiting for a lock that will never be released.
    """
    cleaned = 0
    for lock_dir in [data_dir / "uploads", data_dir / "uploads_excel"]:
        if not lock_dir.exists():
            continue
        for lock_file in lock_dir.rglob(".lock.*"):
            try:
                lock_file.unlink()
                cleaned += 1
            except OSError:
                pass
    if cleaned:
        print(f"[DESKTOP] Cleaned {cleaned} stale lock file(s) from previous session", flush=True)


def _ensure_playwright_chromium(data_dir: Path):
    """Install Playwright Chromium browser if not present.

    Uses a fixed path inside app data to avoid all system path issues.
    Tries multiple installation methods for cross-machine reliability.
    Falls back gracefully — PDF generation is skipped if unavailable.
    """
    browsers_dir = data_dir / "playwright-browsers"
    browsers_dir.mkdir(parents=True, exist_ok=True)

    # Set THE canonical path BEFORE anything else — overrides all system defaults
    # This avoids the "wrong path" issues on different machines
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)

    # Also set for Windows system-level fallback in render.py
    if platform.system() == "Windows":
        os.environ["LOCALAPPDATA"] = os.environ.get("LOCALAPPDATA", "")

    # Quick check: chromium already downloaded?
    if any(browsers_dir.glob("chromium-*")) or any(browsers_dir.glob("chromium_*")):
        print("[DESKTOP] Playwright Chromium found", flush=True)
        return

    print("[DESKTOP] Downloading Chromium for PDF generation (first launch, ~130MB)...", flush=True)
    installed = False

    # Method 1: Use Playwright's bundled node.js driver (works in PyInstaller)
    if not installed:
        try:
            from playwright._impl._driver import compute_driver_executable, get_driver_env
            driver_exec = compute_driver_executable()
            env = get_driver_env()
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)

            print("[DESKTOP] Method 1: Playwright driver install...", flush=True)
            result = subprocess.run(
                [str(driver_exec), "install", "chromium"],
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                print("[DESKTOP] Chromium installed via driver", flush=True)
                installed = True
            else:
                print(f"[DESKTOP] Driver method returned code {result.returncode}: {result.stderr[:300]}", flush=True)
        except ImportError:
            print("[DESKTOP] Playwright driver not available", flush=True)
        except subprocess.TimeoutExpired:
            print("[DESKTOP] Driver install timed out (10min)", flush=True)
        except Exception as e:
            print(f"[DESKTOP] Driver method failed: {e}", flush=True)

    # Method 2: Try PowerShell/system Python as fallback (for Windows)
    if not installed and platform.system() == "Windows":
        try:
            print("[DESKTOP] Method 2: PowerShell pip + playwright install...", flush=True)
            env = os.environ.copy()
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)
            # Try using system python if available
            for py_cmd in ["python", "python3", "py"]:
                try:
                    result = subprocess.run(
                        [py_cmd, "-m", "playwright", "install", "chromium"],
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=600,
                    )
                    if result.returncode == 0:
                        print(f"[DESKTOP] Chromium installed via {py_cmd}", flush=True)
                        installed = True
                        break
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    print(f"[DESKTOP] {py_cmd} method timed out", flush=True)
                    break
        except Exception as e:
            print(f"[DESKTOP] Fallback method failed: {e}", flush=True)

    # Method 3: Try npx playwright (if Node.js is available)
    if not installed:
        try:
            npx_cmd = "npx.cmd" if platform.system() == "Windows" else "npx"
            env = os.environ.copy()
            env["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)
            print("[DESKTOP] Method 3: npx playwright install...", flush=True)
            result = subprocess.run(
                [npx_cmd, "playwright", "install", "chromium"],
                env=env,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if result.returncode == 0:
                print("[DESKTOP] Chromium installed via npx", flush=True)
                installed = True
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[DESKTOP] npx method failed: {e}", flush=True)

    if not installed:
        print("[DESKTOP] WARNING: Chromium not installed — PDF generation unavailable", flush=True)
        print("[DESKTOP] Reports will still generate HTML and Excel formats", flush=True)
        print("[DESKTOP] To fix: run 'playwright install chromium' manually", flush=True)


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

    # Ensure Playwright Chromium is available for PDF generation
    _ensure_playwright_chromium(data_dir)

    # Clean stale file locks from previous crashes
    _clean_stale_locks(data_dir)

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
