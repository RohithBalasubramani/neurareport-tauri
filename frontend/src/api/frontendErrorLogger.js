const runtimeEnv = {
  ...(typeof import.meta !== 'undefined' && import.meta?.env ? import.meta.env : {}),
  ...(globalThis.__NEURA_TEST_ENVIRONMENT__ || {}),
}

const localHosts = new Set(['0.0.0.0', '127.0.0.1', 'localhost', '::1'])
const recentFingerprints = new Map()
const FINGERPRINT_TTL_MS = 2500

const trimText = (value, maxLen = 1000) => {
  if (value == null) return undefined
  const text = String(value)
  if (!text) return undefined
  return text.length > maxLen ? `${text.slice(0, maxLen)}…` : text
}

const compactText = (value, maxLen = 1000) => {
  const text = trimText(value, maxLen * 2)
  if (!text) return undefined
  const compacted = text.replace(/\s+/g, ' ').trim()
  return compacted.length > maxLen ? `${compacted.slice(0, maxLen)}…` : compacted
}

const safeContext = (value) => {
  if (value == null) return undefined
  try {
    const serialized = JSON.parse(JSON.stringify(value))
    return serialized
  } catch (_) {
    return trimText(value, 1000)
  }
}

const resolveApiOrigin = () => {
  const envBaseUrl = runtimeEnv.VITE_API_BASE_URL
  if (envBaseUrl && envBaseUrl !== 'proxy') {
    // Path-based URL (e.g. /neurareport-api) — use as base directly
    if (envBaseUrl.startsWith('/')) return envBaseUrl
    try {
      const hasScheme = /^([a-z][a-z\d+\-.]*:)?\/\//i.test(envBaseUrl)
      const protocol = typeof window !== 'undefined' ? window.location.protocol : 'http:'
      const candidate = hasScheme ? envBaseUrl : `${protocol}//${envBaseUrl}`
      const parsed = new URL(candidate)
      if (typeof window !== 'undefined' && localHosts.has(parsed.hostname)) {
        parsed.hostname = window.location.hostname
      }
      if (!parsed.port && runtimeEnv.VITE_API_PORT) {
        parsed.port = String(runtimeEnv.VITE_API_PORT)
      }
      return parsed.origin
    } catch (_) {
      // Fallback below
    }
  }

  if (typeof window === 'undefined') return undefined
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:'
  const hostname = window.location.hostname || '127.0.0.1'
  const port = runtimeEnv.VITE_API_PORT || '9070'
  return `${protocol}//${hostname}:${port}`
}

const shouldSkip = () => {
  if (typeof fetch === 'undefined') return true
  if (runtimeEnv.MODE === 'test') return true
  if (typeof globalThis.__VITEST__ !== 'undefined') return true
  return false
}

export async function reportFrontendError(payload = {}) {
  if (shouldSkip()) return false

  const message = compactText(payload.message, 2000)
  if (!message) return false

  const route = trimText(payload.route, 512)
  const action = trimText(payload.action, 256)
  const source = trimText(payload.source || 'frontend', 128)
  const fingerprint = `${source || '-'}|${route || '-'}|${action || '-'}|${message}`
  const nowMs = Date.now()
  const lastSeen = recentFingerprints.get(fingerprint)
  if (lastSeen && nowMs - lastSeen < FINGERPRINT_TTL_MS) {
    return false
  }
  recentFingerprints.set(fingerprint, nowMs)

  if (recentFingerprints.size > 400) {
    const cutoff = nowMs - (FINGERPRINT_TTL_MS * 8)
    for (const [key, ts] of recentFingerprints.entries()) {
      if (ts < cutoff) {
        recentFingerprints.delete(key)
      }
    }
  }

  const origin = resolveApiOrigin()
  if (!origin) return false

  try {
    const response = await fetch(`${origin.replace(/\/$/, '')}/api/v1/audit/frontend-error`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
      body: JSON.stringify({
        source,
        message,
        route,
        action,
        status_code: payload.statusCode ?? payload.status_code,
        method: trimText(payload.method, 16),
        request_url: trimText(payload.requestUrl ?? payload.request_url, 2000),
        stack: trimText(payload.stack, 10000),
        user_agent: trimText(typeof navigator !== 'undefined' ? navigator.userAgent : undefined, 1024),
        timestamp: new Date().toISOString(),
        context: safeContext(payload.context),
      }),
    })
    return response.ok
  } catch (_) {
    return false
  }
}

let globalHandlersInstalled = false

export function installGlobalFrontendErrorHandlers() {
  if (globalHandlersInstalled || typeof window === 'undefined') return
  globalHandlersInstalled = true

  window.addEventListener('error', (event) => {
    const err = event.error
    reportFrontendError({
      source: 'window.error',
      message: err?.message || event.message || 'Uncaught window error',
      stack: err?.stack,
      route: window.location?.pathname,
      requestUrl: window.location?.href,
      context: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      },
    })
  })

  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason
    const message =
      reason?.message ||
      (typeof reason === 'string' ? reason : 'Unhandled promise rejection')
    reportFrontendError({
      source: 'window.unhandledrejection',
      message,
      stack: reason?.stack,
      route: window.location?.pathname,
      requestUrl: window.location?.href,
      context: {
        reasonType: typeof reason,
      },
    })
  })
}
