from __future__ import annotations

from fastapi import APIRouter

from backend.legacy.endpoints import (
    artifacts,
    connections,
    health,
    jobs,
    reports,
    schedules,
    templates,
)
from backend.legacy.endpoints.feature_routes import build_feature_routers

router = APIRouter()

# Core routers
for r in (
    health.router,
    connections.router,
    jobs.router,
    schedules.router,
    artifacts.router,
    reports.router,
    templates.router,
):
    router.include_router(r)

# Feature routers (saved charts, chart suggestions, discovery)
saved_charts_router, chart_suggest_router, discover_router = build_feature_routers()
for r in (saved_charts_router, chart_suggest_router, discover_router):
    router.include_router(r)


__all__ = ["router"]
