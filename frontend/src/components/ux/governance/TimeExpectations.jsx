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
import { createContext, useContext, useCallback, useRef } from 'react'
import { useTimeTracker } from './hooks/useTimeTracker'
import EscalationDialog from './EscalationDialog'

// Re-export constants for backwards compatibility
export { TimeExpectations, OperationTimeMap, EscalationLevel, validateTimeExpectation } from './timeConstants'

// ============================================================================
// CONTEXT
// ============================================================================

const TimeExpectationContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function TimeExpectationProvider({ children }) {
  const {
    activeOperations,
    escalationDialog,
    startTracking,
    completeTracking,
    cancelOperation,
    retryOperation,
    getElapsedTime,
    getProgress,
    closeEscalationDialog,
  } = useTimeTracker()

  const contextValue = {
    startTracking,
    completeTracking,
    cancelOperation,
    retryOperation,
    getElapsedTime,
    getProgress,
    activeOperations,
    // Re-export for convenience (imported from timeConstants by consumers)
  }

  return (
    <TimeExpectationContext.Provider value={contextValue}>
      {children}

      <EscalationDialog
        open={escalationDialog.open}
        level={escalationDialog.level}
        operation={escalationDialog.operation}
        operationId={escalationDialog.operationId}
        onClose={closeEscalationDialog}
        onRetry={retryOperation}
        onCancel={cancelOperation}
      />
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
