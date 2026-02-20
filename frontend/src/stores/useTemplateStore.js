import { create } from 'zustand'

/**
 * Template management store.
 *
 * Extracted from useAppStore to provide focused template state management.
 * Handles template CRUD, verification artifacts, and template catalog.
 */
export const useTemplateStore = create((set, get) => ({
  // Templates list
  templates: [],
  setTemplates: (templates) => set({ templates }),
  addTemplate: (tpl) => set((state) => ({ templates: [tpl, ...state.templates] })),

  removeTemplate: (id) =>
    set((state) => {
      const templates = state.templates.filter((tpl) => tpl.id !== id)
      const nextTemplateId = state.templateId === id ? null : state.templateId
      const nextLastApproved =
        state.lastApprovedTemplate?.id === id ? null : state.lastApprovedTemplate
      return { templates, templateId: nextTemplateId, lastApprovedTemplate: nextLastApproved }
    }),

  updateTemplate: (templateId, updater) =>
    set((state) => {
      if (!templateId || typeof updater !== 'function') return {}
      let changed = false
      const templates = state.templates.map((tpl) => {
        if (tpl?.id !== templateId) return tpl
        const next = updater(tpl) || tpl
        if (next !== tpl) changed = true
        return next !== tpl ? next : tpl
      })
      return changed ? { templates } : {}
    }),

  // Active template selection
  templateId: null,
  setTemplateId: (id) => set({ templateId: id }),

  templateKind: 'pdf',
  setTemplateKind: (kind) => set({ templateKind: kind === 'excel' ? 'excel' : 'pdf' }),

  // Verification artifacts
  verifyArtifacts: null,
  setVerifyArtifacts: (arts) => set({ verifyArtifacts: arts }),

  // Last approved template
  lastApprovedTemplate: null,
  setLastApprovedTemplate: (tpl) => set({ lastApprovedTemplate: tpl }),

  // Template catalog (company + starter)
  templateCatalog: [],
  setTemplateCatalog: (items) =>
    set({ templateCatalog: Array.isArray(items) ? items : [] }),

  // Preview cache
  cacheKey: 0,
  bumpCache: () => set({ cacheKey: Date.now() }),
  setCacheKey: (value) => set({ cacheKey: value ?? Date.now() }),

  htmlUrls: { final: null, template: null, llm2: null },
  setHtmlUrls: (urlsOrUpdater) =>
    set((state) => {
      const next =
        typeof urlsOrUpdater === 'function'
          ? urlsOrUpdater(state.htmlUrls)
          : urlsOrUpdater
      return { htmlUrls: { ...state.htmlUrls, ...next } }
    }),
}))
