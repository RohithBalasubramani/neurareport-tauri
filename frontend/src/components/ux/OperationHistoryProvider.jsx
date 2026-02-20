/**
 * Operation History Provider
 * Tracks all user operations for visibility, undo, and recovery
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Make every action reversible where possible
 * - Never leave the user guessing
 */
import { createContext, useCallback, useContext, useMemo, useReducer, useEffect } from 'react'

// Operation states
export const OperationStatus = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  UNDONE: 'undone',
}

// Operation types for consistent terminology
export const OperationType = {
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',
  UPLOAD: 'upload',
  DOWNLOAD: 'download',
  GENERATE: 'generate',
  EXECUTE: 'execute',
  SEND: 'send',
}

// Action types
const ACTIONS = {
  ADD_OPERATION: 'ADD_OPERATION',
  UPDATE_OPERATION: 'UPDATE_OPERATION',
  COMPLETE_OPERATION: 'COMPLETE_OPERATION',
  FAIL_OPERATION: 'FAIL_OPERATION',
  UNDO_OPERATION: 'UNDO_OPERATION',
  CLEAR_COMPLETED: 'CLEAR_COMPLETED',
  CLEAR_ALL: 'CLEAR_ALL',
}

// Reducer
function operationReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADD_OPERATION:
      return {
        ...state,
        operations: [action.payload, ...state.operations].slice(0, 100), // Keep last 100
        activeCount: state.activeCount + 1,
      }

    case ACTIONS.UPDATE_OPERATION:
      return {
        ...state,
        operations: state.operations.map((op) =>
          op.id === action.payload.id ? { ...op, ...action.payload.updates } : op
        ),
      }

    case ACTIONS.COMPLETE_OPERATION:
      return {
        ...state,
        operations: state.operations.map((op) =>
          op.id === action.payload.id
            ? {
                ...op,
                status: OperationStatus.COMPLETED,
                completedAt: Date.now(),
                result: action.payload.result,
              }
            : op
        ),
        activeCount: Math.max(0, state.activeCount - 1),
      }

    case ACTIONS.FAIL_OPERATION:
      return {
        ...state,
        operations: state.operations.map((op) =>
          op.id === action.payload.id
            ? {
                ...op,
                status: OperationStatus.FAILED,
                completedAt: Date.now(),
                error: action.payload.error,
              }
            : op
        ),
        activeCount: Math.max(0, state.activeCount - 1),
      }

    case ACTIONS.UNDO_OPERATION:
      return {
        ...state,
        operations: state.operations.map((op) =>
          op.id === action.payload.id
            ? { ...op, status: OperationStatus.UNDONE, undoneAt: Date.now() }
            : op
        ),
      }

    case ACTIONS.CLEAR_COMPLETED:
      return {
        ...state,
        operations: state.operations.filter(
          (op) => op.status === OperationStatus.PENDING || op.status === OperationStatus.IN_PROGRESS
        ),
      }

    case ACTIONS.CLEAR_ALL:
      return { ...state, operations: [], activeCount: 0 }

    default:
      return state
  }
}

// Initial state
const initialState = {
  operations: [],
  activeCount: 0,
}

// Context
const OperationHistoryContext = createContext(null)

// Generate unique operation ID
let operationIdCounter = 0
const generateOperationId = () => `op_${Date.now()}_${++operationIdCounter}`

/**
 * Operation History Provider
 * Wraps app to provide operation tracking
 */
export function OperationHistoryProvider({ children }) {
  const [state, dispatch] = useReducer(operationReducer, initialState)

  // Start a new operation
  const startOperation = useCallback((config) => {
    const operation = {
      id: generateOperationId(),
      type: config.type || OperationType.UPDATE,
      label: config.label,
      description: config.description,
      status: OperationStatus.IN_PROGRESS,
      startedAt: Date.now(),
      completedAt: null,
      progress: 0,
      canUndo: config.canUndo || false,
      undoFn: config.undoFn || null,
      undoLabel: config.undoLabel || 'Undo',
      metadata: config.metadata || {},
    }

    dispatch({ type: ACTIONS.ADD_OPERATION, payload: operation })
    return operation.id
  }, [])

  // Update operation progress
  const updateProgress = useCallback((operationId, progress, description) => {
    dispatch({
      type: ACTIONS.UPDATE_OPERATION,
      payload: {
        id: operationId,
        updates: { progress, ...(description && { description }) },
      },
    })
  }, [])

  // Complete an operation successfully
  const completeOperation = useCallback((operationId, result) => {
    dispatch({
      type: ACTIONS.COMPLETE_OPERATION,
      payload: { id: operationId, result },
    })
  }, [])

  // Mark operation as failed
  const failOperation = useCallback((operationId, error) => {
    dispatch({
      type: ACTIONS.FAIL_OPERATION,
      payload: { id: operationId, error: typeof error === 'string' ? error : error?.message || 'Unknown error' },
    })
  }, [])

  // Undo an operation
  const undoOperation = useCallback(async (operationId) => {
    const operation = state.operations.find((op) => op.id === operationId)
    if (!operation || !operation.canUndo || !operation.undoFn) {
      return false
    }

    try {
      await operation.undoFn()
      dispatch({ type: ACTIONS.UNDO_OPERATION, payload: { id: operationId } })
      return true
    } catch (err) {
      console.error('Failed to undo operation:', err)
      return false
    }
  }, [state.operations])

  // Clear completed operations
  const clearCompleted = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_COMPLETED })
  }, [])

  // Clear all operations
  const clearAll = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_ALL })
  }, [])

  // Get recent operations (for display)
  const getRecentOperations = useCallback((limit = 10) => {
    return state.operations.slice(0, limit)
  }, [state.operations])

  // Get active operations
  const getActiveOperations = useCallback(() => {
    return state.operations.filter(
      (op) => op.status === OperationStatus.PENDING || op.status === OperationStatus.IN_PROGRESS
    )
  }, [state.operations])

  // Utility: wrap an async function with operation tracking
  const trackOperation = useCallback(async (config, asyncFn) => {
    const operationId = startOperation(config)

    try {
      const result = await asyncFn((progress, description) => {
        updateProgress(operationId, progress, description)
      })
      completeOperation(operationId, result)
      return { success: true, result, operationId }
    } catch (error) {
      failOperation(operationId, error)
      return { success: false, error, operationId }
    }
  }, [startOperation, updateProgress, completeOperation, failOperation])

  const contextValue = useMemo(() => ({
    operations: state.operations,
    activeCount: state.activeCount,
    hasActiveOperations: state.activeCount > 0,
    startOperation,
    updateProgress,
    completeOperation,
    failOperation,
    undoOperation,
    clearCompleted,
    clearAll,
    getRecentOperations,
    getActiveOperations,
    trackOperation,
  }), [
    state.operations,
    state.activeCount,
    startOperation,
    updateProgress,
    completeOperation,
    failOperation,
    undoOperation,
    clearCompleted,
    clearAll,
    getRecentOperations,
    getActiveOperations,
    trackOperation,
  ])

  return (
    <OperationHistoryContext.Provider value={contextValue}>
      {children}
    </OperationHistoryContext.Provider>
  )
}

/**
 * Hook to access operation history
 */
export function useOperationHistory() {
  const context = useContext(OperationHistoryContext)
  if (!context) {
    throw new Error('useOperationHistory must be used within OperationHistoryProvider')
  }
  return context
}

/**
 * Hook for simplified operation tracking
 * Returns a function to track async operations
 */
export function useTrackedOperation() {
  const { trackOperation } = useOperationHistory()
  return trackOperation
}
