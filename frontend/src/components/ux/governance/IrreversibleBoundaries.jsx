/**
 * UX Governance: Irreversible Action Boundaries
 *
 * EXPLICITLY defines which actions are irreversible and enforces:
 * - Confirmation before execution
 * - Clear communication of consequences
 * - Double-confirmation for high-severity actions
 * - Cool-down periods for destructive actions
 *
 * RULE: If an action cannot be undone, it MUST be declared here.
 */
import { createContext, useContext, useCallback } from 'react'
import { useIrreversibleProvider } from './hooks/useIrreversibleProvider'
import IrreversibleConfirmDialog from './IrreversibleConfirmDialog'

// Re-export constants for backwards compatibility
export { ActionSeverity, IrreversibleActions } from './irreversibleConstants'

// ============================================================================
// CONTEXT
// ============================================================================

const IrreversibleContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function IrreversibleBoundaryProvider({ children }) {
  const {
    contextValue,
    dialogState,
    typeConfirmation,
    setTypeConfirmation,
    checkboxConfirmed,
    setCheckboxConfirmed,
    cooldownRemaining,
    isConfirmationValid,
    executeAction,
    closeDialog,
  } = useIrreversibleProvider()

  return (
    <IrreversibleContext.Provider value={contextValue}>
      {children}

      <IrreversibleConfirmDialog
        open={dialogState.open}
        action={dialogState.action}
        itemName={dialogState.itemName}
        typeConfirmation={typeConfirmation}
        onTypeConfirmationChange={setTypeConfirmation}
        checkboxConfirmed={checkboxConfirmed}
        onCheckboxChange={setCheckboxConfirmed}
        cooldownRemaining={cooldownRemaining}
        isConfirmationValid={isConfirmationValid}
        onConfirm={executeAction}
        onCancel={closeDialog}
      />
    </IrreversibleContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useIrreversibleAction() {
  const context = useContext(IrreversibleContext)
  if (!context) {
    throw new Error('useIrreversibleAction must be used within IrreversibleBoundaryProvider')
  }
  return context
}

/**
 * Hook to execute an irreversible action with confirmation
 */
export function useConfirmedAction(actionId) {
  const { requestConfirmation } = useIrreversibleAction()

  return useCallback((itemName, executeAction) => {
    requestConfirmation(actionId, itemName, executeAction)
  }, [actionId, requestConfirmation])
}
