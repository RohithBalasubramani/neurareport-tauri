/**
 * Time Tracking Provider Hook
 *
 * Manages operation time tracking, escalation, and timeout detection.
 */
import { useCallback, useRef, useState, useEffect } from 'react'
import { OperationTimeMap, EscalationLevel } from '../timeConstants'

const MAX_TRACKED_OPERATIONS = 200

export function useTimeTracker() {
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

  // Interval refs for cleanup
  const checkIntervals = useRef(new Map())

  // Use ref to avoid TDZ issues with circular dependencies
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

  // Store in ref for use in timeouts
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
      if (operation.abortController) {
        operation.abortController.abort()
      }
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

  return {
    activeOperations,
    escalationDialog,
    startTracking,
    completeTracking,
    cancelOperation,
    retryOperation,
    getElapsedTime,
    getProgress,
    closeEscalationDialog,
  }
}
