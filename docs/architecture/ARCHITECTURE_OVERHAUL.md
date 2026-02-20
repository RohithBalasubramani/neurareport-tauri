# NeuraReport Backend Architecture Overhaul

> Note (2026-01-23): legacy `src/` references in this document now map to `backend/legacy/`, and the pipeline engine lives under `backend/engine/`.

## Step 1: STRUCTURAL MAP

### Domain Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CURRENT ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        API LAYER (Fragmented)                        │   │
│  │  backend/api.py (monolith) + backend/app/api/ + src/endpoints/      │   │
│  │  - 3 separate routing systems                                       │   │
│  │  - Mixed concerns (routes define business logic)                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SERVICE LAYER (Scattered)                        │   │
│  │  backend/app/services/ + src/services/                              │   │
│  │  - Duplicated: mapping, reports, templates                          │   │
│  │  - Circular imports between backend and src                         │   │
│  │  - 2084-line ReportGenerate.py (god object)                         │   │
│  │  - 873-line ContractBuilderV2.py (LLM-coupled)                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     STATE MANAGEMENT (Monolith)                      │   │
│  │  StateStore: 1366 lines                                             │   │
│  │  - Connections, Templates, Jobs, Schedules, Charts, Activity        │   │
│  │  - Single JSON file for ALL state                                   │   │
│  │  - Thread locks across unrelated domains                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     IO LAYER (Ad-hoc)                                │   │
│  │  - PDF: Tabula + Camelot + PyMuPDF + pdfplumber (no unified API)   │   │
│  │  - Excel: openpyxl + pandas (scattered)                             │   │
│  │  - LLM: Circuit breaker + caching (good) but tightly coupled        │   │
│  │  - DB: SQLite only, hardcoded throughout                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     JOB ORCHESTRATION (Manual)                       │   │
│  │  - ReportScheduler: Polling loop with asyncio                       │   │
│  │  - ThreadPoolExecutor for jobs                                      │   │
│  │  - Manual cancellation via ctypes thread injection                  │   │
│  │  - No retry, no dead-letter, no observability                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Analysis

```
Template Import:
  ZIP Upload → TemplateService.import_zip() → PipelineRunner → StateStore
                  ↓
             Event emission (good pattern, underused)

Report Generation (CRITICAL PATH):
  RunPayload → report_service._run_report_internal()
       │
       ├─→ db_path_from_payload_or_default() [scattered utility]
       ├─→ _ensure_contract_files() [validation buried in runner]
       ├─→ ReportGenerate.fill_and_print() [2084 lines, sync]
       │       │
       │       ├─→ SQLiteDataFrameLoader [direct DB access]
       │       ├─→ ContractAdapter [data mapping]
       │       ├─→ discover_batches_and_counts() [query generation]
       │       ├─→ SQL execution (inline, not parameterized properly)
       │       ├─→ HTML manipulation (regex-based, fragile)
       │       └─→ Playwright PDF render (sync wrapped in asyncio.run)
       │
       ├─→ render_strategy.render_docx() [post-processing]
       ├─→ render_strategy.render_xlsx() [post-processing]
       └─→ notification_strategy.send() [email]
```

### Async/Sync Points (PROBLEM AREAS)

1. **ReportGenerate.fill_and_print**: Synchronous 2000+ line function
   - Calls `asyncio.run()` internally for Playwright
   - Blocks the thread pool executor
   - No cancellation points

2. **StateStore**: All operations under `threading.RLock()`
   - Writes to disk on every mutation
   - No batching, no async IO

3. **LLM Client**: Good async potential but called synchronously
   - `call_chat_completion()` is blocking
   - Circuit breaker is thread-safe but not async

4. **PDF Extraction**: Parallelized via `concurrent.futures`
   - Good, but extraction config is not injectable
   - No streaming results

### Validation Layers (SCATTERED)

- `backend/app/core/validation.py`: Input sanitization
- `backend/app/services/utils/validation.py`: Contract validation
- Pydantic schemas in multiple locations
- Inline validation in route handlers
- No unified validation pipeline

---

## Step 2: OPEN-SOURCE ARCHITECTURE COMPARISONS

### For Report/Document Generation

| Project | Pattern | What NeuraReport Should Learn |
|---------|---------|-------------------------------|
| **WeasyPrint/xhtml2pdf** | Pipeline + Adapter | Clean IO separation, pluggable renderers |
| **JasperReports** | Template Engine + Data Source | Strict separation of template/data/render |
| **Apache POI** | Streaming API | Large document handling without memory bloat |

### For Data Pipeline/ETL

| Project | Pattern | What NeuraReport Should Learn |
|---------|---------|-------------------------------|
| **Dagster** | Asset-Oriented DAG | Declarative pipelines, type-safe contracts |
| **Prefect** | Task Orchestration | Retry, caching, observability built-in |
| **Airbyte** | Source/Destination Adapters | Clean IO abstraction, schema discovery |
| **dbt** | SQL Transformation | Contract-first data modeling |

### For LLM Integration

| Project | Pattern | What NeuraReport Should Learn |
|---------|---------|-------------------------------|
| **LangChain** | Chain/Agent Abstraction | Composable LLM calls, prompt templates |
| **LlamaIndex** | Index + Query Engine | Structured data extraction, caching |
| **Instructor** | Pydantic Output Parsing | Type-safe LLM responses |

### For Job Orchestration

| Project | Pattern | What NeuraReport Should Learn |
|---------|---------|-------------------------------|
| **Temporal** | Workflow-as-Code | Durable execution, automatic retries |
| **Celery** | Task Queue | Distributed workers, result backends |
| **Dramatiq** | Actor Model | Simple task definition, middleware |

### Patterns These Projects Use

1. **Pipeline Pattern** (Dagster, Prefect): Steps are first-class, composable
2. **Adapter Pattern** (Airbyte): IO is abstracted behind interfaces
3. **Repository Pattern** (many): Data access isolated from business logic
4. **CQRS** (Temporal): Commands vs queries separated
5. **Event Sourcing** (Temporal): State changes are events
6. **Strategy Pattern** (existing in code but underused)

---

## Step 3: CURRENT DESIGN IS INADEQUATE

### Why It Does Not Scale

1. **Single JSON State File**: All state in one file under one lock
   - Connection ping writes block template metadata reads
   - Job progress updates compete with schedule writes
   - No horizontal scaling possible

2. **Monolithic Report Generator**: 2084 lines in one function
   - Cannot parallelize batch processing
   - Cannot resume failed reports
   - Memory-bound for large datasets

3. **Sync-First Architecture**: asyncio.run() calls inside sync functions
   - Thread pool exhaustion under load
   - No backpressure mechanism

### Why It Does Not Compose

1. **Circular Dependencies**: `src/` imports from `backend/`, `backend/` imports from `src/`
   - Cannot test in isolation
   - Cannot replace components

2. **God Objects**: StateStore, ReportGenerate, ContractBuilderV2
   - Single Responsibility violated
   - Changes ripple everywhere

3. **Implicit Contracts**: Data flows through dicts, not typed interfaces
   - Runtime errors instead of compile-time
   - No IDE support for refactoring

### Why It Does Not Evolve

1. **LLM Coupling**: ContractBuilderV2 embeds LLM calls
   - Cannot test contract logic without LLM
   - Cannot swap LLM providers easily

2. **Hardcoded SQLite**: Database access scattered throughout
   - Cannot add PostgreSQL without major refactor
   - No query abstraction

3. **Template Format Lock-in**: HTML/PDF logic intertwined
   - Cannot add new output formats
   - Cannot change templating engine

---

## Step 4: NEW ARCHITECTURE DESIGN

### Directory Structure

```
backend/
├── __init__.py
├── main.py                    # FastAPI app factory (thin)
│
├── domain/                    # PURE BUSINESS LOGIC (no IO)
│   ├── __init__.py
│   ├── contracts/             # Report contracts
│   │   ├── __init__.py
│   │   ├── entities.py        # Contract, Token, Mapping dataclasses
│   │   ├── builder.py         # Contract building (no LLM)
│   │   └── validator.py       # Schema validation
│   │
│   ├── reports/               # Report generation
│   │   ├── __init__.py
│   │   ├── entities.py        # Report, Batch, RenderOutput
│   │   ├── renderer.py        # Pure render logic
│   │   └── token_engine.py    # Token substitution
│   │
│   ├── templates/             # Template management
│   │   ├── __init__.py
│   │   ├── entities.py        # Template, Artifact
│   │   └── catalog.py         # Template catalog logic
│   │
│   ├── connections/           # DB connections
│   │   ├── __init__.py
│   │   └── entities.py        # Connection, ConnectionTest
│   │
│   └── jobs/                  # Job tracking
│       ├── __init__.py
│       ├── entities.py        # Job, Step, Schedule
│       └── state_machine.py   # Job status transitions
│
├── adapters/                  # IO ADAPTERS (side effects here)
│   ├── __init__.py
│   │
│   ├── persistence/           # State storage
│   │   ├── __init__.py
│   │   ├── base.py            # Repository interfaces
│   │   ├── json_store.py      # Current JSON implementation
│   │   ├── sqlite_store.py    # SQLite for state (new)
│   │   └── migrations/        # State schema migrations
│   │
│   ├── databases/             # Data source access
│   │   ├── __init__.py
│   │   ├── base.py            # DataSource interface
│   │   ├── sqlite.py          # SQLite adapter
│   │   ├── postgres.py        # PostgreSQL adapter (future)
│   │   └── discovery.py       # Schema discovery
│   │
│   ├── extraction/            # Document extraction
│   │   ├── __init__.py
│   │   ├── base.py            # Extractor interface
│   │   ├── pdf.py             # PDF extraction (unified)
│   │   └── excel.py           # Excel extraction
│   │
│   ├── rendering/             # Output rendering
│   │   ├── __init__.py
│   │   ├── base.py            # Renderer interface
│   │   ├── html.py            # HTML generation
│   │   ├── pdf.py             # PDF via Playwright
│   │   ├── docx.py            # DOCX export
│   │   └── xlsx.py            # XLSX export
│   │
│   ├── llm/                   # LLM integration
│   │   ├── __init__.py
│   │   ├── base.py            # LLM interface
│   │   ├── openai.py          # OpenAI adapter
│   │   ├── anthropic.py       # Anthropic adapter
│   │   └── prompts/           # Prompt templates
│   │
│   └── notifications/         # Notifications
│       ├── __init__.py
│       ├── base.py            # Notifier interface
│       └── email.py           # Email adapter
│
├── pipelines/                 # WORKFLOW ORCHESTRATION
│   ├── __init__.py
│   ├── base.py                # Pipeline, Step, Context
│   ├── report_pipeline.py     # Report generation pipeline
│   ├── import_pipeline.py     # Template import pipeline
│   ├── mapping_pipeline.py    # Auto-mapping pipeline
│   └── steps/                 # Reusable pipeline steps
│       ├── __init__.py
│       ├── validation.py
│       ├── data_loading.py
│       ├── rendering.py
│       └── notifications.py
│
├── orchestration/             # JOB SCHEDULING
│   ├── __init__.py
│   ├── scheduler.py           # Job scheduler (refactored)
│   ├── executor.py            # Job execution
│   ├── worker.py              # Worker pool
│   └── retry.py               # Retry policies
│
├── api/                       # HTTP LAYER (thin)
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── templates.py
│   │   ├── connections.py
│   │   ├── reports.py
│   │   └── jobs.py
│   ├── middleware.py
│   ├── dependencies.py        # DI container
│   └── schemas.py             # Request/Response models
│
├── core/                      # CROSS-CUTTING CONCERNS
│   ├── __init__.py
│   ├── config.py              # Settings
│   ├── errors.py              # Error types
│   ├── events.py              # Event bus
│   ├── result.py              # Result type
│   └── observability.py       # Logging, metrics, traces
│
└── tests/
    ├── unit/
    │   ├── domain/
    │   └── adapters/
    ├── integration/
    └── e2e/
```

### Key Architectural Decisions

#### 1. Domain Layer is Pure
- No IO, no side effects
- Testable without mocks
- Contracts are dataclasses with validation

#### 2. Adapters are Swappable
- Interface-first design
- JSON store → SQLite store → PostgreSQL
- OpenAI → Anthropic → Local LLM

#### 3. Pipelines are Declarative
```python
report_pipeline = Pipeline(
    steps=[
        Step("validate", validate_payload),
        Step("load_contract", load_contract),
        Step("load_data", load_data_batches),
        Step("render_html", render_html),
        Step("render_pdf", render_pdf, guard=lambda ctx: ctx.output_formats.pdf),
        Step("render_docx", render_docx, guard=lambda ctx: ctx.output_formats.docx),
        Step("notify", send_notification, guard=lambda ctx: ctx.recipients),
    ],
    on_error=rollback_artifacts,
    on_success=persist_manifest,
)
```

#### 4. Jobs are First-Class
- Jobs have state machines
- Steps are trackable
- Cancellation is cooperative

#### 5. Observability is Built-In
- Structured logging
- OpenTelemetry traces
- Prometheus metrics

---

## Step 5: IMPLEMENTATION PLAN

### Phase 1: Foundation (This PR)
1. Create new directory structure
2. Define core interfaces (Result, Error, Events)
3. Create adapter interfaces
4. Migrate StateStore to repository pattern

### Phase 2: Domain Extraction
1. Extract Report entities
2. Extract Contract entities
3. Extract Template entities
4. Pure validation logic

### Phase 3: Adapter Implementation
1. Implement persistence adapters
2. Implement rendering adapters
3. Implement LLM adapters

### Phase 4: Pipeline Migration
1. Implement Pipeline base
2. Migrate report generation to pipeline
3. Migrate template import to pipeline

### Phase 5: Orchestration
1. Refactor scheduler
2. Implement worker pool
3. Add retry policies

---

## Breaking Changes

This refactor WILL break:
1. Direct imports from `backend.app.services.reports.ReportGenerate`
2. Direct access to `state_store` singleton
3. Route definitions in `src/` (will be removed)
4. Existing tests that mock internal functions

This is intentional. The old patterns must die.

---

## Step 6: IMPLEMENTATION COMPLETE

### What Was Built

The new architecture has been implemented in `backend/v2/` with the following structure:

```
backend/v2/
├── __init__.py                 # Version 2.0.0
├── main.py                     # FastAPI entry point
├── migration.py                # v1-to-v2 compatibility shims
│
├── core/                       # Cross-cutting concerns
│   ├── __init__.py
│   ├── result.py               # Result<T, E> monad
│   ├── errors.py               # Typed domain errors
│   └── events.py               # Event bus with typed events
│
├── domain/                     # Pure business logic (NO IO)
│   ├── __init__.py
│   ├── contracts/              # Contract entities & validation
│   │   ├── entities.py         # Contract, Token, Mapping
│   │   ├── builder.py          # ContractBuilder
│   │   └── validator.py        # Contract validation
│   ├── reports/                # Report entities & rendering
│   │   ├── entities.py         # Report, Batch, RenderOutput
│   │   └── renderer.py         # TokenEngine (pure)
│   ├── templates/              # Template entities
│   │   └── entities.py         # Template, TemplateArtifacts
│   ├── connections/            # Connection entities
│   │   └── entities.py         # Connection, ConnectionConfig
│   └── jobs/                   # Job tracking
│       ├── entities.py         # Job, JobStep, Schedule
│       └── state_machine.py    # Job lifecycle FSM
│
├── adapters/                   # IO layer (all side effects)
│   ├── __init__.py
│   ├── persistence/            # State storage
│   │   ├── base.py             # Repository interfaces
│   │   └── json_store.py       # JSON implementation (wraps legacy)
│   ├── databases/              # Data source access
│   │   ├── base.py             # DataSource interface
│   │   └── sqlite.py           # SQLite implementation
│   ├── rendering/              # Document output
│   │   ├── base.py             # Renderer interface
│   │   ├── pdf.py              # Playwright PDF
│   │   └── docx.py             # HTML-to-DOCX
│   ├── llm/                    # LLM integration
│   │   ├── base.py             # LLMClient interface
│   │   └── openai.py           # OpenAI implementation
│   └── notifications/          # Notifications
│       ├── base.py             # Notifier interface
│       └── email.py            # SMTP implementation
│
├── pipelines/                  # Workflow orchestration
│   ├── __init__.py
│   ├── base.py                 # Pipeline, Step, PipelineContext
│   ├── report_pipeline.py      # Report generation workflow
│   └── import_pipeline.py      # Template import workflow
│
├── orchestration/              # Job scheduling
│   ├── __init__.py
│   ├── scheduler.py            # Schedule polling & dispatch
│   ├── executor.py             # Job execution & tracking
│   └── worker.py               # Worker pool
│
├── api/                        # HTTP layer (thin)
│   ├── __init__.py
│   ├── app.py                  # FastAPI factory
│   ├── dependencies.py         # DI container
│   └── routes/                 # Endpoint handlers
│       ├── health.py
│       ├── templates.py
│       ├── connections.py
│       ├── reports.py
│       └── jobs.py
│
└── tests/                      # Unit tests
    ├── test_core.py
    ├── test_domain.py
    └── test_pipelines.py
```

### Key Patterns Implemented

1. **Result Monad**: All operations return `Result[T, E]` for explicit error handling
2. **Repository Pattern**: All persistence through interfaces
3. **Adapter Pattern**: All IO behind swappable interfaces
4. **Pipeline Pattern**: Declarative step-based workflows with guards and rollback
5. **Event Bus**: Decoupled communication via typed events
6. **State Machine**: Job lifecycle with validated transitions
7. **Dependency Injection**: Central DI container for testability

### Migration Path

1. **Immediate**: Use `backend.v2.migration` for v1-compatible endpoints
2. **Gradual**: Replace v1 imports with v2 equivalents
3. **Final**: Remove old code paths once migration is validated

### Running the New Backend

```bash
# Run v2 backend
uvicorn backend.v2.main:app --reload --port 8000

# Run tests
pytest backend/v2/tests/ -v
```

### What Was NOT Migrated

The following v1 code remains and should be deleted once v2 is validated:
- `backend/app/services/reports/ReportGenerate.py` (2084 lines)
- `backend/app/services/contracts/ContractBuilderV2.py` (873 lines)
- `src/services/report_service.py` (1268 lines)
- Direct state store usage throughout `src/`

### Metrics

| Metric | v1 | v2 |
|--------|----|----|
| Report generator lines | 2084 | ~200 (pipeline steps) |
| State store coupling | Global singleton | Injected repository |
| Error handling | Try/except everywhere | Result monad |
| Testability | Requires full stack | Pure domain functions |
| Async support | Mixed sync/async | Async-first |

---

## Next Steps

1. **Validate**: Run v2 in parallel with v1, compare outputs
2. **Migrate Frontend**: Update API calls to v2 endpoints
3. **Delete v1**: Remove old code paths
4. **Optimize**: Add caching, streaming for large reports
