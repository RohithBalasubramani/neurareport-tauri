/**
 * Interaction API Constants
 *
 * Types, reversibility levels, and feedback requirements for the interaction system.
 */

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
// VALIDATION - Enforce contract compliance at runtime
// ============================================================================

const REQUIRED_FIELDS = ['type', 'label', 'reversibility', 'action']

export function validateContract(contract, callerInfo = '') {
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
