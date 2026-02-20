/**
 * Tauri desktop detection and backend URL bridge.
 *
 * In Tauri production builds, the Python backend runs on a dynamically
 * chosen port. This module discovers that port via Tauri IPC so the
 * API client can route requests correctly.
 *
 * In web/dev mode all functions are no-ops.
 */

/** Detect if running inside a Tauri webview */
export const isTauri = () =>
  typeof window !== 'undefined' && window.__TAURI__ !== undefined

// Cache so we only invoke once
let _backendUrl = null

/** Race a promise against a timeout */
function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`Tauri IPC timed out after ${ms}ms`)), ms)
    ),
  ])
}

/**
 * Get the backend URL from the Tauri Rust layer.
 * Returns null in non-Tauri environments.
 * Times out after 5 seconds to prevent the app from hanging.
 */
export async function getTauriBackendUrl() {
  if (!isTauri()) return null
  if (_backendUrl) return _backendUrl

  try {
    const { invoke } = await withTimeout(
      import('@tauri-apps/api/core'),
      5000,
    )
    _backendUrl = await withTimeout(invoke('get_backend_url'), 5000)
    return _backendUrl
  } catch (e) {
    console.warn('[tauri] Failed to get backend URL:', e)
    return null
  }
}
