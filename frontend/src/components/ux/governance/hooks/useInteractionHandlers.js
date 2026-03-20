/**
 * Specialized Interaction Hooks
 *
 * Pre-configured interaction handlers for common action types.
 */
import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInteraction } from '../InteractionAPI'
import { InteractionType, Reversibility } from '../interactionConstants'

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
