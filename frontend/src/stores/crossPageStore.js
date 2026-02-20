import { create } from 'zustand'

/**
 * CrossPageStore – The interconnection bus for cross-page data flow.
 *
 * Two mechanisms:
 *
 * 1. pendingTransfer – One-shot payload for navigating with context.
 *    Page A writes { target, action, payload, source }, navigates to Page B,
 *    Page B consumes and clears it on mount. Auto-expires after 30 seconds.
 *
 * 2. outputRegistry – Persistent map keyed by feature (e.g. 'agents', 'query').
 *    Each feature writes its latest output here after producing something meaningful.
 *    Other features can browse what is available without sequential navigation.
 */
const TRANSFER_EXPIRY_MS = 30_000

const useCrossPageStore = create((set, get) => ({
  // === PENDING TRANSFER (one-shot, consumed on arrival) ===
  pendingTransfer: null,

  setPendingTransfer: (transfer) =>
    set({
      pendingTransfer: transfer
        ? { ...transfer, timestamp: Date.now() }
        : null,
    }),

  consumeTransfer: (expectedTarget) => {
    const { pendingTransfer } = get()
    if (!pendingTransfer) return null
    if (expectedTarget && pendingTransfer.target !== expectedTarget) return null
    if (Date.now() - pendingTransfer.timestamp > TRANSFER_EXPIRY_MS) {
      set({ pendingTransfer: null })
      return null
    }
    const transfer = pendingTransfer
    set({ pendingTransfer: null })
    return transfer
  },

  // === OUTPUT REGISTRY (persists until overwritten) ===
  outputRegistry: {},

  registerOutput: (featureKey, output) =>
    set((state) => ({
      outputRegistry: {
        ...state.outputRegistry,
        [featureKey]: {
          ...output,
          featureKey,
          timestamp: Date.now(),
        },
      },
    })),

  clearOutput: (featureKey) =>
    set((state) => {
      const next = { ...state.outputRegistry }
      delete next[featureKey]
      return { outputRegistry: next }
    }),

  getOutput: (featureKey) => get().outputRegistry[featureKey] || null,

  getOutputsByType: (type) => {
    const registry = get().outputRegistry
    return Object.values(registry).filter((o) => o.type === type)
  },

  getAllOutputs: () => Object.values(get().outputRegistry),
}))

export default useCrossPageStore
