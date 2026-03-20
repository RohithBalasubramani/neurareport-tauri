/**
 * UX Governance: Unified Interaction API
 *
 * ALL user actions MUST flow through this API.
 * Enforces immediate feedback, state visibility, error prevention,
 * reversibility warnings, intent tracking, and navigation safety.
 */
import { createContext, useContext, useCallback, useMemo, useRef } from 'react'
import { useOperationHistory } from '../OperationHistoryProvider'
import { useToast } from '@/components/ToastProvider'
import { pushActiveIntent, popActiveIntent } from '@/utils/intentBridge'
import { reportFrontendError } from '@/api/frontendErrorLogger'
import { InteractionType, Reversibility, validateContract } from './interactionConstants'

// Re-export constants and specialized hooks for backwards compatibility
export { InteractionType, Reversibility, FeedbackType, FeedbackRequirement } from './interactionConstants'
export { useNavigateInteraction, useDeleteInteraction, useCreateInteraction, useGenerateInteraction, useExecuteInteraction } from './hooks/useInteractionHandlers'

const InteractionContext = createContext(null)

export function InteractionProvider({ children }) {
  const { startOperation, completeOperation, failOperation } = useOperationHistory()
  const { show: showToast, showWithUndo } = useToast()

  // Track pending confirmations
  const pendingConfirmations = useRef(new Map())

  // Track active interactions for navigation blocking
  const activeInteractions = useRef(new Set())

  /** Execute an interaction with full UX guarantees */
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

  /** Check if navigation is safe (no blocking interactions) */
  const isNavigationSafe = useCallback(() => {
    return activeInteractions.current.size === 0
  }, [])

  /** Get list of active interactions blocking navigation */
  const getBlockingInteractions = useCallback(() => {
    return Array.from(activeInteractions.current)
  }, [])

  /** Create a pre-configured interaction handler for a specific action */
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

/** Hook to access the interaction API */
export function useInteraction() {
  const context = useContext(InteractionContext)
  if (!context) {
    throw new Error(
      '[UX GOVERNANCE VIOLATION] useInteraction must be used within InteractionProvider'
    )
  }
  return context
}
