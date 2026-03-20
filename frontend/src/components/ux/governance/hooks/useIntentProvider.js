/**
 * Intent Provider Hook
 *
 * Manages intent recording, status tracking, and audit trail.
 */
import { useCallback, useMemo, useRef, useState } from 'react'
import { createIntent, IntentStatus } from '../intentConstants'

export function useIntentProvider({ onIntentChange, maxHistory = 100, auditClient }) {
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

  return useMemo(() => ({
    intents,
    recordIntent,
    updateIntentStatus,
    linkChildIntent,
    getIntent,
    getCorrelatedIntents,
    getPendingIntents,
    cancelIntent,
    createCorrelationId,
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
}
