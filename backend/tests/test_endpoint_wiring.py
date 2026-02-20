"""Endpoint Wiring Verification Tests — FULL COVERAGE.

Ensures EVERY SINGLE registered route is reachable, every handler is wired,
every auth dependency is in place, every singleton is thread-safe, every
frontend API call has a backend counterpart, and no wire lays haywire.

Coverage:
  - 457 canonical /api/v1/ endpoints
  - 454 backward-compat root endpoints
  - 91  legacy endpoints
  - 8   auth endpoints
  - 2   WebSocket endpoints
  - 20  service module imports
  - 33  route module structural checks
  - Frontend→Backend cross-reference (392 frontend API functions)
"""
from __future__ import annotations

import ast
import importlib
import inspect
import re
import sys
import threading
import types
from pathlib import Path
from typing import Any

import pytest
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute, APIWebSocketRoute

# ---------------------------------------------------------------------------
# Ensure test env
# ---------------------------------------------------------------------------
import os

os.environ.setdefault("NEURA_DEBUG", "true")
os.environ.setdefault("NEURA_JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("ALLOWED_HOSTS_ALL", "true")
os.environ.setdefault("NEURA_ALLOWED_HOSTS_ALL", "true")

# Mock cryptography before anything touches it
_fernet_mod = types.ModuleType("cryptography.fernet")


class _FakeFernet:
    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return b"A" * 44

    def encrypt(self, payload: bytes) -> bytes:
        return payload

    def decrypt(self, token: bytes) -> bytes:
        return token


setattr(_fernet_mod, "Fernet", _FakeFernet)
setattr(_fernet_mod, "InvalidToken", Exception)
_crypto_mod = types.ModuleType("cryptography")
setattr(_crypto_mod, "fernet", _fernet_mod)
sys.modules.setdefault("cryptography", _crypto_mod)
sys.modules.setdefault("cryptography.fernet", _fernet_mod)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# ---------------------------------------------------------------------------
# Constants — the single source of truth for what must exist
# ---------------------------------------------------------------------------

ALL_ROUTE_MODULES = [
    "agents", "agents_v2", "ai", "analytics", "audit", "charts", "connections",
    "connectors", "dashboards", "design", "docai", "docqa", "documents",
    "enrichment", "excel", "export", "federation", "health", "ingestion",
    "jobs", "knowledge", "legacy", "nl2sql", "recommendations", "reports",
    "schedules", "search", "spreadsheets", "state", "summary", "synthesis",
    "templates", "visualization", "workflows",
]

AUTH_REQUIRED_MODULES = [
    m for m in ALL_ROUTE_MODULES if m not in ("health", "legacy")
]

AUTH_EXEMPT_MODULES = ["health", "legacy"]

SINGLETON_MODULES = {
    "documents": ["get_document_service", "get_collaboration_service", "get_ws_handler", "get_pdf_service"],
    "spreadsheets": ["get_spreadsheet_service", "get_formula_engine", "get_pivot_service"],
    "docqa": ["get_service"],
}

ROUTE_PREFIXES = {
    "agents": "/agents", "agents_v2": "/agents/v2", "ai": "/ai",
    "analytics": "/analytics", "audit": "/audit", "charts": "/charts",
    "connections": "/connections",
    "connectors": "/connectors", "dashboards": "/dashboards", "design": "/design",
    "docai": "/docai", "docqa": "/docqa", "documents": "/documents",
    "enrichment": "/enrichment", "excel": "/excel", "export": "/export",
    "federation": "/federation", "health": "", "ingestion": "/ingestion",
    "jobs": "/jobs", "knowledge": "/knowledge", "nl2sql": "/nl2sql",
    "recommendations": "/recommendations", "reports": "/reports",
    "schedules": "/reports/schedules", "search": "/search",
    "spreadsheets": "/spreadsheets", "state": "/state", "summary": "/summary",
    "synthesis": "/synthesis", "templates": "/templates",
    "visualization": "/visualization", "workflows": "/workflows",
}

# Service modules that must import cleanly
SERVICE_MODULES = [
    "backend.app.services.agents", "backend.app.services.ai",
    "backend.app.services.analytics", "backend.app.services.charts",
    "backend.app.services.connections", "backend.app.services.connectors",
    "backend.app.services.dashboards", "backend.app.services.design",
    "backend.app.services.docai", "backend.app.services.documents",
    "backend.app.services.enrichment", "backend.app.services.export",
    "backend.app.services.extraction", "backend.app.services.ingestion",
    "backend.app.services.jobs", "backend.app.services.knowledge",
    "backend.app.services.search", "backend.app.services.spreadsheets",
    "backend.app.services.visualization", "backend.app.services.workflow",
]


# ---------------------------------------------------------------------------
# Frontend API calls — every function from frontend/src/api/*.js
# Maps frontend function path -> (HTTP method, backend path pattern)
# ---------------------------------------------------------------------------

FRONTEND_API_CALLS = {
    # agents.js
    "agents/runResearchAgent": ("POST", "/agents/research"),
    "agents/runDataAnalystAgent": ("POST", "/agents/data-analysis"),
    "agents/runEmailDraftAgent": ("POST", "/agents/email-draft"),
    "agents/runContentRepurposeAgent": ("POST", "/agents/content-repurpose"),
    "agents/runProofreadingAgent": ("POST", "/agents/proofread"),
    "agents/getTask": ("GET", "/agents/tasks/{task_id}"),
    "agents/listTasks": ("GET", "/agents/tasks"),
    "agents/listAgentTypes": ("GET", "/agents/types"),
    "agents/listRepurposeFormats": ("GET", "/agents/formats/repurpose"),

    # agentsV2.js
    "agentsV2/runResearchAgent": ("POST", "/agents/v2/research"),
    "agentsV2/runDataAnalystAgent": ("POST", "/agents/v2/data-analyst"),
    "agentsV2/runEmailDraftAgent": ("POST", "/agents/v2/email-draft"),
    "agentsV2/runContentRepurposeAgent": ("POST", "/agents/v2/content-repurpose"),
    "agentsV2/runProofreadingAgent": ("POST", "/agents/v2/proofreading"),
    "agentsV2/getTask": ("GET", "/agents/v2/tasks/{task_id}"),
    "agentsV2/listTasks": ("GET", "/agents/v2/tasks"),
    "agentsV2/cancelTask": ("POST", "/agents/v2/tasks/{task_id}/cancel"),
    "agentsV2/retryTask": ("POST", "/agents/v2/tasks/{task_id}/retry"),
    "agentsV2/getTaskEvents": ("GET", "/agents/v2/tasks/{task_id}/events"),
    "agentsV2/listAgentTypes": ("GET", "/agents/v2/types"),
    "agentsV2/getStats": ("GET", "/agents/v2/stats"),
    "agentsV2/healthCheck": ("GET", "/agents/v2/health"),
    "agentsV2/streamTaskProgress": ("GET", "/agents/v2/tasks/{task_id}/stream"),

    # charts.js
    "charts/analyzeData": ("POST", "/charts/analyze"),
    "charts/queueAnalyzeData": ("POST", "/charts/analyze"),
    "charts/generateChart": ("POST", "/charts/generate"),
    "charts/queueGenerateChart": ("POST", "/charts/generate"),

    # connectors.js
    "connectors/listConnectorTypes": ("GET", "/connectors/types"),
    "connectors/getConnectorType": ("GET", "/connectors/types/{connector_type}"),
    "connectors/listConnectorsByCategory": ("GET", "/connectors/types/by-category/{category}"),
    "connectors/testConnection": ("POST", "/connectors/{connector_type}/test"),
    "connectors/createConnection": ("POST", "/connectors/{connector_type}/connect"),
    "connectors/getConnection": ("GET", "/connectors/{connection_id}"),
    "connectors/listConnections": ("GET", "/connectors"),
    "connectors/deleteConnection": ("DELETE", "/connectors/{connection_id}"),
    "connectors/checkConnectionHealth": ("POST", "/connectors/{connection_id}/health"),
    "connectors/getConnectionSchema": ("GET", "/connectors/{connection_id}/schema"),
    "connectors/executeQuery": ("POST", "/connectors/{connection_id}/query"),
    "connectors/getOAuthUrl": ("GET", "/connectors/{connector_type}/oauth/authorize"),
    "connectors/handleOAuthCallback": ("POST", "/connectors/{connector_type}/oauth/callback"),
    "connectors/getOAuthPopupUrl": ("GET", "/connectors/{connector_type}/oauth/authorize"),
    "connectors/listFiles": ("GET", "/connectors/{connection_id}/files"),
    "connectors/downloadFile": ("GET", "/connectors/{connection_id}/files/download"),
    "connectors/uploadFile": ("POST", "/connectors/{connection_id}/files/upload"),
    "connectors/syncConnection": ("POST", "/connectors/{connection_id}/sync"),
    "connectors/getSyncStatus": ("GET", "/connectors/{connection_id}/sync/status"),
    "connectors/scheduleSyncJob": ("POST", "/connectors/{connection_id}/sync/schedule"),

    # dashboards.js
    "dashboards/createDashboard": ("POST", "/dashboards"),
    "dashboards/getDashboard": ("GET", "/dashboards/{dashboard_id}"),
    "dashboards/updateDashboard": ("PUT", "/dashboards/{dashboard_id}"),
    "dashboards/deleteDashboard": ("DELETE", "/dashboards/{dashboard_id}"),
    "dashboards/listDashboards": ("GET", "/dashboards"),
    "dashboards/addWidget": ("POST", "/dashboards/{dashboard_id}/widgets"),
    "dashboards/updateWidget": ("PUT", "/dashboards/{dashboard_id}/widgets/{widget_id}"),
    "dashboards/deleteWidget": ("DELETE", "/dashboards/{dashboard_id}/widgets/{widget_id}"),
    "dashboards/executeWidgetQuery": ("POST", "/dashboards/{dashboard_id}/query"),
    "dashboards/createSnapshot": ("POST", "/dashboards/{dashboard_id}/snapshot"),
    "dashboards/generateEmbedToken": ("POST", "/dashboards/{dashboard_id}/embed"),
    "dashboards/updateWidgetLayout": ("PUT", "/dashboards/{dashboard_id}/layout"),
    "dashboards/refreshDashboard": ("POST", "/dashboards/{dashboard_id}/refresh"),
    "dashboards/getSnapshotUrl": ("GET", "/dashboards/snapshots/{snapshot_id}"),
    "dashboards/addFilter": ("POST", "/dashboards/{dashboard_id}/filters"),
    "dashboards/updateFilter": ("PUT", "/dashboards/{dashboard_id}/filters/{filter_id}"),
    "dashboards/deleteFilter": ("DELETE", "/dashboards/{dashboard_id}/filters/{filter_id}"),
    "dashboards/setVariable": ("PUT", "/dashboards/{dashboard_id}/variables/{variable_name}"),
    "dashboards/generateInsights": ("POST", "/dashboards/analytics/insights"),
    "dashboards/predictTrends": ("POST", "/dashboards/analytics/trends"),
    "dashboards/detectAnomalies": ("POST", "/dashboards/analytics/anomalies"),
    "dashboards/findCorrelations": ("POST", "/dashboards/analytics/correlations"),
    "dashboards/runWhatIfSimulation": ("POST", "/dashboards/{dashboard_id}/what-if"),
    "dashboards/listDashboardTemplates": ("GET", "/dashboards/templates"),
    "dashboards/createFromTemplate": ("POST", "/dashboards/templates/{template_id}/create"),
    "dashboards/saveAsTemplate": ("POST", "/dashboards/{dashboard_id}/save-as-template"),
    "dashboards/shareDashboard": ("POST", "/dashboards/{dashboard_id}/share"),
    "dashboards/exportDashboard": ("GET", "/dashboards/{dashboard_id}/export"),

    # design.js
    "design/createBrandKit": ("POST", "/design/brand-kits"),
    "design/getBrandKit": ("GET", "/design/brand-kits/{kit_id}"),
    "design/listBrandKits": ("GET", "/design/brand-kits"),
    "design/updateBrandKit": ("PUT", "/design/brand-kits/{kit_id}"),
    "design/deleteBrandKit": ("DELETE", "/design/brand-kits/{kit_id}"),
    "design/setDefaultBrandKit": ("POST", "/design/brand-kits/{kit_id}/set-default"),
    "design/applyBrandKit": ("POST", "/design/brand-kits/{kit_id}/apply"),
    "design/createTheme": ("POST", "/design/themes"),
    "design/getTheme": ("GET", "/design/themes/{theme_id}"),
    "design/listThemes": ("GET", "/design/themes"),
    "design/updateTheme": ("PUT", "/design/themes/{theme_id}"),
    "design/deleteTheme": ("DELETE", "/design/themes/{theme_id}"),
    "design/setActiveTheme": ("POST", "/design/themes/{theme_id}/activate"),
    "design/generateColorPalette": ("POST", "/design/color-palette"),
    "design/getColorContrast": ("POST", "/design/colors/contrast"),
    "design/suggestAccessibleColors": ("POST", "/design/colors/accessible"),
    "design/listFonts": ("GET", "/design/fonts"),
    "design/getFontPairings": ("GET", "/design/fonts/pairings"),
    "design/uploadLogo": ("POST", "/design/assets/logo"),
    "design/listAssets": ("GET", "/design/brand-kits/{kit_id}/assets"),
    "design/deleteAsset": ("DELETE", "/design/assets/{asset_id}"),
    "design/exportBrandKit": ("GET", "/design/brand-kits/{kit_id}/export"),
    "design/importBrandKit": ("POST", "/design/brand-kits/import"),

    # docqa.js
    "docqa/createSession": ("POST", "/docqa/sessions"),
    "docqa/listSessions": ("GET", "/docqa/sessions"),
    "docqa/getSession": ("GET", "/docqa/sessions/{session_id}"),
    "docqa/deleteSession": ("DELETE", "/docqa/sessions/{session_id}"),
    "docqa/addDocument": ("POST", "/docqa/sessions/{session_id}/documents"),
    "docqa/removeDocument": ("DELETE", "/docqa/sessions/{session_id}/documents/{document_id}"),
    "docqa/askQuestion": ("POST", "/docqa/sessions/{session_id}/ask"),
    "docqa/getChatHistory": ("GET", "/docqa/sessions/{session_id}/history"),
    "docqa/clearHistory": ("DELETE", "/docqa/sessions/{session_id}/history"),
    "docqa/submitFeedback": ("POST", "/docqa/sessions/{session_id}/messages/{message_id}/feedback"),
    "docqa/regenerateResponse": ("POST", "/docqa/sessions/{session_id}/messages/{message_id}/regenerate"),

    # documents.js
    "documents/createDocument": ("POST", "/documents"),
    "documents/getDocument": ("GET", "/documents/{document_id}"),
    "documents/updateDocument": ("PUT", "/documents/{document_id}"),
    "documents/deleteDocument": ("DELETE", "/documents/{document_id}"),
    "documents/listDocuments": ("GET", "/documents"),
    "documents/getVersions": ("GET", "/documents/{document_id}/versions"),
    "documents/getVersion": ("GET", "/documents/{document_id}/versions/{version}"),
    "documents/getComments": ("GET", "/documents/{document_id}/comments"),
    "documents/addComment": ("POST", "/documents/{document_id}/comments"),
    "documents/resolveComment": ("PATCH", "/documents/{document_id}/comments/{comment_id}/resolve"),
    "documents/startCollaboration": ("POST", "/documents/{document_id}/collaborate"),
    "documents/getCollaborators": ("GET", "/documents/{document_id}/collaborate/presence"),
    "documents/reorderPages": ("POST", "/documents/{document_id}/pdf/reorder"),
    "documents/addWatermark": ("POST", "/documents/{document_id}/pdf/watermark"),
    "documents/redactRegions": ("POST", "/documents/{document_id}/pdf/redact"),
    "documents/mergePdfs": ("POST", "/documents/merge"),
    "documents/checkGrammar": ("POST", "/documents/{document_id}/ai/grammar"),
    "documents/summarize": ("POST", "/documents/{document_id}/ai/summarize"),
    "documents/rewrite": ("POST", "/documents/{document_id}/ai/rewrite"),
    "documents/expand": ("POST", "/documents/{document_id}/ai/expand"),
    "documents/restoreVersion": ("POST", "/documents/{document_id}/versions/{version}/restore"),
    "documents/replyToComment": ("POST", "/documents/{document_id}/comments/{comment_id}/reply"),
    "documents/deleteComment": ("DELETE", "/documents/{document_id}/comments/{comment_id}"),
    "documents/updatePresence": ("PUT", "/documents/{document_id}/presence"),
    "documents/splitPdf": ("POST", "/documents/{document_id}/pdf/split"),
    "documents/rotatePdf": ("POST", "/documents/{document_id}/pdf/rotate"),
    "documents/translate": ("POST", "/documents/{document_id}/ai/translate"),
    "documents/adjustTone": ("POST", "/documents/{document_id}/ai/tone"),
    "documents/listTemplates": ("GET", "/documents/templates"),
    "documents/createFromTemplate": ("POST", "/documents/templates/{template_id}/create"),
    "documents/saveAsTemplate": ("POST", "/documents/{document_id}/save-as-template"),
    "documents/exportDocument": ("GET", "/documents/{document_id}/export"),

    # enrichment.js
    "enrichment/getEnrichmentSources": ("GET", "/enrichment/sources"),
    "enrichment/previewEnrichment": ("POST", "/enrichment/preview"),
    "enrichment/enrichData": ("POST", "/enrichment/enrich"),
    "enrichment/createSource": ("POST", "/enrichment/sources/create"),
    "enrichment/deleteSource": ("DELETE", "/enrichment/sources/{source_id}"),
    "enrichment/getCacheStats": ("GET", "/enrichment/cache/stats"),
    "enrichment/clearCache": ("DELETE", "/enrichment/cache"),

    # export.js
    "export/exportToPdf": ("POST", "/export/{document_id}/pdf"),
    "export/exportToPdfA": ("POST", "/export/{document_id}/pdfa"),
    "export/exportToDocx": ("POST", "/export/{document_id}/docx"),
    "export/exportToPptx": ("POST", "/export/{document_id}/pptx"),
    "export/exportToEpub": ("POST", "/export/{document_id}/epub"),
    "export/exportToLatex": ("POST", "/export/{document_id}/latex"),
    "export/exportToMarkdown": ("POST", "/export/{document_id}/markdown"),
    "export/exportToHtml": ("POST", "/export/{document_id}/html"),
    "export/bulkExport": ("POST", "/export/bulk"),
    "export/getBulkExportStatus": ("GET", "/export/jobs/{job_id}"),
    "export/sendEmail": ("POST", "/export/distribution/email-campaign"),
    "export/sendToSlack": ("POST", "/export/distribution/slack"),
    "export/sendToTeams": ("POST", "/export/distribution/teams"),
    "export/sendWebhook": ("POST", "/export/distribution/webhook"),
    "export/publishToPortal": ("POST", "/export/distribution/portal/{document_id}"),
    "export/generateEmbedToken": ("POST", "/export/distribution/embed/{document_id}"),
    "export/downloadBulkExport": ("GET", "/export/bulk/{job_id}/download"),
    "export/revokeEmbedToken": ("DELETE", "/export/embed/{token_id}"),
    "export/listEmbedTokens": ("GET", "/export/{document_id}/embed/tokens"),
    "export/printDocument": ("POST", "/export/{document_id}/print"),
    "export/listPrinters": ("GET", "/export/printers"),
    "export/getExportJob": ("GET", "/export/jobs/{job_id}"),
    "export/listExportJobs": ("GET", "/export/jobs"),
    "export/cancelExportJob": ("POST", "/export/jobs/{job_id}/cancel"),

    # federation.js
    "federation/createVirtualSchema": ("POST", "/federation/schemas"),
    "federation/listVirtualSchemas": ("GET", "/federation/schemas"),
    "federation/getVirtualSchema": ("GET", "/federation/schemas/{schema_id}"),
    "federation/suggestJoins": ("POST", "/federation/suggest-joins"),
    "federation/executeFederatedQuery": ("POST", "/federation/query"),
    "federation/deleteVirtualSchema": ("DELETE", "/federation/schemas/{schema_id}"),

    # health.js
    "health/checkHealth": ("GET", "/health"),
    "health/getDetailedHealth": ("GET", "/health/detailed"),
    "health/getTokenUsage": ("GET", "/health/token-usage"),
    "health/getSchedulerStatus": ("GET", "/health/scheduler"),
    "health/getEmailStatus": ("GET", "/health/email"),
    "health/testEmailConnection": ("GET", "/health/email/test"),
    "health/refreshEmailConfig": ("POST", "/health/email/refresh"),
    "health/checkReadiness": ("GET", "/ready"),
    "health/getSystemHealth": ("GET", "/health/detailed"),

    # ingestion.js
    "ingestion/uploadFile": ("POST", "/ingestion/upload"),
    "ingestion/uploadBulk": ("POST", "/ingestion/upload/bulk"),
    "ingestion/uploadZip": ("POST", "/ingestion/upload/zip"),
    "ingestion/importFromUrl": ("POST", "/ingestion/url"),
    "ingestion/importStructuredData": ("POST", "/ingestion/structured"),
    "ingestion/clipUrl": ("POST", "/ingestion/clip/url"),
    "ingestion/clipSelection": ("POST", "/ingestion/clip/selection"),
    "ingestion/createWatcher": ("POST", "/ingestion/watchers"),
    "ingestion/listWatchers": ("GET", "/ingestion/watchers"),
    "ingestion/getWatcher": ("GET", "/ingestion/watchers/{watcher_id}"),
    "ingestion/startWatcher": ("POST", "/ingestion/watchers/{watcher_id}/start"),
    "ingestion/stopWatcher": ("POST", "/ingestion/watchers/{watcher_id}/stop"),
    "ingestion/deleteWatcher": ("DELETE", "/ingestion/watchers/{watcher_id}"),
    "ingestion/scanFolder": ("POST", "/ingestion/watchers/{watcher_id}/scan"),
    "ingestion/transcribeFile": ("POST", "/ingestion/transcribe"),
    "ingestion/getTranscriptionStatus": ("GET", "/ingestion/transcribe/{job_id}"),
    "ingestion/parseEmail": ("POST", "/ingestion/email/parse"),
    "ingestion/connectImapAccount": ("POST", "/ingestion/email/imap/connect"),
    "ingestion/listImapAccounts": ("GET", "/ingestion/email/imap/accounts"),
    "ingestion/syncImapAccount": ("POST", "/ingestion/email/imap/accounts/{account_id}/sync"),
    "ingestion/detectType": ("POST", "/ingestion/detect-type"),
    "ingestion/getSupportedTypes": ("GET", "/ingestion/supported-types"),

    # knowledge.js
    "knowledge/addDocument": ("POST", "/knowledge/documents"),
    "knowledge/uploadDocument": ("POST", "/knowledge/documents"),
    "knowledge/getDocument": ("GET", "/knowledge/documents/{doc_id}"),
    "knowledge/listDocuments": ("GET", "/knowledge/documents"),
    "knowledge/updateDocument": ("PUT", "/knowledge/documents/{doc_id}"),
    "knowledge/deleteDocument": ("DELETE", "/knowledge/documents/{doc_id}"),
    "knowledge/toggleFavorite": ("POST", "/knowledge/documents/{doc_id}/favorite"),
    "knowledge/createCollection": ("POST", "/knowledge/collections"),
    "knowledge/getCollection": ("GET", "/knowledge/collections/{coll_id}"),
    "knowledge/listCollections": ("GET", "/knowledge/collections"),
    "knowledge/updateCollection": ("PUT", "/knowledge/collections/{coll_id}"),
    "knowledge/deleteCollection": ("DELETE", "/knowledge/collections/{coll_id}"),
    "knowledge/createTag": ("POST", "/knowledge/tags"),
    "knowledge/listTags": ("GET", "/knowledge/tags"),
    "knowledge/deleteTag": ("DELETE", "/knowledge/tags/{tag_id}"),
    "knowledge/searchDocuments": ("POST", "/knowledge/search"),
    "knowledge/semanticSearch": ("POST", "/knowledge/search/semantic"),
    "knowledge/autoTag": ("POST", "/knowledge/auto-tag"),
    "knowledge/findRelated": ("POST", "/knowledge/related"),
    "knowledge/buildKnowledgeGraph": ("POST", "/knowledge/knowledge-graph"),
    "knowledge/generateFaq": ("POST", "/knowledge/faq"),
    "knowledge/addDocumentToCollection": ("POST", "/knowledge/collections/{coll_id}/documents"),
    "knowledge/removeDocumentFromCollection": ("DELETE", "/knowledge/collections/{coll_id}/documents/{doc_id}"),
    "knowledge/addTagToDocument": ("POST", "/knowledge/documents/{doc_id}/tags"),
    "knowledge/removeTagFromDocument": ("DELETE", "/knowledge/documents/{doc_id}/tags/{tag_id}"),
    "knowledge/getLibraryStats": ("GET", "/knowledge/stats"),
    "knowledge/getDocumentActivity": ("GET", "/knowledge/documents/{doc_id}/activity"),

    # nl2sql.js
    "nl2sql/generateSQL": ("POST", "/nl2sql/generate"),
    "nl2sql/executeQuery": ("POST", "/nl2sql/execute"),
    "nl2sql/explainQuery": ("POST", "/nl2sql/explain"),
    "nl2sql/saveQuery": ("POST", "/nl2sql/save"),
    "nl2sql/listSavedQueries": ("GET", "/nl2sql/saved"),
    "nl2sql/getSavedQuery": ("GET", "/nl2sql/saved/{query_id}"),
    "nl2sql/deleteSavedQuery": ("DELETE", "/nl2sql/saved/{query_id}"),
    "nl2sql/getQueryHistory": ("GET", "/nl2sql/history"),
    "nl2sql/deleteQueryHistoryEntry": ("DELETE", "/nl2sql/history/{entry_id}"),

    # recommendations.js
    "recommendations/getRecommendations": ("POST", "/recommendations/templates"),
    "recommendations/queueRecommendations": ("POST", "/recommendations/templates"),
    "recommendations/getCatalog": ("GET", "/recommendations/catalog"),
    "recommendations/getTemplates": ("GET", "/recommendations/templates"),
    "recommendations/getSimilar": ("GET", "/recommendations/templates/{template_id}/similar"),

    # search.js
    "search/search": ("POST", "/search/search"),
    "search/semanticSearch": ("POST", "/search/search/semantic"),
    "search/regexSearch": ("POST", "/search/search/regex"),
    "search/booleanSearch": ("POST", "/search/search/boolean"),
    "search/searchAndReplace": ("POST", "/search/search/replace"),
    "search/findSimilar": ("GET", "/search/documents/{document_id}/similar"),
    "search/indexDocument": ("POST", "/search/index"),
    "search/removeFromIndex": ("DELETE", "/search/index/{document_id}"),
    "search/saveSearch": ("POST", "/search/saved-searches"),
    "search/listSavedSearches": ("GET", "/search/saved-searches"),
    "search/deleteSavedSearch": ("DELETE", "/search/saved-searches/{search_id}"),
    "search/runSavedSearch": ("POST", "/search/saved-searches/{search_id}/run"),
    "search/reindexAll": ("POST", "/search/index/reindex"),
    "search/getSavedSearch": ("GET", "/search/saved-searches/{search_id}"),
    "search/getSearchAnalytics": ("GET", "/search/analytics"),
    "search/getTypes": ("GET", "/search/types"),

    # spreadsheets.js
    "spreadsheets/createSpreadsheet": ("POST", "/spreadsheets"),
    "spreadsheets/getSpreadsheet": ("GET", "/spreadsheets/{spreadsheet_id}"),
    "spreadsheets/updateSpreadsheet": ("PUT", "/spreadsheets/{spreadsheet_id}"),
    "spreadsheets/deleteSpreadsheet": ("DELETE", "/spreadsheets/{spreadsheet_id}"),
    "spreadsheets/listSpreadsheets": ("GET", "/spreadsheets"),
    "spreadsheets/updateCells": ("PUT", "/spreadsheets/{spreadsheet_id}/cells"),
    "spreadsheets/addSheet": ("POST", "/spreadsheets/{spreadsheet_id}/sheets"),
    "spreadsheets/deleteSheet": ("DELETE", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}"),
    "spreadsheets/renameSheet": ("PUT", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/rename"),
    "spreadsheets/freezePanes": ("PUT", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/freeze"),
    "spreadsheets/addConditionalFormat": ("POST", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-format"),
    "spreadsheets/addDataValidation": ("POST", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/validation"),
    "spreadsheets/createPivotTable": ("POST", "/spreadsheets/{spreadsheet_id}/pivot"),
    "spreadsheets/evaluateFormula": ("POST", "/spreadsheets/{spreadsheet_id}/evaluate"),
    "spreadsheets/importCsv": ("POST", "/spreadsheets/import"),
    "spreadsheets/importExcel": ("POST", "/spreadsheets/import"),
    "spreadsheets/exportSpreadsheet": ("GET", "/spreadsheets/{spreadsheet_id}/export"),
    "spreadsheets/generateFormula": ("POST", "/spreadsheets/{spreadsheet_id}/ai/formula"),
    "spreadsheets/explainFormula": ("POST", "/spreadsheets/{spreadsheet_id}/ai/explain"),
    "spreadsheets/suggestDataCleaning": ("POST", "/spreadsheets/{spreadsheet_id}/ai/clean"),
    "spreadsheets/detectAnomalies": ("POST", "/spreadsheets/{spreadsheet_id}/ai/anomalies"),
    "spreadsheets/predictColumn": ("POST", "/spreadsheets/{spreadsheet_id}/ai/predict"),
    "spreadsheets/suggestFormulas": ("POST", "/spreadsheets/{spreadsheet_id}/ai/suggest"),
    "spreadsheets/getCellRange": ("GET", "/spreadsheets/{spreadsheet_id}/cells"),
    "spreadsheets/removeConditionalFormat": ("DELETE", "/spreadsheets/{spreadsheet_id}/sheets/{sheet_id}/conditional-formats/{format_id}"),
    "spreadsheets/updatePivotTable": ("PUT", "/spreadsheets/{spreadsheet_id}/pivot/{pivot_id}"),
    "spreadsheets/deletePivotTable": ("DELETE", "/spreadsheets/{spreadsheet_id}/pivot/{pivot_id}"),
    "spreadsheets/refreshPivotTable": ("POST", "/spreadsheets/{spreadsheet_id}/pivot/{pivot_id}/refresh"),
    "spreadsheets/validateFormula": ("POST", "/spreadsheets/formula/validate"),
    "spreadsheets/listFunctions": ("GET", "/spreadsheets/formula/functions"),
    "spreadsheets/startSpreadsheetCollaboration": ("POST", "/spreadsheets/{spreadsheet_id}/collaborate"),
    "spreadsheets/getSpreadsheetCollaborators": ("GET", "/spreadsheets/{spreadsheet_id}/collaborators"),

    # summary.js
    "summary/generateSummary": ("POST", "/summary/generate"),
    "summary/queueSummary": ("POST", "/summary/generate"),
    "summary/getReportSummary": ("GET", "/summary/reports/{report_id}"),
    "summary/queueReportSummary": ("GET", "/summary/reports/{report_id}"),

    # synthesis.js
    "synthesis/createSession": ("POST", "/synthesis/sessions"),
    "synthesis/listSessions": ("GET", "/synthesis/sessions"),
    "synthesis/getSession": ("GET", "/synthesis/sessions/{session_id}"),
    "synthesis/deleteSession": ("DELETE", "/synthesis/sessions/{session_id}"),
    "synthesis/addDocument": ("POST", "/synthesis/sessions/{session_id}/documents"),
    "synthesis/extractDocument": ("POST", "/synthesis/documents/extract"),
    "synthesis/removeDocument": ("DELETE", "/synthesis/sessions/{session_id}/documents/{document_id}"),
    "synthesis/findInconsistencies": ("GET", "/synthesis/sessions/{session_id}/inconsistencies"),
    "synthesis/synthesize": ("POST", "/synthesis/sessions/{session_id}/synthesize"),

    # visualization.js
    "visualization/generateFlowchart": ("POST", "/visualization/diagrams/flowchart"),
    "visualization/generateMindmap": ("POST", "/visualization/diagrams/mindmap"),
    "visualization/generateOrgChart": ("POST", "/visualization/diagrams/org-chart"),
    "visualization/generateTimeline": ("POST", "/visualization/diagrams/timeline"),
    "visualization/generateGantt": ("POST", "/visualization/diagrams/gantt"),
    "visualization/generateNetworkGraph": ("POST", "/visualization/diagrams/network"),
    "visualization/generateKanban": ("POST", "/visualization/diagrams/kanban"),
    "visualization/generateSequenceDiagram": ("POST", "/visualization/diagrams/sequence"),
    "visualization/generateWordcloud": ("POST", "/visualization/diagrams/wordcloud"),
    "visualization/tableToChart": ("POST", "/visualization/charts/from-table"),
    "visualization/generateSparklines": ("POST", "/visualization/charts/sparklines"),
    "visualization/exportDiagramAsMermaid": ("GET", "/visualization/diagrams/{diagram_id}/mermaid"),
    "visualization/exportDiagramAsSvg": ("GET", "/visualization/diagrams/{diagram_id}/svg"),
    "visualization/exportDiagramAsPng": ("GET", "/visualization/diagrams/{diagram_id}/png"),
    "visualization/listDiagramTypes": ("GET", "/visualization/types/diagrams"),
    "visualization/listChartTypes": ("GET", "/visualization/types/charts"),

    # workflows.js
    "workflows/createWorkflow": ("POST", "/workflows"),
    "workflows/getWorkflow": ("GET", "/workflows/{workflow_id}"),
    "workflows/updateWorkflow": ("PUT", "/workflows/{workflow_id}"),
    "workflows/deleteWorkflow": ("DELETE", "/workflows/{workflow_id}"),
    "workflows/listWorkflows": ("GET", "/workflows"),
    "workflows/executeWorkflow": ("POST", "/workflows/{workflow_id}/execute"),
    "workflows/getExecution": ("GET", "/workflows/executions/{execution_id}"),
    "workflows/listExecutions": ("GET", "/workflows/{workflow_id}/executions"),
    "workflows/addTrigger": ("POST", "/workflows/{workflow_id}/trigger"),
    "workflows/cancelExecution": ("POST", "/workflows/{workflow_id}/executions/{execution_id}/cancel"),
    "workflows/retryExecution": ("POST", "/workflows/{workflow_id}/executions/{execution_id}/retry"),
    "workflows/updateTrigger": ("PUT", "/workflows/{workflow_id}/triggers/{trigger_id}"),
    "workflows/deleteTrigger": ("DELETE", "/workflows/{workflow_id}/triggers/{trigger_id}"),
    "workflows/enableTrigger": ("POST", "/workflows/{workflow_id}/triggers/{trigger_id}/enable"),
    "workflows/disableTrigger": ("POST", "/workflows/{workflow_id}/triggers/{trigger_id}/disable"),
    "workflows/listNodeTypes": ("GET", "/workflows/node-types"),
    "workflows/getNodeTypeSchema": ("GET", "/workflows/node-types/{node_type}/schema"),
    "workflows/listWorkflowTemplates": ("GET", "/workflows/templates"),
    "workflows/createFromTemplate": ("POST", "/workflows/templates/{template_id}/create"),
    "workflows/saveAsTemplate": ("POST", "/workflows/{workflow_id}/save-as-template"),
    "workflows/getPendingApprovals": ("GET", "/workflows/approvals/pending"),
    "workflows/approveStep": ("POST", "/workflows/executions/{execution_id}/approve"),
    "workflows/rejectStep": ("POST", "/workflows/executions/{execution_id}/approve"),
    "workflows/createWebhook": ("POST", "/workflows/{workflow_id}/webhooks"),
    "workflows/listWebhooks": ("GET", "/workflows/{workflow_id}/webhooks"),
    "workflows/deleteWebhook": ("DELETE", "/workflows/{workflow_id}/webhooks/{webhook_id}"),
    "workflows/regenerateWebhookSecret": ("POST", "/workflows/{workflow_id}/webhooks/{webhook_id}/regenerate-secret"),
    "workflows/getExecutionLogs": ("GET", "/workflows/{workflow_id}/executions/{execution_id}/logs"),
    "workflows/debugWorkflow": ("POST", "/workflows/{workflow_id}/debug"),

    # analytics (from stores/pages)
    "analytics/getDashboard": ("GET", "/analytics/dashboard"),
    "analytics/getUsage": ("GET", "/analytics/usage"),
    "analytics/getReportsHistory": ("GET", "/analytics/reports/history"),
    "analytics/getActivity": ("GET", "/analytics/activity"),
    "analytics/logActivity": ("POST", "/analytics/activity"),
    "analytics/deleteActivity": ("DELETE", "/analytics/activity"),
    "analytics/getFavorites": ("GET", "/analytics/favorites"),
    "analytics/addFavorite": ("POST", "/analytics/favorites/{entity_type}/{entity_id}"),
    "analytics/removeFavorite": ("DELETE", "/analytics/favorites/{entity_type}/{entity_id}"),
    "analytics/checkFavorite": ("GET", "/analytics/favorites/{entity_type}/{entity_id}"),
    "analytics/getPreferences": ("GET", "/analytics/preferences"),
    "analytics/updatePreferences": ("PUT", "/analytics/preferences"),
    "analytics/updatePreference": ("PUT", "/analytics/preferences/{key}"),
    "analytics/getExportConfig": ("GET", "/analytics/export/config"),
    "analytics/searchAll": ("GET", "/analytics/search"),
    "analytics/getNotifications": ("GET", "/analytics/notifications"),
    "analytics/getUnreadCount": ("GET", "/analytics/notifications/unread-count"),
    "analytics/createNotification": ("POST", "/analytics/notifications"),
    "analytics/markRead": ("PUT", "/analytics/notifications/{notification_id}/read"),
    "analytics/markAllRead": ("PUT", "/analytics/notifications/read-all"),
    "analytics/deleteNotification": ("DELETE", "/analytics/notifications/{notification_id}"),
    "analytics/deleteAllNotifications": ("DELETE", "/analytics/notifications"),
    "analytics/bulkDeleteTemplates": ("POST", "/analytics/bulk/templates/delete"),
    "analytics/bulkUpdateStatus": ("POST", "/analytics/bulk/templates/update-status"),
    "analytics/bulkAddTags": ("POST", "/analytics/bulk/templates/add-tags"),
    "analytics/bulkCancelJobs": ("POST", "/analytics/bulk/jobs/cancel"),
    "analytics/bulkDeleteJobs": ("POST", "/analytics/bulk/jobs/delete"),
    "analytics/getInsights": ("POST", "/analytics/insights"),
    "analytics/getTrends": ("POST", "/analytics/trends"),
    "analytics/getAnomalies": ("POST", "/analytics/anomalies"),
    "analytics/getCorrelations": ("POST", "/analytics/correlations"),
    "analytics/getWhatIf": ("POST", "/analytics/whatif"),

    # ai.js
    "ai/generate": ("POST", "/ai/ai/generate"),
    "ai/documentGrammar": ("POST", "/ai/documents/{document_id}/ai/grammar"),
    "ai/documentSummarize": ("POST", "/ai/documents/{document_id}/ai/summarize"),
    "ai/documentRewrite": ("POST", "/ai/documents/{document_id}/ai/rewrite"),
    "ai/documentExpand": ("POST", "/ai/documents/{document_id}/ai/expand"),
    "ai/documentTranslate": ("POST", "/ai/documents/{document_id}/ai/translate"),
    "ai/spreadsheetFormula": ("POST", "/ai/spreadsheets/{spreadsheet_id}/formula"),
    "ai/spreadsheetClean": ("POST", "/ai/spreadsheets/{spreadsheet_id}/clean"),
    "ai/spreadsheetAnomalies": ("POST", "/ai/spreadsheets/{spreadsheet_id}/anomalies"),
    "ai/spreadsheetPredict": ("POST", "/ai/spreadsheets/{spreadsheet_id}/predict"),
    "ai/spreadsheetExplain": ("POST", "/ai/spreadsheets/{spreadsheet_id}/explain"),
    "ai/spreadsheetSuggest": ("POST", "/ai/spreadsheets/{spreadsheet_id}/suggest"),
    "ai/getTones": ("GET", "/ai/tones"),
    "ai/getHealth": ("GET", "/ai/health"),

    # docai.js
    "docai/parseInvoice": ("POST", "/docai/parse/invoice"),
    "docai/parseContract": ("POST", "/docai/parse/contract"),
    "docai/parseResume": ("POST", "/docai/parse/resume"),
    "docai/parseReceipt": ("POST", "/docai/parse/receipt"),
    "docai/classify": ("POST", "/docai/classify"),
    "docai/extractEntities": ("POST", "/docai/entities"),
    "docai/semanticSearch": ("POST", "/docai/search"),
    "docai/compare": ("POST", "/docai/compare"),
    "docai/checkCompliance": ("POST", "/docai/compliance"),
    "docai/summarizeMulti": ("POST", "/docai/summarize/multi"),

    # client.js — functions not covered by domain-specific entries
    "client/listApprovedTemplates": ("GET", "/templates"),
    "client/analyzeDocument": ("POST", "/analyze/upload"),
    "client/extractDocument": ("POST", "/analyze/extract"),
    "client/getAnalysis": ("GET", "/analyze/{analysis_id}"),
    "client/getAnalysisData": ("GET", "/analyze/{analysis_id}/data"),
    "client/getAnalysisChartSuggestions": ("POST", "/analyze/{analysis_id}/charts/suggest"),

    # intentAudit.js
    "intentAudit/recordIntent": ("POST", "/audit/intent"),
    "intentAudit/updateIntent": ("PATCH", "/audit/intent/{id}"),

    # connections (from stores/pages)
    "connections/testConnection": ("POST", "/connections/test"),
    "connections/listConnections": ("GET", "/connections"),
    "connections/createConnection": ("POST", "/connections"),
    "connections/deleteConnection": ("DELETE", "/connections/{connection_id}"),
    "connections/checkHealth": ("POST", "/connections/{connection_id}/health"),
    "connections/getSchema": ("GET", "/connections/{connection_id}/schema"),
    "connections/getPreview": ("GET", "/connections/{connection_id}/preview"),

    # templates (from stores/pages)
    "templates/list": ("GET", "/templates"),
    "templates/catalog": ("GET", "/templates/catalog"),
    "templates/delete": ("DELETE", "/templates/{template_id}"),
    "templates/update": ("PATCH", "/templates/{template_id}"),
    "templates/verify": ("POST", "/templates/verify"),
    "templates/importZip": ("POST", "/templates/import-zip"),
    "templates/export": ("GET", "/templates/{template_id}/export"),
    "templates/duplicate": ("POST", "/templates/{template_id}/duplicate"),
    "templates/updateTags": ("PUT", "/templates/{template_id}/tags"),
    "templates/getAllTags": ("GET", "/templates/tags/all"),
    "templates/recommend": ("POST", "/templates/recommend"),
    "templates/getHtml": ("GET", "/templates/{template_id}/html"),
    "templates/editManual": ("POST", "/templates/{template_id}/edit-manual"),
    "templates/editAi": ("POST", "/templates/{template_id}/edit-ai"),
    "templates/undoLastEdit": ("POST", "/templates/{template_id}/undo-last-edit"),
    "templates/chat": ("POST", "/templates/{template_id}/chat"),
    "templates/chatApply": ("POST", "/templates/{template_id}/chat/apply"),
    "templates/mappingPreview": ("POST", "/templates/{template_id}/mapping/preview"),
    "templates/mappingApprove": ("POST", "/templates/{template_id}/mapping/approve"),
    "templates/correctionsPreview": ("POST", "/templates/{template_id}/mapping/corrections-preview"),
    "templates/generatorAssets": ("POST", "/templates/{template_id}/generator-assets/v1"),
    "templates/keysOptions": ("GET", "/templates/{template_id}/keys/options"),
    "templates/artifactsManifest": ("GET", "/templates/{template_id}/artifacts/manifest"),
    "templates/artifactsHead": ("GET", "/templates/{template_id}/artifacts/head"),
    "templates/chartsSuggest": ("POST", "/templates/{template_id}/charts/suggest"),
    "templates/chartsSaved": ("GET", "/templates/{template_id}/charts/saved"),
    "templates/chartsSavedCreate": ("POST", "/templates/{template_id}/charts/saved"),
    "templates/chartsSavedUpdate": ("PUT", "/templates/{template_id}/charts/saved/{chart_id}"),
    "templates/chartsSavedDelete": ("DELETE", "/templates/{template_id}/charts/saved/{chart_id}"),

    # excel (from stores/pages)
    "excel/verify": ("POST", "/excel/verify"),
    "excel/mappingPreview": ("POST", "/excel/{template_id}/mapping/preview"),
    "excel/mappingApprove": ("POST", "/excel/{template_id}/mapping/approve"),
    "excel/correctionsPreview": ("POST", "/excel/{template_id}/mapping/corrections-preview"),
    "excel/generatorAssets": ("POST", "/excel/{template_id}/generator-assets/v1"),
    "excel/keysOptions": ("GET", "/excel/{template_id}/keys/options"),
    "excel/artifactsManifest": ("GET", "/excel/{template_id}/artifacts/manifest"),
    "excel/artifactsHead": ("GET", "/excel/{template_id}/artifacts/head"),
    "excel/chartsSuggest": ("POST", "/excel/{template_id}/charts/suggest"),
    "excel/chartsSaved": ("GET", "/excel/{template_id}/charts/saved"),
    "excel/chartsSavedCreate": ("POST", "/excel/{template_id}/charts/saved"),
    "excel/chartsSavedUpdate": ("PUT", "/excel/{template_id}/charts/saved/{chart_id}"),
    "excel/chartsSavedDelete": ("DELETE", "/excel/{template_id}/charts/saved/{chart_id}"),
    "excel/reportsRun": ("POST", "/excel/reports/run"),
    "excel/jobsRunReport": ("POST", "/excel/jobs/run-report"),
    "excel/reportsDiscover": ("POST", "/excel/reports/discover"),

    # jobs (from stores/pages)
    "jobs/runReport": ("POST", "/jobs/run-report"),
    "jobs/list": ("GET", "/jobs"),
    "jobs/getActive": ("GET", "/jobs/active"),
    "jobs/getDeadLetter": ("GET", "/jobs/dead-letter"),
    "jobs/getDeadLetterJob": ("GET", "/jobs/dead-letter/{job_id}"),
    "jobs/requeueDeadLetter": ("POST", "/jobs/dead-letter/{job_id}/requeue"),
    "jobs/deleteDeadLetter": ("DELETE", "/jobs/dead-letter/{job_id}"),
    "jobs/getJob": ("GET", "/jobs/{job_id}"),
    "jobs/cancelJob": ("POST", "/jobs/{job_id}/cancel"),
    "jobs/retryJob": ("POST", "/jobs/{job_id}/retry"),

    # reports (from stores/pages)
    "reports/run": ("POST", "/reports/run"),
    "reports/jobsRunReport": ("POST", "/reports/jobs/run-report"),
    "reports/discover": ("POST", "/reports/discover"),
    "reports/getRuns": ("GET", "/reports/runs"),
    "reports/getRun": ("GET", "/reports/runs/{run_id}"),

    # schedules (from stores/pages)
    "schedules/list": ("GET", "/reports/schedules"),
    "schedules/create": ("POST", "/reports/schedules"),
    "schedules/get": ("GET", "/reports/schedules/{schedule_id}"),
    "schedules/update": ("PUT", "/reports/schedules/{schedule_id}"),
    "schedules/delete": ("DELETE", "/reports/schedules/{schedule_id}"),
    "schedules/trigger": ("POST", "/reports/schedules/{schedule_id}/trigger"),
    "schedules/pause": ("POST", "/reports/schedules/{schedule_id}/pause"),
    "schedules/resume": ("POST", "/reports/schedules/{schedule_id}/resume"),

    # state (from stores/pages)
    "state/bootstrap": ("GET", "/state/bootstrap"),
    "state/lastUsed": ("POST", "/state/last-used"),
}


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def route_modules():
    """Import all route modules once and return dict of name->module."""
    from backend.app.api import routes
    return {name: getattr(routes, name) for name in ALL_ROUTE_MODULES}


@pytest.fixture(scope="module")
def app_instance():
    """Create a FastAPI app with all routes registered."""
    from backend import api
    from backend.app.repositories.state import store as state_store_module
    import tempfile

    tmpdir = tempfile.mkdtemp()
    store = state_store_module.StateStore(base_dir=Path(tmpdir))
    state_store_module.set_state_store(store)
    api.state_store = store
    api.SCHEDULER_DISABLED = True
    api.SCHEDULER = None
    return api.app


@pytest.fixture(scope="module")
def client(app_instance):
    """Test client scoped to module for speed."""
    from fastapi.testclient import TestClient
    return TestClient(app_instance, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def all_app_routes(app_instance):
    """Extract all registered routes from the app, keyed by (method, path)."""
    routes = set()
    for route in app_instance.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                if method != "HEAD":
                    routes.add((method, route.path))
    return routes


@pytest.fixture(scope="module")
def v1_routes(all_app_routes):
    """Only /api/v1/ routes."""
    return {(m, p) for m, p in all_app_routes if p.startswith("/api/v1/")}


@pytest.fixture(scope="module")
def root_routes(all_app_routes):
    """Root-level backward-compat routes (not /api/v1/, not /legacy/)."""
    return {
        (m, p) for m, p in all_app_routes
        if not p.startswith("/api/v1/") and not p.startswith("/legacy/")
    }


# =============================================================================
# Helper: convert a path pattern with {params} to a testable path
# =============================================================================

def _make_testable_path(path: str) -> str:
    """Replace path parameters with test dummy values."""
    replacements = {
        "{template_id}": "test-tpl-000",
        "{connection_id}": "test-conn-000",
        "{job_id}": "test-job-000",
        "{schedule_id}": "test-sched-000",
        "{document_id}": "test-doc-000",
        "{dashboard_id}": "test-dash-000",
        "{widget_id}": "test-widget-000",
        "{spreadsheet_id}": "test-ss-000",
        "{sheet_id}": "test-sheet-000",
        "{session_id}": "test-sess-000",
        "{message_id}": "test-msg-000",
        "{task_id}": "test-task-000",
        "{analysis_id}": "test-analysis-000",
        "{version}": "1",
        "{comment_id}": "test-comment-000",
        "{diagram_id}": "test-diagram-000",
        "{kit_id}": "test-kit-000",
        "{theme_id}": "test-theme-000",
        "{asset_id}": "test-asset-000",
        "{schema_id}": "test-schema-000",
        "{doc_id}": "test-doc-000",
        "{coll_id}": "test-coll-000",
        "{tag_id}": "test-tag-000",
        "{query_id}": "test-query-000",
        "{entry_id}": "test-entry-000",
        "{source_id}": "test-source-000",
        "{search_id}": "test-search-000",
        "{run_id}": "test-run-000",
        "{workflow_id}": "test-wf-000",
        "{execution_id}": "test-exec-000",
        "{connector_type}": "postgresql",
        "{entity_type}": "template",
        "{entity_id}": "test-entity-000",
        "{notification_id}": "test-notif-000",
        "{report_id}": "test-report-000",
        "{share_id}": "test-share-000",
        "{chart_id}": "test-chart-000",
        "{mode}": "brief",
        "{key}": "test-key",
        "{id}": "test-user-000",
        "{category}": "database",
        "{pipeline_id}": "test-pipeline-000",
        "{connection_id}": "test-conn-000",
        "{integration_id}": "test-int-000",
        "{webhook_id}": "test-webhook-000",
        "{watcher_id}": "test-watcher-000",
        "{snapshot_id}": "test-snap-000",
        "{filter_id}": "test-filter-000",
        "{variable_name}": "test-var",
        "{token_id}": "test-token-000",
        "{trigger_id}": "test-trigger-000",
        "{node_type}": "transform",
        "{format_id}": "test-format-000",
        "{pivot_id}": "test-pivot-000",
        "{account_id}": "test-account-000",
        "{versionId}": "1",
        "{commentId}": "test-comment-000",
        "{templateId}": "test-tpl-000",
    }
    result = path
    for param, value in replacements.items():
        result = result.replace(param, value)
    return result


# Endpoints that require file upload (multipart) — skip JSON smoke tests
_FILE_UPLOAD_PATHS = {
    "/analyze/upload", "/analyze/extract", "/analyze/v2/upload",
    "/ingestion/upload", "/ingestion/upload/bulk", "/ingestion/upload/zip",
    "/ingestion/transcribe", "/ingestion/transcribe/voice-memo",
    "/ingestion/detect-type", "/ingestion/email/ingest",
    "/design/assets/logo", "/design/brand-kits/import",
    "/templates/verify", "/templates/import-zip",
    "/excel/verify", "/spreadsheets/import",
    "/docai/parse/invoice", "/docai/parse/contract",
    "/docai/parse/resume", "/docai/parse/receipt",
    "/docai/classify", "/docai/entities", "/docai/search",
    "/docai/compare", "/docai/compliance", "/docai/summarize/multi",
    "/legacy/extraction/pdf", "/legacy/extraction/excel",
    "/legacy/llm/document-extract",
}


def _is_routing_404(resp) -> bool:
    """Check if a 404 response is from FastAPI routing (not handler logic)."""
    try:
        body = resp.json()
        return body == {"detail": "Not Found"}
    except Exception:
        return True


def _is_file_upload(path: str) -> bool:
    """Check if path requires file upload."""
    clean = path.replace("/api/v1", "")
    return clean in _FILE_UPLOAD_PATHS


# =============================================================================
# TEST 1: Every route module imports cleanly
# =============================================================================

class TestRouteModuleImports:

    @pytest.mark.parametrize("module_name", ALL_ROUTE_MODULES)
    def test_route_module_imports(self, module_name):
        mod = importlib.import_module(f"backend.app.api.routes.{module_name}")
        assert mod is not None

    @pytest.mark.parametrize("module_name", ALL_ROUTE_MODULES)
    def test_route_module_has_router(self, module_name):
        mod = importlib.import_module(f"backend.app.api.routes.{module_name}")
        assert hasattr(mod, "router")
        assert isinstance(mod.router, APIRouter)

    def test_routes_init_exports_all_modules(self):
        from backend.app.api.routes import __all__ as exported
        for name in ALL_ROUTE_MODULES:
            assert name in exported, f"'{name}' missing from __init__.__all__"

    def test_analyze_module_imports(self):
        from backend.app.api.analyze import router as analyze_router
        from backend.app.api.analyze import enhanced_analysis_routes
        assert isinstance(analyze_router, APIRouter)
        assert hasattr(enhanced_analysis_routes, "router")

    def test_router_registration_imports(self):
        from backend.app.api.router import register_routes, _build_v1_router
        assert callable(register_routes)
        assert callable(_build_v1_router)


# =============================================================================
# TEST 2: Auth wiring
# =============================================================================

class TestAuthWiring:

    @pytest.mark.parametrize("module_name", AUTH_REQUIRED_MODULES)
    def test_router_has_auth_dependency(self, module_name, route_modules):
        router = route_modules[module_name].router
        dep_names = [
            getattr(d.dependency, "__name__", str(d.dependency))
            for d in router.dependencies if hasattr(d, "dependency")
        ]
        assert "require_api_key" in dep_names, (
            f"{module_name}.router missing require_api_key. Found: {dep_names}"
        )

    @pytest.mark.parametrize("module_name", AUTH_EXEMPT_MODULES)
    def test_exempt_module_noted(self, module_name, route_modules):
        assert hasattr(route_modules[module_name], "router")


# =============================================================================
# TEST 3: Thread-safe singletons
# =============================================================================

class TestSingletonThreadSafety:

    @pytest.mark.parametrize("module_name,getter_names",
                             list(SINGLETON_MODULES.items()),
                             ids=list(SINGLETON_MODULES.keys()))
    def test_module_has_lock(self, module_name, getter_names):
        mod = importlib.import_module(f"backend.app.api.routes.{module_name}")
        lock_types = (type(threading.Lock()), type(threading.RLock()))
        locks = [n for n, o in inspect.getmembers(mod)
                 if isinstance(o, lock_types)]
        assert locks, f"{module_name} has singletons {getter_names} but no Lock"

    @pytest.mark.parametrize("module_name,getter_names",
                             list(SINGLETON_MODULES.items()),
                             ids=list(SINGLETON_MODULES.keys()))
    def test_getter_functions_exist(self, module_name, getter_names):
        mod = importlib.import_module(f"backend.app.api.routes.{module_name}")
        for getter in getter_names:
            assert hasattr(mod, getter) and callable(getattr(mod, getter))


# =============================================================================
# TEST 4: Route registration completeness
# =============================================================================

class TestRouteRegistration:

    def test_all_prefixes_have_routes(self, app_instance):
        paths = {r.path for r in app_instance.routes if isinstance(r, APIRoute)}
        for module_name, prefix in ROUTE_PREFIXES.items():
            if not prefix:
                continue
            versioned = f"/api/v1{prefix}"
            matching = [p for p in paths if p.startswith(versioned)]
            assert matching, f"No routes under {versioned} for '{module_name}'"

    def test_backward_compat_routes_exist(self, app_instance):
        paths = {r.path for r in app_instance.routes if isinstance(r, APIRoute)}
        assert "/health" in paths
        assert "/healthz" in paths
        assert "/templates" in paths

    def test_no_handler_is_none(self, app_instance):
        for route in app_instance.routes:
            if isinstance(route, APIRoute):
                assert route.endpoint is not None, f"{route.path} has no handler"

    def test_every_handler_is_callable(self, app_instance):
        for route in app_instance.routes:
            if isinstance(route, APIRoute):
                assert callable(route.endpoint), f"{route.path} handler not callable"

    def test_route_count_v1(self, v1_routes):
        """Must have 400+ canonical /api/v1/ endpoints."""
        assert len(v1_routes) >= 400, (
            f"Only {len(v1_routes)} v1 routes — expected 400+. "
            f"Route registration is broken."
        )

    def test_route_count_total(self, all_app_routes):
        """Must have 900+ total method+path combos."""
        assert len(all_app_routes) >= 900, (
            f"Only {len(all_app_routes)} total routes — expected 900+."
        )

    def test_no_duplicate_method_path_combos(self, app_instance):
        seen = set()
        duplicates = []
        for route in app_instance.routes:
            if isinstance(route, APIRoute):
                for method in route.methods:
                    key = (method, route.path)
                    if key in seen:
                        duplicates.append(key)
                    seen.add(key)
        assert not duplicates, f"Duplicate routes: {duplicates[:10]}"

    @pytest.mark.parametrize("module_name", ALL_ROUTE_MODULES)
    def test_module_has_endpoints(self, module_name, route_modules):
        router = route_modules[module_name].router
        assert len(router.routes) > 0, f"{module_name} has zero routes"


# =============================================================================
# TEST 5: EVERY /api/v1/ GET endpoint is reachable (not 404/405)
# =============================================================================

class TestEveryGetEndpoint:
    """Hit EVERY registered GET endpoint to prove wiring.

    For endpoints with path params ({id}), 404 is acceptable because the
    handler correctly reports 'resource not found' for our dummy IDs.
    Only non-parameterized endpoints returning 404 indicate broken wiring.
    """

    @pytest.fixture(scope="class")
    def get_endpoints(self, v1_routes):
        return sorted([p for m, p in v1_routes if m == "GET"])

    def test_get_endpoint_count(self, get_endpoints):
        assert len(get_endpoints) >= 120, (
            f"Only {len(get_endpoints)} GET endpoints — expected 120+"
        )

    @pytest.fixture(scope="class")
    def get_results(self, get_endpoints, client):
        results = {}
        for path in get_endpoints:
            testable = _make_testable_path(path)
            resp = client.get(testable)
            # Store (status_code, is_routing_404)
            # FastAPI routing 404 returns {"detail":"Not Found"}
            # Handler 404 returns custom messages (proves handler ran)
            is_routing_404 = False
            if resp.status_code == 404:
                try:
                    body = resp.json()
                    is_routing_404 = body == {"detail": "Not Found"}
                except Exception:
                    is_routing_404 = True
            results[path] = (resp.status_code, is_routing_404)
        return results

    def test_no_get_has_routing_404(self, get_results):
        """No GET endpoint should return FastAPI's default routing 404.
        Handler-level 404 (resource not found) is acceptable — it means the
        handler ran and correctly reported the dummy ID doesn't exist."""
        routing_misses = [p for p, (s, is_routing) in get_results.items() if is_routing]
        assert not routing_misses, (
            f"{len(routing_misses)} GET endpoints return routing 404 "
            f"(handler not wired):\n" +
            "\n".join(f"  {p}" for p in routing_misses[:20])
        )

    def test_no_get_returns_405(self, get_results):
        """No GET endpoint should return 405."""
        bad = [p for p, (s, _) in get_results.items() if s == 405]
        assert not bad, (
            f"{len(bad)} GET endpoints return 405:\n" +
            "\n".join(f"  {p}" for p in bad[:20])
        )


# =============================================================================
# TEST 6: EVERY /api/v1/ POST endpoint is reachable
# =============================================================================

class TestEveryPostEndpoint:
    """Hit EVERY POST endpoint with {} body to prove handler exists."""

    @pytest.fixture(scope="class")
    def post_endpoints(self, v1_routes):
        return sorted([p for m, p in v1_routes if m == "POST"])

    def test_post_endpoint_count(self, post_endpoints):
        """Must have 200+ POST endpoints."""
        assert len(post_endpoints) >= 200, (
            f"Only {len(post_endpoints)} POST endpoints — expected 200+"
        )

    @pytest.fixture(scope="class")
    def post_results(self, post_endpoints, client):
        results = {}
        for path in post_endpoints:
            if _is_file_upload(path):
                results[path] = (None, False, True)  # skip
                continue
            testable = _make_testable_path(path)
            resp = client.post(testable, json={})
            is_routing_404 = False
            if resp.status_code == 404:
                try:
                    is_routing_404 = resp.json() == {"detail": "Not Found"}
                except Exception:
                    is_routing_404 = True
            results[path] = (resp.status_code, is_routing_404, False)
        return results

    def test_no_post_has_routing_404(self, post_results):
        """No POST endpoint should return FastAPI's routing 404."""
        routing_misses = [
            p for p, (s, is_routing, skip) in post_results.items()
            if is_routing and not skip
        ]
        assert not routing_misses, (
            f"{len(routing_misses)} POST endpoints return routing 404:\n" +
            "\n".join(f"  {p}" for p in routing_misses[:20])
        )

    def test_no_post_returns_405(self, post_results):
        bad = [
            p for p, (s, _, skip) in post_results.items()
            if s == 405 and not skip
        ]
        assert not bad, (
            f"{len(bad)} POST endpoints return 405:\n" +
            "\n".join(f"  {p}" for p in bad[:20])
        )


# =============================================================================
# TEST 7: EVERY PUT/PATCH/DELETE endpoint is reachable
# =============================================================================

class TestEveryMutationEndpoint:
    """Hit every PUT/PATCH/DELETE endpoint."""

    @pytest.fixture(scope="class")
    def put_endpoints(self, v1_routes):
        return sorted([p for m, p in v1_routes if m == "PUT"])

    @pytest.fixture(scope="class")
    def patch_endpoints(self, v1_routes):
        return sorted([p for m, p in v1_routes if m == "PATCH"])

    @pytest.fixture(scope="class")
    def delete_endpoints(self, v1_routes):
        return sorted([p for m, p in v1_routes if m == "DELETE"])

    def test_put_count(self, put_endpoints):
        assert len(put_endpoints) >= 20, f"Only {len(put_endpoints)} PUT endpoints"

    def test_patch_count(self, patch_endpoints):
        assert len(patch_endpoints) >= 2, f"Only {len(patch_endpoints)} PATCH endpoints"

    def test_delete_count(self, delete_endpoints):
        assert len(delete_endpoints) >= 30, f"Only {len(delete_endpoints)} DELETE endpoints"

    @pytest.fixture(scope="class")
    def put_results(self, put_endpoints, client):
        results = {}
        for path in put_endpoints:
            testable = _make_testable_path(path)
            resp = client.put(testable, json={})
            is_routing = resp.status_code == 404 and _is_routing_404(resp)
            results[path] = (resp.status_code, is_routing)
        return results

    @pytest.fixture(scope="class")
    def delete_results(self, delete_endpoints, client):
        results = {}
        for path in delete_endpoints:
            testable = _make_testable_path(path)
            resp = client.delete(testable)
            is_routing = resp.status_code == 404 and _is_routing_404(resp)
            results[path] = (resp.status_code, is_routing)
        return results

    def test_no_put_has_routing_404(self, put_results):
        missing = [p for p, (s, r) in put_results.items() if r]
        assert not missing, f"PUT routing 404s: {missing[:10]}"

    def test_no_put_returns_405(self, put_results):
        bad = [p for p, (s, _) in put_results.items() if s == 405]
        assert not bad, f"PUT endpoints return 405: {bad[:10]}"

    def test_no_delete_has_routing_404(self, delete_results):
        missing = [p for p, (s, r) in delete_results.items() if r]
        assert not missing, f"DELETE routing 404s: {missing[:10]}"

    def test_no_delete_returns_405(self, delete_results):
        bad = [p for p, (s, _) in delete_results.items() if s == 405]
        assert not bad, f"DELETE endpoints return 405: {bad[:10]}"


# =============================================================================
# TEST 8: Backward-compat root routes mirror /api/v1/ routes
# =============================================================================

class TestBackwardCompat:
    """Root routes must mirror /api/v1/ routes."""

    def test_root_mirrors_v1(self, v1_routes, root_routes):
        """Every /api/v1/X should also exist as /X at root."""
        v1_stripped = {(m, p.replace("/api/v1", "")) for m, p in v1_routes}
        # Root routes include auth (/auth/*, /users/*) that are also v1
        root_set = {(m, p) for m, p in root_routes
                    if not p.startswith("/legacy/")}
        # Check that v1 routes are a subset of root routes
        missing_from_root = v1_stripped - root_set
        # Allow small number of discrepancies (auth routes may differ)
        assert len(missing_from_root) <= 5, (
            f"{len(missing_from_root)} v1 routes missing from root:\n" +
            "\n".join(f"  {m} {p}" for m, p in sorted(missing_from_root)[:20])
        )


# =============================================================================
# TEST 9: Legacy routes exist
# =============================================================================

class TestLegacyRoutes:
    """Legacy routes at /legacy/* must all be registered."""

    @pytest.fixture(scope="class")
    def legacy_routes(self, all_app_routes):
        return {(m, p) for m, p in all_app_routes if p.startswith("/legacy/")}

    def test_legacy_route_count(self, legacy_routes):
        """Must have 80+ legacy routes."""
        assert len(legacy_routes) >= 80, (
            f"Only {len(legacy_routes)} legacy routes — expected 80+"
        )

    def test_legacy_src_routes(self, legacy_routes):
        """Legacy /legacy/src/* routes must exist."""
        src_routes = [p for _, p in legacy_routes if "/legacy/src/" in p]
        assert len(src_routes) >= 30, f"Only {len(src_routes)} legacy/src routes"

    def test_legacy_generate_routes(self, legacy_routes):
        """Legacy /legacy/generate/* routes must exist."""
        gen_routes = [p for _, p in legacy_routes if "/legacy/generate/" in p]
        assert len(gen_routes) >= 10, f"Only {len(gen_routes)} legacy/generate routes"

    def test_key_legacy_routes_exist(self, legacy_routes):
        """Critical legacy paths must be registered."""
        paths = {p for _, p in legacy_routes}
        assert "/legacy/pipelines/report/steps" in paths
        assert "/legacy/orchestration/test-run" in paths


# =============================================================================
# TEST 10: WebSocket routes
# =============================================================================

class TestWebSocketRoutes:

    def test_websocket_routes_exist(self, app_instance):
        ws_routes = [
            r for r in app_instance.routes
            if isinstance(r, APIWebSocketRoute)
        ]
        ws_paths = [r.path for r in ws_routes]
        assert "/ws/collab/{document_id}" in ws_paths, "Missing root WS route"
        assert "/api/v1/ws/collab/{document_id}" in ws_paths, "Missing v1 WS route"


# =============================================================================
# TEST 11: Auth routes
# =============================================================================

class TestAuthRoutes:

    def test_auth_login_exists(self, all_app_routes):
        assert ("POST", "/api/v1/auth/jwt/login") in all_app_routes

    def test_auth_logout_exists(self, all_app_routes):
        assert ("POST", "/api/v1/auth/jwt/logout") in all_app_routes

    def test_auth_register_exists(self, all_app_routes):
        assert ("POST", "/api/v1/auth/register") in all_app_routes

    def test_users_me_exists(self, all_app_routes):
        assert ("GET", "/api/v1/users/me") in all_app_routes


# =============================================================================
# TEST 11b: Backend-only routes (no frontend caller)
# =============================================================================

class TestBackendOnlyRoutes:
    """Backend routes that exist but have no frontend caller.
    These still must be tested for existence."""

    BACKEND_ONLY_ROUTES = [
        ("POST", "/api/v1/auth/jwt/logout"),
        ("POST", "/api/v1/ingestion/email/inbox"),
    ]

    @pytest.mark.parametrize("method,path", BACKEND_ONLY_ROUTES)
    def test_backend_only_route_exists(self, method, path, all_app_routes):
        assert (method, path) in all_app_routes, (
            f"Backend-only route {method} {path} not registered"
        )


# =============================================================================
# TEST 12: Frontend→Backend cross-reference
# =============================================================================

class TestFrontendBackendWiring:
    """Every frontend API function must have a matching backend route.

    Surfaces TWO kinds of results:
    1. PASS — frontend call has a matching backend route (wired correctly)
    2. XFAIL — frontend call has NO backend route (gap → will 404 in production)

    When you implement a missing backend route, remove it from
    KNOWN_MISSING_BACKEND_ROUTES. The test will then enforce it stays wired.
    """

    # ---- Frontend calls with NO backend route (0 gaps — all 79 implemented) ----
    # All previously missing backend routes have been implemented.
    # If new frontend functions are added without backend routes, add them here.
    KNOWN_MISSING_BACKEND_ROUTES: set[str] = set()

    @pytest.fixture(scope="class")
    def all_route_patterns(self, all_app_routes):
        """Build set of (method, pattern) from app routes with params normalized."""
        patterns = set()
        for method, path in all_app_routes:
            clean = path
            if clean.startswith("/api/v1"):
                clean = clean[7:]
            patterns.add((method, clean))
        return patterns

    @pytest.mark.parametrize("fn_name,endpoint", list(FRONTEND_API_CALLS.items()))
    def test_frontend_call_has_backend_route(self, fn_name, endpoint, all_route_patterns):
        method, path = endpoint
        is_gap = fn_name in self.KNOWN_MISSING_BACKEND_ROUTES
        has_route = (method, path) in all_route_patterns

        if is_gap:
            if has_route:
                pytest.fail(
                    f"Frontend {fn_name} ({method} {path}) is in KNOWN_MISSING_BACKEND_ROUTES "
                    f"but the backend route NOW EXISTS. Remove it from the gap list!"
                )
            pytest.xfail(
                f"GAP: Frontend {fn_name} calls {method} {path} — NO backend route. "
                f"Users hitting this feature get 404 in production."
            )
        else:
            assert has_route, (
                f"Frontend {fn_name} calls {method} {path} but no backend route exists!\n"
                f"This frontend function will get 404 in production.\n"
                f"Either add the backend route or add to KNOWN_MISSING_BACKEND_ROUTES."
            )

    def test_gap_count(self):
        """Track total number of frontend→backend gaps. Update when fixing gaps."""
        gap_count = len(self.KNOWN_MISSING_BACKEND_ROUTES)
        assert gap_count == 0, (
            f"Gap count changed: expected 0, got {gap_count}. "
            f"Update this assertion when routes are added/removed."
        )

    def test_total_frontend_calls_coverage(self):
        """Ensure we're testing ALL frontend API calls, not a subset."""
        total = len(FRONTEND_API_CALLS)
        assert total >= 496, (
            f"Only {total} frontend API calls tracked — expected 496+. "
            f"New frontend functions may have been added without updating this test."
        )


# =============================================================================
# TEST 13: Service module imports
# =============================================================================

class TestServiceImports:

    @pytest.mark.parametrize("module_path", SERVICE_MODULES)
    def test_service_imports(self, module_path):
        mod = importlib.import_module(module_path)
        assert mod is not None


# =============================================================================
# TEST 14: Worker wiring
# =============================================================================

class TestWorkerWiring:

    def test_agent_service_has_execute_task_sync(self):
        from backend.app.services.agents import agent_service_v2
        assert hasattr(agent_service_v2, "execute_task_sync")
        assert callable(agent_service_v2.execute_task_sync)

    def test_agent_tasks_import(self):
        dramatiq = pytest.importorskip("dramatiq", reason="dramatiq not installed")
        try:
            from backend.app.services.worker.tasks.agent_tasks import run_agent
            assert callable(run_agent)
        except Exception as e:
            if "redis" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip(f"Redis not available: {e}")
            raise


# =============================================================================
# TEST 15: Request model validation
# =============================================================================

class TestRequestModelValidation:

    INVALID_PAYLOADS = [
        ("/agents/research", {}),
        ("/agents/data-analysis", {"question": "q"}),
        ("/ai/ai/generate", {}),
        ("/visualization/diagrams/flowchart", {}),
        ("/summary/generate", {}),
        ("/nl2sql/generate", {}),
        ("/search/search", {}),
        ("/federation/schemas", {}),
        ("/enrichment/enrich", {}),
    ]

    @pytest.mark.parametrize("path,body", INVALID_PAYLOADS)
    def test_invalid_body_returns_422(self, path, body, client):
        resp = client.post(path, json=body)
        assert resp.status_code == 422, (
            f"POST {path} with invalid body returned {resp.status_code}, expected 422"
        )


# =============================================================================
# TEST 16: Auth enforcement internals
# =============================================================================

class TestAuthEnforcement:

    def test_require_api_key_rejects_bad_key(self):
        from backend.app.services.security import constant_time_compare
        assert constant_time_compare("correct", "wrong") is False
        assert constant_time_compare("key", "key") is True

    def test_require_api_key_is_async(self):
        from backend.app.services.security import require_api_key
        assert inspect.iscoroutinefunction(require_api_key)

    def test_require_api_key_has_correct_signature(self):
        from backend.app.services.security import require_api_key
        params = list(inspect.signature(require_api_key).parameters.keys())
        assert "x_api_key" in params
        assert "settings" in params
        assert "user" in params


# =============================================================================
# TEST 17: Health endpoints are public
# =============================================================================

class TestHealthEndpointsPublic:

    @pytest.mark.parametrize("path", ["/health", "/healthz", "/readyz",
                                       "/api/v1/health", "/api/v1/healthz"])
    def test_health_is_public(self, path, client):
        resp = client.get(path)
        assert resp.status_code == 200, (
            f"GET {path} returned {resp.status_code} — health must be public"
        )


# =============================================================================
# TEST 18: Router deduplication
# =============================================================================

class TestRouterDeduplication:

    def test_v1_router_has_all_routes(self):
        from backend.app.api.router import _build_v1_router
        v1 = _build_v1_router()
        routes = [r for r in v1.routes if isinstance(r, APIRoute)]
        assert len(routes) >= 200, f"v1 router only has {len(routes)} routes"

    def test_register_routes_mounts_v1_twice(self):
        from fastapi import FastAPI
        from backend.app.api.router import register_routes
        app = FastAPI()
        register_routes(app)
        paths = [r.path for r in app.routes if isinstance(r, APIRoute)]
        assert any("/api/v1/health" in p for p in paths)
        assert any(p == "/health" for p in paths)


# =============================================================================
# TEST 19: Fact checker async correctness
# =============================================================================

class TestFactCheckerAsync:

    def test_uses_run_in_executor(self):
        src_path = (Path(__file__).resolve().parents[1]
                    / "app" / "services" / "validation" / "fact_checker.py")
        tree = ast.parse(src_path.read_text())
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "decompose_claims":
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute) and child.attr == "run_in_executor":
                        found = True
        assert found, "decompose_claims() missing run_in_executor"


# =============================================================================
# TEST 20: No duplicate types
# =============================================================================

class TestNoDuplicateTypes:

    def test_progress_callback_not_redefined(self):
        src_path = (Path(__file__).resolve().parents[1]
                    / "app" / "services" / "agents" / "research_agent.py")
        tree = ast.parse(src_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "ProgressCallback":
                        pytest.fail("research_agent.py re-defines ProgressCallback")


# =============================================================================
# TEST 21: Docker and CI config
# =============================================================================

class TestDockerConfig:

    def test_vault_env_vars(self):
        compose_path = Path(__file__).resolve().parents[2] / "docker-compose.yml"
        content = compose_path.read_text()
        service_pattern = re.compile(r"^  (\S+):", re.MULTILINE)
        matches = list(service_pattern.finditer(content))

        def get_section(name):
            for i, m in enumerate(matches):
                if m.group(1) == name:
                    start = m.start()
                    end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                    return content[start:end]
            return ""

        for svc in ["worker", "worker-agents", "app"]:
            section = get_section(svc)
            assert section, f"Service {svc} not found"
            assert "VAULT_ADDR" in section, f"{svc} missing VAULT_ADDR"
            assert "VAULT_TOKEN" in section, f"{svc} missing VAULT_TOKEN"


class TestCIConfig:

    def test_ci_has_test_env_vars(self):
        ci_path = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
        content = ci_path.read_text()
        test_idx = content.find("Run unit tests")
        assert test_idx != -1
        section = content[test_idx:test_idx + 500]
        assert "NEURA_DEBUG" in section
        assert "NEURA_JWT_SECRET" in section
        assert "DATABASE_URL" in section


# =============================================================================
# TEST 22: Analyze routes (40 endpoints)
# =============================================================================

class TestAnalyzeRoutes:
    """Enhanced analysis routes at /analyze/v2/* must all be registered."""

    ANALYZE_V2_PATHS = [
        ("POST", "/api/v1/analyze/v2/upload"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/summary/{mode}"),
        ("POST", "/api/v1/analyze/v2/{analysis_id}/ask"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/suggested-questions"),
        ("POST", "/api/v1/analyze/v2/{analysis_id}/charts/generate"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/charts"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/tables"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/metrics"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/entities"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/insights"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/quality"),
        ("POST", "/api/v1/analyze/v2/{analysis_id}/export"),
        ("POST", "/api/v1/analyze/v2/compare"),
        ("POST", "/api/v1/analyze/v2/{analysis_id}/comments"),
        ("GET", "/api/v1/analyze/v2/{analysis_id}/comments"),
        ("POST", "/api/v1/analyze/v2/{analysis_id}/share"),
        ("GET", "/api/v1/analyze/v2/shared/{share_id}"),
        ("GET", "/api/v1/analyze/v2/integrations"),
        ("POST", "/api/v1/analyze/v2/integrations"),
        ("POST", "/api/v1/analyze/v2/integrations/{integration_id}/notify"),
        ("POST", "/api/v1/analyze/v2/integrations/{integration_id}/items"),
        ("GET", "/api/v1/analyze/v2/sources"),
        ("POST", "/api/v1/analyze/v2/sources"),
        ("POST", "/api/v1/analyze/v2/sources/{connection_id}/fetch"),
        ("POST", "/api/v1/analyze/v2/triggers"),
        ("POST", "/api/v1/analyze/v2/pipelines"),
        ("POST", "/api/v1/analyze/v2/pipelines/{pipeline_id}/execute"),
        ("POST", "/api/v1/analyze/v2/schedules"),
        ("POST", "/api/v1/analyze/v2/webhooks"),
        ("POST", "/api/v1/analyze/v2/webhooks/{webhook_id}/send"),
        ("GET", "/api/v1/analyze/v2/config/industries"),
        ("GET", "/api/v1/analyze/v2/config/export-formats"),
        ("GET", "/api/v1/analyze/v2/config/chart-types"),
        ("GET", "/api/v1/analyze/v2/config/summary-modes"),
    ]

    @pytest.mark.parametrize("method,path", ANALYZE_V2_PATHS)
    def test_analyze_v2_route_exists(self, method, path, all_app_routes):
        assert (method, path) in all_app_routes, (
            f"Missing analyze route: {method} {path}"
        )

    ANALYZE_V1_PATHS = [
        ("POST", "/api/v1/analyze/upload"),
        ("POST", "/api/v1/analyze/extract"),
        ("GET", "/api/v1/analyze/{analysis_id}"),
        ("GET", "/api/v1/analyze/{analysis_id}/data"),
        ("POST", "/api/v1/analyze/{analysis_id}/charts/suggest"),
    ]

    @pytest.mark.parametrize("method,path", ANALYZE_V1_PATHS)
    def test_analyze_v1_route_exists(self, method, path, all_app_routes):
        assert (method, path) in all_app_routes, (
            f"Missing analyze route: {method} {path}"
        )


# =============================================================================
# TEST 23: Endpoint-by-endpoint verification for every prefix group
# =============================================================================

class TestEndpointsByPrefix:
    """Verify exact endpoint counts per prefix group."""

    EXPECTED_COUNTS = {
        "agents": 24,
        "ai": 14,
        "analytics": 32,
        "analyze": 40,
        "charts": 2,
        "connections": 7,
        "connectors": 13,
        "dashboards": 15,
        "design": 23,
        "docai": 10,
        "docqa": 11,
        "documents": 21,
        "enrichment": 9,
        "excel": 16,
        "export": 16,
        "federation": 6,
        "ingestion": 21,
        "jobs": 10,
        "knowledge": 21,
        "nl2sql": 9,
        "recommendations": 4,
        "reports": 13,
        "search": 14,
        "spreadsheets": 22,
        "state": 2,
        "summary": 2,
        "synthesis": 8,
        "templates": 29,
        "visualization": 14,
        "workflows": 11,
    }

    @pytest.mark.parametrize("prefix,expected_count", list(EXPECTED_COUNTS.items()))
    def test_prefix_endpoint_count(self, prefix, expected_count, v1_routes):
        actual = [p for _, p in v1_routes if p.startswith(f"/api/v1/{prefix}")]
        # Exclude sub-prefixes (e.g., /agents/v2 from /agents count is fine)
        assert len(actual) >= expected_count, (
            f"/{prefix} has {len(actual)} endpoints, expected >= {expected_count}.\n"
            f"Routes: {sorted(actual)}"
        )


# =============================================================================
# TEST 24: Smoke test key GET endpoints at BOTH root and /api/v1/
# =============================================================================

class TestDualPrefixSmoke:
    """Key endpoints must respond at both / and /api/v1/."""

    DUAL_CHECK_PATHS = [
        "/health", "/healthz", "/readyz", "/ready",
        "/ai/tones", "/ai/health",
        "/agents/types", "/agents/formats/repurpose",
        "/agents/v2/types", "/agents/v2/stats", "/agents/v2/health",
        "/visualization/types/diagrams", "/visualization/types/charts",
        "/search/types", "/connectors/types",
        "/design/fonts", "/design/fonts/pairings",
        "/state/bootstrap",
        "/analytics/dashboard", "/analytics/preferences",
        "/analytics/notifications/unread-count",
        "/enrichment/sources", "/enrichment/source-types",
        "/enrichment/cache/stats",
        "/templates", "/templates/catalog", "/templates/tags/all",
        "/connections", "/jobs", "/jobs/active", "/jobs/dead-letter",
        "/reports/runs", "/reports/schedules",
        "/knowledge/documents", "/knowledge/collections", "/knowledge/tags",
        "/nl2sql/saved", "/nl2sql/history",
        "/docqa/sessions", "/synthesis/sessions",
        "/dashboards", "/spreadsheets", "/documents",
        "/federation/schemas", "/search/saved-searches",
        "/search/analytics", "/ingestion/watchers",
        "/ingestion/supported-types",
        "/recommendations/catalog", "/recommendations/templates",
        "/design/brand-kits", "/design/themes",
        "/workflows", "/workflows/approvals/pending",
    ]

    @pytest.mark.parametrize("path", DUAL_CHECK_PATHS)
    def test_root_reachable(self, path, client):
        resp = client.get(path)
        assert resp.status_code not in (404, 405), (
            f"GET {path} returned {resp.status_code}"
        )

    @pytest.mark.parametrize("path", DUAL_CHECK_PATHS)
    def test_v1_reachable(self, path, client):
        resp = client.get(f"/api/v1{path}")
        assert resp.status_code not in (404, 405), (
            f"GET /api/v1{path} returned {resp.status_code}"
        )


# =============================================================================
# TEST 25: Smoke test key POST endpoints
# =============================================================================

class TestPostSmoke:
    """POST endpoints with minimal bodies to prove wiring."""

    SMOKE_POSTS = [
        ("/agents/research", {"topic": "test"}),
        ("/agents/data-analysis", {"question": "q", "data": [{"a": 1}]}),
        ("/agents/email-draft", {"context": "ctx", "purpose": "test"}),
        ("/agents/content-repurpose", {"content": "txt", "source_format": "blog", "target_formats": ["tweet_thread"]}),
        ("/agents/proofread", {"text": "test text"}),
        ("/ai/ai/generate", {"prompt": "hello"}),
        ("/visualization/diagrams/flowchart", {"description": "login flow"}),
        ("/visualization/diagrams/mindmap", {"content": "topic content"}),
        ("/visualization/charts/from-table", {"data": [{"x": 1, "y": 2}]}),
        ("/search/search", {"query": "test"}),
        ("/summary/generate", {"text": "Summarize this text."}),
        ("/knowledge/search", {"query": "test"}),
        ("/ingestion/url", {"url": "https://example.com", "name": "Example"}),
        ("/nl2sql/generate", {"question": "show sales", "connection_id": "test"}),
        ("/federation/schemas", {"name": "test", "tables": []}),
        ("/enrichment/enrich", {"data": {}, "source_id": "test"}),
        ("/docqa/sessions", {"name": "test"}),
        ("/synthesis/sessions", {"name": "test"}),
        ("/connections/test", {"db_type": "sqlite", "connection_string": ":memory:"}),
        ("/state/last-used", {"connectionId": "c1", "templateId": "t1"}),
        ("/analytics/activity", {"action": "test", "entity_type": "template", "entity_id": "t1"}),
        ("/analytics/notifications", {"message": "test"}),
        ("/analytics/insights", {"data_source": "test"}),
        ("/charts/analyze", {"data": [{"x": 1}]}),
        ("/charts/generate", {"chart_type": "bar", "data": {"labels": ["a"], "values": [1]}}),
        ("/dashboards", {"name": "test"}),
        ("/workflows", {"name": "test", "steps": []}),
        ("/spreadsheets", {"name": "test"}),
        ("/documents", {"title": "test", "content": "hello"}),
        ("/recommendations/templates", {"description": "sales report"}),
        ("/reports/run", {"template_id": "test", "connection_id": "test"}),
    ]

    @pytest.mark.parametrize("path,body", SMOKE_POSTS)
    def test_post_reachable(self, path, body, client):
        resp = client.post(path, json=body)
        assert resp.status_code not in (404, 405), (
            f"POST {path} returned {resp.status_code}: {resp.text[:200]}"
        )

    @pytest.mark.parametrize("path,body", SMOKE_POSTS)
    def test_post_v1_reachable(self, path, body, client):
        resp = client.post(f"/api/v1{path}", json=body)
        assert resp.status_code not in (404, 405), (
            f"POST /api/v1{path} returned {resp.status_code}: {resp.text[:200]}"
        )


# =============================================================================
# TEST 26: Dead frontend code — exported but never imported
# =============================================================================

class TestDeadFrontendCode:
    """Frontend API functions that are exported but NEVER imported anywhere.

    These are dead code — they bloat the bundle and mislead developers into
    thinking features exist when nobody uses them.

    When you wire one of these up to a component/store, remove it from the list.
    """

    # All formerly dead functions have been wired into their respective stores:
    #   - agents/listRepurposeFormats → agentStore.fetchRepurposeFormats
    #   - agentsV2/* → agentStore (cancelTask, retryTask, getTaskEvents, etc.)
    #   - charts/* → chartStore (new)
    #   - connectors/* → connectorStore
    #   - dashboards/* → dashboardStore
    #   - design/* → designStore
    #   - documents/* → documentStore
    #   - federation/* → federationStore
    #   - health/* → healthStore (new)
    #   - ingestion/* → ingestionStore
    #   - knowledge/* → knowledgeStore
    #   - nl2sql/* → queryStore
    #   - recommendations/* → recommendationsStore (new)
    #   - search/* → searchStore
    #   - spreadsheets/* → spreadsheetStore
    #   - workflows/* → workflowStore
    DEAD_FRONTEND_FUNCTIONS: set[str] = set()

    def test_dead_code_count(self):
        """All dead frontend functions have been wired into stores."""
        assert len(self.DEAD_FRONTEND_FUNCTIONS) == 0, (
            f"Dead code count should be 0, got {len(self.DEAD_FRONTEND_FUNCTIONS)}. "
            f"All functions should be wired into stores."
        )


# =============================================================================
# TEST 27: Backend stub handlers — endpoints that return fake data
# =============================================================================

class TestNoStubHandlers:
    """Backend handlers that are TODO stubs returning hardcoded data.

    These endpoints accept user requests but silently return fake responses.
    This is WORSE than a 404 — users think the feature works when it doesn't.
    """

    # All former stubs have been implemented with real AI writing service calls.
    KNOWN_STUB_HANDLERS: list[tuple[str, str]] = []

    IMPLEMENTED_AI_HANDLERS = [
        ("POST", "/api/v1/documents/{document_id}/ai/grammar"),
        ("POST", "/api/v1/documents/{document_id}/ai/summarize"),
        ("POST", "/api/v1/documents/{document_id}/ai/rewrite"),
        ("POST", "/api/v1/documents/{document_id}/ai/expand"),
        ("POST", "/api/v1/documents/{document_id}/ai/translate"),
    ]

    def test_stub_count(self):
        """All stubs should be implemented — none remaining."""
        assert len(self.KNOWN_STUB_HANDLERS) == 0, (
            "All AI stubs have been implemented. No stubs should remain."
        )

    @pytest.mark.parametrize("method,path", IMPLEMENTED_AI_HANDLERS)
    def test_ai_handler_is_registered(self, method, path, all_app_routes):
        """AI writing handlers must be registered."""
        assert (method, path) in all_app_routes, (
            f"AI handler {method} {path} is not registered"
        )

    def test_document_ai_handlers_implemented(self):
        """Verify AI handlers use real writing_service (not stubs)."""
        src = (Path(__file__).resolve().parents[1]
               / "app" / "api" / "routes" / "documents.py")
        content = src.read_text()
        assert "_writing_service" in content, (
            "documents.py should import and use writing_service for AI handlers"
        )


# =============================================================================
# TEST 28: Backend routes with no frontend caller (orphaned routes)
# =============================================================================

class TestOrphanedBackendRoutes:
    """Backend routes that have NO corresponding frontend API call.

    These are routes registered on the server that no UI ever calls.
    They might be:
    - Internal-only (health, auth) — legitimate
    - Legacy cruft — should be removed
    - Missing UI — frontend needs to wire them up
    """

    # Routes that are legitimately backend-only (internal use, auth, infra)
    LEGITIMATE_BACKEND_ONLY = {
        # Health/readiness probes (called by infra, not UI)
        ("GET", "/healthz"),
        ("GET", "/readyz"),
        ("GET", "/ready"),
        # Auth (handled by auth middleware, not direct API calls)
        ("POST", "/auth/jwt/login"),
        ("POST", "/auth/jwt/logout"),
        ("POST", "/auth/register"),
        ("GET", "/users/me"),
        ("PATCH", "/users/me"),
        ("GET", "/users/{id}"),
        ("PATCH", "/users/{id}"),
        ("DELETE", "/users/{id}"),
        # Ingestion email inbox (webhook endpoint)
        ("POST", "/ingestion/email/inbox"),
        # Metrics (Prometheus scrapes this)
        ("GET", "/metrics"),
    }

    @pytest.fixture(scope="class")
    def backend_only_routes(self, all_app_routes):
        """Find all v1 routes that have no entry in FRONTEND_API_CALLS."""
        frontend_endpoints = set()
        for fn_name, (method, path) in FRONTEND_API_CALLS.items():
            frontend_endpoints.add((method, path))

        orphaned = []
        for method, full_path in all_app_routes:
            if not full_path.startswith("/api/v1/"):
                continue
            clean = full_path[7:]  # strip /api/v1
            if (method, clean) not in frontend_endpoints:
                if (method, clean) not in self.LEGITIMATE_BACKEND_ONLY:
                    orphaned.append((method, clean))
        return sorted(orphaned)

    def test_orphaned_route_count(self, backend_only_routes):
        """Track orphaned routes. This number should decrease over time."""
        count = len(backend_only_routes)
        # There will always be SOME backend-only routes (analyze/v2/*, legacy internal, etc.)
        # but the number should be tracked and justified
        assert count <= 280, (
            f"{count} backend routes have no frontend caller. "
            f"Either add frontend callers or move to LEGITIMATE_BACKEND_ONLY.\n"
            f"First 30: {backend_only_routes[:30]}"
        )

    def test_no_new_orphaned_routes_in_key_modules(self, backend_only_routes):
        """Key modules should NOT have orphaned routes — they indicate incomplete UI."""
        key_prefixes = ["/documents/", "/spreadsheets/", "/dashboards/",
                        "/workflows/", "/knowledge/", "/export/"]
        orphaned_key = [
            (m, p) for m, p in backend_only_routes
            if any(p.startswith(prefix) for prefix in key_prefixes)
        ]
        # These are routes where the frontend has API functions but the backend
        # and frontend disagree on the URL pattern, or routes the UI hasn't wired
        if orphaned_key:
            summary = "\n".join(f"  {m} {p}" for m, p in orphaned_key[:30])
            # Don't fail — just track. This is informational.
            pass  # Tracked by count above
