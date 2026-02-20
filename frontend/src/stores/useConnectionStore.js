import { create } from 'zustand'

/**
 * Connection management store.
 *
 * Extracted from useAppStore to provide focused connection state management.
 * Handles saved connections, active connection selection, and connection status.
 */
export const useConnectionStore = create((set, get) => ({
  // Connection status
  connection: { status: 'disconnected', lastMessage: null, saved: false, name: '' },
  setConnection: (conn) => set({ connection: { ...get().connection, ...conn } }),

  // Saved connections list
  savedConnections: [],
  setSavedConnections: (connections) =>
    set({ savedConnections: Array.isArray(connections) ? connections : [] }),

  addSavedConnection: (conn) =>
    set((state) => {
      const incoming = conn?.id ? conn : { ...conn, id: conn?.id || `conn_${Date.now()}` }
      const filtered = state.savedConnections.filter((c) => c.id !== incoming.id)
      return { savedConnections: [incoming, ...filtered] }
    }),

  updateSavedConnection: (id, updates) =>
    set((state) => ({
      savedConnections: state.savedConnections.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
      activeConnection:
        state.activeConnectionId === id
          ? { ...state.activeConnection, ...updates }
          : state.activeConnection,
    })),

  removeSavedConnection: (id) =>
    set((state) => {
      const activeRemoved = state.activeConnectionId === id
      return {
        savedConnections: state.savedConnections.filter((c) => c.id !== id),
        activeConnectionId: activeRemoved ? null : state.activeConnectionId,
        activeConnection: activeRemoved ? null : state.activeConnection,
      }
    }),

  // Active connection
  activeConnectionId: null,
  activeConnection: null,
  setActiveConnectionId: (id) =>
    set((state) => ({
      activeConnectionId: id,
      activeConnection: state.savedConnections.find((c) => c.id === id) || null,
    })),
  setActiveConnection: (conn) => set({ activeConnection: conn }),
}))
