import './instrument' // Sentry init — must be first import
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'
import { installGlobalFrontendErrorHandlers } from '@/api/frontendErrorLogger'
import { initApiForTauri } from '@/api/client'
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

// In Tauri desktop mode, discover the backend port before rendering.
initApiForTauri()
  .then(() => renderApp())
  .catch((err) => renderError(err))
