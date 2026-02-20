import './instrument' // Sentry init — must be first import
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'
import { installGlobalFrontendErrorHandlers } from '@/api/frontendErrorLogger'
import { initApiForTauri } from '@/api/client'

installGlobalFrontendErrorHandlers()

// In Tauri desktop mode, discover the backend port before rendering.
// In web mode this resolves immediately (no-op).
initApiForTauri().then(() => {
  createRoot(document.getElementById('root'), {
    onUncaughtError: Sentry.reactErrorHandler(),
    onCaughtError: Sentry.reactErrorHandler(),
    onRecoverableError: Sentry.reactErrorHandler(),
  }).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
})
