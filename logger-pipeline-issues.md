# Logger Templates & Reports — Pipeline Issues Log

**Database**: `postgresql://postgres@localhost:5432/meta_data_fast`
**Connection ID**: `330da968-176c-4a80-9770-b431ba3af939`
**Date**: 2026-02-18
**Templates processed**: 14/14
**Reports generated**: 14/14
**Reports with data**: 10/14

---

## Results Summary

| # | Template ID | Table | DB Rows | Report Rows | Data Filled | Issues |
|---|---|---|---|---|---|---|
| 1 | `logger-devices` | app_devices | 32 | 32 | Yes | 0 |
| 2 | `logger-gateways` | app_gateways | 7 | 7 | Yes | 1 |
| 3 | `logger-jobs` | app_jobs | 4 | 4 | Yes | 1 |
| 4 | `logger-job-runs` | app_job_runs | 14 | 14 | Yes | 2 |
| 5 | `logger-schemas` | app_schemas | 4 | 4 | Yes | 0 |
| 6 | `logger-schema-fields` | app_schema_fields | 59 | 59 | Yes | 1 |
| 7 | `logger-device-tables` | app_device_tables | 5 | 5 | Yes | 1 |
| 8 | `logger-db-targets` | app_db_targets | 1 | 1 | Yes | 0 |
| 9 | `logger-protocol-types` | app_protocol_types | 2 | 2 | Yes | 0 |
| 10 | `logger-metadata` | app_meta | 1 | 1 | Yes | 0 |
| 11 | `logger-notifications` | app_notifications | 0 | 1 (empty) | No | 2 |
| 12 | `logger-job-errors-minute` | app_job_errors_minute | 0 | 1 (empty) | No | 2 |
| 13 | `logger-job-metrics-minute` | app_metrics_jobs_minute | 0 | 1 (empty) | No | 3 |
| 14 | `logger-system-metrics-minute` | app_metrics_system_minute | 0 | 1 (empty) | No | 2 |

---

## Issue 1: `date_columns` Contract Bug (CRITICAL)

**Affected**: 7 of 14 templates
**Severity**: Critical — causes all row data to be silently dropped
**Root cause**: The LLM-generated contract picks a column as the "date column" for date-range filtering, but often picks the wrong column (e.g. `id`, `minute_utc` as TEXT, etc.)

### How it breaks

1. Contract `date_columns` maps a table to a column: `{"app_devices": "id"}`
2. Pipeline's `_apply_date_filter_df()` coerces that column to datetime
3. Non-datetime values (UUIDs, integers) get interpreted as UNIX timestamps → dates in 1970
4. Date range filter (2025–2026) removes ALL rows
5. Report renders with correct structure but empty cells
6. Pipeline reports "succeeded" — no error thrown

### Templates that needed fixing

| Template | Wrong date_columns | Fix Applied |
|---|---|---|
| `logger-gateways` | `{"app_gateways": "created_at"}` | `{}` |
| `logger-job-runs` | `{"app_job_runs": "started_at"}` | `{}` |
| `logger-device-tables` | `{"app_device_tables": "last_migrated_at"}` | `{}` |
| `logger-notifications` | `{"app_notifications": "time"}` | `{}` |
| `logger-job-errors-minute` | `{"app_job_errors_minute": "minute_utc"}` | `{}` |
| `logger-job-metrics-minute` | `{"app_metrics_jobs_minute": "minute_utc"}` | `{}` |
| `logger-system-metrics-minute` | `{"app_metrics_system_minute": "minute_utc"}` | `{}` |

**Note**: Some of these (`started_at`, `created_at`, `time`) are legitimate datetime columns stored as TEXT. The issue is that the coercion logic doesn't handle TEXT-typed datetime strings from PostgreSQL correctly, or the date range is wrong for the data.

### Recommended fix

In the contract builder LLM prompt or the `_apply_date_filter_df()` code:
- Validate the date column type before applying filter
- If the column doesn't parse as datetime, skip filtering instead of silently returning 0 rows
- Or add a `"date_filtering": false` flag to the contract spec for tables without date semantics

---

## Issue 2: `generated_at` Scalar Always UNRESOLVED

**Affected**: All 14 templates (minor)
**Severity**: Low — cosmetic only
**What happens**: The `{generated_at}` token in the template header/footer is marked UNRESOLVED in mapping preview. However, the pipeline fills it correctly at render time with the current date (e.g. "18/02/2026").

### Templates where this appeared in preview errors

- `logger-jobs`
- `logger-job-runs`
- `logger-schema-fields`
- `logger-job-metrics-minute`

**No action needed** — this is by design (runtime-injected value).

---

## Issue 3: Empty Tables Produce 1 Empty Row

**Affected**: 4 templates (tables with 0 rows in DB)
**Severity**: Medium — misleading output
**Tables**: `app_notifications`, `app_job_errors_minute`, `app_metrics_jobs_minute`, `app_metrics_system_minute`

### What happens

When the source table has 0 rows, the report still renders 1 `<tr>` row from the BLOCK_REPEAT template — but with all cells empty. This makes it look like there's a data-filling bug rather than an empty table.

### Expected behavior

Either:
- Show 0 rows (don't render the template `<tr>` at all)
- Show a "No data available" message inside the table

### Recommendation

The report engine's BLOCK_REPEAT handler should check if the data array is empty and either skip the row or insert a colspan "No data" row.

---

## Issue 4: Multi-Block Templates Not Supported

**Affected**: Any template with more than 1 `BLOCK_REPEAT` section
**Severity**: High — architectural limitation
**What happens**: When a template has multiple `<!-- BEGIN:BLOCK_REPEAT -->` sections (e.g. one for devices, one for gateways), only the first block gets data. All subsequent blocks are stripped from the output.

### Evidence

- None of the 14 existing sample templates use multiple BLOCK_REPEAT sections
- Earlier attempt with a 5-section template (`logger-system-status-report`) only rendered Section 1

### Impact

Cannot create a single comprehensive report spanning multiple tables. Must create one template per table instead.

### Workaround

Create separate templates per table (as done here) and generate individual reports.

---

## Issue 5: Template ID Auto-Modification

**Affected**: Multiple templates
**Severity**: Low — naming inconsistency
**What happens**: The `create-from-chat` endpoint modifies the template ID from what was requested:

| Requested ID | Actual ID |
|---|---|
| `logger-meta` | `logger-metadata` |
| `logger-job-errors` | `logger-job-errors-minute` |
| `logger-metrics-jobs` | `logger-job-metrics-minute` |
| `logger-metrics-system` | `logger-system-metrics-minute` |

The API derives the ID from the `name` field, not the `template_id` field. This means the `template_id` parameter in the request body is ignored.

---

## Issue 6: Row Token Shared Names Across Blocks

**Affected**: Multi-block templates only
**Severity**: Medium (related to Issue 4)
**What happens**: When multiple blocks share token names like `{row_name}` or `{row_status}`, the mapping maps them to the first table found. The pipeline can't disambiguate which block each token belongs to.

### Example

Both devices and gateways have `{row_name}`, but mapping assigns it to `app_devices.name` only.

### Workaround

Use unique prefixed token names per section: `{row_device_name}`, `{row_gateway_name}`, etc. (Still limited by Issue 4.)

---

## Pipeline Steps That Worked Correctly

- **Template registration**: 14/14 succeeded
- **Mapping preview**: 14/14 succeeded, auto-resolved 68–100% of tokens
- **Mapping approve + contract build**: 14/14 succeeded (LLM contract generation)
- **Report generation**: 14/14 succeeded (dataLoad → contractCheck → renderPdf → finalize)
- **Scalar filling**: date_from, date_to, generated_at all filled correctly
- **Row data filling**: 10/10 tables with data filled correctly after date_columns fix
- **PDF generation**: All 14 PDFs generated successfully

---

## File Locations

### Templates & Reports

| Template ID | HTML Report | PDF Report |
|---|---|---|
| logger-devices | `/uploads/logger-devices/filled_1771434099.html` | `.pdf` |
| logger-gateways | `/uploads/logger-gateways/filled_1771434146.html` | `.pdf` |
| logger-jobs | `/uploads/logger-jobs/filled_1771434191.html` | `.pdf` |
| logger-job-runs | `/uploads/logger-job-runs/filled_1771434244.html` | `.pdf` |
| logger-schemas | `/uploads/logger-schemas/filled_1771434284.html` | `.pdf` |
| logger-schema-fields | `/uploads/logger-schema-fields/filled_1771434332.html` | `.pdf` |
| logger-device-tables | `/uploads/logger-device-tables/filled_1771434380.html` | `.pdf` |
| logger-db-targets | `/uploads/logger-db-targets/filled_1771434428.html` | `.pdf` |
| logger-protocol-types | `/uploads/logger-protocol-types/filled_1771434471.html` | `.pdf` |
| logger-metadata | `/uploads/logger-metadata/filled_1771434515.html` | `.pdf` |
| logger-notifications | `/uploads/logger-notifications/filled_1771434562.html` | `.pdf` |
| logger-job-errors-minute | `/uploads/logger-job-errors-minute/filled_1771434610.html` | `.pdf` |
| logger-job-metrics-minute | `/uploads/logger-job-metrics-minute/filled_1771434664.html` | `.pdf` |
| logger-system-metrics-minute | `/uploads/logger-system-metrics-minute/filled_1771434719.html` | `.pdf` |

All paths relative to: `/home/rohith/desktop/NeuraReport/prodo/backend/`

---

# Excel Pipeline Results

**Date**: 2026-02-19
**Excel templates processed**: 14/14
**Excel reports generated**: 14/14

---

## Excel Results Summary

| # | Template ID | Table | DB Rows | Used Rows | XLSX Size | PDF Size | Issues |
|---|---|---|---|---|---|---|---|
| 1 | `app-gateways-28e5ac` | app_gateways | 7 | 7 | 6.1KB | 26.4KB | 1 |
| 2 | `app-jobs-22d87b` | app_jobs | 4 | 4 | 5.9KB | 18.8KB | 0 |
| 3 | `app-job-runs-ff7393` | app_job_runs | 14 | 14 | 6.4KB | 29.1KB | 1 |
| 4 | `app-schemas-ceb84e` | app_schemas | 4 | 4 | 5.0KB | 7.6KB | 0 |
| 5 | `app-schema-fields-30-0d56ff` | app_schema_fields | 59 | 30 | 7.9KB | 34.6KB | 1 |
| 6 | `app-device-tables-0a3d7a` | app_device_tables | 5 | 5 | 6.1KB | 20.9KB | 1 |
| 7 | `app-db-targets-50130e` | app_db_targets | 1 | 1 | 5.8KB | 23.9KB | 0 |
| 8 | `app-protocol-types-763a9e` | app_protocol_types | 2 | 2 | 5.7KB | 13.7KB | 0 |
| 9 | `app-meta-e35ec9` | app_meta | 1 | 1 | 5.7KB | 14.5KB | 0 |
| 10 | `app-notifications-0e5f36` | app_notifications | 0 | 0 | 5.0KB | 9.8KB | 1 |
| 11 | `app-job-errors-minute-2bb2d6` | app_job_errors_minute | 0 | 0 | 5.0KB | 9.6KB | 1 |
| 12 | `app-metrics-jobs-minute-51ea3b` | app_metrics_jobs_minute | 0 | 0 | 5.1KB | 10.5KB | 1 |
| 13 | `app-metrics-system-minute-2cf1c6` | app_metrics_system_minute | 0 | 0 | 5.1KB | 10.8KB | 1 |
| 14 | `app-devices-30x7-fe9a8c` | app_devices | 32 | 30 | 7.0KB | 25.9KB | 1 |

---

## Excel Issue 1: EXCEL_MAX_DATA_ROWS Limit (30 Rows)

**Affected**: `app_devices` (32 rows), `app_schema_fields` (59 rows)
**Severity**: High — silently fails verification for large tables
**Root cause**: The Excel verify endpoint (`POST /excel/verify`) uses an LLM to convert the uploaded .xlsx into an HTML template with tokens. When the data exceeds `EXCEL_MAX_DATA_ROWS` (default 30), the LLM conversion fails.

### How it breaks

1. User uploads an .xlsx with >30 data rows
2. The LLM-based XLSX→HTML conversion attempts to process all rows
3. Conversion fails — returns `{"event": "error", "detail": "Excel verification failed"}`
4. No template_id is returned; pipeline cannot continue

### Workaround applied

Created reduced versions of the affected .xlsx files:
- `app_devices`: 32 rows → 30 rows (dropped 2 least relevant devices)
- `app_schema_fields`: 59 rows → 30 rows (first 30 fields only)

### Recommended fix

- Surface the `EXCEL_MAX_DATA_ROWS` limit in the error message so users know why it failed
- Consider increasing the default limit or paginating the LLM conversion
- The limit only affects verification (template creation); report generation can fill any number of rows

---

## Excel Issue 2: `date_columns` Bug (Same as HTML Issue 1)

**Affected**: 7 of 14 Excel templates — same tables as the HTML pipeline
**Severity**: Critical
**Details**: Identical to Issue 1 in the HTML pipeline section above. The LLM-generated contract picks wrong date columns, causing all row data to be silently dropped during date-range filtering.

Templates requiring `date_columns` fix: `app_gateways`, `app_job_runs`, `app_device_tables`, `app_notifications`, `app_job_errors_minute`, `app_metrics_jobs_minute`, `app_metrics_system_minute`

---

## Excel Issue 3: Backend Instability Under Heavy LLM Load

**Affected**: Pipeline execution
**Severity**: Medium — requires manual restarts
**What happens**: The Excel verify step is LLM-heavy (converts .xlsx to HTML with token extraction). Processing multiple templates sequentially can cause the backend to become unresponsive or crash after 7-8 templates.

### Symptoms

- Backend stops responding to health checks
- Subsequent verify requests timeout
- Backend process needs manual restart via `systemctl restart neurareport-backend`

### Workaround applied

- Added health checks before each template
- Added cooldown delays (3-5s between steps, 5s between templates)
- Incremental result saving so progress isn't lost on crash

### Recommended fix

- Add rate limiting or queueing for LLM-heavy operations
- Consider async/background processing for Excel verify
- Add memory/resource limits to prevent OOM conditions

---

## Excel Issue 4: Template IDs Include Hash Suffix

**Affected**: All 14 Excel templates
**Severity**: Low — cosmetic
**What happens**: Excel template IDs are auto-generated as `{filename-without-extension}-{6char-hash}` (e.g. `app-gateways-28e5ac`). Unlike the HTML pipeline where you can request a specific template_id, the Excel pipeline always appends a random hash.

This makes it harder to reference templates by ID in automation scripts, since the hash changes each time.

---

## Excel Pipeline Steps That Worked Correctly

- **Excel verify** (XLSX → HTML template): 14/14 succeeded (after row reduction for 2 tables)
- **Mapping preview**: 14/14 succeeded, 100% auto-resolved for all tokens
- **Mapping approve + contract build**: 14/14 succeeded
- **Report generation**: 14/14 succeeded
- **XLSX output**: All 14 Excel reports generated (5.0–7.9KB)
- **PDF output**: All 14 PDFs generated (7.6–34.6KB)
- **Auto-token mapping**: Excel header names mapped perfectly to DB columns (e.g. "Device Name" → `app_devices.name`)

---

## Excel File Locations

All paths relative to: `/home/rohith/desktop/NeuraReport/prodo/backend/uploads_excel/`

| Template ID | Table |
|---|---|
| `app-gateways-28e5ac` | app_gateways |
| `app-jobs-22d87b` | app_jobs |
| `app-job-runs-ff7393` | app_job_runs |
| `app-schemas-ceb84e` | app_schemas |
| `app-schema-fields-30-0d56ff` | app_schema_fields |
| `app-device-tables-0a3d7a` | app_device_tables |
| `app-db-targets-50130e` | app_db_targets |
| `app-protocol-types-763a9e` | app_protocol_types |
| `app-meta-e35ec9` | app_meta |
| `app-notifications-0e5f36` | app_notifications |
| `app-job-errors-minute-2bb2d6` | app_job_errors_minute |
| `app-metrics-jobs-minute-51ea3b` | app_metrics_jobs_minute |
| `app-metrics-system-minute-2cf1c6` | app_metrics_system_minute |
| `app-devices-30x7-fe9a8c` | app_devices |
