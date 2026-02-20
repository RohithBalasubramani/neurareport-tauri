/**
 * UX Governance: Unified Interaction API
 *
 * ALL user actions MUST flow through this API.
 * Direct event handlers that bypass this system are NON-COMPLIANT.
 *
 * This API enforces:
 * - Immediate feedback (100ms)
 * - State visibility
 * - Error prevention
 * - Reversibility or explicit warnings
 * - Intent tracking
 * - Navigation safety
 */
import { createContext, useContext, useCallback, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useOperationHistory, OperationType, OperationStatus } from '../OperationHistoryProvider'
import { useToast } from '@/components/ToastProvider'
import { pushActiveIntent, popActiveIntent } from '@/utils/intentBridge'
import { reportFrontendError } from '@/api/frontendErrorLogger'

// ============================================================================
// INTERACTION TYPES - Every action must have a defined type
// ============================================================================

export const InteractionType = {
  // Data mutations
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',

  // Content operations
  UPLOAD: 'upload',
  DOWNLOAD: 'download',

  // AI/Processing operations
  GENERATE: 'generate',
  ANALYZE: 'analyze',
  EXECUTE: 'execute',

  // Navigation
  NAVIGATE: 'navigate',

  // Session operations
  LOGIN: 'login',
  LOGOUT: 'logout',
}

// ============================================================================
// REVERSIBILITY LEVELS - Every action must declare its reversibility
// ============================================================================

export const Reversibility = {
  // Can be undone with no data loss
  FULLY_REVERSIBLE: 'fully_reversible',

  // Can be undone but may lose some data
  PARTIALLY_REVERSIBLE: 'partially_reversible',

  // Cannot be undone - REQUIRES explicit confirmation
  IRREVERSIBLE: 'irreversible',

  // System will handle (e.g., soft delete)
  SYSTEM_MANAGED: 'system_managed',
}

// ============================================================================
// FEEDBACK REQUIREMENTS - What feedback must be shown
// ============================================================================

export const FeedbackRequirement = {
  // Must show immediate visual feedback
  IMMEDIATE: 'immediate',

  // Must show progress indicator
  PROGRESS: 'progress',

  // Must show completion confirmation
  COMPLETION: 'completion',

  // Must show error with recovery path
  ERROR_RECOVERY: 'error_recovery',
}

export const FeedbackType = FeedbackRequirement

// ============================================================================
// INTERACTION CONTRACT - The required shape of every interaction
// ============================================================================

/**
 * @typedef {Object} InteractionContract
 * @property {string} type - InteractionType value
 * @property {string} label - Human-readable action name
 * @property {string} reversibility - Reversibility level
 * @property {Function} action - The async action to perform
 * @property {Function} [onSuccess] - Success callback
 * @property {Function} [onError] - Error callback
 * @property {Function} [undoAction] - Function to undo (if reversible)
 * @property {Object} [intent] - Intent metadata for audit trail
 * @property {boolean} [requiresConfirmation] - Force confirmation dialog
 * @property {string} [confirmationMessage] - Custom confirmation message
 * @property {Array<string>} [feedbackRequirements] - Required feedback types
 * @property {boolean} [blocksNavigation] - Whether this blocks page navigation
 * @property {boolean} [suppressSuccessToast] - Skip default success toast
 * @property {boolean} [suppressErrorToast] - Skip default error toast
 */

// ============================================================================
// VALIDATION - Enforce contract compliance at runtime
// ============================================================================

const REQUIRED_FIELDS = ['type', 'label', 'reversibility', 'action']

function validateContract(contract, callerInfo = '') {
  const missing = REQUIRED_FIELDS.filter((field) => !contract[field])

  if (missing.length > 0) {
    const error = new Error(
      `[UX GOVERNANCE VIOLATION] ${callerInfo}\n` +
      `Missing required fields: ${missing.join(', ')}\n` +
      `All interactions MUST define: ${REQUIRED_FIELDS.join(', ')}`
    )
    console.error(error)

    // In development, throw to force fix
    if (import.meta.env?.DEV) {
      throw error
    }

    return false
  }

  // Validate reversibility
  if (!Object.values(Reversibility).includes(contract.reversibility)) {
    console.error(
      `[UX GOVERNANCE VIOLATION] Invalid reversibility: ${contract.reversibility}\n` +
      `Must be one of: ${Object.values(Reversibility).join(', ')}`
    )
    return false
  }

  // Irreversible actions MUST require confirmation
  if (contract.reversibility === Reversibility.IRREVERSIBLE && !contract.requiresConfirmation) {
    console.warn(
      `[UX GOVERNANCE WARNING] Irreversible action "${contract.label}" should require confirmation`
    )
  }

  return true
}

// ============================================================================
// CONTEXT
// ============================================================================

const InteractionContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function InteractionProvider({ children }) {
  const { startOperation, completeOperation, failOperation } = useOperationHistory()
  const { show: showToast, showWithUndo } = useToast()

  // Track pending confirmations
  const pendingConfirmations = useRef(new Map())

  // Track active interactions for navigation blocking
  const activeInteractions = useRef(new Set())

  /**
   * Execute an interaction with full UX guarantees
   * @param {InteractionContract} contract
   * @returns {Promise<{success: boolean, result?: any, error?: Error}>}
   */
  const execute = useCallback(async (contract) => {
    // STEP 1: Validate contract
    const callerStack = new Error().stack?.split('\n')[2] || 'unknown'
    if (!validateContract(contract, callerStack)) {
      return { success: false, error: new Error('Invalid interaction contract') }
    }

    // STEP 2: Generate interaction ID
    const interactionId = `int_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

    // STEP 3: Build intent metadata
    const intent = {
      id: interactionId,
      type: contract.type,
      label: contract.label,
      reversibility: contract.reversibility,
      timestamp: new Date().toISOString(),
      userAgent: (navigator.userAgent || '').slice(0, 512),
      ...contract.intent,
    }

    // STEP 4: Start operation tracking (IMMEDIATE FEEDBACK - within 100ms)
    const operationId = startOperation({
      type: contract.type,
      label: contract.label,
      canUndo: contract.reversibility === Reversibility.FULLY_REVERSIBLE && !!contract.undoAction,
      undoFn: contract.undoAction,
      metadata: intent,
    })

    // STEP 5: Track as active (for navigation blocking)
    if (contract.blocksNavigation !== false) {
      activeInteractions.current.add(interactionId)
    }

    try {
    // STEP 6: Execute the action
      pushActiveIntent(intent)
      const result = await contract.action(intent)

      // STEP 7: Complete operation
      completeOperation(operationId, result)

      // STEP 8: Show success feedback
      if (contract.onSuccess) {
        contract.onSuccess(result)
      }

      if (!contract.suppressSuccessToast) {
        // STEP 9: Show undo option if applicable
        if (contract.reversibility === Reversibility.FULLY_REVERSIBLE && contract.undoAction) {
          showWithUndo(
            `${contract.label} completed`,
            async () => {
              await contract.undoAction(result)
              showToast(`${contract.label} undone`, 'info')
            },
            { severity: 'success', duration: 5000 }
          )
        } else {
          showToast(`${contract.label} completed`, 'success')
        }
      }

      return { success: true, result, interactionId }
    } catch (error) {
      // STEP 10: Fail operation
      failOperation(operationId, error)

      // STEP 11: Show error with recovery path
      const userMessage = error.userMessage || error.message || 'An error occurred'
      reportFrontendError({
        source: 'interaction.execute',
        message: userMessage,
        stack: error?.stack,
        route: typeof window !== 'undefined' ? window.location.pathname : undefined,
        action: contract.label,
        context: {
          interactionType: contract.type,
          reversibility: contract.reversibility,
          interactionId,
        },
      })
      if (!contract.suppressErrorToast) {
        showToast(userMessage, 'error')
      }

      if (contract.onError) {
        contract.onError(error)
      }

      return { success: false, error, interactionId }
    } finally {
      // STEP 12: Remove from active interactions
      activeInteractions.current.delete(interactionId)
      popActiveIntent(intent.id)
    }
  }, [startOperation, completeOperation, failOperation, showToast, showWithUndo])

  /**
   * Check if navigation is safe (no blocking interactions)
   */
  const isNavigationSafe = useCallback(() => {
    return activeInteractions.current.size === 0
  }, [])

  /**
   * Get list of active interactions blocking navigation
   */
  const getBlockingInteractions = useCallback(() => {
    return Array.from(activeInteractions.current)
  }, [])

  /**
   * Create a pre-configured interaction handler for a specific action
   * This is the preferred way to create interaction handlers
   */
  const createHandler = useCallback((baseContract) => {
    return async (overrides = {}) => {
      const mergedContract = { ...baseContract, ...overrides }
      return execute(mergedContract)
    }
  }, [execute])

  const contextValue = useMemo(() => ({
    execute,
    isNavigationSafe,
    getBlockingInteractions,
    createHandler,
    InteractionType,
    Reversibility,
  }), [execute, isNavigationSafe, getBlockingInteractions, createHandler])

  return (
    <InteractionContext.Provider value={contextValue}>
      {children}
    </InteractionContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

/**
 * Hook to access the interaction API
 * @returns {Object} Interaction API
 */
export function useInteraction() {
  const context = useContext(InteractionContext)
  if (!context) {
    throw new Error(
      '[UX GOVERNANCE VIOLATION] useInteraction must be used within InteractionProvider'
    )
  }
  return context
}

/**
 * Hook to create a NAVIGATE interaction handler
 */
export function useNavigateInteraction() {
  const navigate = useNavigate()
  const { execute } = useInteraction()

  return useCallback((to, options = {}) => {
    const {
      label = 'Navigate',
      intent = {},
      navigateOptions,
      blocksNavigation = false,
    } = options

    return execute({
      type: InteractionType.NAVIGATE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { to, ...intent },
      action: () => navigate(to, navigateOptions),
    })
  }, [execute, navigate])
}

/**
 * Hook to create a DELETE interaction handler
 */
export function useDeleteInteraction(config) {
  const { execute } = useInteraction()

  return useCallback(async (itemId, itemLabel) => {
    return execute({
      type: InteractionType.DELETE,
      label: config.label || `Delete ${itemLabel}`,
      reversibility: config.softDelete ? Reversibility.SYSTEM_MANAGED : Reversibility.IRREVERSIBLE,
      requiresConfirmation: true,
      confirmationMessage: config.confirmationMessage || `Are you sure you want to delete "${itemLabel}"?`,
      action: () => config.deleteAction(itemId),
      undoAction: config.restoreAction ? () => config.restoreAction(itemId) : undefined,
      intent: { itemId, itemLabel, ...config.intent },
    })
  }, [execute, config])
}

/**
 * Hook to create a CREATE interaction handler
 */
export function useCreateInteraction(config) {
  const { execute } = useInteraction()

  return useCallback(async (data) => {
    return execute({
      type: InteractionType.CREATE,
      label: config.label || 'Create item',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      action: () => config.createAction(data),
      undoAction: config.deleteAction ? (result) => config.deleteAction(result.id) : undefined,
      intent: { data, ...config.intent },
    })
  }, [execute, config])
}

/**
 * Hook to create a GENERATE interaction handler (for AI operations)
 */
export function useGenerateInteraction(config) {
  const { execute } = useInteraction()

  return useCallback(async (input) => {
    return execute({
      type: InteractionType.GENERATE,
      label: config.label || 'Generate',
      reversibility: Reversibility.FULLY_REVERSIBLE, // Can regenerate
      blocksNavigation: true,
      action: () => config.generateAction(input),
      intent: { input, ...config.intent },
    })
  }, [execute, config])
}

/**
 * Hook to create an EXECUTE interaction handler (for query execution)
 */
export function useExecuteInteraction(config) {
  const { execute } = useInteraction()

  return useCallback(async (query) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: config.label || 'Execute',
      reversibility: config.isReadOnly ? Reversibility.FULLY_REVERSIBLE : Reversibility.IRREVERSIBLE,
      requiresConfirmation: !config.isReadOnly,
      blocksNavigation: true,
      action: () => config.executeAction(query),
      intent: { query, isReadOnly: config.isReadOnly, ...config.intent },
    })
  }, [execute, config])
}
