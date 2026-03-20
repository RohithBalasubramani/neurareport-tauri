/**
 * Irreversible Action Constants and Registry
 */
import { keyframes } from '@mui/material'

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

export const shake = keyframes`
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
`

// ============================================================================
// SEVERITY CONFIG HELPER
// ============================================================================

export function getSeverityConfig(severity, theme) {
  const configs = {
    [ActionSeverity.LOW]: {
      color: theme.palette.text.secondary,
      label: 'Low Impact',
    },
    [ActionSeverity.MEDIUM]: {
      color: theme.palette.text.secondary,
      label: 'Medium Impact',
    },
    [ActionSeverity.HIGH]: {
      color: theme.palette.text.secondary,
      label: 'High Impact',
    },
    [ActionSeverity.CRITICAL]: {
      color: theme.palette.text.secondary,
      label: 'CRITICAL - Cannot Be Undone',
    },
  }
  return configs[severity] || configs[ActionSeverity.MEDIUM]
}
