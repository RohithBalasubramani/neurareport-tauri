# API Reference

Quick reference for all NeuraReport backend API endpoints. All routes are defined in `backend/app/api/routes/`.

---

## Health & State

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Basic health check |
| GET | `/healthz` | Liveness probe (filesystem write, clock skew, optional external HEAD) |
| GET | `/readyz` | Readiness probe |
| GET | `/state/bootstrap` | Initial state payload (connections, templates, last-used selection) |

## Templates & Pipeline

| Method | Endpoint | Description |
|---|---|---|
| GET | `/templates` | List all templates |
| POST | `/templates/verify` | Verify and parse a PDF/Excel template (streaming NDJSON) |
| POST | `/templates/{id}/mapping/preview` | Preview field mapping for a template |
| POST | `/templates/{id}/mapping/approve` | Approve mapping and build contract (streaming NDJSON) |
| GET | `/templates/{id}/artifacts/manifest` | Full artifact manifest (files, hashes, timestamps) |
| POST | `/reports/discover` | Discover report data based on template contract |
| POST | `/reports/run` | Generate report batch |

## Connections & Connectors

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/connections` | List database connections |
| POST | `/api/connections` | Create a new connection |
| PUT | `/api/connections/{id}` | Update a connection |
| DELETE | `/api/connections/{id}` | Delete a connection |
| POST | `/api/connections/{id}/test` | Test connection health |
| GET | `/api/connections/{id}/schema` | Browse database schema |
| GET | `/api/connections/{id}/preview` | Preview table data |
| GET | `/api/connectors` | List available connector types |
| POST | `/api/connectors/test` | Test a connector configuration |
| POST | `/api/connectors/{type}/connect` | Connect via a specific connector |

## AI Agents (v2)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v2/agents/tasks` | List agent tasks |
| POST | `/api/v2/agents/tasks` | Create a new agent task |
| GET | `/api/v2/agents/tasks/{id}` | Get task status and result |
| DELETE | `/api/v2/agents/tasks/{id}` | Cancel/delete a task |
| POST | `/api/v2/agents/tasks/{id}/retry` | Retry a failed task |

Agent types: `research`, `data_analyst`, `email_draft`, `content_repurpose`, `proofreading`

## AI Writing Services

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/grammar` | Grammar checking |
| POST | `/api/ai/summarize` | Text summarization |
| POST | `/api/ai/rewrite` | Text rewriting with tone selection |
| POST | `/api/ai/expand` | Content expansion |
| POST | `/api/ai/translate` | Translation with formatting preservation |
| POST | `/api/ai/generate` | General content generation |

## Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analytics/usage` | Usage metrics and statistics |
| GET | `/api/analytics/trends` | Trend data over time |
| GET | `/api/analytics/top-templates` | Most used templates |

## Charts & Visualization

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/charts/suggest` | AI-powered chart suggestions |
| GET | `/api/charts/saved` | List saved charts |
| POST | `/api/charts/saved` | Save a chart configuration |
| POST | `/api/visualization/generate` | Generate a visualization |

## Dashboards

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboards` | List dashboards |
| POST | `/api/dashboards` | Create a dashboard |
| PUT | `/api/dashboards/{id}` | Update a dashboard |
| DELETE | `/api/dashboards/{id}` | Delete a dashboard |
| GET | `/api/dashboards/{id}/widgets` | List widgets |
| POST | `/api/dashboards/{id}/widgets` | Add a widget |
| POST | `/api/dashboards/{id}/snapshot` | Take a dashboard snapshot |

## Documents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/documents` | List documents |
| POST | `/api/documents` | Create a document |
| PUT | `/api/documents/{id}` | Update a document |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/api/documents/{id}/versions` | Version history |
| POST | `/api/documents/{id}/collaborate` | Start collaboration session |
| POST | `/api/documents/pdf/merge` | Merge multiple PDFs |
| POST | `/api/documents/pdf/watermark` | Add watermark to PDF |
| POST | `/api/documents/pdf/redact` | Redact PDF content |

## Document Intelligence (DocAI)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/docai/parse/invoice` | Parse invoice |
| POST | `/api/docai/parse/contract` | Analyze contract risks |
| POST | `/api/docai/parse/resume` | Parse resume/CV |
| POST | `/api/docai/parse/receipt` | Scan receipt |
| POST | `/api/docai/classify` | Classify document type |

## Document Q&A

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/docqa/ask` | Ask a question about a document |
| POST | `/api/docqa/upload` | Upload document for Q&A |

## Enrichment

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/enrichment/enrich` | Enrich records with external data |
| GET | `/api/enrichment/sources` | List available enrichment sources |
| GET | `/api/enrichment/cache/stats` | Cache hit/miss statistics |

Enrichment sources: `company`, `address`, `exchange_rate`

## Export

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/export/pdf` | Export to PDF |
| POST | `/api/export/docx` | Export to DOCX |
| POST | `/api/export/xlsx` | Export to XLSX |
| POST | `/api/export/csv` | Export to CSV |
| POST | `/api/export/html` | Export to HTML |

## Federation

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/federation/query` | Run a cross-source federated query |
| GET | `/api/federation/schemas` | List available federated schemas |

## Ingestion

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ingestion/upload` | Upload files (single, bulk, ZIP) |
| POST | `/api/ingestion/url` | Ingest from URL |
| POST | `/api/ingestion/email` | Ingest email content |
| POST | `/api/ingestion/clip` | Web clipper |
| POST | `/api/ingestion/transcribe` | Audio/video transcription |
| GET | `/api/ingestion/watcher` | Folder watcher status |

## Jobs & Scheduling

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs` | List all jobs |
| GET | `/api/jobs/{id}` | Get job status |
| POST | `/api/jobs/{id}/cancel` | Cancel a running job |
| POST | `/api/jobs/{id}/retry` | Retry a failed job |
| GET | `/api/schedules` | List schedules |
| POST | `/api/schedules` | Create a schedule |
| PUT | `/api/schedules/{id}` | Update a schedule |
| DELETE | `/api/schedules/{id}` | Delete a schedule |
| POST | `/api/schedules/{id}/trigger` | Manually trigger a schedule |

## Knowledge

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/knowledge` | List knowledge entries |
| POST | `/api/knowledge` | Add to knowledge library |
| PUT | `/api/knowledge/{id}` | Update an entry |
| DELETE | `/api/knowledge/{id}` | Remove an entry |
| POST | `/api/knowledge/search` | Search knowledge base |

## NL2SQL

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/nl2sql/generate` | Convert natural language to SQL |
| POST | `/api/nl2sql/execute` | Execute a generated query |
| POST | `/api/nl2sql/explain` | Explain a query in plain English |
| GET | `/api/nl2sql/history` | Query history |
| GET | `/api/nl2sql/saved` | Saved queries |

## Recommendations

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/recommendations` | Get template recommendations |

## Search

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/search` | Full-text search across all content |
| GET | `/api/search/suggest` | Search suggestions/autocomplete |

## Spreadsheets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/spreadsheets` | List spreadsheets |
| POST | `/api/spreadsheets` | Create a spreadsheet |
| PUT | `/api/spreadsheets/{id}` | Update spreadsheet data |
| DELETE | `/api/spreadsheets/{id}` | Delete a spreadsheet |
| POST | `/api/spreadsheets/{id}/formula` | Evaluate a formula |
| POST | `/api/spreadsheets/{id}/pivot` | Generate pivot table |
| POST | `/api/spreadsheets/ai/formula` | NL to formula conversion |
| POST | `/api/spreadsheets/ai/analyze` | AI data quality analysis |

## Summary

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/summary/generate` | Generate AI summary |

## Synthesis

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/synthesis/run` | Run cross-source synthesis |
| GET | `/api/synthesis/sources` | List synthesis sources |

## Workflows

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/workflows` | List workflows |
| POST | `/api/workflows` | Create a workflow |
| PUT | `/api/workflows/{id}` | Update a workflow |
| DELETE | `/api/workflows/{id}` | Delete a workflow |
| POST | `/api/workflows/{id}/execute` | Execute a workflow |
| GET | `/api/workflows/{id}/executions` | List executions |

## Excel Operations

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/excel/verify` | Verify Excel template |
| POST | `/api/excel/upload` | Upload Excel file |
| GET | `/api/excel/{id}/preview` | Preview Excel data |

## Design

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/design/brand-kit` | Get brand kit |
| PUT | `/api/design/brand-kit` | Update brand kit |
| POST | `/api/design/apply` | Apply design system to content |

---

## Common Patterns

### Error Envelope

All error responses follow a standard format:

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "correlation_id": "uuid"
}
```

### Streaming Responses

Endpoints like `/templates/verify` and `/templates/{id}/mapping/approve` return NDJSON (newline-delimited JSON). Each line is a JSON object with an `event` field:

```json
{"event": "stage", "stage": "parsing", "progress": 0.5}
{"event": "complete", "result": {...}}
```

### Correlation ID

All responses include an `X-Correlation-ID` header for request tracing.

### Idempotency

POST/PUT/DELETE requests support the `Idempotency-Key` header to prevent duplicate operations.
