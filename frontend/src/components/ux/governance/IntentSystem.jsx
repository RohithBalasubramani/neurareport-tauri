/**
 * UX Governance: Intent Tracking System
 *
 * Every user action generates an intent that flows:
 * UI → Interaction API → Backend → Audit Log
 *
 * This provides:
 * - Complete audit trail
 * - Action correlation
 * - Error diagnosis
 * - User behavior analytics
 */
import { createContext, useContext, useCallback, useMemo, useRef, useState } from 'react'

// ============================================================================
// INTENT STRUCTURE
// ============================================================================

/**
 * @typedef {Object} Intent
 * @property {string} id - Unique intent ID
 * @property {string} type - Action type (create, delete, etc.)
 * @property {string} label - Human-readable description
 * @property {string} correlationId - Links related intents
 * @property {string} sessionId - User session ID
 * @property {string} timestamp - ISO timestamp
 * @property {string} status - pending | executing | completed | failed | cancelled
 * @property {Object} metadata - Additional context
 * @property {string} [parentIntentId] - For nested/chained actions
 * @property {Array<string>} [childIntentIds] - Sub-actions spawned
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
// CONTEXT
// ============================================================================

const IntentContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function IntentProvider({ children, onIntentChange, maxHistory = 100, auditClient }) {
  const [intents, setIntents] = useState([])
  const intentMap = useRef(new Map())

  /**
   * Record a new intent
   */
  const recordIntent = useCallback((config) => {
    const intent = createIntent(config)

    intentMap.current.set(intent.id, intent)
    // Evict oldest entries when Map exceeds history cap
    if (intentMap.current.size > maxHistory) {
      const oldest = intentMap.current.keys().next().value
      intentMap.current.delete(oldest)
    }

    setIntents((prev) => {
      const updated = [intent, ...prev].slice(0, maxHistory)
      onIntentChange?.(updated)
      return updated
    })

    // Send to backend for audit (async, non-blocking)
    if (auditClient?.recordIntent) {
      auditClient.recordIntent(intent).catch((err) => {
        console.warn('Failed to record intent to backend:', err)
      })
    }

    return intent
  }, [maxHistory, onIntentChange, auditClient])

  /**
   * Update intent status
   */
  const updateIntentStatus = useCallback((intentId, status, result = null) => {
    const intent = intentMap.current.get(intentId)
    if (!intent) {
      console.warn(`Intent not found: ${intentId}`)
      return
    }

    const updatedIntent = {
      ...intent,
      status,
      completedAt: [IntentStatus.COMPLETED, IntentStatus.FAILED, IntentStatus.CANCELLED].includes(status)
        ? new Date().toISOString()
        : null,
      result: status === IntentStatus.COMPLETED ? result : null,
      error: status === IntentStatus.FAILED ? result : null,
    }

    intentMap.current.set(intentId, updatedIntent)

    setIntents((prev) => {
      const updated = prev.map((i) => (i.id === intentId ? updatedIntent : i))
      onIntentChange?.(updated)
      return updated
    })

    // Send update to backend
    if (auditClient?.updateIntent) {
      auditClient.updateIntent(updatedIntent, status, result).catch((err) => {
        console.warn('Failed to update intent on backend:', err)
      })
    }
  }, [onIntentChange, auditClient])

  /**
   * Link child intent to parent
   */
  const linkChildIntent = useCallback((parentId, childId) => {
    const parent = intentMap.current.get(parentId)
    if (parent) {
      parent.childIntentIds = [...(parent.childIntentIds || []), childId]
      intentMap.current.set(parentId, parent)
    }
  }, [])

  /**
   * Get intent by ID
   */
  const getIntent = useCallback((intentId) => {
    return intentMap.current.get(intentId)
  }, [])

  /**
   * Get all intents for correlation ID
   */
  const getCorrelatedIntents = useCallback((correlationId) => {
    return intents.filter((i) => i.correlationId === correlationId)
  }, [intents])

  /**
   * Get pending intents (for navigation blocking)
   */
  const getPendingIntents = useCallback(() => {
    return intents.filter((i) =>
      i.status === IntentStatus.PENDING || i.status === IntentStatus.EXECUTING
    )
  }, [intents])

  /**
   * Cancel a pending intent
   */
  const cancelIntent = useCallback((intentId) => {
    const intent = intentMap.current.get(intentId)
    if (intent && (intent.status === IntentStatus.PENDING || intent.status === IntentStatus.EXECUTING)) {
      updateIntentStatus(intentId, IntentStatus.CANCELLED)
      return true
    }
    return false
  }, [updateIntentStatus])

  /**
   * Generate correlation ID for linking related actions
   */
  const createCorrelationId = useCallback(() => {
    return `corr_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  }, [])

  const contextValue = useMemo(() => ({
    intents,
    recordIntent,
    updateIntentStatus,
    linkChildIntent,
    getIntent,
    getCorrelatedIntents,
    getPendingIntents,
    cancelIntent,
    createCorrelationId,
    sessionId,
  }), [
    intents,
    recordIntent,
    updateIntentStatus,
    linkChildIntent,
    getIntent,
    getCorrelatedIntents,
    getPendingIntents,
    cancelIntent,
    createCorrelationId,
  ])

  return (
    <IntentContext.Provider value={contextValue}>
      {children}
    </IntentContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useIntent() {
  const context = useContext(IntentContext)
  if (!context) {
    throw new Error('useIntent must be used within IntentProvider')
  }
  return context
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
