"""Runtime hook for PyInstaller. Runs BEFORE desktop_entry.py."""
import multiprocessing
import sys

# Force unbuffered output for frozen binaries
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Child worker processes (e.g. pdf2docx multi_processing) inherit the
# runtime hook.  Only print debug info from the main process.
_is_main = multiprocessing.current_process().name == "MainProcess"

if _is_main:
    print("[RUNTIME DEBUG] sys.frozen =", getattr(sys, 'frozen', False), flush=True)
    print("[RUNTIME DEBUG] sys._MEIPASS =", getattr(sys, '_MEIPASS', 'N/A'), flush=True)

    # Check if the problematic module is available in the frozen importer
    for finder in sys.meta_path:
        cls_name = type(finder).__name__
        if not hasattr(finder, 'toc'):
            print(f"[RUNTIME DEBUG] {cls_name}: no toc attribute", flush=True)

    # Try the import directly
    try:
        import backend.app.repositories.state
        print("[RUNTIME DEBUG] Direct import of backend.app.repositories.state: SUCCESS", flush=True)
    except ImportError as e:
        print(f"[RUNTIME DEBUG] Direct import of backend.app.repositories.state: FAILED - {e}", flush=True)
