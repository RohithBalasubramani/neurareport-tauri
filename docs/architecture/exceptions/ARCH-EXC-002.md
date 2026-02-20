# Architecture Exception

Exception ID: ARCH-EXC-002
Date: 2026-01-23
Rule violated: APP-API-IMPORT-SCOPE (Only backend/app/api/* may import backend.app.api.*)
Location in code: backend/api.py
Justification: backend/api.py is the legacy app entrypoint and must wire API middleware/router from backend/app/api without duplicating route registration.
Scope (files affected): backend/api.py (backend.app.api middleware/router imports)
Risk: Entry point coupled to app API module structure; changes to backend/app/api require coordinated updates here.
Expiry condition: Remove when backend/api.py is retired or replaced by an entrypoint under backend/app/api.
Removal plan: Promote a new backend/app/api entrypoint and delete backend/api.py imports of backend.app.api.*.
Owner: Backend Architecture
