/**
 * Background Operations Provider Hook
 *
 * Manages registration, status updates, and lifecycle of background operations.
 */
import { useCallback, useState, useRef } from 'react'
import { BackgroundOperationStatus } from '../backgroundConstants'

export function useBackgroundOps() {
  // Registered background operations
  const [operations, setOperations] = useState([])
  const operationsRef = useRef(operations)
  operationsRef.current = operations

  // Notification queue
  const [notification, setNotification] = useState(null)

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false)

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

          setNotification({
            severity: 'success',
            message: `Completed: ${op.label}`,
          })

          if (op.onComplete) {
            op.onComplete(updated)
          }
        }

        // Handle failure
        if (updates.status === BackgroundOperationStatus.FAILED) {
          updated.completedAt = Date.now()

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

  // Close notification
  const closeNotification = useCallback(() => {
    setNotification(null)
  }, [])

  return {
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
  }
}
