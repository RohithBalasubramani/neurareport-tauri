# Architecture Exception

Exception ID: ARCH-EXC-001
Date: 2026-01-23
Rule violated: APP-IMPORT-ENGINE (backend/app/* must not import backend.engine.*)
Location in code: backend/app/api/routes/legacy.py
Justification: Legacy compatibility endpoints require direct engine access until v1 pipeline endpoints are retired.
Scope (files affected): backend/app/api/routes/legacy.py (engine import blocks)
Risk: Tight coupling to engine internals; harder to evolve engine API.
Expiry condition: Remove when legacy pipeline endpoints are retired or routed through backend/app/services.
Removal plan: Replace direct engine imports with service-layer adapters and delete legacy endpoints.
Owner: Backend Architecture
