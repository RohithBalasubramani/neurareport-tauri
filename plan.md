NeuraReport Architecture Modernization Report (Research-Only Blueprint)
Per your instruction: I am not implementing fixes. This is a plan derived from the curated repos you listed, mapped onto NeuraReport’s concrete gaps (29 routes / 2534 UI actions, backend “god files”, CI and architecture enforcement issues).

1) Current-State Findings (Repo Reality)
UI surface

Inventory: MASTER-ACTION-INVENTORY.json = 29 routes / 2534 actions.
Highest-action routes (risk hotspots): /design 342, /history 245, /jobs 240, /connections 204, /templates 195.
Accessibility/testability gaps (from the same inventory):
698/2534 actions have no accessible name (ariaLabel empty + text empty + href empty), worst on /documents (106/136) and /design (158/342).
909/2534 actions have type="unknown", worst on /history and /jobs.
Backend architecture

Governance rules exist and are correct in spirit: ARCHITECTURE_GOVERNANCE.md.
Enforcement currently fails on:
report_tasks.py importing backend.engine.* (forbidden by your rules).
prodo/** being scanned as if it were source (deployment snapshot is triggering violations).
Code hotspots (where architecture debt concentrates)

store.py ~2680 LOC (multi-domain state monolith)
ReportGenerate.py ~2104 LOC (report generation monolith)
pdf_extractors.py ~1661 LOC
client.py ~1205 LOC
client.js ~3293 LOC
Feature-unlock blockers

CI runs verify_pipeline.py with samples/uploads, but samples/uploads/ is empty, so pipeline verification is not reproducible.
Worker/job orchestration is fragmented (legacy scheduler/executor patterns + new worker tasks), so “async job processing” features won’t be reliably SOTA until unified.
2) Target Backend Architecture (Use Clean/Hexagonal Pattern, Not Ad-Hoc Services)
Reference: ivan-borovets/fastapi-clean-example
This repo’s structure formalizes a clean split across domain / application (commands+queries) / infrastructure / presentation / setup (IoC).

How to apply to NeuraReport (mapping, not code changes)

Keep your backend/app/api as presentation (FastAPI routers, request/response DTOs).
Replace “fat services” with an explicit application layer:
backend/app/application/commands/* (mutations: run report, approve mapping, enqueue job, ingest docs)
backend/app/application/queries/* (reads: list templates, preview mapping, search docs, get job status)
Make backend/app/domain/* real:
Entities + rules for Templates, Contracts, Jobs, Documents, Connections.
This is where you remove business logic from StateStore, ReportGenerate, and route handlers.
Consolidate integration details in backend/app/infrastructure/*:
DB session factories, file storage adapters, vector store adapters, LLM provider adapters.
Dependency enforcement: import-linter
Clean-example explicitly calls out import-linter as part of its architecture toolchain (and your repo is already doing a custom AST enforcer).

How to apply

Use import-linter contracts to enforce:
Presentation cannot import infrastructure directly.
Domain cannot import FastAPI/SQLAlchemy/LLM providers.
Application orchestrates domain + ports (interfaces), infrastructure provides adapters.
This replaces “tribal knowledge” with a mechanically enforced architecture contract.

3) Persistence + Migrations (Replace JSON “StateStore” as the System of Record)
Reference: Full-stack template + SQLAlchemy/Alembic
The FastAPI full-stack template is explicitly built around a “production-grade” backend stack with DB + migrations patterns, and highlights “automatic” frontend client generation.
Alembic exists for schema migrations and supports “autogenerate” from SQLAlchemy metadata.

How to apply

Define DB-backed tables for the things StateStore currently multiplexes:
templates, contracts, mappings, jobs, job_steps, schedules, documents, document_versions, agent_tasks.
Keep file artifacts on disk/S3, but store metadata and references in DB (manifest rows, checksums, build timestamps).
Use Alembic for versioning, including autogeneration where safe.
Why this unlocks features

True multi-worker execution (jobs state isn’t a single locked JSON file).
Reliable history pages (/history, /jobs, /reports) without race conditions.
Real queryability for analytics and monitoring.
4) Vector Search + RAG (Pick One Storage + One Pipeline Framework)
Storage options
Option A: Postgres + pgvector

pgvector is a Postgres extension (you “CREATE EXTENSION vector”).
pgvector-python provides a Python client integration.
Option B: Qdrant

Qdrant is a dedicated vector DB; quickstart is container-first.
How to choose

If you want one operational surface (Postgres only): pgvector.
If you want scalable ANN retrieval + dedicated vector ops: Qdrant.
Pipeline/framework options
Haystack (pipeline-first RAG)

Haystack provides explicit pipelines with generator components (example shows Pipeline + OpenAIGenerator).
LangChain (abstraction layer across models/tools/retrievers)

LangChain positions itself as a “standard interface” for many LLM providers and composable chains/agents.
LlamaIndex (data connectors + retrieval/query engine)

LlamaIndex focuses on ingesting “unstructured data into LLM-friendly formats” and building “Index / Retriever / Query Engine” flows.
How to apply to NeuraReport

Define an internal VectorStorePort + RetrieverPort (interfaces) in application/domain.
Implement adapters:
PgvectorVectorStoreAdapter OR QdrantVectorStoreAdapter.
Implement a single “RAG orchestration” service in application layer, backed by:
Haystack pipelines (if you want explicit DAGs)
OR LlamaIndex (if connectors/indexing are key)
OR LangChain (if agents/tool-calling is dominant)
This prevents your current “LLM client” from becoming the universal god-object.

5) Durable Orchestration (Unify Jobs/Reports into One System)
Options you listed
Dramatiq

Actor-based background tasks with a simple “define actor → run worker” model.
Celery

Distributed task queue model (battle-tested patterns).
Temporal

Durable execution/workflows with reliability/resumability as a platform goal.
How to apply (recommended decision path)

Pick one as the “source of truth” for job execution.
Make HTTP routes enqueue workflows/tasks and return job IDs.
Make /jobs, /history, /reports read from the durable job state store (DB tables).
Why this matters for your 29-page UI

Many disabled actions (Generate Report, Schedule, Queue in Background, etc.) become reliably usable only when orchestration + job state are coherent.
6) Observability (API + Workers + Pipelines)
OpenTelemetry
FastAPI instrumentation is first-class (FastAPIInstrumentor.instrument_app(...)).

Prometheus metrics
prometheus/client_python provides the Python client for Prometheus instrumentation.

How to apply

Instrument:
HTTP requests (latency, status counts)
Job/workflow step durations
LLM call latency, tokens, retries, circuit breaker opens
Vector store latency and hit rates
Emit correlation IDs into traces and job events so /ops can actually diagnose failures.
7) Security + Secrets + IAM (MFA/RBAC That Scales)
Secrets
Vault AppRole is a standard pattern for machine auth/secret rotation.
hashicorp/vault-examples provides example setups.

Identity + authorization
Ory Kratos: identity/auth system.
Ory Keto: authorization engine.
Keycloak: widely used IAM/IdP.
How to apply

Decide: “Bring your own IdP” (Keycloak/Ory) vs “in-app auth”.
Keep NeuraReport backend as a resource server; validate JWT/OIDC tokens; map roles/permissions to your existing RBAC checks.
Add MFA at the IdP layer rather than reinventing it inside FastAPI.
8) Frontend Contract Safety + Testing + Accessibility (Make 2534 Actions Sustainable)
Typed API clients: openapi-generator
The CLI exists specifically to generate clients/SDKs from OpenAPI specs.
The full-stack FastAPI template explicitly calls out automatic frontend client generation.

How to apply

Generate a typed TS client from FastAPI OpenAPI.
Replace the monolithic client.js with per-domain clients:
templates, reports, jobs, documents, agents, search, connectors, etc.
This will eliminate drift and reduce the need for massive manual endpoint wiring maps.
Unit tests: vitest
Vitest is designed for Vite-native test workflows and includes “watch mode” + compatibility goals.

Accessibility testing: axe-core + Playwright + pa11y
Playwright docs show using @axe-core/playwright for automated a11y checks.
pa11y-ci exists as CI-first accessibility automation.

How to apply to your action inventory

Make “accessible name present” a baseline rule for interactive elements:
Your inventory shows 698 unnamed actions; concentrate first on /documents and /design.
Standardize stable selectors:
Add data-testid to elements that are icon-only or structurally unstable.
Gate in CI:
Playwright smoke on all 29 routes
Axe scan on critical pages (/documents, /design, /templates, /reports, /jobs)
pa11y-ci as an additional safety net
State management: pmndrs/zustand
Zustand is explicitly a state management library and supports modular patterns that fit your “store sprawl” issue.

How to apply

Move from one “god store” toward store slices per domain:
templates slice, jobs slice, documents slice, etc.
Match the backend’s future domain boundaries so pages don’t cross-import random state.
9) Contract Testing + Fuzzing (Stop Regressions at the API Boundary)
Schemathesis
Schemathesis is explicitly for “property-based testing” of APIs using OpenAPI.

Pact (consumer-driven contracts)
Pact JS is built for consumer-driven contract testing.

How to apply

Generate OpenAPI from FastAPI; run Schemathesis in CI against a test server.
Use Pact on frontend for critical consumer contracts (templates, reports, jobs) to prevent breaking UI flows.
10) Prompt Versioning + Hallucination/Factuality Gates (Make AI Features SOTA)
Prompt registry/versioning: promptsource
Promptsource is a prompt toolkit/repository concept you can adapt to formalize prompt versioning and evaluation.

Factuality evaluation: OpenFactCheck + hallucination detector
OpenFactCheck proposes an evaluation approach for “LLM factuality”.
Exa hallucination detector provides tooling ideas for detecting hallucinations.
How to apply

Add offline evals for:
agents outputs
NL2SQL generation (correctness + safety)
doc QA citations/attribution quality
Gate releases on eval scores, not anecdotes.
11) Route-by-Route “Unlock” Focus (29 Pages, Practical Priorities)
Given action volume and current “disabled” states, prioritize unlock work in this order:

/templates + /connections + /reports + /jobs
These power the core template → mapping → contract → report → job history loop.
Architecture unlock depends on DB-backed state + durable orchestration + typed API clients.
/documents + /docqa + /search + /knowledge
These become SOTA only when retrieval (pgvector/Qdrant) + RAG framework (Haystack/LlamaIndex/LangChain) is consistent and observable.
/design + /dashboard-builder + /visualization
Highest UI action density and a11y naming gaps; needs stable selectors and accessibility gates.
12) Phased Delivery Plan (What To Do Next, Using Only Your Curated Repos)
Phase 0: Make enforcement + CI truthful (days)

Make architecture enforcement ignore deployment snapshots (prodo/) or remove them from the “source” contract.
Fix CI pipeline artifact verification by adding deterministic fixtures or generating them in CI (so verify_pipeline.py can pass).
Choose orchestration system (Dramatiq vs Celery vs Temporal) and define the “job state model”.
Phase 1: Core workflow SOTA (1–2 weeks)

Introduce application layer (commands/queries) and start moving logic out of route modules and monolithic services.
Introduce DB tables + Alembic migrations for jobs/templates/contracts; begin retiring StateStore as system-of-record.
Generate typed frontend client from OpenAPI and split the frontend API surface by domain.
Phase 2: Retrieval + AI evals + a11y gates (1–2 months)

Pick pgvector or Qdrant and build a single retrieval interface.
Pick Haystack/LlamaIndex/LangChain and standardize RAG + agents.
Add a11y gating (Playwright + axe + pa11y) until the “698 unnamed actions” number trends toward zero.
Add factuality/hallucination evaluation harness for AI features.
If you want, I can produce a second report that is a strict “implementation checklist” (file-by-file tasks) that directly maps:

each of the 29 UI routes
to the backend route module(s) in backend/app/api/routes/*
to the exact architecture upgrade steps above (DB, orchestration, RAG, observability, a11y, contract tests).

implement all these and stick to this only. dont deviate or go on your own track applying your own solutions