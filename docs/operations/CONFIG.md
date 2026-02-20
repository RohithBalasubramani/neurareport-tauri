# Configuration Reference

NeuraReport reads the following environment variables and settings when launching the backend, scripts, and frontend.

## Backend Environment Variables

### Core service

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes (OpenAI provider) | _none_ | OpenAI API token when `LLM_PROVIDER` resolves to OpenAI. Allow missing only for offline testing. |
| `NEURA_ALLOW_MISSING_OPENAI` | No | `false` | Set to `true` to bypass the API key requirement when running offline. |
| `OPENAI_MODEL` | No | `gpt-5` | OpenAI model name (fallback when `LLM_MODEL` is unset). |
| `UPLOAD_ROOT` | No | `backend/uploads` | Directory that stores per-template artifacts and manifests. Created on boot. |
| `EXCEL_UPLOAD_ROOT` | No | `backend/uploads_excel` | Directory for Excel pipeline artifacts and manifests. Created on boot. |
| `NR_DEFAULT_DB` | No | _none_ | Default SQLite database path used when the UI omits a connection id. |
| `DB_PATH` | No | _none_ | Legacy fallback path for the default database (`NR_DEFAULT_DB` takes precedence). |
| `NEURA_STATE_DIR` | No | `backend/state` | Location of the encrypted state store (`state.json`) and generated secret. |
| `NEURA_STATE_SECRET` | No | auto-generated | Base64 Fernet key. Provide to share state across installs or retain secrets. |
| `NEURA_MAX_VERIFY_PDF_BYTES` | No | `52428800` (50 MiB) | Maximum upload size (bytes) for `/templates/verify`. `0` disables the limit. |
| `PDF_DPI` | No | `400` | DPI used when rasterising PDFs to PNG during verification. |
| `MAX_FIX_PASSES` | No | `1` | Number of refinement passes attempted during Call 2 (`VERIFY_FIX_HTML_ENABLED` must be true). |
| `VERIFY_FIX_HTML_ENABLED` | No | `true` | Disable (`false`/`0`) to skip the Call 2 HTML refinement stage. |
| `ARTIFACT_WARN_BYTES` | No | `5242880` (5 MiB) | Threshold used by `scripts/artifact_stats.py` and CI for artifact sizes. |
| `ARTIFACT_WARN_RENDER_MS` | No | `2000` | Threshold used by `scripts/artifact_stats.py` and CI for render durations. |
| `NEURA_VERSION` | No | `version.json` value or `dev` | Overrides the version stamped on logs and health endpoints. |
| `NEURA_COMMIT` | No | `version.json` value or `unknown` | Overrides the commit hash exposed in logs and health endpoints. |

### Security & auth

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `NEURA_API_KEY` | No | _none_ | Shared API key for protecting endpoints when enabled. |
| `NEURA_ALLOW_ANON_API` | No | `false` | Set to `true` to allow anonymous API access. |
| `NEURA_JWT_SECRET` | No | `change-me` | JWT signing secret for auth flows. Replace in production. |
| `NEURA_JWT_LIFETIME_SECONDS` | No | `3600` | JWT lifetime in seconds. |

### Rate limiting

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `NEURA_RATE_LIMIT_ENABLED` | No | `true` | Enable/disable API rate limiting. |
| `NEURA_RATE_LIMIT_REQUESTS` | No | `100` | Requests per window when rate limiting is enabled. |
| `NEURA_RATE_LIMIT_WINDOW_SECONDS` | No | `60` | Rate limit window size (seconds). |
| `NEURA_RATE_LIMIT_BURST` | No | `20` | Allowed burst over the steady-state limit. |

### Idempotency

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `NEURA_IDEMPOTENCY_ENABLED` | No | `true` | Enable/disable idempotency checks for write endpoints. |
| `NEURA_IDEMPOTENCY_TTL_SECONDS` | No | `86400` | Idempotency record TTL in seconds. |

### Debug & safety

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `NEURA_DEBUG` | No | `false` | Enable debug mode in the backend. |
| `NEURA_ALLOW_UNSAFE_PDF_PATHS` | No | `false` | Permit unsafe PDF path inputs (use only in trusted environments). |
| `NEURA_UX_GOVERNANCE_STRICT` | No | `true` | Enforce strict UX governance headers from the frontend. |

### LLM behaviour

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `LLM_PROVIDER` | No | auto-detect (`openai`) | Provider selection: `openai`, `litellm`, `ollama`, `deepseek`, `anthropic`, `azure`, `gemini`, `custom`. |
| `NEURA_LLM_ENGINE` | No | `litellm` | Engine selection (`litellm` or `native`). |
| `LLM_MODEL` | No | provider default | Override model name (falls back to `<PROVIDER>_MODEL` or `OPENAI_MODEL`). |
| `LLM_API_KEY` | No | _none_ | Override provider API key (falls back to `<PROVIDER>_API_KEY` or `OPENAI_API_KEY`). |
| `LLM_BASE_URL` | No | _none_ | Base URL for OpenAI-compatible endpoints or custom providers. |
| `LLM_TIMEOUT_SECONDS` | No | `120` | Per-request timeout in seconds (preferred). |
| `LLM_MAX_RETRIES` | No | `3` | Retry count (preferred). |
| `LLM_RETRY_DELAY` | No | `1.5` | Initial backoff delay between retries (seconds, preferred). |
| `LLM_RETRY_MULTIPLIER` | No | `2.0` | Multiplier applied to each retry delay (preferred). |
| `LLM_TEMPERATURE` | No | _none_ | Optional model temperature override. |
| `LLM_MAX_TOKENS` | No | _none_ | Optional max tokens override. |
| `LLM_FALLBACK_PROVIDER` | No | _none_ | Optional fallback provider (LiteLLM engine). |
| `LLM_FALLBACK_MODEL` | No | provider default | Optional fallback model when the provider above is set. |
| `NEURA_FORCE_GPT5` | No | `true` | Forces `gpt-5` in legacy/OpenAI paths. |
| `LLM_RAW_OUTPUT_PATH` | No | `llm_raw_outputs.md` | Absolute or relative path for dumping raw LLM responses. |

Provider-specific keys (used when `LLM_PROVIDER` targets a vendor):

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes (OpenAI provider) | _none_ | OpenAI API token. |
| `OPENAI_MODEL` | No | `gpt-5` | OpenAI model name (fallback when `LLM_MODEL` is unset). |
| `OPENAI_BASE_URL` | No | _none_ | Optional OpenAI base URL override. |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server base URL. |
| `OLLAMA_MODEL` | No | `llama3.2` | Ollama model name. |
| `DEEPSEEK_API_KEY` | No | _none_ | DeepSeek API token. |
| `DEEPSEEK_MODEL` | No | `deepseek-chat` | DeepSeek model name. |
| `ANTHROPIC_API_KEY` | No | _none_ | Anthropic API token. |
| `ANTHROPIC_MODEL` | No | `claude-3-5-sonnet-20241022` | Anthropic model name. |
| `AZURE_OPENAI_ENDPOINT` | No | _none_ | Azure OpenAI endpoint URL. |
| `AZURE_OPENAI_KEY` | No | _none_ | Azure OpenAI API key. |
| `AZURE_OPENAI_DEPLOYMENT` | No | _none_ | Azure OpenAI deployment name. |
| `AZURE_OPENAI_API_VERSION` | No | `2024-02-15-preview` | Azure OpenAI API version. |
| `GOOGLE_API_KEY` | No | _none_ | Google API key for Gemini. |
| `GEMINI_MODEL` | No | `gemini-1.5-pro` | Gemini model name. |
| `CUSTOM_LLM_BASE_URL` | No | _none_ | Base URL for custom OpenAI-compatible providers. |

Legacy aliases (still accepted by legacy OpenAI call paths):

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OPENAI_REQUEST_TIMEOUT_SECONDS` | No | _none_ | Legacy alias for `LLM_TIMEOUT_SECONDS`. Leave unset or `0` to disable. |
| `OPENAI_MAX_ATTEMPTS` | No | `3` | Legacy alias for `LLM_MAX_RETRIES`. |
| `OPENAI_BACKOFF_SECONDS` | No | `1.5` | Legacy alias for `LLM_RETRY_DELAY`. |
| `OPENAI_BACKOFF_MULTIPLIER` | No | `2.0` | Legacy alias for `LLM_RETRY_MULTIPLIER`. |

### Health & diagnostics

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `NEURA_HEALTH_EXTERNAL_HEAD` | No | `https://api.openai.com/v1/models` | Optional URL probed via HTTP HEAD in `/healthz` and `/readyz`. |
| `NEURA_FAIL_AFTER_STEP` | No | _none_ | Testing hook that raises after the named pipeline step (for rollback drills). |

### CLI / tooling helpers

| Variable | Used by | Description |
| --- | --- | --- |
| `CONNECTION_ID` | `backend/app/services/connections/db_connection.py` CLI | Supplies a connection id when resolving DB paths via the helper script. |
| `DB_URL` | same | Alternative to `--db-url` when running the helper script. |
| `DB_PATH` | same | Legacy override for SQLite paths (also used as a backend fallback). |

## Frontend (Vite) Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | No | `http://127.0.0.1:8000` | Base URL used by the frontend HTTP client. |
| `VITE_USE_MOCK` | No | `true` | Serve mock API responses when set to `true`. Use `false` for real backend integration. |

## Ports

- Backend (FastAPI via uvicorn): `8000`
- Frontend (Vite dev server): `5173`

## Key Paths

- Backend source: `backend/`
- Template uploads: `backend/uploads/<template_id>/`
- Artifact manifest: `backend/uploads/<template_id>/artifact_manifest.json`
- State store: `backend/state/state.json`
- LLM output log: `llm_raw_outputs.md` (configurable)
- Scripts: `scripts/*.py`

## Runtime Validation

On startup the backend:

1. Ensures `OPENAI_API_KEY` is present unless `NEURA_ALLOW_MISSING_OPENAI=true`.
2. Creates/verifies the uploads directory (`UPLOAD_ROOT`).
3. Logs a sanitized configuration summary (model, version, commit, storage paths).
4. Generates `NEURA_STATE_SECRET` if absent and persists it next to `state.json`.

## Example Session Configuration

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "sk-..."
$env:UPLOAD_ROOT = "$PWD\\backend\\uploads"
$env:NEURA_STATE_SECRET = "my-shared-secret"
uvicorn backend.api:app --reload
```

Unix shells:

```bash
export OPENAI_API_KEY="sk-..."
export UPLOAD_ROOT="$PWD/backend/uploads"
export NEURA_STATE_SECRET="my-shared-secret"
uvicorn backend.api:app --reload
```
