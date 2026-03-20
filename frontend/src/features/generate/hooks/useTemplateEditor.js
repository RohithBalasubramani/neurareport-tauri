import { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useLocation, UNSAFE_NavigationContext } from 'react-router-dom'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { buildLastEditInfo } from '@/utils/templateMeta'
import {
  getTemplateHtml,
  editTemplateManual,
  editTemplateAi,
  undoTemplateEdit,
} from '@/api/client'
import { useEditorKeyboardShortcuts, getShortcutDisplay } from './useEditorKeyboardShortcuts.js'
import { useEditorDraft } from './useEditorDraft.js'

export { getShortcutDisplay }

export function useTemplateEditor() {
  const { templateId } = useParams()
  const navigate = useNavigateInteraction()
  const location = useLocation()
  const toast = useToast()
  const { execute } = useInteraction()
  const templates = useAppStore((state) => state.templates)
  const updateTemplateEntry = useAppStore((state) => state.updateTemplate)

  const referrer = location.state?.from || '/generate'

  const template = useMemo(
    () => templates.find((t) => t.id === templateId) || null,
    [templates, templateId],
  )

  // Core editor state
  const [loading, setLoading] = useState(true)
  const [html, setHtml] = useState('')
  const [initialHtml, setInitialHtml] = useState('')
  const [instructions, setInstructions] = useState('')
  const [previewUrl, setPreviewUrl] = useState(null)
  const [saving, setSaving] = useState(false)
  const [aiBusy, setAiBusy] = useState(false)
  const [undoBusy, setUndoBusy] = useState(false)
  const [serverMeta, setServerMeta] = useState(null)
  const [diffSummary, setDiffSummary] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)

  // UI state
  const [editMode, setEditMode] = useState('manual')
  const [diffOpen, setDiffOpen] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [previewFullscreen, setPreviewFullscreen] = useState(false)
  const [modeSwitchConfirm, setModeSwitchConfirm] = useState({ open: false, nextMode: null })

  const dirty = html !== initialHtml
  const hasInstructions = (instructions || '').trim().length > 0

  // Block in-app navigation when there are unsaved changes
  const { navigator } = useContext(UNSAFE_NavigationContext)
  const dirtyRef = useRef(dirty)
  dirtyRef.current = dirty

  useEffect(() => {
    const originalPush = navigator.push
    const originalReplace = navigator.replace

    navigator.push = (...args) => {
      if (dirtyRef.current && !window.confirm('You have unsaved changes in the template editor. Leave without saving?')) {
        return
      }
      originalPush.apply(navigator, args)
    }
    navigator.replace = (...args) => {
      if (dirtyRef.current && !window.confirm('You have unsaved changes in the template editor. Leave without saving?')) {
        return
      }
      originalReplace.apply(navigator, args)
    }

    return () => {
      navigator.push = originalPush
      navigator.replace = originalReplace
    }
  }, [navigator])

  // Draft auto-save
  const {
    hasDraft,
    draftData,
    lastSaved,
    scheduleAutoSave,
    discardDraft,
    clearDraftAfterSave,
    saveDraft,
  } = useEditorDraft(templateId, { enabled: editMode === 'manual' })

  useEffect(() => {
    if (dirty && editMode === 'manual') {
      scheduleAutoSave(html, instructions)
    }
  }, [html, instructions, dirty, editMode, scheduleAutoSave])

  const syncTemplateMetadata = useCallback(
    (metadata) => {
      if (!metadata || !templateId || typeof updateTemplateEntry !== 'function') return
      updateTemplateEntry(templateId, (tpl) => {
        if (!tpl) return tpl
        const prevGenerator = tpl.generator || {}
        const prevSummary = prevGenerator.summary || {}
        const nextSummary = { ...prevSummary }
        const fields = ['lastEditType', 'lastEditAt', 'lastEditNotes']
        let summaryChanged = false
        fields.forEach((field) => {
          if (Object.prototype.hasOwnProperty.call(metadata, field) && metadata[field] !== undefined) {
            if (nextSummary[field] !== metadata[field]) {
              nextSummary[field] = metadata[field]
              summaryChanged = true
            }
          }
        })
        if (!summaryChanged) {
          return tpl
        }
        return {
          ...tpl,
          generator: {
            ...prevGenerator,
            summary: nextSummary,
          },
        }
      })
    },
    [templateId, updateTemplateEntry],
  )

  const loadTemplate = useCallback(async () => {
    if (!templateId) return
    setLoading(true)
    setError(null)
    try {
      const data = await getTemplateHtml(templateId)
      if (!data || typeof data !== 'object' || typeof data.html !== 'string') {
        throw new Error('Template not found or returned invalid data')
      }
      const nextHtml = data.html
      setHtml(nextHtml)
      setInitialHtml(nextHtml)
      setServerMeta(data?.metadata || null)
      setDiffSummary(data?.diff_summary || null)
      setHistory(Array.isArray(data?.history) ? data.history : [])
      if (data?.metadata) {
        syncTemplateMetadata(data.metadata)
      }
    } catch (err) {
      setError(String(err?.message || err))
      toast.show(String(err), 'error')
    } finally {
      setLoading(false)
    }
  }, [templateId, toast, syncTemplateMetadata])

  useEffect(() => {
    loadTemplate()
  }, [loadTemplate])

  useEffect(() => {
    if (!html) {
      setPreviewUrl(null)
      return
    }
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    setPreviewUrl(url)
    return () => {
      URL.revokeObjectURL(url)
    }
  }, [html])

  useEffect(() => {
    const handleBeforeUnload = (event) => {
      if (!dirty) return
      event.preventDefault()
      event.returnValue = ''
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [dirty])

  const handleSave = useCallback(async () => {
    if (!templateId) return
    await execute({
      type: InteractionType.UPDATE,
      label: 'Save template',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        action: 'edit_manual',
      },
      action: async () => {
        setSaving(true)
        try {
          const data = await editTemplateManual(templateId, html)
          const nextHtml = typeof data?.html === 'string' ? data.html : html
          setHtml(nextHtml)
          setInitialHtml(nextHtml)
          setServerMeta(data?.metadata || null)
          setDiffSummary(data?.diff_summary || null)
          setHistory(Array.isArray(data?.history) ? data.history : history)
          if (data?.metadata) {
            syncTemplateMetadata(data.metadata)
          }
          clearDraftAfterSave()
          toast.show('Template HTML saved.', 'success')
          return data
        } catch (err) {
          toast.show(String(err), 'error')
          throw err
        } finally {
          setSaving(false)
        }
      },
    })
  }, [templateId, html, toast, syncTemplateMetadata, clearDraftAfterSave, history, execute])

  const handleApplyAi = useCallback(async () => {
    if (!templateId) return
    const text = (instructions || '').trim()
    if (!text) {
      toast.show('Enter AI instructions before applying.', 'info')
      return
    }
    await execute({
      type: InteractionType.GENERATE,
      label: 'Apply AI edit',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        action: 'edit_ai',
      },
      action: async () => {
        setAiBusy(true)
        try {
          const data = await editTemplateAi(templateId, text, html)
          const nextHtml = typeof data?.html === 'string' ? data.html : html
          setHtml(nextHtml)
          setInitialHtml(nextHtml)
          setServerMeta(data?.metadata || null)
          setDiffSummary(data?.diff_summary || null)
          setHistory(Array.isArray(data?.history) ? data.history : history)
          if (data?.metadata) {
            syncTemplateMetadata(data.metadata)
          }
          setInstructions('')
          clearDraftAfterSave()
          const changes = Array.isArray(data?.summary) ? data.summary : []
          if (changes.length) {
            toast.show(`AI updated template: ${changes.join('; ')}`, 'success')
          } else {
            toast.show('AI updated the template HTML.', 'success')
          }
          return data
        } catch (err) {
          toast.show(String(err), 'error')
          throw err
        } finally {
          setAiBusy(false)
        }
      },
    })
  }, [templateId, html, instructions, toast, syncTemplateMetadata, clearDraftAfterSave, history, execute])

  const handleUndo = useCallback(async () => {
    if (!templateId) return
    await execute({
      type: InteractionType.UPDATE,
      label: 'Undo template edit',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        action: 'undo_edit',
      },
      action: async () => {
        setUndoBusy(true)
        try {
          const data = await undoTemplateEdit(templateId)
          const nextHtml = typeof data?.html === 'string' ? data.html : html
          setHtml(nextHtml)
          setInitialHtml(nextHtml)
          setServerMeta(data?.metadata || null)
          setDiffSummary(data?.diff_summary || null)
          setHistory(Array.isArray(data?.history) ? data.history : history)
          if (data?.metadata) {
            syncTemplateMetadata(data.metadata)
          }
          toast.show('Reverted to the previous template version.', 'success')
          return data
        } catch (err) {
          toast.show(String(err), 'error')
          throw err
        } finally {
          setUndoBusy(false)
        }
      },
    })
  }, [templateId, html, toast, syncTemplateMetadata, history, execute])

  const handleBack = () => {
    if (dirty && typeof window !== 'undefined') {
      const confirmed = window.confirm(
        'You have unsaved changes. Leave the editor and discard them?',
      )
      if (!confirmed) return
    }
    navigate(referrer, {
      label: 'Back to templates',
      intent: { referrer },
    })
  }

  const handleEditModeChange = (event, newMode) => {
    if (newMode !== null) {
      if (dirty && newMode === 'chat') {
        setModeSwitchConfirm({ open: true, nextMode: newMode })
        return
      }
      setEditMode(newMode)
    }
  }

  const handleChatHtmlUpdate = useCallback((newHtml) => {
    setHtml(newHtml)
    setInitialHtml(newHtml)
  }, [])

  const handleChatApplySuccess = useCallback((result) => {
    if (result?.metadata) {
      setServerMeta(result.metadata)
      syncTemplateMetadata(result.metadata)
    }
    if (result?.diff_summary) {
      setDiffSummary(result.diff_summary)
    }
    if (Array.isArray(result?.history)) {
      setHistory(result.history)
    }
  }, [syncTemplateMetadata])

  const handleRestoreDraft = useCallback(() => {
    if (draftData) {
      setHtml(draftData.html || '')
      if (draftData.instructions) {
        setInstructions(draftData.instructions)
      }
      discardDraft()
      toast.show('Draft restored successfully.', 'success')
    }
  }, [draftData, discardDraft, toast])

  // Keyboard shortcuts
  useEditorKeyboardShortcuts({
    onSave: handleSave,
    onUndo: handleUndo,
    onApplyAi: handleApplyAi,
    onEscape: () => {
      if (diffOpen) setDiffOpen(false)
      if (shortcutsOpen) setShortcutsOpen(false)
    },
    enabled: editMode === 'manual' && !loading,
    dirty,
    hasInstructions,
  })

  const lastEditInfo = buildLastEditInfo(serverMeta)
  const breadcrumbLabel = referrer === '/' ? 'Setup' : 'Generate'

  return {
    templateId,
    template,
    referrer,
    breadcrumbLabel,
    // State
    loading,
    html,
    setHtml,
    initialHtml,
    instructions,
    setInstructions,
    previewUrl,
    saving,
    aiBusy,
    undoBusy,
    error,
    editMode,
    diffOpen,
    setDiffOpen,
    shortcutsOpen,
    setShortcutsOpen,
    previewFullscreen,
    setPreviewFullscreen,
    modeSwitchConfirm,
    setModeSwitchConfirm,
    dirty,
    hasInstructions,
    serverMeta,
    diffSummary,
    history,
    lastEditInfo,
    // Draft
    hasDraft,
    draftData,
    lastSaved,
    saveDraft,
    discardDraft,
    // Handlers
    handleSave,
    handleApplyAi,
    handleUndo,
    handleBack,
    handleEditModeChange,
    handleChatHtmlUpdate,
    handleChatApplySuccess,
    handleRestoreDraft,
    // Misc
    toast,
    setEditMode,
  }
}
