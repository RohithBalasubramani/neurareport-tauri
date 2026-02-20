import { useMemo, lazy, Suspense, useState, useCallback, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import {
  ThemeProvider,
  CssBaseline,
  Box,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import ErrorBoundary from '@/components/ErrorBoundary.jsx'
import JobsPanel from '@/features/jobs/components/JobsPanel.jsx'
import CommandPalette from '@/features/shell/components/CommandPalette.jsx'
import { recordIntent, updateIntent } from '@/api/intentAudit'
import theme, { neutral } from './theme.js'
import { useBootstrapState } from '@/hooks/useBootstrapState.js'
import { useKeyboardShortcuts, SHORTCUTS } from '@/hooks/useKeyboardShortcuts.js'
import ProjectLayout from '@/layouts/ProjectLayout.jsx'
import { readPreferences, subscribePreferences } from '@/utils/preferences'
// UX Infrastructure - Premium interaction components
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import NetworkStatusBanner from '@/components/ux/NetworkStatusBanner'
import ActivityPanel from '@/components/ux/ActivityPanel'
// UX Governance - Enforced interaction safety
import {
  UXGovernanceProvider,
  useInteraction,
  useNavigateInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'

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
const SetupWizard = lazy(() => import('@/pages/Setup/SetupWizard.jsx'))
const TemplateEditorPage = lazy(() => import('@/pages/Generate/TemplateEditor.jsx'))
const TemplateChatCreatePage = lazy(() => import('@/pages/templates/TemplateChatCreatePage.jsx'))

const intentAuditClient = { recordIntent, updateIntent }

// Loading fallback component
function PageLoader() {
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

// Query client configuration
function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 30000,
      },
    },
  })
}

// App Providers wrapper
function AppProviders({ children }) {
  const queryClient = useMemo(createQueryClient, [])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  )
}

// Main app content with shell layout
function AppContent() {
  // Bootstrap state (hydrate from localStorage)
  useBootstrapState()

  // UI State
  const { execute } = useInteraction()
  const [jobsOpen, setJobsOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [activityOpen, setActivityOpen] = useState(false)

  // Handlers
  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'app', ...intent },
      action,
    })
  }, [execute])

  const handleOpenJobs = useCallback(
    () => executeUI('Open jobs panel', () => setJobsOpen(true), { panel: 'jobs' }),
    [executeUI],
  )
  const handleCloseJobs = useCallback(
    () => executeUI('Close jobs panel', () => setJobsOpen(false), { panel: 'jobs' }),
    [executeUI],
  )
  const handleOpenCommandPalette = useCallback(
    () => executeUI('Open command palette', () => setCommandPaletteOpen(true), { panel: 'command-palette' }),
    [executeUI],
  )
  const handleCloseCommandPalette = useCallback(
    () => executeUI('Close command palette', () => setCommandPaletteOpen(false), { panel: 'command-palette' }),
    [executeUI],
  )
  const handleOpenActivity = useCallback(
    () => executeUI('Open activity panel', () => setActivityOpen(true), { panel: 'activity' }),
    [executeUI],
  )
  const handleCloseActivity = useCallback(
    () => executeUI('Close activity panel', () => setActivityOpen(false), { panel: 'activity' }),
    [executeUI],
  )

  const handleSkipToContent = useCallback(() => {
    return executeUI('Skip to content', () => {
      const target = document.getElementById('main-content')
      if (target) {
        target.focus()
        target.scrollIntoView({ behavior: 'smooth' })
      }
    }, { action: 'skip-to-content' })
  }, [executeUI])

  // Register global keyboard shortcuts
  useKeyboardShortcuts({
    [SHORTCUTS.COMMAND_PALETTE]: handleOpenCommandPalette,
    'escape': () => {
      if (commandPaletteOpen) handleCloseCommandPalette()
      else if (activityOpen) handleCloseActivity()
      else if (jobsOpen) handleCloseJobs()
    },
  })

  useEffect(() => {
    const handleOpenCommandPaletteEvent = () => {
      handleOpenCommandPalette().catch(() => {})
    }
    const handleOpenJobsPanelEvent = () => {
      handleOpenJobs().catch(() => {})
    }
    const handleOpenActivityPanelEvent = () => {
      handleOpenActivity().catch(() => {})
    }
    window.addEventListener('neura:open-command-palette', handleOpenCommandPaletteEvent)
    window.addEventListener('neura:open-jobs-panel', handleOpenJobsPanelEvent)
    window.addEventListener('neura:open-activity-panel', handleOpenActivityPanelEvent)
    return () => {
      window.removeEventListener('neura:open-command-palette', handleOpenCommandPaletteEvent)
      window.removeEventListener('neura:open-jobs-panel', handleOpenJobsPanelEvent)
      window.removeEventListener('neura:open-activity-panel', handleOpenActivityPanelEvent)
    }
  }, [handleOpenCommandPalette, handleOpenJobs, handleOpenActivity])

  useEffect(() => {
    if (typeof document === 'undefined') return undefined
    const applyCompactTables = (prefs) => {
      const enabled = prefs?.compactTables ?? false
      document.body.dataset.compactTables = enabled ? 'true' : 'false'
    }
    applyCompactTables(readPreferences())
    return subscribePreferences(applyCompactTables)
  }, [])

  return (
    <>
      {/* Network Status Banner - Visible connectivity feedback */}
      <NetworkStatusBanner />

      {/* Skip to content link for accessibility */}
      <Box
        component="a"
        href="#main-content"
        data-testid="skip-to-content"
        onClick={(e) => {
          e.preventDefault()
          handleSkipToContent()
        }}
        sx={{
          position: 'fixed',
          top: -40,
          left: 16,
          zIndex: 9999,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          color: 'primary.contrastText',
          px: 2,
          py: 1,
          borderRadius: 1,
          textDecoration: 'none',
          fontWeight: 600,
          transition: 'top 160ms ease',
          '&:focus-visible': {
            top: 16,
            outline: '2px solid',
            outlineColor: 'primary.dark',
            outlineOffset: 2,
          },
        }}
      >
        Skip to content
      </Box>

      {/* Main Content */}
      <Box
        id="main-content"
        component="main"
        tabIndex={-1}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          outline: 'none',
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
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
      </Box>

      {/* Overlays */}
      <JobsPanel open={jobsOpen} onClose={handleCloseJobs} />
      <CommandPalette open={commandPaletteOpen} onClose={handleCloseCommandPalette} />
      <ActivityPanel open={activityOpen} onClose={handleCloseActivity} />
    </>
  )
}

function StaticErrorFallback() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 4,
      }}
    >
      <Stack spacing={1} sx={{ maxWidth: 520, textAlign: 'center' }}>
        <Typography variant="h5" fontWeight={600} color="text.primary">
          Something went wrong
        </Typography>
        <Typography variant="body2" color="text.secondary">
          An unexpected error occurred. Refresh the page to continue.
        </Typography>
      </Stack>
    </Box>
  )
}

function GovernedErrorBoundary({ children }) {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'error-boundary', ...intent },
      action,
    })
  }, [execute])

  const handleReload = useCallback(
    () => executeUI('Reload application', () => window.location.reload(), { action: 'reload' }),
    [executeUI],
  )

  const handleGoHome = useCallback(
    () => navigate('/', { label: 'Go to dashboard', intent: { source: 'error-boundary' } }),
    [navigate],
  )

  return (
    <ErrorBoundary onReload={handleReload} onGoHome={handleGoHome}>
      {children}
    </ErrorBoundary>
  )
}

// Root App component
export default function App() {
  return (
    <ErrorBoundary fallback={StaticErrorFallback}>
      <BrowserRouter basename={import.meta.env.VITE_ROUTER_BASENAME || import.meta.env.BASE_URL.replace(/\/+$/, '') || ''}>
        <AppProviders>
          <OperationHistoryProvider>
            <UXGovernanceProvider auditClient={intentAuditClient}>
              <ToastProvider>
                <GovernedErrorBoundary>
                  <AppContent />
                </GovernedErrorBoundary>
              </ToastProvider>
            </UXGovernanceProvider>
          </OperationHistoryProvider>
        </AppProviders>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
