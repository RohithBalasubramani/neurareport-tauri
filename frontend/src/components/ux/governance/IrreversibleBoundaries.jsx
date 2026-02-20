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
import { createContext, useContext, useCallback, useEffect, useMemo, useState, useRef } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Alert,
  Checkbox,
  FormControlLabel,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import {
  Warning as WarningIcon,
  Error as DangerIcon,
  DeleteForever as DeleteIcon,
} from '@mui/icons-material'

// ============================================================================
// SEVERITY LEVELS
// ============================================================================

export const ActionSeverity = {
  // Low: Data can be recovered from backup
  LOW: 'low',

  // Medium: Data is soft-deleted (30-day recovery)
  MEDIUM: 'medium',

  // High: Data is permanently deleted
  HIGH: 'high',

  // Critical: Affects multiple users or system configuration
  CRITICAL: 'critical',
}

// ============================================================================
// IRREVERSIBLE ACTIONS REGISTRY
// ============================================================================

/**
 * Registry of all irreversible actions in the application.
 * Add new irreversible actions here to enforce confirmation.
 */
export const IrreversibleActions = {
  // Session/Document actions
  DELETE_SESSION: {
    id: 'delete_session',
    label: 'Delete Session',
    severity: ActionSeverity.HIGH,
    consequences: [
      'All documents in this session will be permanently deleted',
      'All chat history will be lost',
      'This action cannot be undone',
    ],
    requiresTypeConfirmation: false,
    cooldownMs: 0,
  },

  DELETE_DOCUMENT: {
    id: 'delete_document',
    label: 'Delete Document',
    severity: ActionSeverity.MEDIUM,
    consequences: [
      'Document will be removed from this session',
      'References in chat history may become invalid',
    ],
    requiresTypeConfirmation: false,
    cooldownMs: 0,
  },

  // Query actions
  DELETE_SAVED_QUERY: {
    id: 'delete_saved_query',
    label: 'Delete Saved Query',
    severity: ActionSeverity.LOW,
    consequences: [
      'Saved query will be permanently deleted',
      'You can recreate it by running the same question again',
    ],
    requiresTypeConfirmation: false,
    cooldownMs: 0,
  },

  EXECUTE_WRITE_QUERY: {
    id: 'execute_write_query',
    label: 'Execute Write Query',
    severity: ActionSeverity.CRITICAL,
    consequences: [
      'This query will modify data in the database',
      'Changes may affect multiple records',
      'This action cannot be automatically undone',
    ],
    requiresTypeConfirmation: true,
    confirmationPhrase: 'EXECUTE',
    cooldownMs: 3000,
  },

  // Connection actions
  DELETE_CONNECTION: {
    id: 'delete_connection',
    label: 'Delete Connection',
    severity: ActionSeverity.HIGH,
    consequences: [
      'Connection settings will be permanently removed',
      'Saved queries using this connection may stop working',
      'Scheduled reports using this connection will fail',
    ],
    requiresTypeConfirmation: true,
    confirmationPhrase: 'DELETE',
    cooldownMs: 2000,
  },

  // Template actions
  DELETE_TEMPLATE: {
    id: 'delete_template',
    label: 'Delete Template',
    severity: ActionSeverity.HIGH,
    consequences: [
      'Template will be permanently deleted',
      'Scheduled reports using this template will fail',
      'Historical reports will remain but cannot be regenerated',
    ],
    requiresTypeConfirmation: false,
    cooldownMs: 1000,
  },

  // Schedule actions
  DELETE_SCHEDULE: {
    id: 'delete_schedule',
    label: 'Delete Schedule',
    severity: ActionSeverity.MEDIUM,
    consequences: [
      'Scheduled report will stop running',
      'Historical runs will be preserved',
    ],
    requiresTypeConfirmation: false,
    cooldownMs: 0,
  },

  // Account actions
  CLEAR_ALL_DATA: {
    id: 'clear_all_data',
    label: 'Clear All Data',
    severity: ActionSeverity.CRITICAL,
    consequences: [
      'ALL sessions, documents, queries, and templates will be deleted',
      'ALL scheduled reports will be cancelled',
      'This action is PERMANENT and cannot be undone',
    ],
    requiresTypeConfirmation: true,
    confirmationPhrase: 'DELETE ALL DATA',
    cooldownMs: 5000,
  },
}

// ============================================================================
// ANIMATIONS
// ============================================================================

const shake = keyframes`
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
`

// ============================================================================
// CONTEXT
// ============================================================================

const IrreversibleContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function IrreversibleBoundaryProvider({ children }) {
  const theme = useTheme()

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
   * @param {string} actionId - ID from IrreversibleActions
   * @param {string} itemName - Name of item being affected
   * @param {Function} onConfirm - Callback when confirmed
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
      // Clear any existing interval before starting a new one
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

  // Get severity config
  const getSeverityConfig = (severity) => {
    const configs = {
      [ActionSeverity.LOW]: {
        color: theme.palette.text.secondary,
        icon: WarningIcon,
        label: 'Low Impact',
      },
      [ActionSeverity.MEDIUM]: {
        color: theme.palette.text.secondary,
        icon: WarningIcon,
        label: 'Medium Impact',
      },
      [ActionSeverity.HIGH]: {
        color: theme.palette.text.secondary,
        icon: DangerIcon,
        label: 'High Impact',
      },
      [ActionSeverity.CRITICAL]: {
        color: theme.palette.text.secondary,
        icon: DeleteIcon,
        label: 'CRITICAL - Cannot Be Undone',
      },
    }
    return configs[severity] || configs[ActionSeverity.MEDIUM]
  }

  const contextValue = useMemo(() => ({
    requestConfirmation,
    IrreversibleActions,
    ActionSeverity,
  }), [requestConfirmation])

  const severityConfig = dialogState.action ? getSeverityConfig(dialogState.action.severity) : null
  const SeverityIcon = severityConfig?.icon

  return (
    <IrreversibleContext.Provider value={contextValue}>
      {children}

      {/* Irreversible Action Confirmation Dialog */}
      <Dialog
        open={dialogState.open}
        onClose={closeDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: alpha(theme.palette.background.paper, 0.98),
            borderRadius: 1,  // Figma spec: 8px
            border: `2px solid ${severityConfig?.color || theme.palette.divider}`,
          },
        }}
      >
        {dialogState.action && (
          <>
            <DialogTitle
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                bgcolor: alpha(severityConfig.color, 0.1),
                borderBottom: `1px solid ${alpha(severityConfig.color, 0.2)}`,
              }}
            >
              <SeverityIcon sx={{ color: severityConfig.color, fontSize: 28 }} />
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  {dialogState.action.label}
                </Typography>
                <Typography variant="caption" sx={{ color: severityConfig.color, fontWeight: 600 }}>
                  {severityConfig.label}
                </Typography>
              </Box>
            </DialogTitle>

            <DialogContent sx={{ pt: 3 }}>
              {dialogState.itemName && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  You are about to {dialogState.action.label.toLowerCase()} <strong>"{dialogState.itemName}"</strong>
                </Alert>
              )}

              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                This action will:
              </Typography>
              <Box component="ul" sx={{ mt: 1, pl: 2 }}>
                {dialogState.action.consequences.map((consequence, idx) => (
                  <Typography component="li" variant="body2" key={idx} sx={{ mb: 0.5 }}>
                    {consequence}
                  </Typography>
                ))}
              </Box>

              {/* Type confirmation for critical actions */}
              {dialogState.action.requiresTypeConfirmation && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Type <strong>{dialogState.action.confirmationPhrase}</strong> to confirm:
                  </Typography>
                  <TextField
                    fullWidth
                    value={typeConfirmation}
                    onChange={(e) => setTypeConfirmation(e.target.value)}
                    placeholder={dialogState.action.confirmationPhrase}
                    error={typeConfirmation.length > 0 && typeConfirmation !== dialogState.action.confirmationPhrase}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        animation: typeConfirmation.length > 0 && typeConfirmation !== dialogState.action.confirmationPhrase
                          ? `${shake} 0.4s ease-in-out`
                          : 'none',
                      },
                    }}
                  />
                </Box>
              )}

              {/* Checkbox for high/critical severity */}
              {[ActionSeverity.HIGH, ActionSeverity.CRITICAL].includes(dialogState.action.severity) && (
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={checkboxConfirmed}
                      onChange={(e) => setCheckboxConfirmed(e.target.checked)}
                      sx={{ color: severityConfig.color }}
                    />
                  }
                  label={
                    <Typography variant="body2">
                      I understand this action is <strong>permanent</strong> and cannot be undone
                    </Typography>
                  }
                  sx={{ mt: 2 }}
                />
              )}
            </DialogContent>

            <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
              <Button onClick={closeDialog} variant="outlined">
                Cancel
              </Button>
              <Button
                onClick={executeAction}
                variant="contained"
                disabled={!isConfirmationValid}
                sx={{ minWidth: 120, color: 'text.secondary' }}
              >
                {cooldownRemaining > 0 ? (
                  `Wait ${cooldownRemaining}s`
                ) : (
                  dialogState.action.label
                )}
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
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
