# NeuraReport Architecture + Feature-Unlock + SOTA Report

**Report Date:** 2026-02-15

## Scope / Evidence (What I Actually Checked)

- UI surface inventory: `MASTER-ACTION-INVENTORY.json` (generated 2026-02-01T11:55:49Z): 29 routes, 2534 actions.
- UI audit writeup: `AUDIT-REPORT.md` (TDZ crash fixes + audit methodology).
- Backend architecture rules: `ARCHITECTURE_GOVERNANCE.md` + enforcer `enforce_backend_arch.py`.
- Backend size/shape: `backend_inventory_2026-01-23.md` + direct file scans.
- API surface: `API_REFERENCE.md` + `backend/app/api/routes/*`.
- CI reality check: `ci.yml` + `verify_pipeline.py`.

## 1) Executive Summary (What's Strong vs What's Missing)

### Strong foundations already present

- Clear intended boundaries (frontend layer map + backend `api/services/domain/repositories/schemas/utils`) and automated enforcement (frontend ESLint boundaries, backend AST import enforcer).
- End-to-end UI discovery/execution approach exists (the audit harness is genuinely useful to keep 2500+ UI actions from regressing).
- Backend has broad feature coverage (agents, templates, reports, connectors, docs, enrichment, federation, spreadsheets, etc.) and a documented API reference.

### What the architecture currently lacks (blocking "SOTA" + full feature unlock)

- A single, clean source tree: `prodo/` is a tracked production deployment snapshot and it breaks architectural enforcement (and will keep breaking it). This is the biggest structural hygiene issue.
- A real domain layer: `backend/app/domain/` is effectively empty, so "business rules" live in giant services/repositories instead of being testable/composable.
- Durable workflow orchestration: job/report execution is split across multiple systems (legacy scheduler/executor patterns, engine orchestration, and Dramatiq worker tasks). This causes reliability gaps (retry/idempotency/cancel/progress) and duplicated logic.
- State management that scales: `store.py` is ~2680 LOC and acts as a multi-domain database. This is a long-term correctness and concurrency risk and makes distributed execution hard.
- Monolith modules ("god files"): report generation, PDF extraction, LLM client, frontend API client are all too large, too coupled, and hard to evolve safely.
- UI a11y/testability completeness: a large fraction of actions lack accessible naming and stable semantics, especially on high-action routes like `/documents` and `/design`.

## 2) Frontend: Full 29-Route / 2534-Action Coverage

### 2.1 Route Inventory (All audited routes + action counts)

From `MASTER-ACTION-INVENTORY.json`:

| Route | Actions |
|---|---:|
| `/` | 48 |
| `/activity` | 44 |
| `/agents` | 41 |
| `/analyze` | 46 |
| `/connections` | 204 |
| `/connectors` | 49 |
| `/dashboard-builder` | 33 |
| `/design` | 342 |
| `/docqa` | 59 |
| `/documents` | 136 |
| `/enrichment` | 57 |
| `/federation` | 4 |
| `/history` | 245 |
| `/ingestion` | 30 |
| `/jobs` | 240 |
| `/knowledge` | 42 |
| `/ops` | 149 |
| `/query` | 46 |
| `/reports` | 76 |
| `/schedules` | 37 |
| `/search` | 54 |
| `/settings` | 79 |
| `/spreadsheets` | 49 |
| `/stats` | 46 |
| `/summary` | 75 |
| `/synthesis` | 36 |
| `/templates` | 195 |
| `/visualization` | 38 |
| `/workflows` | 34 |

High-risk UI areas by sheer action volume: `/design` (342), `/history` (245), `/jobs` (240), `/connections` (204), `/templates` (195), `/ops` (149), `/documents` (136).

### 2.2 Action Quality (a11y + selector stability + taxonomy)

From the same inventory:

- Disabled actions: 19 (see list below)
- Type classification: unknown for 909 / 2534 actions (35.9%)
- Worst ratios: `/history` (63%), `/jobs` (62%), `/templates` (56%), `/connections` (56%)
- Accessible name coverage (practical a11y/testability signal):
  - Named via `ariaLabel`: 285
  - Named via text: 1524
  - Named via `href`: 27
  - No accessible name at all: 698 / 2534 (27.5%)
  - Worst ratios: `/documents` 106/136 (78%), `/design` 158/342 (46%), `/settings` 35/79 (44%)
- Icon-only buttons (no text + no `ariaLabel`): 253, concentrated in:
  - `/documents`: 102
  - `/design`: 101

What this means:

Your UI audit engine can "click everything", but maintaining this at SOTA quality requires semantic naming:

- For accessibility (screen readers, keyboard users)
- For testing stability (Playwright selectors that don't rely on `nth-of-type`)
- For product clarity (tooltips/labels match user intent)

### 2.3 Disabled Actions (All 19)

These were disabled in the audit's baseline state (often expected because prerequisites weren't met: no selection, empty table page, etc.):

- `/agents`: Run Research Agent
- `/connections`: Go to previous page
- `/enrichment`: Preview, Enrich All, Parse Data
- `/history`: Go to previous page, Go to next page
- `/jobs`: Go to previous page
- `/query`: Generate SQL
- `/reports`: Schedule, Generate Report, Find Batches
- `/search`: Search
- `/summary`: Add, Generate Summary, Queue in Background
- `/templates`: Go to previous page, Go to next page
- `/visualization`: Generate

Unlock requirement: don't just "enable the button"; ensure the UI provides:

- A clear prerequisite (selected template/connection/document)
- A reason string (tooltip or inline helper)
- A "fix it" action (e.g., "Select a connection" link)

## 3) Backend: Architecture, Gaps, and Concrete Violations

### 3.1 Intended Architecture (Already codified)

`ARCHITECTURE_GOVERNANCE.md` defines strict placement and import rules:

- `backend/app/api` can only depend on services + schemas
- services orchestrates domain/repositories/utils
- domain is pure business logic
- engine should be isolated from app/legacy imports (and app should not import engine except one legacy compat route)

This is the right direction.

### 3.2 Current Enforcement Status (Not Green)

Running `enforce_backend_arch.py` currently reports violations, including:

- `report_tasks.py`
  - imports `backend.engine.pipelines.report_pipeline` (rule: app must not import engine)
- Many violations under `prodo/backend/...`
  - rule: only `backend/app/api/*` may import `backend.app.api.*`
  - `prodo/` is a deployment snapshot, but it's being scanned as if it's source.

Practical impact: backend CI will fail on "Enforce backend architecture" until `prodo/` is excluded or removed, and the worker/report pipeline boundary is fixed.

### 3.3 "God Files" / Hotspots (Where architecture debt concentrates)

Measured LOC (indicative of coupling + refactor need):

| File | LOC |
|---|---:|
| `store.py` | 2680 |
| `ReportGenerate.py` | 2104 |
| `pdf_extractors.py` | 1661 |
| `client.py` | 1205 |
| `ContractBuilderV2.py` | 872 |
| `client.js` | 3293 |

These files aren't "bad" by themselves, but they become the place where every new feature gets shoved. That blocks SOTA iteration speed.

### 3.4 Reliability Red Flags (Correctness under load)

- Unsafe cancellation patterns exist (thread exception injection via `PyThreadState_SetAsyncExc`) in:
  - `report_service.py`
  - `executor.py`
- Sync/async boundary leaks (`asyncio.run(...)`) appear in multiple core paths (template verification, report generation, pipeline execution, background tasks). This typically causes:
  - hard-to-debug deadlocks
  - threadpool exhaustion
  - cancellation that doesn't work

### 3.5 Concrete "Feature Unlock" Bug in Worker Report Task

`report_tasks.py` calls:

```python
state_store.record_job_step(job_id, "generate", "Starting report generation", status="running")
```

But `record_job_step` is keyword-only after name (signature uses `*`), so this will throw a `TypeError` at runtime. This is an immediate blocker for "async job processing for report batches".

## 4) "Unlock All Features Fully": What's Actually Blocking End-to-End

### Blocker A: CI + Reproducibility is currently broken

CI runs:

```bash
python scripts/verify_pipeline.py --template-id ad6a0b1f-... --uploads-root samples/uploads
```

But `samples/uploads/` contains only `.gitkeep`, and `verify_pipeline.py` requires the template directory to exist. So pipeline verification is not reproducible as-is.

Unlock options:

- Commit a deterministic fixture under `samples/uploads/<template_uuid>/...` that satisfies `verify_pipeline.py`.
- Change CI to generate those artifacts during the workflow (more expensive, but "true integration").
- Make the step optional/skipped when fixtures are absent (least ideal: reduces trust).

### Blocker B: Architecture enforcement includes deployment artifacts (`prodo/`)

Because `prodo/` is tracked and contains Python code that imports app modules, the architecture enforcer flags it. This prevents "architecture governance" from being enforceable in CI.

Unlock options:

- Move `prodo/` out of git entirely (preferred).
- Keep it, but update the enforcer to ignore it (second best).
- Treat `prodo/` as a separate package with its own rules (most complex).

### Blocker C: Workflow orchestration is fragmented

You have multiple overlapping ways to "run a report/job":

- legacy service patterns
- engine orchestration
- Dramatiq worker tasks

Unlock requirement: pick one durable orchestration path (Dramatiq+Redis is already in tree) and make everything call that, with:

- idempotency keys
- retry policy
- progress events (NDJSON or SSE)
- cancellation that is cooperative, not unsafe thread injection
- a single job-state model

### Blocker D: UI actions aren't "feature complete" in an empty-state

Your audit discovered disabled actions that are likely correct in an empty state, but feature unlock means:

- seed demo state (templates + connection + docs) so the entire UI can be exercised end-to-end
- ensure every critical flow has a "happy path" without manual DB/state editing

## 5) What "SOTA" Looks Like Here (Concrete, Repo-Specific)

### SOTA backend (for this product)

- Durable workflows: one orchestration system, step-level state, retries, DLQ strategy, resumability.
- State as data: move from monolithic JSON "state store" toward a real DB schema (even SQLite with proper tables is a big step).
- Pipeline as a graph: report/template pipelines decomposed into steps with typed inputs/outputs, with manifest + checksums (you already have manifests; make them first-class).
- LLM architecture: provider abstraction + structured outputs + prompt registry versioning + eval harness (golden tests) + caching/rate limiting.
- Observability everywhere: OpenTelemetry traces across API + workers, plus correlation IDs across streaming events.

### SOTA frontend (for 2534 actions)

- Accessible names for all interactive elements, especially icon-only controls.
- Stable selectors: prefer `data-testid` for automation and `aria-label`/semantic HTML for a11y.
- API contract discipline: generate a typed client from a shared API contract, and run contract tests that map UI flows to API endpoints.
- Modular API client: split `client.js` by domain (templates/reports/jobs/docs/etc).

## 6) Priority Roadmap (Shortest Path to "Everything Works" + SOTA Trajectory)

### P0 (Get Green + Stop Bleeding) - 1 to 3 days

- Fix `prodo/` vs enforcement (exclude or remove from git scan).
- Fix worker report task correctness + architecture boundary (and remove engine import or formalize the boundary via services).
- Fix CI pipeline verification by adding deterministic fixtures or generating artifacts in CI.

### P1 (Unlock Core Flows) - 1 to 2 weeks

- End-to-end "golden path" fixtures: a template + connection + sample DB + document set.
- Convert the 19 "disabled" audit actions into explicitly reasoned states (tooltips + prerequisites).
- Add a11y naming for `/documents` and `/design` first (they're the worst offenders).

### P2 (Make It SOTA) - 1 to 2 months

- Break up `StateStore` into domain stores or real DB tables.
- Break up report generation into step modules with typed contracts.
- Add evaluation harness for LLM features (agents, NL2SQL, docAI) and run it in CI.

## 7) Special Note: HMWSSB Scripts (Current State)

`hmwssb_billing.py` + `hmwssb_report.txt` are standalone (SQLite + hardcoded sample transaction) and `register_hmwssb.py` writes directly into internal state store internals. Architecturally, this is a prototype, not a product feature.

To make it "real" (SOTA-level):

- model it as a first-class integration/connector + ingestion pipeline
- store transactions in the same persistence layer as the rest of the app (not a sidecar DB file)
- expose it via `backend/app/api/routes/*` and a UI surface (or background job + report artifact pipeline)
