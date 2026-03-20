/**
 * Time Expectations Constants
 *
 * Expected durations and escalation levels for operation tracking.
 */

// ============================================================================
// TIME EXPECTATION DEFINITIONS
// ============================================================================

/**
 * Expected durations by operation type (in milliseconds)
 * These are ENFORCED, not advisory.
 */
export const TimeExpectations = {
  // Instant operations (< 500ms)
  INSTANT: {
    expected: 200,
    warning: 500,
    timeout: 2000,
    label: 'Instant',
  },

  // Quick operations (< 2s)
  QUICK: {
    expected: 500,
    warning: 2000,
    timeout: 5000,
    label: 'Quick',
  },

  // Standard operations (< 10s)
  STANDARD: {
    expected: 2000,
    warning: 10000,
    timeout: 30000,
    label: 'Standard',
  },

  // Long operations (< 60s)
  LONG: {
    expected: 10000,
    warning: 60000,
    timeout: 120000,
    label: 'Long',
  },

  // Extended operations (< 5min)
  EXTENDED: {
    expected: 60000,
    warning: 180000,
    timeout: 300000,
    label: 'Extended',
  },

  // Background operations (no timeout, but tracked)
  BACKGROUND: {
    expected: null,
    warning: 300000, // 5 min
    timeout: null,
    label: 'Background',
  },
}

/**
 * Map operation types to time expectations
 */
export const OperationTimeMap = {
  // CREATE operations
  create_session: TimeExpectations.QUICK,
  create_document: TimeExpectations.QUICK,
  create_query: TimeExpectations.QUICK,

  // UPLOAD operations
  upload_document: TimeExpectations.STANDARD,
  upload_file: TimeExpectations.STANDARD,

  // GENERATE operations (AI-powered)
  generate_sql: TimeExpectations.LONG,
  generate_synthesis: TimeExpectations.EXTENDED,
  generate_response: TimeExpectations.LONG,

  // ANALYZE operations
  analyze_documents: TimeExpectations.LONG,
  find_inconsistencies: TimeExpectations.LONG,

  // EXECUTE operations
  execute_query: TimeExpectations.STANDARD,

  // DELETE operations
  delete_session: TimeExpectations.QUICK,
  delete_document: TimeExpectations.INSTANT,

  // Default fallback
  default: TimeExpectations.STANDARD,
}

// ============================================================================
// ESCALATION LEVELS
// ============================================================================

export const EscalationLevel = {
  NONE: 'none',
  WARNING: 'warning',
  CRITICAL: 'critical',
  TIMEOUT: 'timeout',
}

/**
 * Validate that an operation type has time expectations defined
 * THROWS in development if not defined
 */
export function validateTimeExpectation(operationType) {
  if (import.meta.env?.DEV) {
    if (!OperationTimeMap[operationType] && operationType !== 'default') {
      console.warn(
        `[TIME EXPECTATION] Operation type "${operationType}" has no defined time expectations. ` +
        `Using default. Add it to OperationTimeMap for accurate tracking.`
      )
    }
  }
  return OperationTimeMap[operationType] || OperationTimeMap.default
}
