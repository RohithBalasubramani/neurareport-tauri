# Architecture Exception

Exception ID: ARCH-EXC-003
Date: 2026-01-23
Rule violated: APP-API-IMPORT-SCOPE (Only backend/app/api/* may import backend.app.api.*)
Location in code: backend/legacy/endpoints/feature_routes.py
Justification: Legacy feature routes are composed from backend.app.api.generate router builders; removing these imports would require duplicating API route logic or introduce circular imports.
Scope (files affected): backend/legacy/endpoints/feature_routes.py (generate router builder imports)
Risk: Legacy layer depends on app API router builders; changes to generate routes can break legacy endpoints.
Expiry condition: Remove when legacy feature endpoints are retired or migrated into backend/app/api/routes/legacy.
Removal plan: Replace legacy feature routers with service-layer adapters or delete the legacy endpoints entirely.
Owner: Backend Architecture
