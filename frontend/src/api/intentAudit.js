import { API_BASE } from './client'

/**
 * Intent Audit API Client
 *
 * NOTE: Backend audit endpoint is optional. The UX governance system on the backend
 * handles intent tracking via middleware headers. This client provides additional
 * explicit audit logging when the endpoint is available.
 *
 * These functions fail silently (return false) when the endpoint is not available,
 * allowing the app to function without explicit audit endpoints.
 */

const buildIntentHeaders = (intent, idempotencyKey) => ({
  'Content-Type': 'application/json',
  'Idempotency-Key': idempotencyKey,
  'X-Idempotency-Key': idempotencyKey,
  'X-Intent-Id': intent.id,
  'X-Intent-Type': intent.type,
  'X-Intent-Label': encodeURIComponent(intent.label || ''),
  'X-Correlation-Id': intent.correlationId,
  'X-Session-Id': intent.sessionId,
})

const generateIdempotencyKey = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  const rand = Math.random().toString(36).slice(2)
  return `idem-${Date.now().toString(36)}-${rand}`
}

// Track if audit endpoint is available (avoid repeated 404 calls)
let auditEndpointAvailable = true

export async function recordIntent(intent) {
  if (!auditEndpointAvailable) {
    return false // Silently skip if endpoint not available
  }

  try {
    const idempotencyKey = generateIdempotencyKey()
    const response = await fetch(`${API_BASE}/audit/intent`, {
      method: 'POST',
      headers: buildIntentHeaders(intent, idempotencyKey),
      body: JSON.stringify(intent),
    })

    if (response.status === 404) {
      // Endpoint not implemented - disable further attempts
      auditEndpointAvailable = false
      return false
    }

    return response.ok
  } catch (error) {
    // Network error - don't disable, might be temporary
    console.debug('[IntentAudit] Failed to record intent:', error.message)
    return false
  }
}

export async function updateIntent(intent, status, result) {
  if (!auditEndpointAvailable) {
    return false // Silently skip if endpoint not available
  }

  try {
    const idempotencyKey = generateIdempotencyKey()
    const response = await fetch(`${API_BASE}/audit/intent/${intent.id}`, {
      method: 'PATCH',
      headers: buildIntentHeaders(intent, idempotencyKey),
      body: JSON.stringify({ status, result }),
    })

    if (response.status === 404) {
      // Endpoint not implemented - disable further attempts
      auditEndpointAvailable = false
      return false
    }

    return response.ok
  } catch (error) {
    // Network error - don't disable, might be temporary
    console.debug('[IntentAudit] Failed to update intent:', error.message)
    return false
  }
}

