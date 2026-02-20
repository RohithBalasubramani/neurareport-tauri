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

# --- Hidden imports: modules loaded dynamically via importlib ---
hidden_imports = [
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
    # Agent modules (dynamically discovered via importlib)
    'backend.app.services.agents',
    'backend.app.services.agents.agent_registry',
    'backend.app.services.agents.agent_service',
    'backend.app.services.agents.base_agent',
    'backend.app.services.agents.content_repurpose_agent',
    'backend.app.services.agents.data_analyst_agent',
    'backend.app.services.agents.email_draft_agent',
    'backend.app.services.agents.proofreading_agent',
    'backend.app.services.agents.report_analyst_agent',
    'backend.app.services.agents.research_agent',
    'backend.app.services.agents.service',
    # All route modules (registered by router.py)
    'backend.app.api.routes.agents',
    'backend.app.api.routes.agents_v2',
    'backend.app.api.routes.ai',
    'backend.app.api.routes.analytics',
    'backend.app.api.routes.audit',
    'backend.app.api.routes.charts',
    'backend.app.api.routes.connections',
    'backend.app.api.routes.connectors',
    'backend.app.api.routes.dashboards',
    'backend.app.api.routes.design',
    'backend.app.api.routes.docai',
    'backend.app.api.routes.docqa',
    'backend.app.api.routes.documents',
    'backend.app.api.routes.enrichment',
    'backend.app.api.routes.excel',
    'backend.app.api.routes.export',
    'backend.app.api.routes.federation',
    'backend.app.api.routes.health',
    'backend.app.api.routes.ingestion',
    'backend.app.api.routes.jobs',
    'backend.app.api.routes.knowledge',
    'backend.app.api.routes.legacy',
    'backend.app.api.routes.logger',
    'backend.app.api.routes.nl2sql',
    'backend.app.api.routes.recommendations',
    'backend.app.api.routes.reports',
    'backend.app.api.routes.schedules',
    'backend.app.api.routes.search',
    'backend.app.api.routes.spreadsheets',
    'backend.app.api.routes.state',
    'backend.app.api.routes.summary',
    'backend.app.api.routes.synthesis',
    'backend.app.api.routes.templates',
    'backend.app.api.routes.visualization',
    'backend.app.api.routes.widgets',
    'backend.app.api.routes.workflows',
    # Legacy services with importlib
    'backend.legacy.services.report_service',
    'backend.legacy.services.file_service',
    'backend.legacy.services.mapping',
    'backend.legacy.services.scheduler_service',
    # Auth
    'backend.app.services.auth',
    # DB
    'backend.app.services.db.engine',
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
