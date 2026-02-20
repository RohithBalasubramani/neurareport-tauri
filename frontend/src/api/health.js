import api, { API_BASE } from './client'

const getHealthUrl = () => `${API_BASE.replace(/[\\/]+$/, '')}/health`

/**
 * Basic health check - lightweight ping
 */
export async function checkHealth({ timeoutMs = 5000, signal } = {}) {
  const controller = signal ? null : new AbortController()
  const effectiveSignal = signal || controller?.signal
  let timeoutId

  if (!signal && controller) {
    timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  }

  try {
    const response = await fetch(getHealthUrl(), {
      method: 'HEAD',
      signal: effectiveSignal,
      cache: 'no-store',
    })
    return response.ok
  } finally {
    if (timeoutId) clearTimeout(timeoutId)
  }
}

/**
 * Get detailed health status including all dependencies
 */
export async function getDetailedHealth() {
  const response = await api.get('/health/detailed')
  return response.data
}

/**
 * Get LLM token usage statistics
 */
export async function getTokenUsage() {
  const response = await api.get('/health/token-usage')
  return response.data
}

/**
 * Get scheduler status and inflight jobs
 */
export async function getSchedulerStatus() {
  const response = await api.get('/health/scheduler')
  return response.data
}

/**
 * Get email/SMTP configuration status
 */
export async function getEmailStatus() {
  const response = await api.get('/health/email')
  return response.data
}

/**
 * Test SMTP connection
 */
export async function testEmailConnection() {
  const response = await api.get('/health/email/test')
  return response.data
}

/**
 * Refresh email configuration
 */
export async function refreshEmailConfig() {
  const response = await api.post('/health/email/refresh')
  return response.data
}

/**
 * Check readiness probe
 */
export async function checkReadiness() {
  const response = await api.get('/ready')
  return response.data
}

/**
 * Get all system health information at once
 */
export async function getSystemHealth() {
  const [detailed, tokenUsage, scheduler, email] = await Promise.allSettled([
    getDetailedHealth(),
    getTokenUsage(),
    getSchedulerStatus(),
    getEmailStatus(),
  ])

  return {
    detailed: detailed.status === 'fulfilled' ? detailed.value : null,
    tokenUsage: tokenUsage.status === 'fulfilled' ? tokenUsage.value : null,
    scheduler: scheduler.status === 'fulfilled' ? scheduler.value : null,
    email: email.status === 'fulfilled' ? email.value : null,
  }
}
