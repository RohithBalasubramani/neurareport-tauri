/**
 * Irreversible Boundary Provider Hook
 *
 * Manages dialog state, type confirmation, checkbox, and cooldown for
 * irreversible action confirmations.
 */
import { useCallback, useEffect, useMemo, useState, useRef } from 'react'
import { IrreversibleActions, ActionSeverity } from '../irreversibleConstants'

export function useIrreversibleProvider() {
  // Dialog state
  const [dialogState, setDialogState] = useState({
    open: false,
    action: null,
    itemName: '',
    onConfirm: null,
  })

  // Type confirmation input
  const [typeConfirmation, setTypeConfirmation] = useState('')
  const [checkboxConfirmed, setCheckboxConfirmed] = useState(false)

  // Cooldown state
  const [cooldownRemaining, setCooldownRemaining] = useState(0)
  const cooldownInterval = useRef(null)

  /**
   * Request confirmation for an irreversible action
   */
  const requestConfirmation = useCallback((actionId, itemName, onConfirm) => {
    const action = IrreversibleActions[actionId]
    if (!action) {
      console.error(`Unknown irreversible action: ${actionId}`)
      return
    }

    setDialogState({
      open: true,
      action,
      itemName,
      onConfirm,
    })

    // Start cooldown if required
    if (action.cooldownMs > 0) {
      if (cooldownInterval.current) {
        clearInterval(cooldownInterval.current)
      }
      const seconds = Math.ceil(action.cooldownMs / 1000)
      setCooldownRemaining(seconds)
      cooldownInterval.current = setInterval(() => {
        setCooldownRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(cooldownInterval.current)
            cooldownInterval.current = null
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
  }, [])

  /**
   * Close dialog and reset state
   */
  const closeDialog = useCallback(() => {
    setDialogState({ open: false, action: null, itemName: '', onConfirm: null })
    setTypeConfirmation('')
    setCheckboxConfirmed(false)
    setCooldownRemaining(0)
    if (cooldownInterval.current) {
      clearInterval(cooldownInterval.current)
    }
  }, [])

  /**
   * Execute the confirmed action
   */
  const executeAction = useCallback(() => {
    if (dialogState.onConfirm) {
      dialogState.onConfirm()
    }
    closeDialog()
  }, [dialogState, closeDialog])

  // Clean up cooldown interval on unmount
  useEffect(() => {
    return () => {
      if (cooldownInterval.current) {
        clearInterval(cooldownInterval.current)
      }
    }
  }, [])

  // Compute if confirmation is valid
  const isConfirmationValid = useMemo(() => {
    if (!dialogState.action) return false

    // Check cooldown
    if (cooldownRemaining > 0) return false

    // Check type confirmation if required
    if (dialogState.action.requiresTypeConfirmation) {
      if (typeConfirmation !== dialogState.action.confirmationPhrase) {
        return false
      }
    }

    // For high/critical severity, require checkbox
    if ([ActionSeverity.HIGH, ActionSeverity.CRITICAL].includes(dialogState.action.severity)) {
      if (!checkboxConfirmed) return false
    }

    return true
  }, [dialogState.action, cooldownRemaining, typeConfirmation, checkboxConfirmed])

  const contextValue = useMemo(() => ({
    requestConfirmation,
    IrreversibleActions,
    ActionSeverity,
  }), [requestConfirmation])

  return {
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
  }
}
