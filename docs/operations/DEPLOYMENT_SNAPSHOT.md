# Deployment Snapshot (`prodo/`)

`prodo/` is a **local production deployment snapshot** directory used for desktop/server deployment (built frontend + backend code + runtime folders).

It is intentionally **not tracked in git**:
- It contains environment-specific files (e.g., `.env`, virtualenvs, logs, state DBs).
- It bloats the repo and breaks architecture governance if treated as source code.

## Generate a Snapshot

From the repo root:

```bash
bash scripts/export_deployment_snapshot.sh
```

By default this writes a snapshot to `./prodo/`:
- `prodo/frontend/`: static frontend build output
- `prodo/backend/`: backend source tree (code only; excludes runtime state/uploads/venvs)
- `prodo/config/`, `prodo/logs/`, `prodo/state/`: created as empty directories for deployment wiring

To write to a custom directory:

```bash
bash scripts/export_deployment_snapshot.sh /path/to/snapshot-dir
```

## What The Script Does Not Copy

For safety and reproducibility, the snapshot export excludes:
- Python virtualenvs (`.venv/`, `venv/`)
- caches (`__pycache__/`, `*.pyc`)
- runtime data (`backend/state/`, `backend/uploads/`, `backend/uploads_excel/`)

If you need to migrate runtime state/artifacts into a deployment, do that explicitly as part of your ops process (backup/restore, rsync, etc.).

