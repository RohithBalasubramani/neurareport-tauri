Backend services are implemented with FastAPI and orchestrate PDF template verification,
mapping, report generation, AI agents, data enrichment, document intelligence, and more.

## Environment

Refer to `docs/operations/CONFIG.md` for the complete list of supported environment variables. The bare minimum for production is:

- Claude Code CLI installed and authenticated (`claude --version` to verify)
- `CLAUDE_CODE_MODEL` (defaults to `sonnet`; options: `sonnet`, `opus`, `haiku`)
- `UPLOAD_ROOT` (defaults to `backend/uploads`)
- `NEURA_STATE_SECRET` (optional but recommended so encrypted state survives restarts)

The backend will read a `.env` file if present (highest to lowest priority):

1. `NEURA_ENV_FILE` (explicit path)
2. Repo root `.env`
3. `backend/.env` (created by `scripts/setup.ps1`)

Set variables in PowerShell with:

```powershell
$env:CLAUDE_CODE_MODEL = "sonnet"
$env:UPLOAD_ROOT = "$PWD\backend\uploads"
```

macOS/Linux shells:

```bash
export CLAUDE_CODE_MODEL="sonnet"
export UPLOAD_ROOT="$PWD/backend/uploads"
```

## Running Locally

```bash
pip install -r backend/requirements.txt
uvicorn backend.api:app --reload
```

Run `uvicorn` from the repository root so `backend.api` and `backend.legacy` imports resolve correctly.

Static artifacts such as verified templates and mapping results are written to `backend/uploads/` by default.

## API Routes (35 modules)

All routes live under `backend/app/api/routes/`. Major route groups:

| Module | Prefix | Description |
|---|---|---|
| `health.py` | `/health`, `/healthz`, `/readyz` | Readiness/liveness checks |
| `state.py` | `/state` | Bootstrap state payload |
| `templates.py` | `/templates` | Template CRUD, verify, mapping, approve |
| `reports.py` | `/reports` | Report discover and run |
| `connections.py` | `/api/connections` | Database connection management |
| `connectors.py` | `/api/connectors` | External connectors (DB, cloud storage) |
| `agents.py` | `/api/agents` | Agent tasks (v1) |
| `agents_v2.py` | `/api/v2/agents` | Agent tasks (v2 - research, analyst, email, proofread, repurpose) |
| `analytics.py` | `/api/analytics` | Usage analytics and metrics |
| `ai.py` | `/api/ai` | AI writing services (grammar, summarize, rewrite, translate) |
| `charts.py` | `/api/charts` | Chart suggestions and saved charts |
| `dashboards.py` | `/api/dashboards` | Dashboard builder, widgets, snapshots |
| `design.py` | `/api/design` | Brand kit and design system |
| `docai.py` | `/api/docai` | Document intelligence (invoice, contract, resume, receipt) |
| `docqa.py` | `/api/docqa` | Document Q&A |
| `documents.py` | `/api/documents` | Document CRUD, collaboration, PDF ops |
| `enrichment.py` | `/api/enrichment` | Data enrichment (company, address, exchange) |
| `excel.py` | `/api/excel` | Excel operations and verification |
| `export.py` | `/api/export` | Multi-format export (PDF, DOCX, XLSX, CSV, HTML) |
| `federation.py` | `/api/federation` | Cross-source federated queries |
| `ingestion.py` | `/api/ingestion` | File, URL, email, folder watcher ingestion |
| `jobs.py` | `/api/jobs` | Async job tracking and management |
| `knowledge.py` | `/api/knowledge` | Knowledge library CRUD |
| `legacy.py` | `/api/legacy` | Legacy compatibility routes |
| `nl2sql.py` | `/api/nl2sql` | Natural language to SQL |
| `recommendations.py` | `/api/recommendations` | Template recommendations |
| `schedules.py` | `/api/schedules` | Report scheduling (cron triggers) |
| `search.py` | `/api/search` | Full-text search |
| `spreadsheets.py` | `/api/spreadsheets` | Spreadsheet editor, formulas, pivot tables |
| `summary.py` | `/api/summary` | AI-generated summaries |
| `synthesis.py` | `/api/synthesis` | Cross-source data synthesis |
| `visualization.py` | `/api/visualization` | Chart/visualization generation |
| `workflows.py` | `/api/workflows` | Workflow automation |

## Service Layer (40+ modules)

Services under `backend/app/services/` handle business logic:

- **agents/** - 5 specialized AI agents (research, data analyst, email draft, content repurpose, proofreading)
- **ai/** - Writing services, spreadsheet AI
- **analytics/** - Usage analytics
- **analyze/** - Document analysis, extraction pipeline, visualization engine
- **charts/** - Auto chart service, QuickChart integration
- **connections/** - Database connection lifecycle
- **connectors/** - Multi-database connectors (PostgreSQL, MySQL, SQLServer, MongoDB, Elasticsearch, BigQuery, Snowflake, DuckDB) + cloud storage (S3, Azure Blob, Dropbox, Google Drive, OneDrive, SFTP)
- **dashboards/** - Dashboard service, widgets, snapshots, embed
- **design/** - Brand kit service
- **docai/** - Invoice, contract, resume, receipt parsers
- **docqa/** - Document Q&A service
- **documents/** - Document service, collaboration, PDF signing/operations
- **enrichment/** - Data enrichment with caching (company, address, exchange rate sources)
- **export/** - Multi-format export service
- **federation/** - Federated query service
- **generate/** - Chart suggestions, discovery, saved charts
- **ingestion/** - File upload, folder watcher, web clipper, transcription, email ingestion
- **jobs/** - Job tracking, webhook service, error classifier, recovery daemon, report scheduler
- **knowledge/** - Knowledge library service
- **llm/** - LLM client, RAG, text-to-SQL, vision, document extraction
- **nl2sql/** - Natural language to SQL service
- **reports/** - Report generation (PDF/HTML/Excel), discovery, DOCX/XLSX export
- **search/** - Full-text search service
- **spreadsheets/** - Spreadsheet service, formula engine, pivot tables
- **summary/** - AI summary service
- **synthesis/** - Cross-source synthesis service
- **templates/** - Template service, catalog, CSS merge, layout hints

## DataFrame-First Query Engine

The API never talks to a live SQL database. Instead, every uploaded SQLite file is
immediately materialized into pandas DataFrames (`SQLiteDataFrameLoader`) and all
legacy SQL statements run through DuckDB (`sqlite_shim`) on top of those in-memory
frames. Verifiers such as `verify_sqlite` now validate that a DB can be hydrated
into DataFrames rather than that sqlite3 can execute a query. This keeps the
existing SQL assets usable while guaranteeing the backend is "DataFrame ready".

## Persistent State

Database connection metadata, template records, and the last-used selections live in `backend/state/state.json`. Secrets (e.g., connection strings) are encrypted with Fernet; provide `NEURA_STATE_SECRET` for deterministic keys or keep the generated secret safe.

All HTTP responses include a correlation ID and standardized error envelope (`status`, `code`, `message`, `correlation_id`).

## Security & Middleware

- Rate limiting with configurable per-route limits
- Idempotency keys for POST/PUT/DELETE operations
- CSP headers, CORS, and security headers on all responses
- SQL injection prevention via read-only SQL validation
- Path traversal prevention on file operations
- UX governance guards enforcing frontend/backend contract alignment

## Health Checks (PowerShell)

```powershell
curl.exe http://127.0.0.1:8000/healthz
curl.exe http://127.0.0.1:8000/readyz
```

## Automated Tests

```bash
pytest backend/tests                                          # full suite
pytest backend/tests/api/                                     # API route tests
pytest backend/tests/unit/                                    # unit tests
pytest backend/tests/services/                                # service tests
pytest backend/tests/simulation/                              # chaos scenarios
pytest backend/tests/test_pipeline_verification.py            # pipeline verification
pytest backend/tests/test_locking.py                          # locking tests
pytest backend/tests/test_html_sanitizer.py                   # HTML sanitizer
```

Test coverage includes property-based testing (Hypothesis), connector security tests, webhook service tests, enrichment cache tests, and architecture enforcement.

## Architecture

See `docs/architecture/ARCHITECTURE_GOVERNANCE.md` for enforced import boundaries and the contribution contract. The backend follows a layered architecture:

```
api/ → services/ → domain/ + repositories/ + schemas/
         ↓
       utils/ (pure helpers)
```

Import boundaries are enforced by `scripts/architecture/enforce_backend_arch.py` and CI.
