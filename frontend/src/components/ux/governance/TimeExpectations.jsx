/**
 * UX Governance Level-2: Time Expectations and Escalation
 *
 * ENFORCES that:
 * - Every operation has defined time expectations
 * - Users see accurate progress and time estimates
 * - Stalled operations are detected and escalated
 * - Long-running operations provide cancellation options
 *
 * VIOLATIONS FAIL FAST - no silent timeouts.
 */
import { createContext, useContext, useCallback, useRef, useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  LinearProgress,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Timer as TimerIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RetryIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// ============================================================================
// TIME EXPECTATION DEFINITIONS
// ============================================================================

/**
 * Expected durations by operation type (in milliseconds)
 * These are ENFORCED, not advisory.
 */
export const TimeExpectations = {
  // Instant operations (< 500ms)
  INSTANT: {
    expected: 200,
    warning: 500,
    timeout: 2000,
    label: 'Instant',
  },

  // Quick operations (< 2s)
  QUICK: {
    expected: 500,
    warning: 2000,
    timeout: 5000,
    label: 'Quick',
  },

  // Standard operations (< 10s)
  STANDARD: {
    expected: 2000,
    warning: 10000,
    timeout: 30000,
    label: 'Standard',
  },

  // Long operations (< 60s)
  LONG: {
    expected: 10000,
    warning: 60000,
    timeout: 120000,
    label: 'Long',
  },

  // Extended operations (< 5min)
  EXTENDED: {
    expected: 60000,
    warning: 180000,
    timeout: 300000,
    label: 'Extended',
  },

  // Background operations (no timeout, but tracked)
  BACKGROUND: {
    expected: null,
    warning: 300000, // 5 min
    timeout: null,
    label: 'Background',
  },
}

/**
 * Map operation types to time expectations
 */
export const OperationTimeMap = {
  // CREATE operations
  create_session: TimeExpectations.QUICK,
  create_document: TimeExpectations.QUICK,
  create_query: TimeExpectations.QUICK,

  // UPLOAD operations
  upload_document: TimeExpectations.STANDARD,
  upload_file: TimeExpectations.STANDARD,

  // GENERATE operations (AI-powered)
  generate_sql: TimeExpectations.LONG,
  generate_synthesis: TimeExpectations.EXTENDED,
  generate_response: TimeExpectations.LONG,

  // ANALYZE operations
  analyze_documents: TimeExpectations.LONG,
  find_inconsistencies: TimeExpectations.LONG,

  // EXECUTE operations
  execute_query: TimeExpectations.STANDARD,

  // DELETE operations
  delete_session: TimeExpectations.QUICK,
  delete_document: TimeExpectations.INSTANT,

  // Default fallback
  default: TimeExpectations.STANDARD,
}

// ============================================================================
// ESCALATION LEVELS
// ============================================================================

export const EscalationLevel = {
  NONE: 'none',
  WARNING: 'warning',
  CRITICAL: 'critical',
  TIMEOUT: 'timeout',
}

// ============================================================================
// CONTEXT
// ============================================================================

const TimeExpectationContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function TimeExpectationProvider({ children }) {
  const theme = useTheme()

  // Active operations being tracked
  const [activeOperations, setActiveOperations] = useState(new Map())
  const activeOpsRef = useRef(activeOperations)
  activeOpsRef.current = activeOperations

  // Escalation dialog state
  const [escalationDialog, setEscalationDialog] = useState({
    open: false,
    operationId: null,
    level: EscalationLevel.NONE,
    operation: null,
  })

  // Interval refs for cleanup (capped to prevent unbounded growth)
  const MAX_TRACKED_OPERATIONS = 200
  const checkIntervals = useRef(new Map())

  // Use ref to avoid TDZ issues with circular dependencies between hooks
  const escalateOperationRef = useRef()

  /**
   * Escalate an operation to a higher level
   */
  const escalateOperation = useCallback((operationId, level) => {
    setActiveOperations((prev) => {
      const next = new Map(prev)
      const operation = next.get(operationId)
      if (operation && operation.escalationLevel !== EscalationLevel.TIMEOUT) {
        operation.escalationLevel = level
        next.set(operationId, { ...operation })

        // Show escalation dialog for warning and above
        if (level === EscalationLevel.WARNING || level === EscalationLevel.TIMEOUT) {
          setEscalationDialog({
            open: true,
            operationId,
            level,
            operation,
          })
        }
      }
      return next
    })
  }, [])

  // Store in ref for use in other hooks
  escalateOperationRef.current = escalateOperation

  /**
   * Start tracking an operation with time expectations
   */
  const startTracking = useCallback((operationId, operationType, options = {}) => {
    const timeConfig = OperationTimeMap[operationType] || OperationTimeMap.default
    const startTime = Date.now()

    const operation = {
      id: operationId,
      type: operationType,
      label: options.label || operationType,
      timeConfig,
      startTime,
      escalationLevel: EscalationLevel.NONE,
      onCancel: options.onCancel,
      onRetry: options.onRetry,
      abortController: options.abortController,
    }

    setActiveOperations((prev) => {
      const next = new Map(prev)
      // Evict oldest entries if cap reached
      if (next.size >= MAX_TRACKED_OPERATIONS) {
        const oldest = next.keys().next().value
        next.delete(oldest)
      }
      next.set(operationId, operation)
      return next
    })

    // Set up escalation checks
    if (timeConfig.warning) {
      const warningTimeout = setTimeout(() => {
        escalateOperationRef.current?.(operationId, EscalationLevel.WARNING)
      }, timeConfig.warning)

      checkIntervals.current.set(`${operationId}-warning`, warningTimeout)
    }

    if (timeConfig.timeout) {
      const timeoutTimeout = setTimeout(() => {
        escalateOperationRef.current?.(operationId, EscalationLevel.TIMEOUT)
      }, timeConfig.timeout)

      checkIntervals.current.set(`${operationId}-timeout`, timeoutTimeout)
    }

    return operation
  }, [])

  /**
   * Complete tracking for an operation
   */
  const completeTracking = useCallback((operationId, success = true) => {
    // Clear all timeouts for this operation
    const warningKey = `${operationId}-warning`
    const timeoutKey = `${operationId}-timeout`

    if (checkIntervals.current.has(warningKey)) {
      clearTimeout(checkIntervals.current.get(warningKey))
      checkIntervals.current.delete(warningKey)
    }
    if (checkIntervals.current.has(timeoutKey)) {
      clearTimeout(checkIntervals.current.get(timeoutKey))
      checkIntervals.current.delete(timeoutKey)
    }

    // Remove from active operations
    setActiveOperations((prev) => {
      const next = new Map(prev)
      next.delete(operationId)
      return next
    })

    // Close escalation dialog if it was for this operation
    setEscalationDialog((prev) => {
      if (prev.operationId === operationId) {
        return { open: false, operationId: null, level: EscalationLevel.NONE, operation: null }
      }
      return prev
    })
  }, [])

  /**
   * Cancel an operation
   */
  const cancelOperation = useCallback((operationId) => {
    const operation = activeOpsRef.current.get(operationId)
    if (operation) {
      // Abort if controller exists
      if (operation.abortController) {
        operation.abortController.abort()
      }

      // Call cancel callback
      if (operation.onCancel) {
        operation.onCancel()
      }

      completeTracking(operationId, false)
    }
  }, [completeTracking])

  /**
   * Retry an operation
   */
  const retryOperation = useCallback((operationId) => {
    const operation = activeOpsRef.current.get(operationId)
    if (operation && operation.onRetry) {
      completeTracking(operationId, false)
      operation.onRetry()
    }
  }, [completeTracking])

  /**
   * Get elapsed time for an operation
   */
  const getElapsedTime = useCallback((operationId) => {
    const operation = activeOpsRef.current.get(operationId)
    if (!operation) return 0
    return Date.now() - operation.startTime
  }, [])

  /**
   * Get progress percentage (based on expected time)
   */
  const getProgress = useCallback((operationId) => {
    const operation = activeOpsRef.current.get(operationId)
    if (!operation || !operation.timeConfig.expected) return null

    const elapsed = Date.now() - operation.startTime
    const expected = operation.timeConfig.expected
    return Math.min(100, (elapsed / expected) * 100)
  }, [])

  // Clean up all pending timeouts on unmount
  useEffect(() => {
    const intervals = checkIntervals.current
    return () => {
      intervals.forEach((timeout) => clearTimeout(timeout))
      intervals.clear()
    }
  }, [])

  // Close escalation dialog
  const closeEscalationDialog = useCallback(() => {
    setEscalationDialog({ open: false, operationId: null, level: EscalationLevel.NONE, operation: null })
  }, [])

  // Get escalation config
  const getEscalationConfig = (level) => {
    const configs = {
      [EscalationLevel.WARNING]: {
        icon: WarningIcon,
        color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
        title: 'Operation Taking Longer Than Expected',
        message: 'This operation is taking longer than usual. You can wait, retry, or cancel.',
      },
      [EscalationLevel.TIMEOUT]: {
        icon: ErrorIcon,
        color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
        title: 'Operation Timed Out',
        message: 'This operation has exceeded its time limit. Please retry or cancel.',
      },
    }
    return configs[level] || configs[EscalationLevel.WARNING]
  }

  const contextValue = {
    startTracking,
    completeTracking,
    cancelOperation,
    retryOperation,
    getElapsedTime,
    getProgress,
    activeOperations,
    TimeExpectations,
    OperationTimeMap,
  }

  const escalationConfig = escalationDialog.level !== EscalationLevel.NONE
    ? getEscalationConfig(escalationDialog.level)
    : null
  const EscalationIcon = escalationConfig?.icon

  return (
    <TimeExpectationContext.Provider value={contextValue}>
      {children}

      {/* Escalation Dialog */}
      <Dialog
        open={escalationDialog.open}
        onClose={closeEscalationDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 1,  // Figma spec: 8px
            border: `2px solid ${escalationConfig?.color || theme.palette.divider}`,
          },
        }}
      >
        {escalationConfig && (
          <>
            <DialogTitle
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
              }}
            >
              <EscalationIcon sx={{ color: escalationConfig.color }} />
              <Typography variant="h6" fontWeight={600}>
                {escalationConfig.title}
              </Typography>
            </DialogTitle>

            <DialogContent sx={{ pt: 3 }}>
              <Alert severity={escalationDialog.level === EscalationLevel.TIMEOUT ? 'error' : 'warning'} sx={{ mb: 2 }}>
                {escalationConfig.message}
              </Alert>

              {escalationDialog.operation && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Operation: <strong>{escalationDialog.operation.label}</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Elapsed: <strong>{Math.round((Date.now() - escalationDialog.operation.startTime) / 1000)}s</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expected: <strong>{escalationDialog.operation.timeConfig.label}</strong>
                  </Typography>
                </Box>
              )}
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
              <Button
                onClick={closeEscalationDialog}
                variant="outlined"
              >
                Keep Waiting
              </Button>
              {escalationDialog.operation?.onRetry && (
                <Button
                  onClick={() => retryOperation(escalationDialog.operationId)}
                  startIcon={<RetryIcon />}
                  variant="outlined"
                >
                  Retry
                </Button>
              )}
              <Button
                onClick={() => cancelOperation(escalationDialog.operationId)}
                startIcon={<CancelIcon />}
                variant="contained"
                sx={{ color: 'text.secondary' }}
              >
                Cancel
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </TimeExpectationContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useTimeExpectations() {
  const context = useContext(TimeExpectationContext)
  if (!context) {
    throw new Error('useTimeExpectations must be used within TimeExpectationProvider')
  }
  return context
}

/**
 * Hook to track a single operation with time expectations
 */
export function useTrackedOperation(operationType) {
  const { startTracking, completeTracking, getElapsedTime, getProgress } = useTimeExpectations()
  const operationIdRef = useRef(null)

  const start = useCallback((options = {}) => {
    const id = `op-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    operationIdRef.current = id
    return startTracking(id, operationType, options)
  }, [operationType, startTracking])

  const complete = useCallback((success = true) => {
    if (operationIdRef.current) {
      completeTracking(operationIdRef.current, success)
      operationIdRef.current = null
    }
  }, [completeTracking])

  const elapsed = operationIdRef.current ? getElapsedTime(operationIdRef.current) : 0
  const progress = operationIdRef.current ? getProgress(operationIdRef.current) : null

  return { start, complete, elapsed, progress, isActive: !!operationIdRef.current }
}

/**
 * Validate that an operation type has time expectations defined
 * THROWS in development if not defined
 */
export function validateTimeExpectation(operationType) {
  if (import.meta.env?.DEV) {
    if (!OperationTimeMap[operationType] && operationType !== 'default') {
      console.warn(
        `[TIME EXPECTATION] Operation type "${operationType}" has no defined time expectations. ` +
        `Using default. Add it to OperationTimeMap for accurate tracking.`
      )
    }
  }
  return OperationTimeMap[operationType] || OperationTimeMap.default
}
