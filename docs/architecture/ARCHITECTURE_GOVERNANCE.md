# Architecture Governance

This document defines enforced structural rules for the NeuraReport codebase. These rules are enforced by linting and CI. Any change that violates them must update the enforcement config explicitly.

## Frontend folder responsibilities (frontend/src)

Only the folders below are allowed for JS/JSX source code. Any new JS/JSX files must live under one of these folders or at the src root (app files).

- app (src/*.js[x]): entry composition (App, main, theme, setupTests). This layer wires the app together.
- pages/: route-level composition and wiring.
- features/: feature modules and domain-facing UI logic.
- layouts/: structural shells used by pages.
- navigation/: navigation components used by layouts/pages.
- components/: reusable UI building blocks.
- ui/: design primitives (no domain logic).
- hooks/: reusable logic hooks.
- stores/: state containers.
- api/: API client boundary.
- utils/: shared helpers.
- content/: static content modules.
- assets/: static assets modules.

## Backend folder responsibilities (backend)

Only the folders below are allowed to contain Python code.

- backend/app/: HTTP API layer, orchestration, and app-facing services.
- backend/engine/: current pipeline engine and domain logic.
- backend/legacy/: legacy pipeline engine and compatibility layer.
- backend/tests/: test suite.
- backend/scripts/: operational scripts.
- backend/api.py: legacy app entrypoint.

## Backend app sub-layers (backend/app)

Required sub-layers:

- api/: HTTP routing only.
- application/: use-cases (commands/queries) orchestrating domain + ports.
- domain/: core business logic (pure rules).
- infrastructure/: adapters for DB/files/external services (no HTTP).
- services/: orchestration, workflows, integrations.
- repositories/: persistence & data access (if present).
- schemas/: DTOs, validation, contracts.
- utils/: pure helpers only (no business logic).

Placement rule:
- Any Python file under backend/app must live in one of the sub-layer folders above (except backend/app/__init__.py).

Import rules:
- api/ MAY import: application, services, schemas. MUST NOT import: domain, repositories, utils, infrastructure.
- application/ MAY import: domain, repositories, infrastructure, utils, schemas. MUST NOT import: api.
- services/ MAY import: domain, repositories, utils, schemas. MUST NOT import: api.
- domain/ MAY import: utils only. MUST NOT import: api, services, repositories, schemas.
- infrastructure/ MAY import: domain, repositories, utils, schemas, application (ports). MUST NOT import: api.
- repositories/ MAY import: domain, utils. MUST NOT import: api, services.
- schemas/ MAY import: utils only. MUST NOT import: api, services, domain, repositories.
- utils/ MUST NOT import: api, services, domain, repositories, schemas.

## Dependency boundaries (enforced)

### Frontend (ESLint boundaries)

Allowed imports by source type:

- app -> app, pages, features, layouts, navigation, components, ui, hooks, stores, api, utils, content, assets
- pages -> features, layouts, navigation, components, ui, hooks, stores, api, utils, content, assets
- features -> features, components, ui, hooks, stores, api, utils, content, assets
- layouts -> layouts, navigation, components, ui, hooks, stores, api, utils, content, assets
- navigation -> navigation, components, ui, hooks, stores, api, utils, content, assets
- components -> components, ui, hooks, utils, content, assets
- ui -> ui, utils, assets
- hooks -> hooks, stores, api, utils
- stores -> stores, api, utils
- api -> api, utils
- utils -> utils, api
- content -> content, assets, utils
- assets -> assets

Notes:
- UI layers (components/ui) cannot import features/pages/layouts/navigation/stores/api.
- Network access is constrained to api, hooks, stores, features, pages, layouts, navigation.
- New folders under frontend/src are not allowed unless added to the boundary list.

### Backend (AST import checks)

- Only backend/app/api/* and backend/tests/* may import backend.app.api.* (tests need router access for testing)
- backend/engine/* must not import backend.app.*
- backend/engine/* must not import backend.legacy.*
- backend/legacy/* must not import backend.engine.*
- backend/app/api/* must not import backend.engine.* (engine is domain logic, accessed via application/services)
  - Exception: `backend/app/api/routes/legacy.py` (ARCH-EXC-001 legacy compat)
- backend/app/* may only import backend.legacy.* from backend/app/api/routes/* or backend/api.py
- Python files under backend/ must live in app/, engine/, legacy/, tests/, scripts/ or backend/api.py
- backend/app sub-layer placement and import rules (see Backend app sub-layers section)

## Dependency boundary diagram (text)

Frontend layers:
app
  -> pages -> features -> components -> ui
  -> layouts -> navigation -> components -> ui
  -> hooks -> stores -> api -> utils
  -> content/assets (read-only)

Backend layers:
backend/engine (isolated; no app/legacy imports)
backend/legacy -> backend/app (allowed)
backend/app/api/routes/legacy.py -> backend/engine (single exception)
backend/app/api/routes/* and backend/api.py -> backend/legacy (compat entrypoints only)

## Automated enforcement

Frontend:
- ESLint boundaries rules in frontend/eslint.config.js enforce the folder map and allowed imports.
- Violations fail npm run lint and the frontend CI job.

Backend:
- scripts/architecture/enforce_backend_arch.py parses Python AST imports and enforces backend boundaries and allowed paths.
- scripts/architecture/architecture_exceptions.json is the central exception allowlist for backend architecture rules.
- Violations fail the backend CI job.

CI:
- .github/workflows/ci.yml runs the backend architecture check and frontend lint on every push and PR.

## Contribution contract (checklist)

- New page: add under frontend/src/pages and wire in src/App.jsx; do not import from other pages.
- New feature logic: add under frontend/src/features; compose in pages/layouts only.
- New shared UI: add under frontend/src/components or frontend/src/ui (primitives only).
- New hook: add under frontend/src/hooks; only depend on hooks/stores/api/utils.
- New state: add under frontend/src/stores; only depend on stores/api/utils.
- New API client or endpoint wrapper: add under frontend/src/api; only depend on utils.
- Backend API route: add under backend/app/api/routes; it may call backend.app services and may call backend.legacy only via the allowed compat entrypoints.
- Backend pipeline/domain logic: add under backend/engine; do not import backend.app or backend.legacy.
- Legacy-only changes: add under backend/legacy; do not import backend.engine.

## Violation handling

- If a rule is broken, CI fails; the change cannot merge.
- Backend exceptions require:
  - an entry in scripts/architecture/architecture_exceptions.json
  - an inline code comment with the exception ID (ARCH-EXC-###) in the affected file
  - a filled-out exception doc at docs/architecture/exceptions/ARCH-EXC-###.md using ARCHITECTURE_EXCEPTION_TEMPLATE.md
- Frontend exceptions require updating frontend/eslint.config.js.
- Exceptions must be removed by the next planned refactor touching the affected area.

## Service-layer re-export pattern

When the api layer needs access to types or functions from utils or repositories, they MUST be re-exported through a services module. This preserves the api → services → utils/repositories dependency chain.

Existing re-export modules:
- `services/errors.py` → re-exports `AppError`, `DomainError` from `utils/errors.py`
- `services/job_status.py` → re-exports job status constants and functions from `utils/job_status.py`
- `services/validation.py` → re-exports `is_read_only_sql`, `validate_path_safety`, etc. from `utils/validation.py`
- `services/state_access.py` → re-exports `state_store` and helpers from `repositories/state.py`
- `services/agents/__init__.py` → re-exports `AgentTaskStatus`, `TaskConflictError`, `TaskNotFoundError` from `repositories/agent_tasks`

## Migration log

### 2026-01-31: Architecture violation elimination (66 → 0)

**APP-LAYER-IMPORT violations fixed (9):**
- `api/error_handlers.py`: Changed `utils.errors.AppError` → `services.errors.AppError`
- `api/routes/agents_v2.py` (×3): Changed `repositories.agent_tasks.*` → `services.agents.*`
- `api/routes/analytics.py`: Changed `utils.job_status.*` → `services.job_status.*`
- `api/routes/jobs.py`: Changed `utils.job_status.*` → `services.job_status.*`
- `api/routes/connectors.py`: Changed `utils.validation.*` → `services.validation.*`, `repositories.state.*` → `services.state_access.*`
- `api/routes/documents.py`: Changed `utils.validation.*` → `services.validation.*`

**APP-API-IMPORT-SCOPE violations fixed (57):**
- Enforcer updated to exempt `backend/tests/` — tests must import routers/middleware to test them

**Service re-export modules created:**
- `backend/app/services/errors.py` (new)
- `backend/app/services/job_status.py` (new)
- `backend/app/services/validation.py` (updated with `is_read_only_sql`, `validate_path_safety`)
- `backend/app/services/agents/__init__.py` (updated with `AgentTaskStatus`, `TaskConflictError`, `TaskNotFoundError`)

**Remaining intentional exceptions (3):**
- ARCH-EXC-001: `legacy.py` → `backend.engine` (legacy compat, expires on v1 retirement)
- ARCH-EXC-002: `backend/api.py` → `backend.app.api` (entrypoint, expires on api.py retirement)
- ARCH-EXC-003: `feature_routes.py` → `backend.app.api.generate.*` (legacy compat, expires on migration)

## Do-not list

- Do not add new frontend/src folders without updating boundaries.
- Do not import backend.engine from backend.app (except backend/app/api/routes/legacy.py).
- Do not import backend.legacy from backend.app outside the allowed compat entrypoints.
- Do not import backend.engine from backend.legacy.
- Do not import feature/page logic into components or ui primitives.
- Do not create new backend Python files outside app/, engine/, legacy/, tests/, scripts/ or backend/api.py.
