import { create } from 'zustand'

/**
 * Discovery results store with localStorage persistence.
 *
 * Extracted from useAppStore to isolate the discovery cache logic.
 * Provides LRU eviction, size limits, and cross-tab synchronization.
 */

const DISCOVERY_STORAGE_KEY = 'neura.discovery.v1'
const DISCOVERY_MAX_SIZE_BYTES = 2 * 1024 * 1024
const DISCOVERY_MAX_TEMPLATES = 50

const defaultDiscoveryState = { results: {}, meta: null }

const loadDiscoveryFromStorage = () => {
  if (typeof window === 'undefined') return defaultDiscoveryState
  try {
    const raw = window.localStorage.getItem(DISCOVERY_STORAGE_KEY)
    if (!raw) return defaultDiscoveryState
    if (raw.length > DISCOVERY_MAX_SIZE_BYTES) {
      window.localStorage.removeItem(DISCOVERY_STORAGE_KEY)
      return defaultDiscoveryState
    }
    const parsed = JSON.parse(raw)
    const results =
      parsed && parsed.results && typeof parsed.results === 'object' ? parsed.results : {}
    const meta = parsed && parsed.meta && typeof parsed.meta === 'object' ? parsed.meta : null
    return { results, meta }
  } catch {
    return defaultDiscoveryState
  }
}

const evictOldestResults = (results, maxSize, maxTemplates) => {
  if (!results || typeof results !== 'object') return {}
  const entries = Object.entries(results)
  if (entries.length <= 1) return results

  entries.sort((a, b) => {
    const timeA = a[1]?._accessedAt || 0
    const timeB = b[1]?._accessedAt || 0
    return timeA - timeB
  })

  const trimmed = entries.slice(-maxTemplates)
  const evicted = Object.fromEntries(trimmed)
  const serialized = JSON.stringify(evicted)
  if (serialized.length > maxSize && trimmed.length > 1) {
    const [, ...rest] = trimmed
    return evictOldestResults(Object.fromEntries(rest), maxSize, maxTemplates)
  }
  return evicted
}

const persistDiscoveryToStorage = (results, meta) => {
  if (typeof window === 'undefined') return
  try {
    const timestampedResults = {}
    if (results && typeof results === 'object') {
      Object.entries(results).forEach(([key, value]) => {
        timestampedResults[key] = { ...value, _accessedAt: value?._accessedAt || Date.now() }
      })
    }

    const evictedResults = evictOldestResults(timestampedResults, DISCOVERY_MAX_SIZE_BYTES, DISCOVERY_MAX_TEMPLATES)
    const payload = JSON.stringify({
      results: evictedResults,
      meta: meta && typeof meta === 'object' ? meta : null,
      ts: Date.now(),
    })

    if (payload.length > DISCOVERY_MAX_SIZE_BYTES) {
      const entries = Object.entries(evictedResults)
      if (entries.length > 1) {
        const newest = entries[entries.length - 1]
        window.localStorage.setItem(DISCOVERY_STORAGE_KEY, JSON.stringify({
          results: { [newest[0]]: newest[1] },
          meta: meta && typeof meta === 'object' ? meta : null,
          ts: Date.now(),
        }))
        return
      }
    }

    window.localStorage.setItem(DISCOVERY_STORAGE_KEY, payload)
  } catch (err) {
    if (err?.name === 'QuotaExceededError' || err?.code === 22) {
      try { window.localStorage.removeItem(DISCOVERY_STORAGE_KEY) } catch { /* swallow */ }
    }
  }
}

const clearDiscoveryStorage = () => {
  if (typeof window === 'undefined') return
  try { window.localStorage.removeItem(DISCOVERY_STORAGE_KEY) } catch { /* swallow */ }
}

const discoveryInitial = loadDiscoveryFromStorage()

export const useDiscoveryStore = create((set, get) => ({
  discoveryResults: discoveryInitial.results,
  discoveryMeta: discoveryInitial.meta,
  discoveryFinding: false,

  setDiscoveryResults: (results, meta) =>
    set((state) => {
      const nextResults = results && typeof results === 'object' ? results : defaultDiscoveryState.results
      const nextMeta = meta ? { ...(state.discoveryMeta || {}), ...meta } : state.discoveryMeta
      persistDiscoveryToStorage(nextResults, nextMeta)
      return { discoveryResults: nextResults, discoveryMeta: nextMeta }
    }),

  setDiscoveryMeta: (meta) =>
    set((state) => {
      if (!meta || typeof meta !== 'object') return {}
      const nextMeta = { ...(state.discoveryMeta || {}), ...meta }
      persistDiscoveryToStorage(state.discoveryResults, nextMeta)
      return { discoveryMeta: nextMeta }
    }),

  clearDiscoveryResults: () =>
    set(() => {
      clearDiscoveryStorage()
      return { discoveryResults: defaultDiscoveryState.results, discoveryMeta: defaultDiscoveryState.meta }
    }),

  updateDiscoveryBatchSelection: (tplId, batchIdx, selected) =>
    set((state) => {
      const target = state.discoveryResults?.[tplId]
      if (!target || !Array.isArray(target.batches)) return {}
      const nextBatches = target.batches.map((batch, idx) =>
        idx === batchIdx ? { ...batch, selected } : batch,
      )
      const nextResults = { ...state.discoveryResults, [tplId]: { ...target, batches: nextBatches } }
      persistDiscoveryToStorage(nextResults, state.discoveryMeta)
      return { discoveryResults: nextResults }
    }),

  setDiscoveryFinding: (flag = false) => set({ discoveryFinding: !!flag }),
}))

// Cross-tab synchronization via storage events
if (typeof window !== 'undefined') {
  if (!window.__NEURA_DISCOVERY_HANDLER__) {
    window.__NEURA_DISCOVERY_HANDLER__ = (event) => {
      if (event.key !== DISCOVERY_STORAGE_KEY) return
      try {
        const parsed = event.newValue ? JSON.parse(event.newValue) : null
        useDiscoveryStore.setState({
          discoveryResults:
            parsed && parsed.results && typeof parsed.results === 'object'
              ? parsed.results
              : defaultDiscoveryState.results,
          discoveryMeta:
            parsed && parsed.meta && typeof parsed.meta === 'object'
              ? parsed.meta
              : defaultDiscoveryState.meta,
        })
      } catch {
        useDiscoveryStore.setState({
          discoveryResults: defaultDiscoveryState.results,
          discoveryMeta: defaultDiscoveryState.meta,
        })
      }
    }
    window.addEventListener('storage', window.__NEURA_DISCOVERY_HANDLER__)
  }
}
