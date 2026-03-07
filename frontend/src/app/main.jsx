import './instrument' // Sentry init — must be first import
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'
import { installGlobalFrontendErrorHandlers } from '@/api/frontendErrorLogger'
import { initApiForTauri, getApiBase } from '@/api/client'
import { isTauri } from '@/utils/tauri'

installGlobalFrontendErrorHandlers()

function renderApp() {
  createRoot(document.getElementById('root'), {
    onUncaughtError: Sentry.reactErrorHandler(),
    onCaughtError: Sentry.reactErrorHandler(),
    onRecoverableError: Sentry.reactErrorHandler(),
  }).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}

function renderError(err) {
  const root = document.getElementById('root')
  root.innerHTML = `
    <div style="padding:40px;font-family:system-ui;color:#333;max-width:600px;margin:0 auto">
      <h1 style="color:#e53e3e">NeuraReport failed to start</h1>
      <pre style="background:#f5f5f5;padding:16px;border-radius:8px;overflow:auto;font-size:13px">${
        err?.stack || err?.message || String(err)
      }</pre>
      <p style="color:#666;margin-top:16px">
        Environment: ${isTauri() ? 'Tauri desktop' : 'Browser'}<br/>
        URL: ${window.location.href}
      </p>
    </div>
  `
}

/** Show a loading splash while the backend starts up, with elapsed timer. */
function showLoading() {
  const root = document.getElementById('root')
  root.innerHTML = `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:system-ui;color:#64748b;background:#f8fafc">
      <div style="width:48px;height:48px;border:4px solid #e2e8f0;border-top-color:#3B82F6;border-radius:50%;animation:spin 0.8s linear infinite"></div>
      <p style="margin-top:20px;font-size:15px">Starting NeuraReport...</p>
      <p id="loading-elapsed" style="margin-top:8px;font-size:13px;color:#94a3b8"></p>
      <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
    </div>
  `
  const startTime = Date.now()
  window._loadingTimer = setInterval(() => {
    const el = document.getElementById('loading-elapsed')
    if (el) {
      const secs = Math.floor((Date.now() - startTime) / 1000)
      el.textContent = secs < 10 ? '' : `${secs}s — first launch takes longer`
    }
  }, 1000)
}

function clearLoadingTimer() {
  if (window._loadingTimer) {
    clearInterval(window._loadingTimer)
    window._loadingTimer = null
  }
}

/**
 * In Tauri desktop mode, the Python backend may take 60-90s on first launch.
 * Uses Tauri IPC to check backend health (bypasses browser CORS/CSP).
 * Falls back to HTTP fetch for non-Tauri or if IPC is unavailable.
 */
async function waitForBackend(baseUrl, maxWaitMs = 120000) {
  const start = Date.now()
  const interval = 1000

  // Prefer Tauri IPC health check — no CORS, no CSP, no mixed-content issues
  let invoke = null
  if (isTauri()) {
    try {
      const core = await import('@tauri-apps/api/core')
      invoke = core.invoke
    } catch (_) {
      console.warn('[tauri] IPC unavailable, falling back to HTTP health check')
    }
  }

  while (Date.now() - start < maxWaitMs) {
    try {
      if (invoke) {
        // IPC: Rust does a TCP connect check — no browser restrictions
        const healthy = await invoke('check_backend_health')
        if (healthy) {
          // Backend port is open — verify HTTP is actually serving
          try {
            const resp = await fetch(`${baseUrl}/health`, { signal: AbortSignal.timeout(3000) })
            if (resp.ok) return
          } catch (_) {
            // HTTP not ready yet but TCP is open — keep trying
          }
        }
      } else {
        const resp = await fetch(`${baseUrl}/health`, { signal: AbortSignal.timeout(2000) })
        if (resp.ok) return
      }
    } catch (e) {
      console.debug('[health] waiting...', e?.message || '')
    }
    await new Promise((r) => setTimeout(r, interval))
  }
  throw new Error('Backend did not start within 120 seconds')
}

// In Tauri desktop mode, discover the backend port, wait for it, then render.
async function bootstrap() {
  await initApiForTauri()

  if (isTauri()) {
    showLoading()
    console.log('[tauri] Waiting for backend at:', getApiBase())
    await waitForBackend(getApiBase())
    clearLoadingTimer()
  }

  renderApp()
}

bootstrap().catch((err) => {
  clearLoadingTimer()
  renderError(err)
})
