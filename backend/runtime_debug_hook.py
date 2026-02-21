"""Runtime hook for PyInstaller debugging. Runs BEFORE desktop_entry.py."""
import sys

print("[RUNTIME DEBUG] sys.frozen =", getattr(sys, 'frozen', False))
print("[RUNTIME DEBUG] sys._MEIPASS =", getattr(sys, '_MEIPASS', 'N/A'))

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
        print(f"[RUNTIME DEBUG] {cls_name} TOC: {len(all_keys)} total, {backend_count} backend.*")
        print(f"[RUNTIME DEBUG] {cls_name} repo/state entries: {repo_mods}")

        if 'backend.app.repositories.state' in [str(k) for k in all_keys]:
            print("[RUNTIME DEBUG] OK: backend.app.repositories.state IS in frozen TOC")
        else:
            print("[RUNTIME DEBUG] !!! MISSING: backend.app.repositories.state NOT in frozen TOC !!!")
    else:
        print(f"[RUNTIME DEBUG] {cls_name}: no toc attribute")

# Try the import directly
try:
    import backend.app.repositories.state
    print("[RUNTIME DEBUG] Direct import of backend.app.repositories.state: SUCCESS")
except ImportError as e:
    print(f"[RUNTIME DEBUG] Direct import of backend.app.repositories.state: FAILED - {e}")
    # Check parent packages
    for pkg in ['backend', 'backend.app', 'backend.app.repositories']:
        try:
            __import__(pkg)
            print(f"[RUNTIME DEBUG]   {pkg}: importable")
        except ImportError as e2:
            print(f"[RUNTIME DEBUG]   {pkg}: FAILED - {e2}")
            break
