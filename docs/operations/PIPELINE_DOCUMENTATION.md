# Pipeline Documentation

This document explains the end-to-end pipeline that powers the NeuraReport backend. Each numbered stage corresponds to a FastAPI endpoint or helper invoked by the React client.

## Overview

1. **Template Verification** (`POST /templates/verify`) - stream-driven ingestion of a PDF page that produces HTML, schema, and previews (LLM Calls 1-2).
2. **Mapping Preview** (`POST /templates/{id}/mapping/preview`) - auto-mapping using the DB catalog (LLM Call 3).
3. **Corrections Preview** (`POST /templates/{id}/mapping/corrections-preview`) - optional inline edits and narrative summary (LLM Call 3.5).
4. **Mapping Approval** (`POST /templates/{id}/mapping/approve`) - persists the mapping, drafts the contract, and builds generator assets (LLM Calls 4-5).
5. **Generator Assets (direct)** (`POST /templates/{id}/generator-assets/v1`) - re-runs Call 5 without saving a new mapping.
6. **Discovery** (`POST /reports/discover`) - enumerates batches/row counts against the approved contract.
7. **Run** (`POST /reports/run`) - fills the template with DB data and renders HTML/PDF outputs.

Every stage updates `uploads/<template_id>/` and appends to `artifact_manifest.json` for traceability. Template metadata lives in `state/state.json` and advances through statuses (`draft` -> `mapping_previewed` -> `approved` / `pending`).

## Directory Layout

For a given `template_id`, the uploads directory contains:

- `source.pdf` - uploaded template.
- `reference_pN.png` - rasterized pages from the PDF.
- `template_p1.html` - working HTML shell (mutated after Call 3).
- `render_p1.png`, `render_p1_llm.png` - HTML renderings used for QA.
- `schema_ext.json` - tokens discovered during verification.
- `mapping_step3.json`, `constant_replacements.json`, `token_samples`.
- `mapping_pdf_labels.json` - persisted mapping after approval.
- `page_summary.txt` - prose summary from Call 3.5.
- `report_final.html`, `report_final.png` - final HTML/thumbnail.
- `contract.json`, `contract_overview.md`, `step5_requirements.md`.
- Generator bundle (`generator_assets.json`, zipped SQL pack, params spec).
- Run outputs (`filled_<ts>.html` / `.pdf`).
- `artifact_manifest.json` - union of all artifacts and metadata.

## Stage 1: Template Verification (`POST /templates/verify`)

- **Inputs**: multipart form with `file` (PDF) and `connection_id`. Optional `refine_iters` (ignored, compatibility only).
- **Process** (emits NDJSON lines with `event: stage|result|error`):
  1. `verify.upload_pdf` - writes upload to `source.pdf` respecting `NEURA_MAX_VERIFY_PDF_BYTES`.
  2. `verify.render_reference_preview` - rasterises first page via `pdf_to_pngs` (controlled by `PDF_DPI`); extracts layout hints.
  3. `verify.generate_html` - LLM Call 1 (`request_initial_html`) produces `template_p1.html` and optional schema JSON.
  4. `verify.render_html_preview` - renders HTML to PNG for QA (`render_html_to_png` + panel preview).
  5. `verify.refine_html_layout` - optional Call 2 (`request_fix_html`) controlled by `VERIFY_FIX_HTML_ENABLED`/`MAX_FIX_PASSES`.
  6. `verify.save_artifacts` - writes manifest (`step: templates_verify`), thumbnails, schema, metrics.
- **Outputs**: final line uses `event="result"` with artifact URLs and elapsed time. State store records the template as `draft`, associates artifacts, and remembers the connection.
- **Files**: `source.pdf`, `reference_p1.png`, `template_p1.html`, `schema_ext.json` (optional), `render_p1.png`, `render_p1_llm.png`, `fix_metrics.json`, manifest entry.
- **Locks**: none required (new template).

## Stage 2: Mapping Preview (`POST /templates/{id}/mapping/preview`) - LLM Call 3

- **Inputs**: template id and connection id. Backend resolves `template_p1.html`, `schema_ext.json`, DB catalog (via `_build_catalog_from_db`), and `reference_p1.png`.
- **Caching**: cache key = `sha256(pdf_hash + db_signature + template_sha + prompt_version + catalog_sha + schema_sha)`. If `mapping_step3.json` exists with matching hashes, reply immediately with `status: cached`.
- **LLM Call**: `MappingInline.run_llm_call_3` (prompt version `PROMPT_VERSION`, schema `mapping_inline_v4.schema.json`).
  - Produces `mapping` (token -> `table.column` / `params.*` / SQL fragment / `UNRESOLVED`), `constant_replacements`, `token_samples`, `meta`.
  - Inlines constants into `template_p1.html` and returns the updated HTML SHA.
- **Validation**: rejects legacy wrappers (`DERIVED:` etc.), ensures mappings reference only allow-listed columns, and runs `approval_errors` for diagnostics.
- **Artifacts**:
  - `mapping_step3.json` - stored with `prompt_meta` (hashes, catalog/schema SHA, cache key, prompt version).
  - `constant_replacements.json`.
  - Updated `template_p1.html`.
  - Manifest `step: mapping_inline_llm_call_3` listing HTML + JSON.
- **State store**: status -> `mapping_previewed`, saves artifact URLs and `mapping_keys.json` (subset of approved keys).

## Stage 3: Corrections Preview (`POST /templates/{id}/mapping/corrections-preview`) - LLM Call 3.5

- **Inputs**: template id, optional `page` (default 1), `user_input` (free text), optional `mapping_override`, `sample_tokens`, `model_selector`.
- **Process**:
  - Loads `template_p1.html`, `mapping_step3.json`, `schema_ext.json`.
  - Picks `reference_p{page}.png` when it exists for grounding.
  - Calls `run_corrections_preview` (prompt version `PROMPT_VERSION_3_5`, schema `llm_call_3_5.schema.json`).
- **Outputs**:
  - Overwrites `template_p1.html` with `final_template_html` from the LLM (no structural drift allowed except token constants).
  - Writes `page_summary.txt` and `stage_3_5.json` (raw payload + cache key).
  - Emits streaming `stage` (start/done) and `result` lines including cache hits.
  - Updates manifest (`step: mapping_corrections_preview`) and state store artifacts (`template_html_url`, `page_summary_url`). Status remains `mapping_corrections_previewed` unless already `approved`.

## Stage 4: Mapping Approval (`POST /templates/{id}/mapping/approve`) - Calls 4 & 5

Streaming endpoint that saves operator mapping, drafts the contract, and builds generator assets. Stages:

1. **`mapping.save`** - Normalises payload via `_normalize_mapping_for_autofill`, validates JSON schema, writes `mapping_pdf_labels.json`, updates `mapping_keys.json`, records manifest entry (`step: mapping_save`).
2. **`mapping.prepare_template`** - Ensures `report_final.html` exists (copy from `template_p1.html` if absent); prepares URLs.
3. **`contract_build_v2`** - Call 4 (`build_or_load_contract_v2`):
   - Inputs: catalog, schema, auto-mapping proposal, override mapping, user instructions, dialect hint, DB signature, key tokens.
   - Outputs: `contract.json`, overview markdown, requirements list, warnings, assumptions. Records `contract_stage` summary with prompt version `PROMPT_VERSION_4`.
   - Cached when DB signature + mapping + HTML hash match previous run.
4. **`generator_assets_v1`** - Call 5 (`build_generator_assets_from_payload`):
   - Inputs: Call 4 output, final HTML, catalog allow-list, dialect (payload or hint, default `sqlite`), params spec/sample params, key tokens.
   - Outputs: generator summary, SQL pack, params description, optional invalid tokens, `generator_assets.json`.
5. **`mapping.thumbnail`** - Attempts to render `report_final.html` to `report_final.png` for UI preview.

At completion the endpoint emits `event="result"` with:

- Artifact URLs (final HTML, thumbnail, contract, generator bundle, manifest, page summary, mapping keys).
- `contract_stage` / `generator_stage` metadata and prompt versions.
- `keys` array (approved mapping keys) and `keys_count`.

**State Store Update**:
- Status becomes `approved` when contract + generator assets succeed (otherwise `pending`).
- Saves artifact URLs, generator metadata (`dialect`, `params`, `needsUserFix`, `summary`, etc.), and `last_connection_id`.
- `set_last_used` persists the connection/template pair.

**Locking**: `acquire_template_lock(template_dir, "mapping_approve")` guards the entire approval run.

## Stage 5: Generator Assets API (`POST /templates/{id}/generator-assets/v1`)

- Allows rebuilding Call 5 without re-approving mapping.
- Accepts payload with optional contract overrides (`step4_output`, `contract`, `catalog`, `dialect`, etc.).
- Reuses the approval lock, writes generator artifacts, updates manifest (`step: generator_assets_v1`), and refreshes state store generator metadata.
- Streaming output mirrors the approval stage (`event: stage` -> `result`) and includes cached flag if unchanged.

## Stage 6: Discovery (`POST /reports/discover`)

- **Prerequisites**: `contract.json` must exist (mapping approved). Template directory resolved via `_template_dir`.
- **Inputs**: `template_id`, `connection_id`, `start_date`, `end_date`, optional `key_values` map (token -> literal).
- **Processing**:
  - Loads contract JSON via `load_contract_v2`.
  - Resolves DB path from connection or `NR_DEFAULT_DB`.
  - Invokes `discover_batches_and_counts` to compute batches, row totals, parent relationships.
- **Outputs**: JSON with `batches[]` (id, rows, parent, default `selected: true`), `batches_count`, `rows_total`, `manifest_url`, `manifest_produced_at`.
- State store updates last-used template/connection pair.

## Stage 7: Report Run (`POST /reports/run`)

- **Inputs**: `template_id`, `connection_id`, `start_date`, `end_date`, optional `batch_ids`, optional `key_values`.
- **Pre-flight**:
  - Ensures `report_final.html` (falls back to `template_p1.html`) and `contract.json` exist (`_ensure_contract_files`).
  - Validates contract schema via `validate_contract_schema`.
  - Resolves DB path (`_db_path_from_payload_or_default`) and acquires lock `reports_run`.
- **Execution**:
  - Calls `fill_and_print` with contract object, template HTML, DB path, temp output files, date range, batch list, and key overrides.
  - Moves temp files to `filled_<ts>.html`/`.pdf` on success.
  - Writes manifest entry (`step: reports_run`) listing the new artifacts and inputs (contract path, DB path).
- **Outputs**: JSON response with run id, artifact URLs, manifest URL, and correlation id. State store records template run timestamp and marks last-used connection/template.

## Locking, Caching, and Testing Hooks

- `acquire_template_lock` wraps mapping preview, corrections preview, approval, generator assets, and report runs to avoid concurrent writes. 409 is returned when locked.
- Caches:
  - Call 3: keyed by PDF hash, template HTML SHA (pre/post), catalog SHA, schema SHA, DB signature, prompt version.
  - Call 3.5: keyed by HTML SHA, mapping SHA, user input SHA, prompt version.
  - Call 4/5: handled internally by their modules via DB signature and artifact hashes.
- `NEURA_FAIL_AFTER_STEP` raises after the named manifest step to simulate failures (useful in tests).
- `llm_raw_outputs.md` captures raw LLM responses when enabled to aid debugging.

## State & Manifests

- `state/state.json` tracks:
  - Connections (encrypted secret payloads, latency, status history).
  - Template metadata (name, status, artifacts, mapping keys, generator metadata, last run).
  - `last_used` structure (connection/template pair) consumed by `/state/bootstrap`.
- `artifact_manifest.json` records for each step: files (relative paths), produced_at timestamp, inputs list, and producing step. This enables replay, caching validation, and regression checks by scripts (`scripts/verify_pipeline.py`, `scripts/artifact_stats.py`).
