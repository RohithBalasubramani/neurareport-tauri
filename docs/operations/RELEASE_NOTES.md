# Release Notes

## 2026-02-10 - Phase 9: Cross-Page Data Sharing, LLM Simplification & AI QA Agent

### Highlights
- New cross-page data sharing system enabling seamless data transfer between all feature pages.
- Simplified LLM provider configuration — Claude Code CLI is now the sole primary provider; removed legacy OpenAI-first complexity from providers and config.
- Enhanced AI agent brain with expanded capabilities for the E2E testing harness.
- Published `@neurareport/ai-qa-agent` as a standalone, framework-agnostic AI testing package.
- Updated `.gitignore` for connection dumps, nested node_modules, test artifacts, and temp files.

### Backend
- Simplified `llm/providers.py` and `llm/config.py`, removing ~1,500 lines of multi-provider boilerplate in favour of Claude Code CLI as the default path.
- Updated `llm/client.py` and `utils/llm.py` to use the streamlined provider configuration.
- Updated agent services (`base_agent.py`, `research_agent.py`, `service.py`) with improved task handling and error recovery.
- Updated routes (`agents.py`, `ai.py`, `health.py`, `ingestion.py`) with refined LLM integration.
- Updated enrichment, federation, synthesis, docqa, and chart services for simplified LLM calls.
- Updated `.env.example` to document Claude Code CLI as the primary LLM provider.

### Frontend
- Added reusable cross-page components: `ConnectionSelector`, `ImportFromMenu`, `SendToMenu`, `TemplateSelector`.
- Added shared hooks: `useCrossPageActions`, `useIncomingTransfer`, `useSharedData`.
- Added `crossPageStore` (Zustand) with `crossPageTypes.js` constants for type-safe transfers.
- Updated all 20+ page containers to integrate cross-page actions (SendTo/ImportFrom menus).
- Updated `Sidebar`, `GlobalSearch`, `WizardLayout`, and `stores/index.js` with cross-page support.

### Packages
- Upgraded `@neurareport/ai-qa-agent` with expanded agent brain (~550 lines of new reasoning logic).
- Added UI framework presets, persona modifiers, QA profiles, and structured failure categorization.
- Published as standalone npm package with CJS/ESM dual exports.

### Testing
- Updated AI agent E2E test specs and browser agent with expanded scenario support.
- Added new E2E specs: `e2e-comprehensive.spec.ts`, `verify-upload.spec.ts`, `water-bill-e2e.spec.ts`.
- Updated agent service tests to match new LLM provider configuration.

### Operations
- Updated `.gitignore` to exclude `conns.json`, `conns2.json`, `frontend.env`, nested `node_modules/`, `test-screenshots/`, `templates_check.json`, and temp template files.

### Documentation
- Updated root `README.md`, `backend/README.md`, `frontend/README.md` to reflect Claude Code CLI as primary LLM, React 19, 33 pages, and new cross-page features.
- Updated `FEATURES.md` with cross-page data sharing (Section 50), AI QA Agent (Section 51), and revised feature counts (210+).
- Updated `backend/requirements.txt` with Claude Code CLI documentation.

### Upgrade Notes
1. Claude Code CLI must be installed and authenticated (`claude --version`). No OpenAI API key is required for default operation.
2. Run `pip install -r backend/requirements.txt` to update backend dependencies.
3. Run `npm install` in `frontend/` for updated frontend dependencies.

---

## 2026-02-01 - Phase 8: Hardening, Documentation & Governance

### Highlights
- Comprehensive security hardening across middleware, routes, and services.
- Architecture violation count reduced from 66 to 0 with enforced import boundaries.
- Expanded test coverage with property-based testing (Hypothesis), chaos simulation, connector security, and 20 Playwright e2e integration specs.
- Full documentation overhaul: updated README files, created API reference, expanded frontend and backend docs.
- Cleaned up git tracking: removed large binaries (.fig), generated images, sample data, and analysis artifacts from version control.

### Backend
- Hardened all 35 route modules with improved input validation, error handling, and consistent error envelopes.
- Created service re-export modules (`errors.py`, `job_status.py`, `validation.py`) to enforce layered architecture.
- Updated schemas for connections, enrichment, federation, NL2SQL, and synthesis with tighter validation.
- Improved webhook service with retry logic and error classification.
- Strengthened enrichment cache with TTL-based stats.
- Added soft delete utilities and SQL safety guards.
- Updated middleware with enhanced rate limiting and idempotency handling.
- UX governance guards updated for frontend/backend contract alignment.

### Frontend
- Refactored API client modules (dashboards, documents, export, ingestion, knowledge, search, spreadsheets, visualization, workflows) for consistency.
- Updated Zustand stores (connectionStore, designStore, spreadsheetStore, useAppStore) with improved state management.
- Hardened hooks (useFormErrorFocus, useJobs, useUploadProgress) and containers.
- Added OAuthButton improvements for connectors.
- Added 20 Playwright e2e integration specs covering all major features (dashboard, connections, connectors, templates, reports, jobs, schedules, query builder, documents, spreadsheets, enrichment, federation, synthesis, docqa, workflows, dashboards, knowledge, design/visualization, agents/ingestion, settings).
- Added phase verification specs and audit specs.

### Operations
- Architecture enforcement: `enforce_backend_arch.py` now checks all backend sub-layer import rules.
- 3 documented architecture exceptions (ARCH-EXC-001 through ARCH-EXC-003) with expiration plans.
- Git hygiene: added `.fig`, generated images, analysis artifacts, sample data to `.gitignore` and removed from tracking.
- Updated CI workflow to run architecture checks on every push/PR.

### Documentation
- Updated root `README.md` with current repository layout, new endpoints, and documentation links.
- Expanded `frontend/README.md` with all 28 page modules, state management, API clients, folder structure, and testing guide.
- Expanded `backend/README.md` with all 35 route modules, 40+ services, security middleware, and test commands.
- Updated `ARCHITECTURE_GOVERNANCE.md` with migration log and service re-export pattern.
- Created `docs/API_REFERENCE.md` with endpoint reference for all route modules.
- Added Phase 8 release notes.

### Upgrade Notes
1. Reinstall backend dependencies: `pip install -r backend/requirements.txt`.
2. Run `npm install` in `frontend/` for updated dev dependencies.
3. Architecture enforcement is now stricter — run `python scripts/architecture/enforce_backend_arch.py` to verify compliance before committing.

---

## 2025-10-23 - Phase 6: End-to-End Integration

### Highlights
- Completed the full verification -> mapping -> contract -> generator -> run pipeline with streaming NDJSON updates and per-stage manifests.
- Added auto-mapping Call 3, corrections Call 3.5, contract builder (Call 4), and generator asset builder (Call 5) with cache-aware re-entry points.
- State store now tracks mapping keys, generator metadata, and last-used selections, enabling the React client to hydrate instantly.
- Documentation overhaul: updated `docs/product/requirements.md`, `docs/operations/CONFIG.md`, `docs/product/immediate-requirements.md`, `docs/operations/PIPELINE_DOCUMENTATION.md`, and this README to reflect the implemented stack.

### Backend
- `/templates/verify` streams stage events, supports size limits via `NEURA_MAX_VERIFY_PDF_BYTES`, and records panel renders plus schema artifacts.
- `/templates/{id}/mapping/preview` produces `mapping_step3.json`, `constant_replacements.json`, and updated HTML with cache keys.
- `/templates/{id}/mapping/approve` persists `mapping_pdf_labels.json`, builds contracts and generator assets, renders thumbnails, and updates manifests in one streaming response.
- `/reports/discover` and `/reports/run` expose the new discovery/fill pipeline backed by the `ReportGenerate.fill_and_print` engine.
- Template-level locking prevents double submissions; manifests capture SHA lineage for regression tooling.

### Frontend
- Setup page redesigned with 25% navigation rail and 75% work area, matching the spec in `docs/product/immediate-requirements.md`.
- Streaming progress bars cover verification, mapping, approval, and generator steps with toast feedback on every action.
- Templates view renders thumbnail cards with tags, output badges, and quick download affordances; state hydrates from `/state/bootstrap`.

### Operations
- New environment variables: `NEURA_MAX_VERIFY_PDF_BYTES`, `MAX_FIX_PASSES`, `VERIFY_FIX_HTML_ENABLED`, `LLM_RAW_OUTPUT_PATH`, and expanded health-check configuration (`NEURA_HEALTH_EXTERNAL_HEAD`).
- `scripts/verify_pipeline.py` and `scripts/artifact_stats.py` updated to validate new manifest entries and generator outputs.
- `llm_raw_outputs.md` logging can be redirected via `LLM_RAW_OUTPUT_PATH` for compliance-friendly retention.

### Upgrade Notes
1. Reinstall backend dependencies to ensure Playwright, OpenCV, and Skimage versions match (`pip install -r backend/requirements.txt`).
2. Supply `NEURA_STATE_SECRET` in environments that need stable encryption keys before upgrading.
3. If existing templates lack `mapping_pdf_labels.json`, run `/templates/{id}/mapping/approve` once to populate the new artifacts.

### Rollback Guide
1. `git reset --hard <previous_commit>` to revert code changes.
2. Reinstall dependencies if versions changed.
3. Remove newly created manifest entries (`mapping_pdf_labels.json`, generator bundles) if the previous release cannot read them.
4. Point the frontend back to the prior API build (`VITE_API_BASE_URL`) if rolling back only the backend.

---

## 2025-09-30 - Phase 5: Hardening

### Highlights
- Centralised configuration loader with version/commit logging and environment validation.
- `/healthz` and `/readyz` endpoints perform filesystem write checks, clock skew detection, and optional external HEAD probes.
- Standardised security headers, manifest APIs, and correlation-aware logging across all routes.
- Added HTML sanitisation regression tests, per-template locking coverage, and manifest-driven artifact checks (`scripts/artifact_stats.py`).
- CI workflow runs pre-commit, pytest, pipeline verifier, and artifact stats with the configured thresholds.

### Frontend Impact
- Mapping and preview flows revalidate manifests after approvals to guarantee fresh HTML and PNG assets.

### Rollback Guide
1. `git reset --hard <previous_commit>` on the backend.
2. `pip install -r backend/requirements.txt` if dependency versions changed.
3. Redeploy the previous backend build; frontend only needs an updated API target.
