import { useMemo, useState, useCallback, useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import {
  Box,
  Stack,
  Typography,
} from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '@/components/ToastProvider.jsx'
import ErrorBoundary from '@/components/ErrorBoundary.jsx'
import JobsPanel from '@/features/jobs/components/JobsPanel.jsx'
import CommandPalette from '@/features/shell/components/CommandPalette.jsx'
import { recordIntent, updateIntent } from '@/api/intentAudit'
import { ThemeProvider } from '@/shared/theme'
import { neutral } from './theme.js'
import { useBootstrapState } from '@/hooks/useBootstrapState.js'
import { useKeyboardShortcuts, SHORTCUTS } from '@/hooks/useKeyboardShortcuts.js'
import { readPreferences, subscribePreferences } from '@/utils/preferences'
import { OperationHistoryProvider } from '@/components/ux/OperationHistoryProvider'
import NetworkStatusBanner from '@/components/ux/NetworkStatusBanner'
import ActivityPanel from '@/components/ux/ActivityPanel'
import {
  UXGovernanceProvider,
  useInteraction,
  InteractionType,
  Reversibility,
} from '@/components/ux/governance'
import AppRoutes from './AppRoutes.jsx'
import GovernedErrorBoundary from './GovernedErrorBoundary.jsx'

const intentAuditClient = { recordIntent, updateIntent }

function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { refetchOnWindowFocus: false, retry: 1, staleTime: 30000 },
    },
  })
}

function AppProviders({ children }) {
  const queryClient = useMemo(createQueryClient, [])
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </ThemeProvider>
  )
}

function AppContent() {
  useBootstrapState()
  const { execute } = useInteraction()
  const [jobsOpen, setJobsOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [activityOpen, setActivityOpen] = useState(false)

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
      if (target) { target.focus(); target.scrollIntoView({ behavior: 'smooth' }) }
    }, { action: 'skip-to-content' })
  }, [executeUI])

  useKeyboardShortcuts({
    [SHORTCUTS.COMMAND_PALETTE]: handleOpenCommandPalette,
    'escape': () => {
      if (commandPaletteOpen) handleCloseCommandPalette()
      else if (activityOpen) handleCloseActivity()
      else if (jobsOpen) handleCloseJobs()
    },
  })

  useEffect(() => {
    const onCmd = () => { handleOpenCommandPalette().catch(() => {}) }
    const onJobs = () => { handleOpenJobs().catch(() => {}) }
    const onActivity = () => { handleOpenActivity().catch(() => {}) }
    window.addEventListener('neura:open-command-palette', onCmd)
    window.addEventListener('neura:open-jobs-panel', onJobs)
    window.addEventListener('neura:open-activity-panel', onActivity)
    return () => {
      window.removeEventListener('neura:open-command-palette', onCmd)
      window.removeEventListener('neura:open-jobs-panel', onJobs)
      window.removeEventListener('neura:open-activity-panel', onActivity)
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
      <NetworkStatusBanner />
      <Box
        component="a"
        href="#main-content"
        data-testid="skip-to-content"
        onClick={(e) => { e.preventDefault(); handleSkipToContent() }}
        sx={{
          position: 'fixed', top: -40, left: 16, zIndex: 9999,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          color: 'primary.contrastText', px: 2, py: 1, borderRadius: 1,
          textDecoration: 'none', fontWeight: 600, transition: 'top 160ms ease',
          '&:focus-visible': { top: 16, outline: '2px solid', outlineColor: 'primary.dark', outlineOffset: 2 },
        }}
      >
        Skip to content
      </Box>
      <Box id="main-content" component="main" tabIndex={-1}
        sx={{ display: 'flex', flexDirection: 'column', outline: 'none', minHeight: '100vh', bgcolor: 'background.default' }}
      >
        <AppRoutes />
      </Box>
      <JobsPanel open={jobsOpen} onClose={handleCloseJobs} />
      <CommandPalette open={commandPaletteOpen} onClose={handleCloseCommandPalette} />
      <ActivityPanel open={activityOpen} onClose={handleCloseActivity} />
    </>
  )
}

function StaticErrorFallback() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'background.default', p: 4 }}>
      <Stack spacing={1} sx={{ maxWidth: 520, textAlign: 'center' }}>
        <Typography variant="h5" fontWeight={600} color="text.primary">Something went wrong</Typography>
        <Typography variant="body2" color="text.secondary">An unexpected error occurred. Refresh the page to continue.</Typography>
      </Stack>
    </Box>
  )
}

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
