"""API route modules for the NeuraReport FastAPI application.

This package contains all API route modules, organized by domain:

Core Routes:
- health: Health checks and readiness probes
- connections: Database connection management
- templates: Template CRUD, verification, and editing
- excel: Excel-specific template operations
- reports: Report generation and history
- jobs: Background job management
- schedules: Report scheduling
- state: Application state management

Analytics:
- analytics: Dashboard stats, activity log, bulk operations

AI Features:
- nl2sql: Natural language to SQL queries
- enrichment: Data enrichment
- federation: Cross-database federation
- recommendations: AI recommendations
- charts: Chart generation
- summary: Document summarization
- synthesis: Multi-document synthesis
- docqa: Document Q&A chat
"""

from . import (
    agents,
    agents_v2,
    ai,
    analytics,
    audit,
    charts,
    connections,
    connectors,
    dashboards,
    design,
    docai,
    docqa,
    documents,
    enrichment,
    excel,
    export,
    federation,
    health,
    ingestion,
    jobs,
    knowledge,
    legacy,
    nl2sql,
    recommendations,
    reports,
    schedules,
    search,
    spreadsheets,
    state,
    summary,
    synthesis,
    templates,
    visualization,
    workflows,
)

__all__ = [
    "agents",
    "agents_v2",
    "ai",
    "analytics",
    "audit",
    "charts",
    "connections",
    "connectors",
    "dashboards",
    "design",
    "docai",
    "docqa",
    "documents",
    "enrichment",
    "excel",
    "export",
    "federation",
    "health",
    "ingestion",
    "jobs",
    "knowledge",
    "legacy",
    "nl2sql",
    "recommendations",
    "reports",
    "schedules",
    "search",
    "spreadsheets",
    "state",
    "summary",
    "synthesis",
    "templates",
    "visualization",
    "workflows",
]
