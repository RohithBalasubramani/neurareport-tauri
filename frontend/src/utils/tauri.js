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

/**
 * Get the backend URL from the Tauri Rust layer.
 * Returns null in non-Tauri environments.
 */
export async function getTauriBackendUrl() {
  if (!isTauri()) return null
  if (_backendUrl) return _backendUrl

  try {
    const { invoke } = await import('@tauri-apps/api/core')
    _backendUrl = await invoke('get_backend_url')
    return _backendUrl
  } catch (e) {
    console.warn('[tauri] Failed to get backend URL:', e)
    return null
  }
}
