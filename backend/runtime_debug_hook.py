"""Runtime hook for PyInstaller debugging. Runs BEFORE desktop_entry.py."""
import sys

# Force unbuffered output for frozen binaries
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

print("[RUNTIME DEBUG] sys.frozen =", getattr(sys, 'frozen', False), flush=True)
print("[RUNTIME DEBUG] sys._MEIPASS =", getattr(sys, '_MEIPASS', 'N/A'), flush=True)

# Check if the problematic module is available in the frozen importer
for finder in sys.meta_path:
    cls_name = type(finder).__name__
    if hasattr(finder, 'toc'):
        toc = finder.toc
        if isinstance(toc, dict):
            all_keys = list(toc.keys())
        else:
            all_keys = [getattr(e, 'name', str(e)) for e in toc]

        backend_count = sum(1 for k in all_keys if str(k).startswith('backend.'))
        repo_mods = [k for k in all_keys if 'repositor' in str(k) or 'state_access' in str(k)]
        print(f"[RUNTIME DEBUG] {cls_name} TOC: {len(all_keys)} total, {backend_count} backend.*", flush=True)
        print(f"[RUNTIME DEBUG] {cls_name} repo/state entries: {repo_mods}", flush=True)

        if 'backend.app.repositories.state' in [str(k) for k in all_keys]:
            print("[RUNTIME DEBUG] OK: backend.app.repositories.state IS in frozen TOC", flush=True)
        else:
            print("[RUNTIME DEBUG] !!! MISSING: backend.app.repositories.state NOT in frozen TOC !!!", flush=True)
    else:
        print(f"[RUNTIME DEBUG] {cls_name}: no toc attribute", flush=True)

# Try the import directly
try:
    import backend.app.repositories.state
    print("[RUNTIME DEBUG] Direct import of backend.app.repositories.state: SUCCESS", flush=True)
except ImportError as e:
    print(f"[RUNTIME DEBUG] Direct import of backend.app.repositories.state: FAILED - {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.stderr.flush()
    # Check parent packages
    for pkg in ['backend', 'backend.app', 'backend.app.repositories']:
        try:
            __import__(pkg)
            print(f"[RUNTIME DEBUG]   {pkg}: importable", flush=True)
        except ImportError as e2:
            print(f"[RUNTIME DEBUG]   {pkg}: FAILED - {e2}", flush=True)
            break
