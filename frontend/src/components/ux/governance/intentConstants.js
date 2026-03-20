/**
 * Intent System Constants and Factory
 *
 * Shared types, statuses, and intent creation utilities.
 */

// ============================================================================
// INTENT STATUS
// ============================================================================

export const IntentStatus = {
  PENDING: 'pending',
  EXECUTING: 'executing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
}

// ============================================================================
// INTENT FACTORY
// ============================================================================

let intentCounter = 0
let sessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export { sessionId }

export function createIntent(config) {
  const id = `intent_${Date.now()}_${++intentCounter}`

  return {
    id,
    type: config.type,
    label: config.label,
    correlationId: config.correlationId || id,
    sessionId,
    timestamp: new Date().toISOString(),
    status: IntentStatus.PENDING,
    metadata: config.metadata || {},
    parentIntentId: config.parentIntentId || null,
    childIntentIds: [],
    // UX-specific fields
    reversibility: config.reversibility,
    requiresConfirmation: config.requiresConfirmation || false,
    blocksNavigation: config.blocksNavigation || false,
  }
}

// ============================================================================
// INTENT HEADERS - Add to API requests
// ============================================================================

/**
 * Create headers with intent context for API requests
 */
export function createIntentHeaders(intent) {
  return {
    'X-Intent-Id': intent.id,
    'X-Correlation-Id': intent.correlationId,
    'X-Session-Id': intent.sessionId,
    'X-Intent-Type': intent.type,
    'X-Intent-Label': encodeURIComponent(intent.label),
  }
}

/**
 * Axios interceptor to add intent headers
 */
export function createIntentInterceptor(getActiveIntent) {
  return (config) => {
    const intent = getActiveIntent?.()
    if (intent) {
      config.headers = {
        ...config.headers,
        ...createIntentHeaders(intent),
      }
    }
    return config
  }
}
