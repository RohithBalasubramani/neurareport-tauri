# NeuraReport Requirements

## Product Summary

- Desktop-first report automation assistant that packages a FastAPI backend with a React/Tauri shell.
- Primary use case: ingest PDF report templates, map them to SQL data, and render scheduled batches to PDF/HTML with LLM assistance.
- Operates offline by default; remote LLM calls are only executed when an operator provides credentials.

## Goals

- Deliver a single-install desktop experience that bundles the UI and Python services.
- Support a repeatable template lifecycle: verify -> map -> approve -> generate -> download.
- Produce audit-friendly artifacts (HTML, JSON manifests, mapping DSL, contract metadata, run outputs).
- Provide resilient automation with retryable LLM stages, locking, caching, and manifest tracking.
- Keep operator UX approachable through guided flows, real-time feedback, and safe defaults.

## Non-Goals

- Multi-tenant SaaS hosting or cloud tenancy isolation.
- Real-time dashboards or ad-hoc exploratory analytics.
- Arbitrary machine learning beyond template understanding and validation.
- Handling of write-heavy workloads or destructive DML against source databases.

## Personas & Primary Flows

### Operator

1. Connect a SQL data source (SQLite today; other drivers planned).
2. Upload a template PDF and monitor the verification stream (LLM Call 1/2 produce HTML and schema).
3. Trigger auto-mapping, review corrections, and approve mappings (LLM Call 3/3.5).
4. Approve the template to produce contract and generator assets (LLM Call 4/5).
5. Discover available batches for a date range and provide any key token overrides.
6. Run a batch, download PDF/HTML outputs, and archive manifests.
7. Consult logs and manifests when troubleshooting.

### Admin / Power User

- Configure environment secrets and defaults (OpenAI key, upload root, default DB).
- Maintain connection metadata, encrypted state keys, and artifact retention.
- Monitor health endpoints and system logs.

### Developer / Support

- Run diagnostic hooks (for example `NEURA_FAIL_AFTER_STEP`), capture `llm_raw_outputs.md`, and inspect manifests.
- Extend pipeline scripts or regression tests as part of delivery.

## Experience Requirements

### Desktop Shell

- Implemented with Tauri; launches the Python backend as a managed sidecar.
- Integrates with OS keychain to protect encrypted state (`NEURA_STATE_SECRET` overrides for reproducible keys).
- Must support Windows, macOS, and Linux with code-signed installers and delta updates (future automation).

### Frontend (React 18 + Vite)

- Single-page app with sticky global header (connection heartbeat, active setup step).
- Setup workspace uses a 25%/75% split between navigation and content (see `immediate-requirements.md` for layout details).
- Tabs: Connect, Upload & Verify, Run Reports.
- React Query manages server state; Zustand provides app-wide store.
- Streams NDJSON responses for verification, mapping approval, and generator runs; renders progress live.
- Toast notifications for every async action and disabled states until prerequisites succeed.
- Templates view renders a responsive card grid with thumbnails, tags, output badges, and quick download actions.
- Supports mock/offline mode via `VITE_USE_MOCK=true` and configurable API base through `VITE_API_BASE_URL`.

### Backend (FastAPI)

- Exposes endpoints:
  - `/health`, `/healthz`, `/readyz` (filesystem, clock, OpenAI, optional external HEAD).
  - `/connections` CRUD, `/connections/test`, `/connections/{id}/health`.
  - `/state/bootstrap`, `/state/last-used`.
  - `/templates/verify` (stream), `/templates/{id}/mapping/preview`, `/templates/{id}/mapping/corrections-preview`, `/templates/{id}/mapping/approve`, `/templates/{id}/keys/options`.
  - `/templates/{id}/generator-assets/v1`, `/templates/{id}/artifacts/{manifest|head}`.
  - `/reports/discover`, `/reports/run`.
- Static `/uploads/<template_id>/...` served with ETag, cache-control headers, and optional `download=1` disposition.
- All streaming endpoints emit JSON lines (`event: stage|result|error`) with correlation IDs.
- Per-template locks (`acquire_template_lock`) prevent concurrent mutations.

### AI & LLM Orchestration

- Call 1: `TemplateVerify.request_initial_html` converts reference PNG to HTML + schema JSON.
- Call 2: `TemplateVerify.request_fix_html` refines CSS and metrics when enabled.
- Call 3: `MappingInline.run_llm_call_3` inlines constants, emits mapping JSON, token samples, and prompt metadata.
- Call 3.5: `CorrectionsPreview.run_corrections_preview` applies operator edits and produces `page_summary.txt`.
- Call 4: `ContractBuilderV2.build_or_load_contract_v2` drafts the contract blueprint and overview.
- Call 5: `GeneratorAssetsV1.build_generator_assets_from_payload` generates SQL packs, params spec, and runtime bundle.
- Raw responses captured in `llm_raw_outputs.md` when `LLM_RAW_OUTPUT_PATH` is set.

## Template Lifecycle & Artifacts

- Each template owns `uploads/<template_id>/` containing:
  - `source.pdf`, `reference_pN.png`, `template_p1.html`, `schema_ext.json`, render previews.
  - `mapping_step3.json`, `constant_replacements.json`, `page_summary.txt` when available.
  - `mapping_pdf_labels.json` (approved mapping), `report_final.html`, `contract.json`, generator bundles, thumbnails.
  - `artifact_manifest.json` updated after every step with file hashes and input lineage.
- `state/state.json` stores encrypted connections, template metadata, generator status, and last-used selections.
- Mapping tokens tracked in `mapping_keys.json`; generator metadata persisted under the template record.

## Reporting Workflow

1. `/reports/discover` loads `contract.json`, queries the DB for batch IDs, row counts, and totals, and returns selectable batches.
2. `/reports/run` loads the contract, calls `fill_and_print`, writes `filled_<timestamp>.html`/`.pdf`, updates the manifest, and records run metadata.
3. The UI surfaces download links immediately and records recent artifacts for operator convenience.

## Security & Privacy

- Secrets encrypted with Fernet (auto-generated unless `NEURA_STATE_SECRET` supplied).
- No outbound network requests occur unless an OpenAI key is provided.
- PDF uploads and generated artifacts remain on local disk; manifests expose relative paths only.
- Health endpoints safe to expose; artifact retrieval requires local filesystem access.

## Observability & Performance

- Every request logs `X-Correlation-ID`, elapsed time, and structured metadata.
- Verification targets <8 seconds for 5-10 page PDFs on development hardware.
- Mapping + contract pipeline aims for <45 seconds; generator assets <10 seconds with warm caches.
- Streaming payloads include `elapsed_ms`; manifests capture `produced_at`.
- `ARTIFACT_WARN_BYTES` and `ARTIFACT_WARN_RENDER_MS` control CI guardrails.

## Failure Handling

- Atomic writes for JSON/HTML to avoid partial artifacts; rollbacks can be simulated through `NEURA_FAIL_AFTER_STEP`.
- Template-level locks prevent concurrent writes during mapping, approval, and run stages.
- LLM retries use exponential backoff (configurable via `OPENAI_MAX_ATTEMPTS`, `OPENAI_BACKOFF_*`).
- Cached artifacts reused when SHA256 signatures match prompt metadata.

## Future Enhancements

- Additional connectors (Postgres, MySQL, SQL Server) and credential vault integration.
- Scheduled runs, email/webhook delivery, and batch orchestration.
- Multi-page correction workflows and cross-template batch runs.
- CI-driven packaging and auto-updater channels for the desktop shell.
