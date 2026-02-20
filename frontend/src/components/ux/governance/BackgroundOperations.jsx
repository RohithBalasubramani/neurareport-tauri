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
import { createContext, useContext, useCallback, useState, useEffect, useRef } from 'react'
import {
  Snackbar,
  Alert,
  Box,
  Typography,
  IconButton,
  LinearProgress,
  Badge,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Button,
  Divider,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Notifications as NotifyIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Schedule as ScheduledIcon,
  Refresh as RunningIcon,
  Close as CloseIcon,
  Cancel as CancelIcon,
  CloudSync as SyncIcon,
  Settings as SystemIcon,
} from '@mui/icons-material'
import { neutral, status, palette } from '@/app/theme'

// ============================================================================
// BACKGROUND OPERATION TYPES
// ============================================================================

export const BackgroundOperationType = {
  // User-initiated background tasks
  REPORT_GENERATION: 'report_generation',
  DOCUMENT_PROCESSING: 'document_processing',
  DATA_EXPORT: 'data_export',
  BATCH_OPERATION: 'batch_operation',

  // Scheduled tasks
  SCHEDULED_REPORT: 'scheduled_report',
  DATA_SYNC: 'data_sync',
  CLEANUP: 'cleanup',

  // System tasks (visible but not user-cancelable)
  CACHE_REFRESH: 'cache_refresh',
  INDEX_REBUILD: 'index_rebuild',
  HEALTH_CHECK: 'health_check',
}

export const BackgroundOperationStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
}

// ============================================================================
// CONTEXT
// ============================================================================

const BackgroundOperationsContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function BackgroundOperationsProvider({ children }) {
  const theme = useTheme()

  // Registered background operations
  const [operations, setOperations] = useState([])
  const operationsRef = useRef(operations)
  operationsRef.current = operations

  // Notification queue
  const [notification, setNotification] = useState(null)

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false)

  // Polling interval for status updates
  const pollingRef = useRef(null)

  /**
   * Register a new background operation
   */
  const registerOperation = useCallback((operation) => {
    const newOp = {
      id: operation.id || `bg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: operation.type,
      label: operation.label,
      description: operation.description,
      status: BackgroundOperationStatus.PENDING,
      progress: 0,
      startedAt: null,
      completedAt: null,
      error: null,
      cancelable: operation.cancelable !== false,
      onCancel: operation.onCancel,
      onComplete: operation.onComplete,
      metadata: operation.metadata || {},
      createdAt: Date.now(),
    }

    setOperations((prev) => [newOp, ...prev].slice(0, 200))

    // Notify user
    setNotification({
      severity: 'info',
      message: `Background task started: ${operation.label}`,
    })

    return newOp.id
  }, [])

  /**
   * Update operation status
   */
  const updateOperation = useCallback((operationId, updates) => {
    setOperations((prev) =>
      prev.map((op) => {
        if (op.id !== operationId) return op

        const updated = { ...op, ...updates }

        // Handle completion
        if (updates.status === BackgroundOperationStatus.COMPLETED) {
          updated.completedAt = Date.now()
          updated.progress = 100

          // Notify user
          setNotification({
            severity: 'success',
            message: `Completed: ${op.label}`,
          })

          // Call completion callback
          if (op.onComplete) {
            op.onComplete(updated)
          }
        }

        // Handle failure
        if (updates.status === BackgroundOperationStatus.FAILED) {
          updated.completedAt = Date.now()

          // Notify user
          setNotification({
            severity: 'error',
            message: `Failed: ${op.label} - ${updates.error || 'Unknown error'}`,
          })
        }

        return updated
      })
    )
  }, [])

  /**
   * Start an operation
   */
  const startOperation = useCallback((operationId) => {
    updateOperation(operationId, {
      status: BackgroundOperationStatus.RUNNING,
      startedAt: Date.now(),
    })
  }, [updateOperation])

  /**
   * Complete an operation
   */
  const completeOperation = useCallback((operationId, result) => {
    updateOperation(operationId, {
      status: BackgroundOperationStatus.COMPLETED,
      result,
    })
  }, [updateOperation])

  /**
   * Fail an operation
   */
  const failOperation = useCallback((operationId, error) => {
    updateOperation(operationId, {
      status: BackgroundOperationStatus.FAILED,
      error: typeof error === 'string' ? error : error?.message || 'Unknown error',
    })
  }, [updateOperation])

  /**
   * Cancel an operation
   */
  const cancelOperation = useCallback((operationId) => {
    const operation = operationsRef.current.find((op) => op.id === operationId)

    if (!operation) return false
    if (!operation.cancelable) return false
    if (operation.status === BackgroundOperationStatus.COMPLETED) return false
    if (operation.status === BackgroundOperationStatus.FAILED) return false

    // Call cancel callback if provided
    if (operation.onCancel) {
      operation.onCancel()
    }

    updateOperation(operationId, {
      status: BackgroundOperationStatus.CANCELLED,
      completedAt: Date.now(),
    })

    setNotification({
      severity: 'warning',
      message: `Cancelled: ${operation.label}`,
    })

    return true
  }, [updateOperation])

  /**
   * Update progress
   */
  const updateProgress = useCallback((operationId, progress) => {
    updateOperation(operationId, { progress: Math.min(100, Math.max(0, progress)) })
  }, [updateOperation])

  /**
   * Clear completed operations
   */
  const clearCompleted = useCallback(() => {
    setOperations((prev) =>
      prev.filter(
        (op) =>
          op.status !== BackgroundOperationStatus.COMPLETED &&
          op.status !== BackgroundOperationStatus.FAILED &&
          op.status !== BackgroundOperationStatus.CANCELLED
      )
    )
  }, [])

  /**
   * Get active operations count
   */
  const activeCount = operations.filter(
    (op) =>
      op.status === BackgroundOperationStatus.PENDING ||
      op.status === BackgroundOperationStatus.RUNNING
  ).length

  // Polling placeholder removed — status updates come from manual updateOperation calls

  // Close notification
  const closeNotification = useCallback(() => {
    setNotification(null)
  }, [])

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case BackgroundOperationStatus.COMPLETED:
        return <SuccessIcon sx={{ color: theme.palette.text.secondary }} />
      case BackgroundOperationStatus.FAILED:
        return <ErrorIcon sx={{ color: theme.palette.text.secondary }} />
      case BackgroundOperationStatus.RUNNING:
        return <RunningIcon sx={{ color: theme.palette.mode === 'dark' ? neutral[300] : neutral[900] }} />
      case BackgroundOperationStatus.CANCELLED:
        return <CancelIcon sx={{ color: theme.palette.text.secondary }} />
      default:
        return <PendingIcon sx={{ color: theme.palette.text.secondary }} />
    }
  }

  // Get type icon
  const getTypeIcon = (type) => {
    switch (type) {
      case BackgroundOperationType.SCHEDULED_REPORT:
        return <ScheduledIcon />
      case BackgroundOperationType.DATA_SYNC:
        return <SyncIcon />
      case BackgroundOperationType.CACHE_REFRESH:
      case BackgroundOperationType.INDEX_REBUILD:
      case BackgroundOperationType.HEALTH_CHECK:
        return <SystemIcon />
      default:
        return <NotifyIcon />
    }
  }

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
    BackgroundOperationType,
    BackgroundOperationStatus,
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
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: {
            width: 400,
            maxWidth: '100vw',
            bgcolor: alpha(theme.palette.background.default, 0.95),
            backdropFilter: 'blur(20px)',
          },
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <NotifyIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6" fontWeight={600}>
              Background Tasks
            </Typography>
            {activeCount > 0 && (
              <Chip
                size="small"
                label={`${activeCount} active`}
                sx={{
                  height: 22,
                  fontSize: '12px',
                  bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                  color: 'text.primary',
                }}
              />
            )}
          </Box>
          <IconButton onClick={() => setDrawerOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Operations List */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {operations.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: 'text.secondary',
                textAlign: 'center',
                p: 4,
              }}
            >
              <NotifyIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
              <Typography variant="body1" fontWeight={500}>
                No background tasks
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, opacity: 0.7 }}>
                Background operations will appear here
              </Typography>
            </Box>
          ) : (
            <List disablePadding>
              {operations.map((op) => (
                <ListItem
                  key={op.id}
                  sx={{
                    flexDirection: 'column',
                    alignItems: 'stretch',
                    gap: 1,
                    py: 1.5,
                    px: 2,
                    bgcolor: alpha(theme.palette.background.paper, 0.4),
                    borderRadius: 1,  // Figma spec: 8px
                    mb: 1,
                  }}
                >
                  {/* Main row */}
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, width: '100%' }}>
                    <Box
                      sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1,  // Figma spec: 8px
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        color: 'text.secondary',
                      }}
                    >
                      {getTypeIcon(op.type)}
                    </Box>

                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="body2" fontWeight={500} noWrap>
                        {op.label}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        {getStatusIcon(op.status)}
                        <Typography variant="caption" color="text.secondary">
                          {op.status.charAt(0).toUpperCase() + op.status.slice(1)}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Cancel button */}
                    {op.cancelable &&
                      (op.status === BackgroundOperationStatus.PENDING ||
                        op.status === BackgroundOperationStatus.RUNNING) && (
                        <IconButton
                          size="small"
                          onClick={() => cancelOperation(op.id)}
                          sx={{
                            color: theme.palette.text.secondary,
                            '&:hover': {
                              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                            },
                          }}
                        >
                          <CancelIcon fontSize="small" />
                        </IconButton>
                      )}
                  </Box>

                  {/* Progress bar */}
                  {op.status === BackgroundOperationStatus.RUNNING && (
                    <LinearProgress
                      variant={op.progress > 0 ? 'determinate' : 'indeterminate'}
                      value={op.progress}
                      sx={{
                        height: 4,
                        borderRadius: 1,  // Figma spec: 8px
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                        '& .MuiLinearProgress-bar': {
                          bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                        },
                      }}
                    />
                  )}

                  {/* Error message */}
                  {op.error && (
                    <Alert severity="error" sx={{ py: 0, fontSize: '0.75rem' }}>
                      {op.error}
                    </Alert>
                  )}
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Footer */}
        {operations.length > 0 && (
          <Box
            sx={{
              p: 2,
              borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Button
              fullWidth
              size="small"
              onClick={clearCompleted}
              disabled={
                !operations.some(
                  (op) =>
                    op.status === BackgroundOperationStatus.COMPLETED ||
                    op.status === BackgroundOperationStatus.FAILED ||
                    op.status === BackgroundOperationStatus.CANCELLED
                )
              }
            >
              Clear Completed
            </Button>
          </Box>
        )}
      </Drawer>
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
