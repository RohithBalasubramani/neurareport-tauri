# NeuraReport Frontend

This package contains the NeuraReport web UI built with React 19 + Vite + MUI v7. The theme enforces flat 12px surfaces with outlined papers, so please avoid reintroducing component-level elevations or oversized rounded corners.

## Install

```sh
npm install
```

## Development

- `npm run dev` - start the Vite dev server
- `npm run lint` - run ESLint checks
- `npm run build` - production bundle
- `npm run test:ui` / `npm run test:a11y` / `npm run test:visual` - execute Playwright suites

Tip: copy `frontend/.env.example` to `frontend/.env.local` to configure the backend URL and mock mode.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Backend API URL |
| `VITE_USE_MOCK` | `true` | Enable mock mode (no backend required) |

## Architecture

### Pages (33 modules)

Route-level composition lives under `src/pages/`:

| Page | Route | Description |
|---|---|---|
| `DashboardPage` | `/` | Main dashboard overview |
| `ConnectionsPage` | `/connections` | Database connection management |
| `ConnectorsPage` | `/connectors` | External connector configuration |
| `TemplatesPage` | `/templates` | Template catalog and management |
| `ReportsPage` | `/reports` | Report generation and history |
| `JobsPage` | `/jobs` | Async job monitoring |
| `SchedulesPage` | `/schedules` | Report scheduling with cron triggers |
| `SetupWizard` | `/setup` | Connect → Upload → Verify wizard |
| `TemplateEditor` | `/generate/edit` | Template editing with AI chat |
| `AgentsPage` | `/agents` | AI agent task management |
| `DocumentEditorPage` | `/documents` | Document editing and collaboration |
| `SpreadsheetEditorPage` | `/spreadsheets` | Spreadsheet editor with formulas |
| `EnrichmentConfigPage` | `/enrichment` | Data enrichment configuration |
| `SchemaBuilderPage` | `/federation` | Federated schema queries |
| `DocumentQAPage` | `/docqa` | Document Q&A interface |
| `KnowledgePage` | `/knowledge` | Knowledge library management |
| `SearchPage` | `/search` | Full-text search |
| `QueryBuilderPage` | `/query` | NL2SQL query builder |
| `DashboardBuilderPage` | `/dashboards` | Custom dashboard builder |
| `DesignPage` | `/design` | Brand kit and design system |
| `VisualizationPage` | `/visualization` | Chart and visualization builder |
| `WorkflowBuilderPage` | `/workflows` | Workflow automation builder |
| `SynthesisPage` | `/synthesis` | Cross-source data synthesis |
| `SummaryPage` | `/summary` | AI-generated summaries |
| `IngestionPage` | `/ingestion` | File, URL, and email ingestion |
| `HistoryPage` | `/history` | Activity history |
| `UsageStatsPage` | `/stats` | Usage metrics |
| `OpsConsolePage` | `/ops` | Operations console and diagnostics |
| `ActivityPage` | `/activity` | User activity logs |
| `AnalyzePage` | `/analyze` | Data analysis engine |
| `FavoritesPage` | *(cross-feature)* | Bookmarking system |
| `ShellPage` | *(global)* | Command palette (Cmd+K) |
| `SettingsPage` | `/settings` | Application settings |

### State Management (Zustand)

State stores live under `src/stores/`. Each feature domain has its own store:

`useAppStore`, `agentStore`, `connectionStore`, `connectorStore`, `crossPageStore`, `dashboardStore`, `designStore`, `docqaStore`, `documentStore`, `enrichmentStore`, `exportStore`, `federationStore`, `ingestionStore`, `knowledgeStore`, `queryStore`, `searchStore`, `spreadsheetStore`, `summaryStore`, `synthesisStore`, `templateChatStore`, `visualizationStore`, `workflowStore`

### API Clients

API client modules under `src/api/` handle all backend communication:

`agents.js`, `agentsV2.js`, `charts.js`, `connectors.js`, `dashboards.js`, `design.js`, `docqa.js`, `documents.js`, `enrichment.js`, `export.js`, `federation.js`, `health.js`, `ingestion.js`, `knowledge.js`, `nl2sql.js`, `recommendations.js`, `search.js`, `spreadsheets.js`, `summary.js`, `synthesis.js`, `visualization.js`, `workflows.js`

### Folder Structure

See `docs/architecture/ARCHITECTURE_GOVERNANCE.md` for enforced dependency boundaries. In summary:

- `src/pages/` → route-level composition
- `src/features/` → feature modules and domain UI logic
- `src/layouts/` → structural shells (AppLayout, ProjectLayout, WizardLayout, SettingsLayout)
- `src/navigation/` → Sidebar, TopNav, Breadcrumbs, GlobalSearch, NotificationCenter
- `src/components/` → reusable UI building blocks (ConnectionSelector, ImportFromMenu, SendToMenu, TemplateSelector, DataTable, ErrorBoundary, etc.)
- `src/ui/` → design primitives (Button, Input, IconButton, Kbd, ScrollArea)
- `src/hooks/` → reusable logic (useJobs, useUploadProgress, useKeyboardShortcuts, useCrossPageActions, useIncomingTransfer, useSharedData, useBootstrapState, useNetworkStatus, useFormErrorFocus, useStepTimingEstimator)
- `src/stores/` → Zustand state containers
- `src/api/` → API client boundary
- `src/utils/` → shared helpers

## Testing

### Unit Tests

```sh
npm run test
```

### End-to-End Tests (Playwright)

```sh
npx playwright install --with-deps   # once per machine
npm run test:ui                       # UI tests
npm run test:a11y                     # Accessibility (axe)
npm run test:visual                   # Visual regression
```

Test specs live under `tests/`:

- `tests/e2e/` - Navigation, user flows, visual regression, store governance, horizontal scroll checks
- `tests/e2e/integration/` - 20 feature-level integration specs (dashboard, connections, connectors, templates, reports, jobs, schedules, query builder, documents, spreadsheets, enrichment, federation, synthesis, docqa, workflows, dashboards, knowledge, design/visualization, agents/ingestion, settings)
- `tests/unit/` - Unit tests for API clients, utilities, and stores
- `tests/a11y/` - Axe accessibility audit

Snapshots live under `frontend/playwright-report` and `playwright-results`.

## Layout Sanity Checklist

- Spot-check Setup (Connect, Generate Templates, Generate Report) and Generate routes at 360, 390, 414, 768, 1024, 1280, and 1440 px widths for zero horizontal scroll.
- Run the automated viewport guard: `npm run test:ui -- tests/e2e/no-horizontal-scroll.spec.js`.
- Ensure tables, previews, and dialogs stay within their containers with responsive wrapping before merging layout changes.

## Release Checklist

Run the build pipeline from a clean slate to ensure the UI renders with the latest theme overrides:

1. `npm run clean`
2. `npm run build`
3. `npm run preview`

The `clean` script removes the Vite build output and cache folders (`dist`, `node_modules/.vite`) so the subsequent build reflects current sources.
