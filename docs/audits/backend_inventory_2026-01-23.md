# Backend Inventory

Date: 2026-01-23

## Summary
- Python files: 355
- app: 1
- app/api: 33
- app/domain: 1
- app/repositories: 11
- app/schemas: 18
- app/services: 137
- app/utils: 12
- backend: 1
- engine: 44
- entrypoint: 1
- legacy: 43
- scripts: 1
- tests: 52

## Entrypoints ("__main__")
- `backend/app/repositories/connections/db_connection.py`
- `backend/app/services/governance_guards.py`
- `backend/app/services/reports/ReportGenerate.py`
- `backend/app/services/reports/ReportGenerateExcel.py`
- `backend/app/services/templates/TemplateVerify.py`
- `backend/scripts/raster_html.py`
- `backend/tests/test_adapters.py`
- `backend/tests/test_ai_integrations.py`
- `backend/tests/test_docqa_feedback.py`
- `backend/tests/test_enrichment_cache_stats.py`
- `backend/tests/test_enrichment_sources.py`
- `backend/tests/test_federation.py`
- `backend/tests/test_mailer.py`
- `backend/tests/test_mapping_utils.py`
- `backend/tests/test_scheduler_date_range.py`

## Background Jobs / Schedulers
- `backend/app/services/jobs/report_scheduler.py`
- `backend/app/services/background_tasks.py`
- `backend/app/services/jobs/job_tracking.py`
- `backend/engine/orchestration/scheduler.py`
- `backend/engine/orchestration/worker.py`
- `backend/engine/orchestration/executor.py`

## Pipelines
- `backend/engine/pipelines/base.py`
- `backend/engine/pipelines/import_pipeline.py`
- `backend/engine/pipelines/report_pipeline.py`
- `backend/app/services/analyze/extraction_pipeline.py`

## Utilities
- `backend/app/utils/`
- `backend/app/services/utils/`
- `backend/legacy/utils/`
- `backend/engine/core/`

## File Inventory
| File | Layer | Responsibility | Flags |
| --- | --- | --- | --- |
| `backend/__init__.py` | backend |   init   |  |
| `backend/api.py` | entrypoint | FastAPI entrypoint (app init, middleware, routes, startup/shutdown) |  |
| `backend/app/__init__.py` | app | App package init |  |
| `backend/app/api/__init__.py` | app/api | API module:   init   |  |
| `backend/app/api/analyze/__init__.py` | app/api | API analyze routes:   init   |  |
| `backend/app/api/analyze/analysis_routes.py` | app/api | API analyze routes: analysis routes |  |
| `backend/app/api/analyze/enhanced_analysis_routes.py` | app/api | API analyze routes: enhanced analysis routes |  |
| `backend/app/api/generate/__init__.py` | app/api | API generate routes:   init   |  |
| `backend/app/api/generate/chart_suggest_routes.py` | app/api | API generate routes: chart suggest routes |  |
| `backend/app/api/generate/discover_routes.py` | app/api | API generate routes: discover routes |  |
| `backend/app/api/generate/run_routes.py` | app/api | API generate routes: run routes |  |
| `backend/app/api/generate/saved_charts_routes.py` | app/api | API generate routes: saved charts routes |  |
| `backend/app/api/middleware.py` | app/api | API module: middleware |  |
| `backend/app/api/router.py` | app/api | API module: router |  |
| `backend/app/api/routes/__init__.py` | app/api | API route handlers for   init   |  |
| `backend/app/api/routes/analytics.py` | app/api | API route handlers for analytics |  |
| `backend/app/api/routes/charts.py` | app/api | API route handlers for charts |  |
| `backend/app/api/routes/connections.py` | app/api | API route handlers for connections |  |
| `backend/app/api/routes/docqa.py` | app/api | API route handlers for docqa |  |
| `backend/app/api/routes/documents.py` | app/api | API route handlers for documents |  |
| `backend/app/api/routes/enrichment.py` | app/api | API route handlers for enrichment |  |
| `backend/app/api/routes/excel.py` | app/api | API route handlers for excel |  |
| `backend/app/api/routes/federation.py` | app/api | API route handlers for federation |  |
| `backend/app/api/routes/health.py` | app/api | API route handlers for health |  |
| `backend/app/api/routes/jobs.py` | app/api | API route handlers for jobs |  |
| `backend/app/api/routes/legacy.py` | app/api | API route handlers for legacy |  |
| `backend/app/api/routes/nl2sql.py` | app/api | API route handlers for nl2sql |  |
| `backend/app/api/routes/recommendations.py` | app/api | API route handlers for recommendations |  |
| `backend/app/api/routes/reports.py` | app/api | API route handlers for reports |  |
| `backend/app/api/routes/schedules.py` | app/api | API route handlers for schedules |  |
| `backend/app/api/routes/spreadsheets.py` | app/api | API route handlers for spreadsheets |  |
| `backend/app/api/routes/state.py` | app/api | API route handlers for state |  |
| `backend/app/api/routes/summary.py` | app/api | API route handlers for summary |  |
| `backend/app/api/routes/synthesis.py` | app/api | API route handlers for synthesis |  |
| `backend/app/api/routes/templates.py` | app/api | API route handlers for templates |  |
| `backend/app/api/ux_governance.py` | app/api | API module: ux governance |  |
| `backend/app/domain/__init__.py` | app/domain | Domain logic: __init__ |  |
| `backend/app/repositories/__init__.py` | app/repositories | Repository: __init__ |  |
| `backend/app/repositories/connections/__init__.py` | app/repositories | Repository: connections |  |
| `backend/app/repositories/connections/db_connection.py` | app/repositories | Repository: connections |  |
| `backend/app/repositories/connections/repository.py` | app/repositories | Repository: connections |  |
| `backend/app/repositories/connections/schema.py` | app/repositories | Repository: connections |  |
| `backend/app/repositories/dataframes/__init__.py` | app/repositories | Repository: dataframes |  |
| `backend/app/repositories/dataframes/sqlite_loader.py` | app/repositories | Repository: dataframes |  |
| `backend/app/repositories/dataframes/sqlite_shim.py` | app/repositories | Repository: dataframes |  |
| `backend/app/repositories/dataframes/store.py` | app/repositories | Repository: dataframes |  |
| `backend/app/repositories/state/__init__.py` | app/repositories | Repository: state |  |
| `backend/app/repositories/state/store.py` | app/repositories | Repository: state | god-file |
| `backend/app/schemas/__init__.py` | app/schemas | Schema definitions: __init__ |  |
| `backend/app/schemas/analyze/__init__.py` | app/schemas | Schema definitions: analyze |  |
| `backend/app/schemas/analyze/analysis.py` | app/schemas | Schema definitions: analyze |  |
| `backend/app/schemas/analyze/enhanced_analysis.py` | app/schemas | Schema definitions: analyze |  |
| `backend/app/schemas/connections/__init__.py` | app/schemas | Schema definitions: connections |  |
| `backend/app/schemas/docqa/__init__.py` | app/schemas | Schema definitions: docqa |  |
| `backend/app/schemas/documents/__init__.py` | app/schemas | Schema definitions: documents |  |
| `backend/app/schemas/documents/document.py` | app/schemas | Schema definitions: documents |  |
| `backend/app/schemas/enrichment/__init__.py` | app/schemas | Schema definitions: enrichment |  |
| `backend/app/schemas/federation/__init__.py` | app/schemas | Schema definitions: federation |  |
| `backend/app/schemas/generate/__init__.py` | app/schemas | Schema definitions: generate |  |
| `backend/app/schemas/generate/charts.py` | app/schemas | Schema definitions: generate |  |
| `backend/app/schemas/generate/reports.py` | app/schemas | Schema definitions: generate |  |
| `backend/app/schemas/nl2sql/__init__.py` | app/schemas | Schema definitions: nl2sql |  |
| `backend/app/schemas/spreadsheets/__init__.py` | app/schemas | Schema definitions: spreadsheets |  |
| `backend/app/schemas/spreadsheets/spreadsheet.py` | app/schemas | Schema definitions: spreadsheets |  |
| `backend/app/schemas/synthesis/__init__.py` | app/schemas | Schema definitions: synthesis |  |
| `backend/app/schemas/templates/__init__.py` | app/schemas | Schema definitions: templates |  |
| `backend/app/services/__init__.py` | app/services | Service layer: __init__ |  |
| `backend/app/services/analyze/__init__.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/advanced_ai_features.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/analysis_engines.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/data_transform_export.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/document_analysis_service.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/enhanced_analysis_orchestrator.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/enhanced_analysis_store.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/enhanced_extraction_service.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/extraction_pipeline.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/integrations.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/user_experience.py` | app/services | Service layer: analyze |  |
| `backend/app/services/analyze/visualization_engine.py` | app/services | Service layer: analyze |  |
| `backend/app/services/auth.py` | app/services | Service layer: auth |  |
| `backend/app/services/background_tasks.py` | app/services | Service layer: background_tasks |  |
| `backend/app/services/charts/__init__.py` | app/services | Service layer: charts |  |
| `backend/app/services/charts/auto_chart_service.py` | app/services | Service layer: charts |  |
| `backend/app/services/charts/quickchart.py` | app/services | Service layer: charts |  |
| `backend/app/services/config.py` | app/services | Service layer: config |  |
| `backend/app/services/connections/__init__.py` | app/services | Service layer: connections |  |
| `backend/app/services/connections/service.py` | app/services | Service layer: connections |  |
| `backend/app/services/connectors/__init__.py` | app/services | Service layer: connectors |  |
| `backend/app/services/connectors/base.py` | app/services | Service layer: connectors |  |
| `backend/app/services/connectors/databases/__init__.py` | app/services | Service layer: connectors/databases |  |
| `backend/app/services/connectors/databases/mongodb.py` | app/services | Service layer: connectors/databases |  |
| `backend/app/services/connectors/databases/mysql.py` | app/services | Service layer: connectors/databases |  |
| `backend/app/services/connectors/databases/postgresql.py` | app/services | Service layer: connectors/databases |  |
| `backend/app/services/connectors/registry.py` | app/services | Service layer: connectors |  |
| `backend/app/services/contract/ContractBuilderV2.py` | app/services | Service layer: contract |  |
| `backend/app/services/contract/__init__.py` | app/services | Service layer: contract |  |
| `backend/app/services/dashboards/__init__.py` | app/services | Service layer: dashboards |  |
| `backend/app/services/design/__init__.py` | app/services | Service layer: design |  |
| `backend/app/services/docai/__init__.py` | app/services | Service layer: docai |  |
| `backend/app/services/docqa/service.py` | app/services | Service layer: docqa |  |
| `backend/app/services/documents/__init__.py` | app/services | Service layer: documents |  |
| `backend/app/services/documents/collaboration.py` | app/services | Service layer: documents |  |
| `backend/app/services/documents/pdf_operations.py` | app/services | Service layer: documents |  |
| `backend/app/services/documents/service.py` | app/services | Service layer: documents |  |
| `backend/app/services/enrichment/cache.py` | app/services | Service layer: enrichment |  |
| `backend/app/services/enrichment/service.py` | app/services | Service layer: enrichment |  |
| `backend/app/services/enrichment/sources/__init__.py` | app/services | Service layer: enrichment/sources |  |
| `backend/app/services/enrichment/sources/address.py` | app/services | Service layer: enrichment/sources |  |
| `backend/app/services/enrichment/sources/base.py` | app/services | Service layer: enrichment/sources |  |
| `backend/app/services/enrichment/sources/company.py` | app/services | Service layer: enrichment/sources |  |
| `backend/app/services/enrichment/sources/exchange.py` | app/services | Service layer: enrichment/sources |  |
| `backend/app/services/errors.py` | app/services | Service layer: errors |  |
| `backend/app/services/excel/ExcelVerify.py` | app/services | Service layer: excel |  |
| `backend/app/services/excel/__init__.py` | app/services | Service layer: excel |  |
| `backend/app/services/export/__init__.py` | app/services | Service layer: export |  |
| `backend/app/services/extraction/__init__.py` | app/services | Service layer: extraction |  |
| `backend/app/services/extraction/excel_extractors.py` | app/services | Service layer: extraction |  |
| `backend/app/services/extraction/pdf_extractors.py` | app/services | Service layer: extraction | god-file |
| `backend/app/services/federation/service.py` | app/services | Service layer: federation |  |
| `backend/app/services/generate/__init__.py` | app/services | Service layer: generate |  |
| `backend/app/services/generate/chart_suggestions_service.py` | app/services | Service layer: generate |  |
| `backend/app/services/generate/discovery_service.py` | app/services | Service layer: generate |  |
| `backend/app/services/generate/saved_charts_service.py` | app/services | Service layer: generate |  |
| `backend/app/services/generator/GeneratorAssetsV1.py` | app/services | Service layer: generator |  |
| `backend/app/services/generator/__init__.py` | app/services | Service layer: generator |  |
| `backend/app/services/governance_guards.py` | app/services | Service layer: governance_guards |  |
| `backend/app/services/idempotency.py` | app/services | Service layer: idempotency |  |
| `backend/app/services/jobs/__init__.py` | app/services | Service layer: jobs |  |
| `backend/app/services/jobs/job_tracking.py` | app/services | Service layer: jobs |  |
| `backend/app/services/jobs/report_scheduler.py` | app/services | Service layer: jobs |  |
| `backend/app/services/knowledge/__init__.py` | app/services | Service layer: knowledge |  |
| `backend/app/services/llm/__init__.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/agents.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/client.py` | app/services | Service layer: llm | god-file |
| `backend/app/services/llm/config.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/document_extractor.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/providers.py` | app/services | Service layer: llm | god-file |
| `backend/app/services/llm/rag.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/text_to_sql.py` | app/services | Service layer: llm |  |
| `backend/app/services/llm/vision.py` | app/services | Service layer: llm |  |
| `backend/app/services/mapping/AutoMapInline.py` | app/services | Service layer: mapping |  |
| `backend/app/services/mapping/CorrectionsPreview.py` | app/services | Service layer: mapping |  |
| `backend/app/services/mapping/HeaderMapping.py` | app/services | Service layer: mapping |  |
| `backend/app/services/mapping/__init__.py` | app/services | Service layer: mapping |  |
| `backend/app/services/mapping/auto_fill.py` | app/services | Service layer: mapping |  |
| `backend/app/services/nl2sql/service.py` | app/services | Service layer: nl2sql |  |
| `backend/app/services/prompts/__init__.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_analysis.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_charts.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_excel.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_template_chat.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_template_edit.py` | app/services | Service layer: prompts |  |
| `backend/app/services/prompts/llm_prompts_templates.py` | app/services | Service layer: prompts |  |
| `backend/app/services/recommendations/service.py` | app/services | Service layer: recommendations |  |
| `backend/app/services/render/__init__.py` | app/services | Service layer: render |  |
| `backend/app/services/render/html_raster.py` | app/services | Service layer: render |  |
| `backend/app/services/reports/ReportGenerate.py` | app/services | Service layer: reports | god-file |
| `backend/app/services/reports/ReportGenerateExcel.py` | app/services | Service layer: reports | god-file |
| `backend/app/services/reports/__init__.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/common_helpers.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/contract_adapter.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/date_utils.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/discovery.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/discovery_excel.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/discovery_metrics.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/docx_export.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/html_table_parser.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/strategies.py` | app/services | Service layer: reports |  |
| `backend/app/services/reports/xlsx_export.py` | app/services | Service layer: reports |  |
| `backend/app/services/security.py` | app/services | Service layer: security |  |
| `backend/app/services/spreadsheets/__init__.py` | app/services | Service layer: spreadsheets |  |
| `backend/app/services/spreadsheets/formula_engine.py` | app/services | Service layer: spreadsheets |  |
| `backend/app/services/spreadsheets/pivot_service.py` | app/services | Service layer: spreadsheets |  |
| `backend/app/services/spreadsheets/service.py` | app/services | Service layer: spreadsheets |  |
| `backend/app/services/state_access.py` | app/services | Service layer: state_access |  |
| `backend/app/services/static_files.py` | app/services | Service layer: static_files |  |
| `backend/app/services/summary/service.py` | app/services | Service layer: summary |  |
| `backend/app/services/synthesis/service.py` | app/services | Service layer: synthesis |  |
| `backend/app/services/templates/TemplateVerify.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/__init__.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/catalog.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/css_merge.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/errors.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/layout_hints.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/service.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/starter_catalog.py` | app/services | Service layer: templates |  |
| `backend/app/services/templates/strategies.py` | app/services | Service layer: templates |  |
| `backend/app/services/utils/__init__.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/artifacts.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/context.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/html.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/llm.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/lock.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/mailer.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/prompts.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/render.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/text.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/tokens.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/validation.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/utils/zip_tools.py` | app/services | Service layer: utils | utility-cluster |
| `backend/app/services/validation.py` | app/services | Service layer: validation |  |
| `backend/app/services/workflow/__init__.py` | app/services | Service layer: workflow |  |
| `backend/app/utils/__init__.py` | app/utils | Utility:   init   |  |
| `backend/app/utils/email_utils.py` | app/utils | Utility: email utils |  |
| `backend/app/utils/env_loader.py` | app/utils | Utility: env loader |  |
| `backend/app/utils/errors.py` | app/utils | Utility: errors |  |
| `backend/app/utils/event_bus.py` | app/utils | Utility: event bus |  |
| `backend/app/utils/fs.py` | app/utils | Utility: fs |  |
| `backend/app/utils/pipeline.py` | app/utils | Utility: pipeline |  |
| `backend/app/utils/result.py` | app/utils | Utility: result |  |
| `backend/app/utils/soft_delete.py` | app/utils | Utility: soft delete |  |
| `backend/app/utils/sql_safety.py` | app/utils | Utility: sql safety |  |
| `backend/app/utils/strategies.py` | app/utils | Utility: strategies |  |
| `backend/app/utils/validation.py` | app/utils | Utility: validation |  |
| `backend/engine/__init__.py` | engine |   init   |  |
| `backend/engine/adapters/__init__.py` | engine | Engine adapter: __init__ |  |
| `backend/engine/adapters/databases/__init__.py` | engine | Engine adapter: databases |  |
| `backend/engine/adapters/databases/base.py` | engine | Engine adapter: databases |  |
| `backend/engine/adapters/databases/dataframes/__init__.py` | engine | Engine adapter: databases/dataframes |  |
| `backend/engine/adapters/databases/dataframes/sqlite_loader.py` | engine | Engine adapter: databases/dataframes |  |
| `backend/engine/adapters/databases/dataframes/sqlite_shim.py` | engine | Engine adapter: databases/dataframes |  |
| `backend/engine/adapters/databases/dataframes/store.py` | engine | Engine adapter: databases/dataframes |  |
| `backend/engine/adapters/databases/sqlite.py` | engine | Engine adapter: databases |  |
| `backend/engine/adapters/extraction/__init__.py` | engine | Engine adapter: extraction |  |
| `backend/engine/adapters/extraction/base.py` | engine | Engine adapter: extraction |  |
| `backend/engine/adapters/extraction/excel.py` | engine | Engine adapter: extraction |  |
| `backend/engine/adapters/extraction/pdf.py` | engine | Engine adapter: extraction |  |
| `backend/engine/adapters/llm/__init__.py` | engine | Engine adapter: llm |  |
| `backend/engine/adapters/llm/base.py` | engine | Engine adapter: llm |  |
| `backend/engine/adapters/llm/openai.py` | engine | Engine adapter: llm |  |
| `backend/engine/adapters/persistence/__init__.py` | engine | Engine adapter: persistence |  |
| `backend/engine/adapters/persistence/base.py` | engine | Engine adapter: persistence |  |
| `backend/engine/adapters/persistence/repositories.py` | engine | Engine adapter: persistence |  |
| `backend/engine/adapters/rendering/__init__.py` | engine | Engine adapter: rendering |  |
| `backend/engine/adapters/rendering/base.py` | engine | Engine adapter: rendering |  |
| `backend/engine/adapters/rendering/docx.py` | engine | Engine adapter: rendering |  |
| `backend/engine/adapters/rendering/html.py` | engine | Engine adapter: rendering |  |
| `backend/engine/adapters/rendering/pdf.py` | engine | Engine adapter: rendering |  |
| `backend/engine/adapters/rendering/xlsx.py` | engine | Engine adapter: rendering |  |
| `backend/engine/core/__init__.py` | engine | Engine core utility:   init   | check-layer |
| `backend/engine/core/errors.py` | engine | Engine core utility: errors | check-layer |
| `backend/engine/core/events.py` | engine | Engine core utility: events | check-layer |
| `backend/engine/core/result.py` | engine | Engine core utility: result | check-layer |
| `backend/engine/core/types.py` | engine | Engine core utility: types | check-layer |
| `backend/engine/domain/__init__.py` | engine | Engine domain model:   init   |  |
| `backend/engine/domain/connections.py` | engine | Engine domain model: connections |  |
| `backend/engine/domain/contracts.py` | engine | Engine domain model: contracts |  |
| `backend/engine/domain/jobs.py` | engine | Engine domain model: jobs |  |
| `backend/engine/domain/reports.py` | engine | Engine domain model: reports |  |
| `backend/engine/domain/templates.py` | engine | Engine domain model: templates |  |
| `backend/engine/orchestration/__init__.py` | engine | Orchestration:   init   |  |
| `backend/engine/orchestration/executor.py` | engine | Orchestration: executor |  |
| `backend/engine/orchestration/scheduler.py` | engine | Orchestration: scheduler |  |
| `backend/engine/orchestration/worker.py` | engine | Orchestration: worker |  |
| `backend/engine/pipelines/__init__.py` | engine | Pipeline:   init   |  |
| `backend/engine/pipelines/base.py` | engine | Pipeline: base |  |
| `backend/engine/pipelines/import_pipeline.py` | engine | Pipeline: import pipeline |  |
| `backend/engine/pipelines/report_pipeline.py` | engine | Pipeline: report pipeline |  |
| `backend/legacy/__init__.py` | legacy |   init   |  |
| `backend/legacy/core/__init__.py` | legacy |   init   | check-layer |
| `backend/legacy/core/config.py` | legacy | config | check-layer |
| `backend/legacy/endpoints/__init__.py` | legacy | Legacy API endpoint:   init   |  |
| `backend/legacy/endpoints/artifacts.py` | legacy | Legacy API endpoint: artifacts |  |
| `backend/legacy/endpoints/connections.py` | legacy | Legacy API endpoint: connections |  |
| `backend/legacy/endpoints/feature_routes.py` | legacy | Legacy API endpoint: feature routes |  |
| `backend/legacy/endpoints/health.py` | legacy | Legacy API endpoint: health |  |
| `backend/legacy/endpoints/jobs.py` | legacy | Legacy API endpoint: jobs |  |
| `backend/legacy/endpoints/reports.py` | legacy | Legacy API endpoint: reports |  |
| `backend/legacy/endpoints/schedules.py` | legacy | Legacy API endpoint: schedules |  |
| `backend/legacy/endpoints/templates.py` | legacy | Legacy API endpoint: templates |  |
| `backend/legacy/routes.py` | legacy | routes |  |
| `backend/legacy/schemas/__init__.py` | legacy | Legacy schema:   init   |  |
| `backend/legacy/schemas/connection_schema.py` | legacy | Legacy schema: connection schema |  |
| `backend/legacy/schemas/report_schema.py` | legacy | Legacy schema: report schema |  |
| `backend/legacy/schemas/template_schema.py` | legacy | Legacy schema: template schema |  |
| `backend/legacy/services/__init__.py` | legacy | Legacy service:   init   |  |
| `backend/legacy/services/connection_inspector.py` | legacy | Legacy service: connection inspector |  |
| `backend/legacy/services/connection_service.py` | legacy | Legacy service: connection service |  |
| `backend/legacy/services/file_service/__init__.py` | legacy | Legacy service:   init   |  |
| `backend/legacy/services/file_service/artifacts.py` | legacy | Legacy service: artifacts |  |
| `backend/legacy/services/file_service/edit.py` | legacy | Legacy service: edit |  |
| `backend/legacy/services/file_service/generator.py` | legacy | Legacy service: generator |  |
| `backend/legacy/services/file_service/helpers.py` | legacy | Legacy service: helpers |  |
| `backend/legacy/services/file_service/verify.py` | legacy | Legacy service: verify |  |
| `backend/legacy/services/llm_service.py` | legacy | Legacy service: llm service |  |
| `backend/legacy/services/mapping/__init__.py` | legacy | Legacy service:   init   |  |
| `backend/legacy/services/mapping/approve.py` | legacy | Legacy service: approve |  |
| `backend/legacy/services/mapping/corrections.py` | legacy | Legacy service: corrections |  |
| `backend/legacy/services/mapping/helpers.py` | legacy | Legacy service: helpers |  |
| `backend/legacy/services/mapping/key_options.py` | legacy | Legacy service: key options |  |
| `backend/legacy/services/mapping/preview.py` | legacy | Legacy service: preview |  |
| `backend/legacy/services/report_service.py` | legacy | Legacy service: report service | god-file |
| `backend/legacy/services/scheduler_service.py` | legacy | Legacy service: scheduler service |  |
| `backend/legacy/services/template_service.py` | legacy | Legacy service: template service |  |
| `backend/legacy/utils/__init__.py` | legacy | Legacy utility:   init   |  |
| `backend/legacy/utils/connection_utils.py` | legacy | Legacy utility: connection utils |  |
| `backend/legacy/utils/email_utils.py` | legacy | Legacy utility: email utils |  |
| `backend/legacy/utils/health_utils.py` | legacy | Legacy utility: health utils |  |
| `backend/legacy/utils/mapping_utils.py` | legacy | Legacy utility: mapping utils |  |
| `backend/legacy/utils/schedule_utils.py` | legacy | Legacy utility: schedule utils |  |
| `backend/legacy/utils/template_utils.py` | legacy | Legacy utility: template utils |  |
| `backend/scripts/raster_html.py` | scripts | Backend script: raster html |  |
| `backend/tests/__init__.py` | tests | Test module for   init |  |
| `backend/tests/conftest.py` | tests | Test module for conftest |  |
| `backend/tests/test_adapters.py` | tests | Test module for adapters |  |
| `backend/tests/test_ai_integrations.py` | tests | Test module for ai integrations |  |
| `backend/tests/test_api_endpoints_comprehensive.py` | tests | Test module for api endpoints comprehensive |  |
| `backend/tests/test_api_mapping_approve_contract_v2.py` | tests | Test module for api mapping approve contract v2 |  |
| `backend/tests/test_chart_suggestions.py` | tests | Test module for chart suggestions |  |
| `backend/tests/test_chart_suggestions_fallback.py` | tests | Test module for chart suggestions fallback |  |
| `backend/tests/test_contract_adapter_filters.py` | tests | Test module for contract adapter filters |  |
| `backend/tests/test_contract_builder_sql.py` | tests | Test module for contract builder sql |  |
| `backend/tests/test_contract_schema_validation.py` | tests | Test module for contract schema validation |  |
| `backend/tests/test_contract_v2_schema.py` | tests | Test module for contract v2 schema |  |
| `backend/tests/test_critical_bugs.py` | tests | Test module for critical bugs |  |
| `backend/tests/test_css_merge.py` | tests | Test module for css merge |  |
| `backend/tests/test_discovery.py` | tests | Test module for discovery |  |
| `backend/tests/test_discovery_excel.py` | tests | Test module for discovery excel |  |
| `backend/tests/test_discovery_metrics_helpers.py` | tests | Test module for discovery metrics helpers |  |
| `backend/tests/test_docqa_feedback.py` | tests | Test module for docqa feedback |  |
| `backend/tests/test_enrichment_cache_stats.py` | tests | Test module for enrichment cache stats |  |
| `backend/tests/test_enrichment_sources.py` | tests | Test module for enrichment sources |  |
| `backend/tests/test_excel_verify_db_mapping.py` | tests | Test module for excel verify db mapping |  |
| `backend/tests/test_federation.py` | tests | Test module for federation |  |
| `backend/tests/test_fix_html.py` | tests | Test module for fix html |  |
| `backend/tests/test_generator_assets_v1_api.py` | tests | Test module for generator assets v1 api |  |
| `backend/tests/test_generator_assets_validation.py` | tests | Test module for generator assets validation |  |
| `backend/tests/test_html_raster_400dpi.py` | tests | Test module for html raster 400dpi |  |
| `backend/tests/test_html_sanitizer.py` | tests | Test module for html sanitizer |  |
| `backend/tests/test_jobs.py` | tests | Test module for jobs |  |
| `backend/tests/test_llm_call_3_5_invariants.py` | tests | Test module for llm call 3 5 invariants |  |
| `backend/tests/test_llm_call_3_5_schema.py` | tests | Test module for llm call 3 5 schema |  |
| `backend/tests/test_llm_call_3_validation.py` | tests | Test module for llm call 3 validation |  |
| `backend/tests/test_locking.py` | tests | Test module for locking |  |
| `backend/tests/test_mailer.py` | tests | Test module for mailer |  |
| `backend/tests/test_manifest_updates.py` | tests | Test module for manifest updates |  |
| `backend/tests/test_mapping_utils.py` | tests | Test module for mapping utils |  |
| `backend/tests/test_pdf_extractors_cache.py` | tests | Test module for pdf extractors cache |  |
| `backend/tests/test_persistence.py` | tests | Test module for persistence |  |
| `backend/tests/test_pipeline_integration.py` | tests | Test module for pipeline integration |  |
| `backend/tests/test_pipeline_stage_3_5_integration.py` | tests | Test module for pipeline stage 3 5 integration |  |
| `backend/tests/test_pipeline_verification.py` | tests | Test module for pipeline verification |  |
| `backend/tests/test_report_generate_autoload.py` | tests | Test module for report generate autoload |  |
| `backend/tests/test_saved_charts.py` | tests | Test module for saved charts |  |
| `backend/tests/test_scheduler_date_range.py` | tests | Test module for scheduler date range |  |
| `backend/tests/test_scheduler_email.py` | tests | Test module for scheduler email |  |
| `backend/tests/test_schema_normalize.py` | tests | Test module for schema normalize |  |
| `backend/tests/test_template_edit.py` | tests | Test module for template edit |  |
| `backend/tests/test_template_initial_html.py` | tests | Test module for template initial html |  |
| `backend/tests/test_template_recommend_api.py` | tests | Test module for template recommend api |  |
| `backend/tests/test_v4_connections.py` | tests | Test module for v4 connections |  |
| `backend/tests/test_v4_templates.py` | tests | Test module for v4 templates |  |
| `backend/tests/test_validate_excel_bundle.py` | tests | Test module for validate excel bundle |  |
| `backend/tests/test_zip_tools_limits.py` | tests | Test module for zip tools limits |  |
