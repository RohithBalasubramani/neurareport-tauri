import { create } from 'zustand'

/**
 * Setup flow and demo mode store.
 *
 * Extracted from useAppStore to isolate setup wizard state and demo mode.
 */

const DEMO_CONNECTIONS = [
  { id: 'demo_conn_1', name: 'Sample Sales Database', db_type: 'postgresql', status: 'connected', lastConnected: new Date().toISOString(), lastLatencyMs: 45, summary: 'Demo PostgreSQL connection' },
  { id: 'demo_conn_2', name: 'Marketing Analytics', db_type: 'mysql', status: 'connected', lastConnected: new Date().toISOString(), lastLatencyMs: 32, summary: 'Demo MySQL connection' },
]

const DEMO_TEMPLATES = [
  { id: 'demo_tpl_1', name: 'Monthly Sales Report', kind: 'pdf', status: 'approved', description: 'Comprehensive monthly sales overview', tags: ['sales', 'monthly'], createdAt: new Date().toISOString(), mappingKeys: ['date', 'region', 'product'] },
  { id: 'demo_tpl_2', name: 'Quarterly Revenue Summary', kind: 'excel', status: 'approved', description: 'Revenue breakdown by quarter', tags: ['finance', 'quarterly'], createdAt: new Date().toISOString(), mappingKeys: ['quarter', 'department'] },
  { id: 'demo_tpl_3', name: 'Customer Analytics Dashboard', kind: 'pdf', status: 'approved', description: 'Customer behavior and insights', tags: ['customers', 'analytics'], createdAt: new Date().toISOString(), mappingKeys: ['customer_segment', 'date_range'] },
]

export const useSetupStore = create((set, get) => ({
  // Demo mode
  demoMode: false,
  setDemoMode: (enabled) => {
    set({ demoMode: enabled })
  },
  getDemoConnections: () => DEMO_CONNECTIONS,
  getDemoTemplates: () => DEMO_TEMPLATES,
  initDemoMode: () => {
    try {
      const prefs = localStorage.getItem('neurareport_preferences')
      if (prefs) {
        const parsed = JSON.parse(prefs)
        if (parsed.demoMode) {
          get().setDemoMode(true)
        }
      }
    } catch { /* ignore */ }
  },

  // Setup navigation
  setupNav: 'connect',
  setSetupNav: (pane) => set({ setupNav: pane }),

  // Setup flow gating
  setupStep: 'connect',
  setSetupStep: (step) => set({ setupStep: step }),

  // Reset setup flow
  resetSetup: () =>
    set({
      setupNav: 'connect',
      setupStep: 'connect',
    }),

  // Hydration flag
  hydrated: false,
  setHydrated: (flag = true) => set({ hydrated: !!flag }),

  // Last used tracking
  lastUsed: { connectionId: null, templateId: null },
  setLastUsed: (payload) =>
    set((state) => {
      const prev = state.lastUsed || { connectionId: null, templateId: null }
      const hasConn = payload && Object.prototype.hasOwnProperty.call(payload, 'connectionId')
      const hasTpl = payload && Object.prototype.hasOwnProperty.call(payload, 'templateId')
      return {
        lastUsed: {
          connectionId: hasConn ? payload?.connectionId ?? null : prev.connectionId ?? null,
          templateId: hasTpl ? payload?.templateId ?? null : prev.templateId ?? null,
        },
      }
    }),
}))
