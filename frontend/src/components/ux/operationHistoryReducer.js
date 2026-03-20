/**
 * Operation History Reducer and Constants
 * Pure state management for operation tracking
 */

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
export const ACTIONS = {
  ADD_OPERATION: 'ADD_OPERATION',
  UPDATE_OPERATION: 'UPDATE_OPERATION',
  COMPLETE_OPERATION: 'COMPLETE_OPERATION',
  FAIL_OPERATION: 'FAIL_OPERATION',
  UNDO_OPERATION: 'UNDO_OPERATION',
  CLEAR_COMPLETED: 'CLEAR_COMPLETED',
  CLEAR_ALL: 'CLEAR_ALL',
}

// Initial state
export const initialState = {
  operations: [],
  activeCount: 0,
}

// Generate unique operation ID
let operationIdCounter = 0
export const generateOperationId = () => `op_${Date.now()}_${++operationIdCounter}`

// Reducer
export default function operationReducer(state, action) {
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
