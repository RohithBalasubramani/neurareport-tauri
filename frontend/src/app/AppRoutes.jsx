/**
 * Application Route Definitions
 * All lazy-loaded page imports and route configuration
 */
import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import {
  Box,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material'
import ProjectLayout from '@/layouts/ProjectLayout.jsx'

// Loading fallback component
export function PageLoader() {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
      }}
    >
      <Stack alignItems="center" spacing={2}>
        <CircularProgress size={32} />
        <Typography variant="body2" color="text.secondary">
          Loading...
        </Typography>
      </Stack>
    </Box>
  )
}

// Lazy-loaded pages - Main app pages
const DashboardPage = lazy(() => import('@/pages/DashboardPage.jsx'))
const ConnectionsPage = lazy(() => import('@/pages/connections/ConnectionsPage.jsx'))
const TemplatesPage = lazy(() => import('@/pages/templates/TemplatesPage.jsx'))
const JobsPage = lazy(() => import('@/pages/jobs/JobsPage.jsx'))
const ReportsPage = lazy(() => import('@/pages/reports/ReportsPage.jsx'))
const SchedulesPage = lazy(() => import('@/pages/schedules/SchedulesPage.jsx'))
const AnalyzePage = lazy(() => import('@/features/analyze/containers/AnalyzePageContainer.jsx'))
const EnhancedAnalyzePage = lazy(() => import('@/features/analyze/containers/EnhancedAnalyzePageContainer.jsx'))
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage.jsx'))
const ActivityPage = lazy(() => import('@/pages/activity/ActivityPage.jsx'))
const HistoryPage = lazy(() => import('@/pages/history/HistoryPage.jsx'))
const UsageStatsPage = lazy(() => import('@/pages/stats/UsageStatsPage.jsx'))
const OpsConsolePage = lazy(() => import('@/pages/ops/OpsConsolePage.jsx'))

// AI Features
const QueryBuilderPage = lazy(() => import('@/pages/query/QueryBuilderPage.jsx'))
const EnrichmentConfigPage = lazy(() => import('@/pages/enrichment/EnrichmentConfigPage.jsx'))
const SchemaBuilderPage = lazy(() => import('@/pages/federation/SchemaBuilderPage.jsx'))
const SynthesisPage = lazy(() => import('@/pages/synthesis/SynthesisPage.jsx'))
const DocumentQAPage = lazy(() => import('@/pages/docqa/DocumentQAPage.jsx'))
const SummaryPage = lazy(() => import('@/pages/summary/SummaryPage.jsx'))

// Document Editing & Creation
const DocumentEditorPage = lazy(() => import('@/pages/documents/DocumentEditorPage.jsx'))
const SpreadsheetEditorPage = lazy(() => import('@/pages/spreadsheets/SpreadsheetEditorPage.jsx'))
const DashboardBuilderPage = lazy(() => import('@/pages/dashboards/DashboardBuilderPage.jsx'))
const ConnectorsPage = lazy(() => import('@/pages/connectors/ConnectorsPage.jsx'))
const WorkflowBuilderPage = lazy(() => import('@/pages/workflows/WorkflowBuilderPage.jsx'))

// New Feature Pages
const AgentsPage = lazy(() => import('@/pages/agents/AgentsPage.jsx'))
const SearchPage = lazy(() => import('@/pages/search/SearchPage.jsx'))
const VisualizationPage = lazy(() => import('@/pages/visualization/VisualizationPage.jsx'))
const KnowledgePage = lazy(() => import('@/pages/knowledge/KnowledgePage.jsx'))
const DesignPage = lazy(() => import('@/pages/design/DesignPage.jsx'))
const IngestionPage = lazy(() => import('@/pages/ingestion/IngestionPage.jsx'))
const WidgetsPage = lazy(() => import('@/pages/widgets/WidgetsPage.jsx'))
const LoggerPage = lazy(() => import('@/pages/logger/LoggerPage.jsx'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage.jsx'))

// Lazy-loaded pages - Setup and editing
const SetupWizard = lazy(() => import('@/pages/setup/SetupWizard.jsx'))
const TemplateEditorPage = lazy(() => import('@/pages/generate/TemplateEditor.jsx'))
const TemplateChatCreatePage = lazy(() => import('@/pages/templates/TemplateChatCreatePage.jsx'))

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Setup Wizard - Standalone route with its own layout */}
        <Route path="/setup/wizard" element={<SetupWizard />} />

        {/* Legacy routes redirect to new layout */}
        <Route path="/setup" element={<Navigate to="/" replace />} />
        <Route path="/generate" element={<Navigate to="/reports" replace />} />

        {/* Main app routes with ProjectLayout (Supabase-style sidebar) */}
        <Route element={<ProjectLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/connections" element={<ConnectionsPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/templates/new/chat" element={<TemplateChatCreatePage />} />
          <Route path="/templates/:templateId/edit" element={<TemplateEditorPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/schedules" element={<SchedulesPage />} />
          <Route path="/analyze" element={<EnhancedAnalyzePage />} />
          <Route path="/analyze/legacy" element={<AnalyzePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/activity" element={<ActivityPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/stats" element={<UsageStatsPage />} />
          <Route path="/ops" element={<OpsConsolePage />} />
          {/* AI Features */}
          <Route path="/query" element={<QueryBuilderPage />} />
          <Route path="/enrichment" element={<EnrichmentConfigPage />} />
          <Route path="/federation" element={<SchemaBuilderPage />} />
          <Route path="/synthesis" element={<SynthesisPage />} />
          <Route path="/docqa" element={<DocumentQAPage />} />
          <Route path="/summary" element={<SummaryPage />} />
          {/* Document Editing & Creation Tools */}
          <Route path="/documents" element={<DocumentEditorPage />} />
          <Route path="/spreadsheets" element={<SpreadsheetEditorPage />} />
          <Route path="/dashboard-builder" element={<DashboardBuilderPage />} />
          <Route path="/connectors" element={<ConnectorsPage />} />
          <Route path="/workflows" element={<WorkflowBuilderPage />} />
          {/* New Feature Pages */}
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/visualization" element={<VisualizationPage />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="/design" element={<DesignPage />} />
          <Route path="/ingestion" element={<IngestionPage />} />
          <Route path="/widgets" element={<WidgetsPage />} />
          <Route path="/logger" element={<LoggerPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
