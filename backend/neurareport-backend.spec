# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for NeuraReport desktop backend sidecar.

Run from the repo root:
  cd /home/rohith/desktop/neurareport-tauri
  .venv/bin/pyinstaller backend/neurareport-backend.spec
"""
import os
from pathlib import Path

repo_root = Path(SPECPATH).parent  # /home/rohith/desktop/neurareport-tauri
backend_dir = repo_root / 'backend'

# --- Auto-discover ALL backend.* modules so nothing is missed ---
_auto_backend = []
for py_file in sorted(backend_dir.rglob('*.py')):
    rel = py_file.relative_to(repo_root)
    # Skip tests, migrations, .venv, __pycache__
    parts = rel.parts
    if any(skip in parts for skip in ('tests', '.venv', '__pycache__', 'migrations')):
        continue
    # Convert path to module name: backend/app/foo.py -> backend.app.foo
    if rel.name == '__init__.py':
        mod = '.'.join(parts[:-1])
    else:
        mod = '.'.join(parts)[:-3]  # strip .py
    if mod:
        _auto_backend.append(mod)

# --- Hidden imports: auto-discovered + known dynamic imports ---
hidden_imports = _auto_backend + [
    # uvicorn internals
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    # SQLAlchemy dialects
    'sqlalchemy.dialects.sqlite',
    'aiosqlite',
    'sqlmodel',
    # FastAPI / Pydantic
    'fastapi',
    'pydantic',
    'pydantic_settings',
    'pydantic.deprecated.decorator',
    'multipart',
    # Email validator (often missed)
    'email_validator',
    # Starlette internals
    'starlette.responses',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
]

# --- Data files needed at runtime ---
datas = []

# JSON schemas loaded at module level by validation.py
schemas_dir = backend_dir / 'app' / 'schemas'
if schemas_dir.exists():
    datas.append((str(schemas_dir), 'backend/app/schemas'))

# JSON schemas used by validation helpers
json_schemas_dir = backend_dir / 'app' / 'services' / 'utils' / 'json_schemas'
if json_schemas_dir.exists():
    datas.append((str(json_schemas_dir), 'backend/app/services/utils/json_schemas'))

# RBAC model and policy files (casbin)
rbac_dir = backend_dir / 'app' / 'services' / 'rbac'
for rbac_file in ['model.conf', 'policy.csv']:
    rbac_path = rbac_dir / rbac_file
    if rbac_path.exists():
        datas.append((str(rbac_path), 'backend/app/services/rbac'))

# Prompt YAML templates
prompts_dir = backend_dir / 'app' / 'services' / 'prompts' / 'registry'
if prompts_dir.exists():
    datas.append((str(prompts_dir), 'backend/app/services/prompts/registry'))

# Database migrations
migrations_dir = backend_dir / 'app' / 'services' / 'db' / 'migrations'
if migrations_dir.exists():
    datas.append((str(migrations_dir), 'backend/app/services/db/migrations'))

# Version info
version_file = backend_dir / 'app' / 'version.json'
if version_file.exists():
    datas.append((str(version_file), 'backend/app'))

# Alembic config
alembic_ini = backend_dir / 'alembic.ini'
if alembic_ini.exists():
    datas.append((str(alembic_ini), 'backend'))

a = Analysis(
    [str(backend_dir / 'desktop_entry.py')],
    pathex=[str(repo_root)],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional deps not needed for desktop SQLite mode
        'psycopg2',
        'asyncpg',
        'pymysql',
        'pymongo',
        'elasticsearch',
        'redis',
        'dramatiq',
        'celery',
        'boto3',
        'botocore',
        'google',
        'azure',
        'dropbox',
        'msal',
        'notion_client',
        'slack_sdk',
        'pymsteams',
        'sentence_transformers',
        'torch',
        'transformers',
        'spacy',
        'sklearn',
        'scikit-learn',
        'statsmodels',
        'playwright',
        'opentelemetry',
        'prometheus_client',
        'sentry_sdk',
        'hvac',
        'casbin',
        'strawberry',
        'prefect',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='neurareport-backend',
    strip=False,
    upx=True,
    console=True,  # Required for sidecar stdout/stderr capture by Tauri
)
