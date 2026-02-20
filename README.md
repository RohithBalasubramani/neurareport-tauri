# NeuraReport

NeuraReport is an AI-powered reporting and document workspace. It pairs a **FastAPI** backend with a **React 19 + Vite** front-end. Operators ingest PDF templates, auto-map fields to SQL data sources, approve the mapping contract, and generate PDF/HTML report batches — all with full artifact traceability.

The platform also provides AI agents, document intelligence (DocAI), cross-page data sharing, data enrichment, federated schema queries, knowledge management, NL2SQL, workflow automation, real-time collaboration, and a visualization engine.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Production Deployment](#production-deployment)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Logging & Observability](#logging--observability)
- [Troubleshooting](#troubleshooting)
- [Additional Documentation](#additional-documentation)

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│  React 19 SPA   │────▶│  FastAPI Backend (uvicorn)                   │
│  Vite + MUI     │     │                                              │
│  Port 5173 (dev)│     │  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  Port 9071 (prod│     │  │ Template  │  │ Mapping  │  │  Report   │  │
└─────────────────┘     │  │ Verify    │→ │ Preview  │→ │ Generate  │  │
                        │  └──────────┘  └──────────┘  └───────────┘  │
                        │        │             │             │         │
                        │  ┌─────▼─────────────▼─────────────▼──────┐  │
                        │  │         Claude Code CLI (LLM)          │  │
                        │  └────────────────────────────────────────┘  │
                        │  ┌────────────────────────────────────────┐  │
                        │  │  SQLite State Store + DataFrame Pipeline│  │
                        │  └────────────────────────────────────────┘  │
                        │  Port 8000 (dev) / Port 9070 (prod)         │
                        └──────────────────────────────────────────────┘
```

### Pipeline Flow

1. **PDF Upload** — User uploads a PDF template
2. **Template Verify** (LLM Call 1/2) — AI extracts structure, generates HTML replica
3. **Mapping Preview** (LLM Call 3) — AI maps template tokens to database columns
4. **Mapping Approve** (LLM Call 4 contract, Call 5 generator) — Builds execution contract + SQL generator
5. **Report Generation** — `fill_and_print` populates HTML with live data and renders PDF

### Key Subsystems

| Subsystem | Description |
|-----------|-------------|
| **AI Agents** | 6 agent types: research, data_analyst, email_draft, content_repurpose, proofreading, report_analyst |
| **DataFrame Pipeline** | Feature-flagged (`NEURA_USE_DATAFRAME_PIPELINE=true`) pandas-based alternative to SQL/DuckDB |
| **Document Intelligence** | DocAI extraction, DocQA question-answering over uploaded documents |
| **Enrichment** | Company, address, and exchange rate data enrichment |
| **Federation** | Cross-source federated queries across connected databases |
| **Knowledge Base** | Searchable document repository with full-text indexing |
| **NL2SQL** | Natural language to SQL query conversion |
| **Real-time Collaboration** | Yjs + WebSocket-based concurrent editing |
| **Visualization** | ECharts/Recharts-powered dashboards and chart builder |
| **Workflow Engine** | Automated multi-step pipelines with scheduling |

## Repository Layout

```
NeuraReport/
├── backend/                    # FastAPI application
│   ├── api.py                  # Entry point
│   ├── app/
│   │   ├── api/routes/         # 35 route modules
│   │   ├── services/           # 40+ service modules
│   │   ├── schemas/            # Pydantic models
│   │   └── repositories/       # Data access layer
│   ├── legacy/                 # Legacy service layer (compatibility)
│   ├── engine/                 # Legacy pipeline engine
│   ├── tests/                  # 155 test files (pytest)
│   ├── uploads/                # Runtime artifacts (created at runtime)
│   ├── uploads_excel/          # Excel uploads (created at runtime)
│   └── state/                  # SQLite state store
├── frontend/                   # Vite + React 19 SPA
│   ├── src/
│   │   ├── api/                # API client layer (Axios)
│   │   ├── features/           # 33 page modules
│   │   ├── stores/             # Zustand state management
│   │   └── components/         # Shared UI components
│   └── dist/                   # Production build output
├── prodo/                      # Production deployment
│   ├── backend/                # Deployed backend (with .venv)
│   ├── frontend/               # Static build served by http-server
│   ├── config/                 # ports.env, deployment.env
│   └── logs/                   # Runtime logs
├── packages/                   # Standalone packages (@neurareport/ai-qa-agent)
├── scripts/                    # Developer utilities
└── docs/                       # Architecture, operations, product docs
```

## Prerequisites

- **Python 3.11+** (pyenv recommended)
- **Node.js 18+** (or 20 LTS)
- **npm 9+**
- **Claude Code CLI** installed and authenticated (`claude --version` to verify)
- (Optional) **Playwright** browsers for E2E tests: `npx playwright install --with-deps`

## Local Development

### Backend

```bash
cd NeuraReport
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# Required environment
export NEURA_DEBUG=true                   # Bypasses JWT secret requirement
export NEURA_ALLOW_MISSING_OPENAI=true    # Claude CLI is the primary LLM

uvicorn backend.api:app --reload
```

The API runs on **http://127.0.0.1:8000**. Interactive docs at **/docs**.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit **http://127.0.0.1:5173**. The Vite dev server proxies `/api` requests to the backend automatically.

To configure: copy `frontend/.env.example` to `frontend/.env.local` and set `VITE_USE_MOCK=false` for live backend.

## Running Tests

### Backend (pytest)

```bash
source backend/.venv/bin/activate
NEURA_DEBUG=true pytest backend/tests/ -q
```

**Test suite:** 155 test files covering unit, integration, API, security, property-based, chaos simulation, and concurrency tests. The suite runs in ~20 minutes.

**Current status:** 5333 passing, 41 skipped (optional dependencies), with a small number of pre-existing failures in OpenAI-to-Claude migration stubs, soft-delete module, and zip handling edge cases.

### Frontend

```bash
cd frontend
npm run lint              # ESLint
npm run build             # Production bundle
npm run test              # Vitest unit tests
npx playwright install    # Once per machine
npm run test:ui           # Playwright E2E tests
npm run test:a11y         # Accessibility checks
npm run test:visual       # Visual regression suite
```

### Pipeline Verification

```bash
python scripts/verify_pipeline.py --template-id <id> --uploads-root ./backend/uploads
python scripts/artifact_stats.py --template-id <id>
```

## Production Deployment

NeuraReport is deployed via the `prodo/` directory using **systemd user services**.

### Architecture

| Component | Technology | Port | Systemd Unit |
|-----------|-----------|------|-------------|
| Backend | FastAPI + uvicorn | **9070** | `neurareport-backend.service` |
| Frontend | http-server (static) | **9071** | `neurareport-frontend.service` |

### Access URLs

| Network | Frontend | Backend API | API Docs |
|---------|----------|-------------|----------|
| Localhost | http://127.0.0.1:9071 | http://127.0.0.1:9070 | http://127.0.0.1:9070/docs |
| Tailscale | http://100.90.185.31:9071 | http://100.90.185.31:9070 | http://100.90.185.31:9070/docs |
| LAN | http://192.168.1.20:9071 | http://192.168.1.20:9070 | http://192.168.1.20:9070/docs |

### Service Management

```bash
# Check status
systemctl --user status neurareport-backend.service
systemctl --user status neurareport-frontend.service

# Restart
systemctl --user restart neurareport-backend.service
systemctl --user restart neurareport-frontend.service

# Stop / Start
systemctl --user stop neurareport-backend.service neurareport-frontend.service
systemctl --user start neurareport-backend.service neurareport-frontend.service

# View logs
journalctl --user -u neurareport-backend.service -f
journalctl --user -u neurareport-frontend.service -f
```

### Redeployment

```bash
# 1. Stop services
systemctl --user stop neurareport-backend.service neurareport-frontend.service

# 2. Rebuild frontend
cd /home/rohith/desktop/NeuraReport/frontend
npm run build

# 3. Sync to prodo
cd /home/rohith/desktop/NeuraReport
cp backend/api.py backend/requirements.txt prodo/backend/
rm -rf prodo/backend/app prodo/backend/legacy prodo/backend/engine
cp -r backend/app backend/legacy backend/engine prodo/backend/
rm -rf prodo/frontend/dist prodo/frontend/assets
cp -r frontend/dist prodo/frontend/dist
cp frontend/dist/index.html prodo/frontend/
cp -r frontend/dist/assets prodo/frontend/assets

# 4. Install any new dependencies
source prodo/backend/.venv/bin/activate && pip install -r prodo/backend/requirements.txt -q

# 5. Restart
systemctl --user start neurareport-backend.service neurareport-frontend.service
```

### Health Checks

```bash
# Backend health
curl -s http://127.0.0.1:9070/health | python3 -m json.tool

# Frontend reachable
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9071/

# Templates API
curl -s http://127.0.0.1:9070/templates | python3 -m json.tool | head -20

# Tailscale access
curl -s http://100.90.185.31:9070/health
```

### Database Backup

```bash
cp /home/rohith/desktop/NeuraReport/prodo/backend/state/*.db /path/to/backup/
```

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (status, timestamp) |
| `GET` | `/templates` | List all templates |
| `POST` | `/templates/verify` | Upload & verify PDF template (NDJSON stream) |
| `POST` | `/templates/{id}/mapping/preview` | Generate mapping preview |
| `POST` | `/templates/{id}/mapping/approve` | Approve mapping & build contract (NDJSON stream) |
| `POST` | `/reports/generate` | Generate report from approved template |
| `GET` | `/connections` | List data connections |
| `GET` | `/jobs` | List background jobs |
| `GET` | `/state/bootstrap` | Initial state payload (connections, templates, last-used) |

### Extended APIs

| Category | Key Endpoints |
|----------|--------------|
| **Agents** | `GET /api/v2/agents/tasks`, `POST /api/v2/agents/tasks` |
| **Analytics** | `POST /api/analyze/enhanced` |
| **Connectors** | `POST /api/connectors/test`, `GET /api/connectors` |
| **Dashboards** | `GET /api/dashboards`, `POST /api/dashboards` |
| **Documents** | `GET /api/documents`, `POST /api/documents` |
| **DocQA** | `POST /api/docqa/ask` |
| **Enrichment** | `POST /api/enrichment/enrich` |
| **Federation** | `POST /api/federation/query` |
| **Ingestion** | `POST /api/ingestion/ingest` |
| **Knowledge** | `GET /api/knowledge/documents`, `POST /api/knowledge/search` |
| **NL2SQL** | `POST /api/nl2sql/generate` |
| **Search** | `GET /api/search` |
| **Synthesis** | `POST /api/synthesis/generate` |
| **Visualization** | `GET /api/visualization/charts` |
| **Workflows** | `GET /api/workflows`, `POST /api/workflows` |

Full interactive docs available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEURA_DEBUG` | `false` | Bypasses JWT secret requirement for local dev |
| `NEURA_JWT_SECRET` | — | JWT signing secret (**required in production**) |
| `NEURA_ALLOW_MISSING_OPENAI` | `false` | Allow running without OpenAI key (Claude CLI is primary) |
| `NEURA_USE_DATAFRAME_PIPELINE` | `false` | Enable pandas DataFrame pipeline instead of SQL/DuckDB |
| `NEURA_CORS_ORIGINS` | `[]` | Explicit CORS origins (JSON array) |
| `NEURA_CORS_ORIGIN_REGEX` | — | Regex pattern for CORS origin matching |
| `UPLOAD_ROOT` | `backend/uploads` | File upload directory |
| `EXCEL_UPLOAD_ROOT` | `backend/uploads_excel` | Excel upload directory |
| `NEURA_STATE_DIR` | `backend/state` | SQLite state store directory |
| `NEURA_ERROR_LOG` | — | Path for error-only log file |
| `NEURA_LLM_LOG` | — | Path for LLM interaction logs |
| `NEURA_MAIL_HOST` | — | SMTP host for email delivery |
| `NEURA_MAIL_PORT` | — | SMTP port |
| `NEURA_MAIL_SENDER` | — | Sender email address |

### Production Config Files

| File | Purpose |
|------|---------|
| `prodo/config/ports.env` | `BACKEND_PORT=9070`, `FRONTEND_PORT=9071` |
| `prodo/config/deployment.env` | Deployment metadata and timestamps |
| `prodo/backend/.env` | Backend environment variables (secrets, paths, CORS) |

## Logging & Observability

### Log Files (Production)

| Log | Path | Content |
|-----|------|---------|
| Backend | `prodo/logs/backend.log` | All backend stdout |
| Backend Errors | `prodo/logs/backend.error.log` | Backend stderr |
| Backend Errors Only | `prodo/logs/backend.only-errors.log` | Filtered error-level entries |
| Frontend | `prodo/logs/frontend.log` | HTTP server access log |
| LLM | `prodo/logs/llm.log` | All LLM request/response logs |

### Structured Logging

- All API responses include `X-Correlation-ID` for request tracing
- Log events are structured: `request_start`, `request_complete`, `verify_template_stage`, etc.
- Enable raw LLM dumps via `LLM_RAW_OUTPUT_PATH` (defaults to `llm_raw_outputs.md`)

### UX Governance

All mutating API requests must include intent headers:
- `X-Intent-Id` — Unique intent identifier
- `X-Intent-Type` — Intent category
- `X-Intent-Label` — Human-readable intent description

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check `prodo/logs/backend.error.log`. Ensure `.env` has valid `JWT_SECRET` |
| Frontend 404 on page refresh | The `--proxy` flag on http-server handles SPA fallback routing |
| Port conflicts | Edit `prodo/config/ports.env` and `prodo/backend/.env`, then restart |
| Module import errors | Ensure uvicorn runs from `prodo/` (the `WorkingDirectory` in the service file) |
| Claude CLI not found | Ensure `~/.local/bin/claude` exists and is on PATH |
| CORS errors | Add the frontend origin to `NEURA_CORS_ORIGINS` in `prodo/backend/.env` |
| Database locked | Stop duplicate backend processes; SQLite allows one writer at a time |
| High memory usage | Backend uses ~470MB at steady state; monitor with `systemctl --user status` |

### Uninstall

```bash
systemctl --user stop neurareport-backend.service neurareport-frontend.service
systemctl --user disable neurareport-backend.service neurareport-frontend.service
rm ~/.config/systemd/user/neurareport-backend.service
rm ~/.config/systemd/user/neurareport-frontend.service
systemctl --user daemon-reload
rm -rf /home/rohith/desktop/NeuraReport/prodo
```

## Additional Documentation

| Document | Description |
|----------|-------------|
| `FEATURES.md` | Complete feature inventory (150+ features) |
| `docs/product/requirements.md` | Product requirements and scope |
| `docs/product/immediate-requirements.md` | Detailed UI spec for the Setup flow |
| `docs/operations/CONFIG.md` | All environment variables and configuration |
| `docs/operations/PIPELINE_DOCUMENTATION.md` | Backend pipeline step-by-step breakdown |
| `docs/operations/RELEASE_NOTES.md` | Latest release summary and rollback notes |
| `docs/architecture/ARCHITECTURE_GOVERNANCE.md` | Structural rules and contribution contract |
| `docs/API_REFERENCE.md` | Full API endpoint reference (35 route modules) |
| `prodo/README.md` | Production deployment operations guide |
