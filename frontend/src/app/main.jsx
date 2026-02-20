import './instrument' // Sentry init — must be first import
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
import App from './App.jsx'
import { installGlobalFrontendErrorHandlers } from '@/api/frontendErrorLogger'
import { initApiForTauri } from '@/api/client'
import { isTauri } from '@/utils/tauri'

// Write to the persistent debug banner (outside #root, React can't touch it)
const dbg = window.dbg || ((msg) => console.log('[main]', msg))

dbg('main.jsx module loaded')
dbg('isTauri: ' + isTauri())

installGlobalFrontendErrorHandlers()
dbg('Error handlers installed')

function renderApp() {
  dbg('renderApp() called — mounting React on #root')
  try {
    const root = document.getElementById('root')
    dbg('#root found: ' + !!root + ', innerHTML length: ' + (root?.innerHTML?.length || 0))

    createRoot(root, {
      onUncaughtError: (err) => {
        dbg('React onUncaughtError: ' + (err?.message || err))
        Sentry.reactErrorHandler()(err)
      },
      onCaughtError: (err) => {
        dbg('React onCaughtError: ' + (err?.message || err))
        Sentry.reactErrorHandler()(err)
      },
      onRecoverableError: (err) => {
        dbg('React onRecoverableError: ' + (err?.message || err))
        Sentry.reactErrorHandler()(err)
      },
    }).render(
      <StrictMode>
        <App />
      </StrictMode>,
    )
    dbg('React render() called — waiting for first paint')
  } catch (err) {
    dbg('RENDER THREW: ' + (err?.stack || err?.message || err))
    renderError(err)
  }
}

function renderError(err) {
  dbg('renderError: ' + (err?.message || err))
  const root = document.getElementById('root')
  root.innerHTML = `
    <div style="padding:40px;font-family:system-ui;color:#333;max-width:600px;margin:0 auto">
      <h1 style="color:#e53e3e">NeuraReport failed to start</h1>
      <pre style="background:#f5f5f5;padding:16px;border-radius:8px;overflow:auto;font-size:13px">${
        err?.stack || err?.message || String(err)
      }</pre>
      <p style="color:#666;margin-top:16px">
        Environment: ${isTauri() ? 'Tauri desktop' : 'Browser'}<br/>
        URL: ${window.location.href}<br/>
        Check the log file at:<br/>
        <code>%APPDATA%/com.neurareport.desktop/neurareport.log</code>
      </p>
    </div>
  `
}

// In Tauri desktop mode, discover the backend port before rendering.
dbg('Calling initApiForTauri()...')

initApiForTauri()
  .then(() => {
    dbg('initApiForTauri resolved — calling renderApp()')
    renderApp()
  })
  .catch((err) => {
    dbg('initApiForTauri REJECTED: ' + (err?.stack || err?.message || err))
    renderError(err)
  })
