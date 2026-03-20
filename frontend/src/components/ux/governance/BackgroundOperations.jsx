/**
 * UX Governance Level-2: Background Operations Visibility
 *
 * ENFORCES that:
 * - All background/scheduled operations are registered and visible
 * - Users are notified when background tasks complete or fail
 * - Long-running operations show progress
 * - Users can cancel background operations where allowed
 *
 * NO SILENT BACKGROUND WORK - everything is visible and tracked.
 */
import { createContext, useContext, useCallback, useRef } from 'react'
import { Snackbar, Alert, IconButton, Badge, useTheme } from '@mui/material'
import { Notifications as NotifyIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { useBackgroundOps } from './hooks/useBackgroundOps'
import BackgroundOpsDrawer from './BackgroundOpsDrawer'

// Re-export constants for backwards compatibility
export { BackgroundOperationType, BackgroundOperationStatus } from './backgroundConstants'

// ============================================================================
// CONTEXT
// ============================================================================

const BackgroundOperationsContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function BackgroundOperationsProvider({ children }) {
  const {
    operations,
    activeCount,
    notification,
    closeNotification,
    drawerOpen,
    setDrawerOpen,
    registerOperation,
    startOperation,
    completeOperation,
    failOperation,
    cancelOperation,
    updateProgress,
    updateOperation,
    clearCompleted,
  } = useBackgroundOps()

  const contextValue = {
    operations,
    activeCount,
    registerOperation,
    startOperation,
    completeOperation,
    failOperation,
    cancelOperation,
    updateProgress,
    updateOperation,
    clearCompleted,
    openDrawer: () => setDrawerOpen(true),
    closeDrawer: () => setDrawerOpen(false),
  }

  return (
    <BackgroundOperationsContext.Provider value={contextValue}>
      {children}

      {/* Notification Snackbar */}
      <Snackbar
        open={!!notification}
        autoHideDuration={4000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {notification && (
          <Alert
            onClose={closeNotification}
            severity={notification.severity}
            variant="filled"
            sx={{ minWidth: 300 }}
          >
            {notification.message}
          </Alert>
        )}
      </Snackbar>

      {/* Background Operations Drawer */}
      <BackgroundOpsDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        operations={operations}
        activeCount={activeCount}
        onCancelOperation={cancelOperation}
        onClearCompleted={clearCompleted}
      />
    </BackgroundOperationsContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useBackgroundOperations() {
  const context = useContext(BackgroundOperationsContext)
  if (!context) {
    throw new Error('useBackgroundOperations must be used within BackgroundOperationsProvider')
  }
  return context
}

/**
 * Hook to manage a single background operation
 */
export function useBackgroundTask(type, label) {
  const {
    registerOperation,
    startOperation,
    completeOperation,
    failOperation,
    updateProgress,
  } = useBackgroundOperations()

  const operationIdRef = useRef(null)

  const start = useCallback((options = {}) => {
    const id = registerOperation({
      type,
      label,
      ...options,
    })
    operationIdRef.current = id
    startOperation(id)
    return id
  }, [type, label, registerOperation, startOperation])

  const complete = useCallback((result) => {
    if (operationIdRef.current) {
      completeOperation(operationIdRef.current, result)
      operationIdRef.current = null
    }
  }, [completeOperation])

  const fail = useCallback((error) => {
    if (operationIdRef.current) {
      failOperation(operationIdRef.current, error)
      operationIdRef.current = null
    }
  }, [failOperation])

  const setProgress = useCallback((progress) => {
    if (operationIdRef.current) {
      updateProgress(operationIdRef.current, progress)
    }
  }, [updateProgress])

  return { start, complete, fail, setProgress, isActive: !!operationIdRef.current }
}

// ============================================================================
// BUTTON COMPONENT FOR HEADER
// ============================================================================

export function BackgroundTasksButton() {
  const theme = useTheme()
  const { activeCount, openDrawer } = useBackgroundOperations()

  return (
    <IconButton
      onClick={openDrawer}
      sx={{
        color: activeCount > 0 ? (theme.palette.mode === 'dark' ? neutral[300] : neutral[900]) : theme.palette.text.secondary,
      }}
    >
      <Badge
        badgeContent={activeCount}
        max={99}
        sx={{
          '& .MuiBadge-badge': {
            fontSize: '10px',
            height: 16,
            minWidth: 16,
            bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
            color: 'common.white',
          },
        }}
      >
        <NotifyIcon />
      </Badge>
    </IconButton>
  )
}
