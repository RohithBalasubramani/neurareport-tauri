/**
 * Custom hook for Document Editor state, effects, and handlers.
 */
import { useState, useEffect, useCallback } from 'react'
import useDocumentStore from '@/stores/documentStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export const LANGUAGE_OPTIONS = [
  { value: 'Spanish', label: 'Spanish' },
  { value: 'French', label: 'French' },
  { value: 'German', label: 'German' },
  { value: 'Italian', label: 'Italian' },
  { value: 'Portuguese', label: 'Portuguese' },
  { value: 'Chinese', label: 'Chinese (Simplified)' },
  { value: 'Japanese', label: 'Japanese' },
  { value: 'Korean', label: 'Korean' },
  { value: 'Arabic', label: 'Arabic' },
  { value: 'Hindi', label: 'Hindi' },
]

export const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional', description: 'Formal and business-appropriate' },
  { value: 'casual', label: 'Casual', description: 'Friendly and conversational' },
  { value: 'formal', label: 'Formal', description: 'Very formal and official' },
  { value: 'simplified', label: 'Simplified', description: 'Easy to understand, plain language' },
  { value: 'persuasive', label: 'Persuasive', description: 'Compelling and convincing' },
  { value: 'empathetic', label: 'Empathetic', description: 'Warm and understanding' },
]

export function useDocumentEditor() {
  const toast = useToast()
  const { execute } = useInteraction()
  const { templates } = useSharedData()

  const store = useDocumentStore()
  const {
    documents, currentDocument, versions, comments,
    loading, saving, error, aiResult,
    fetchDocuments, createDocument, getDocument, updateDocument,
    deleteDocument, fetchVersions, restoreVersion, fetchComments,
    addComment, resolveComment, replyToComment, deleteComment,
    checkGrammar, summarize, rewrite, expand, translate, adjustTone,
    clearAiResult, reset,
  } = store

  // UI State
  const [showDocList, setShowDocList] = useState(true)
  const [editorContent, setEditorContent] = useState(null)
  const [selectedText, setSelectedText] = useState('')
  const [aiLoading, setAiLoading] = useState(false)

  // Panel visibility
  const [showVersions, setShowVersions] = useState(false)
  const [showComments, setShowComments] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState(null)
  const [highlightedCommentId, setHighlightedCommentId] = useState(null)

  // Dialogs
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newDocName, setNewDocName] = useState('')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [docToDelete, setDocToDelete] = useState(null)
  const [aiMenuAnchor, setAiMenuAnchor] = useState(null)

  // AI Tool dialogs
  const [translateDialogOpen, setTranslateDialogOpen] = useState(false)
  const [toneDialogOpen, setToneDialogOpen] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('Spanish')
  const [selectedTone, setSelectedTone] = useState('professional')

  // Auto-save
  const [autoSaveEnabled] = useState(true)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)

  // Cross-page transfer
  useIncomingTransfer(FeatureKey.DOCUMENTS, {
    [TransferAction.CREATE_FROM]: async (payload) => {
      const doc = await createDocument({
        title: payload.title || 'Imported Document',
        content: typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content),
      })
      if (doc) getDocument(doc.id)
    },
  })

  // Initialize
  useEffect(() => {
    fetchDocuments()
    return () => reset()
  }, [fetchDocuments, reset])

  // Load document content
  useEffect(() => {
    if (currentDocument?.content) {
      setEditorContent(currentDocument.content)
      setHasUnsavedChanges(false)
    }
  }, [currentDocument])

  // Auto-save effect
  useEffect(() => {
    if (!autoSaveEnabled || !currentDocument || !hasUnsavedChanges || saving) return
    const autoSaveTimer = setTimeout(async () => {
      try {
        await updateDocument(currentDocument.id, { content: editorContent })
        setHasUnsavedChanges(false)
        setLastSaved(new Date())
      } catch (err) {
        console.error('Auto-save failed:', err)
      }
    }, 2000)
    return () => clearTimeout(autoSaveTimer)
  }, [autoSaveEnabled, currentDocument, editorContent, hasUnsavedChanges, saving, updateDocument])

  // UX Governance helper
  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'documents', ...intent },
      action,
    })
  }, [execute])

  // ---- Document handlers ----

  const handleOpenCreateDialog = useCallback(() => {
    return executeUI('Open create document', () => setCreateDialogOpen(true))
  }, [executeUI])

  const handleCloseCreateDialog = useCallback(() => {
    return executeUI('Close create document', () => {
      setCreateDialogOpen(false)
      setNewDocName('')
      setSelectedTemplateId('')
    })
  }, [executeUI])

  const handleCreateDocument = useCallback(async () => {
    if (!newDocName.trim()) return
    return execute({
      type: InteractionType.CREATE,
      label: 'Create document',
      reversibility: Reversibility.SYSTEM_MANAGED,
      successMessage: 'Document created',
      intent: { source: 'documents', name: newDocName },
      action: async () => {
        const doc = await createDocument({
          name: newDocName.trim(),
          content: { type: 'doc', content: [{ type: 'paragraph', content: [] }] },
        })
        if (doc) {
          setCreateDialogOpen(false)
          setNewDocName('')
          setSelectedTemplateId('')
          await getDocument(doc.id)
        }
        return doc
      },
    })
  }, [createDocument, execute, getDocument, newDocName])

  const handleSelectDocument = useCallback((docId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Open document',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { source: 'documents', documentId: docId },
      action: async () => {
        await getDocument(docId)
        setShowVersions(false)
        setShowComments(false)
      },
    })
  }, [execute, getDocument])

  const handleDeleteDocument = useCallback(async () => {
    if (!docToDelete) return
    return execute({
      type: InteractionType.DELETE,
      label: `Delete document "${docToDelete.name}"`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: 'Document deleted',
      intent: { source: 'documents', documentId: docToDelete.id },
      action: async () => {
        await deleteDocument(docToDelete.id)
        setDeleteConfirmOpen(false)
        setDocToDelete(null)
      },
    })
  }, [deleteDocument, docToDelete, execute])

  const handleSave = useCallback(async () => {
    if (!currentDocument || !editorContent) return
    return execute({
      type: InteractionType.UPDATE,
      label: 'Save document',
      reversibility: Reversibility.SYSTEM_MANAGED,
      successMessage: 'Document saved',
      intent: { source: 'documents', documentId: currentDocument.id },
      action: async () => {
        await updateDocument(currentDocument.id, { content: editorContent })
      },
    })
  }, [currentDocument, editorContent, execute, updateDocument])

  const handleEditorUpdate = useCallback((content) => {
    setEditorContent(content)
    setHasUnsavedChanges(true)
  }, [])

  const handleSelectionChange = useCallback((text) => {
    setSelectedText(text)
  }, [])

  // ---- Version handlers ----

  const handleToggleVersions = useCallback(() => {
    if (!currentDocument) return
    return executeUI('Toggle version history', () => {
      const next = !showVersions
      setShowVersions(next)
      setShowComments(false)
      if (next) fetchVersions(currentDocument.id)
    })
  }, [currentDocument, executeUI, fetchVersions, showVersions])

  const handleSelectVersion = useCallback((version) => {
    setSelectedVersion(version)
  }, [])

  const handleRestoreVersion = useCallback(async (version) => {
    if (!currentDocument || !restoreVersion) return
    return execute({
      type: InteractionType.UPDATE,
      label: `Restore version ${version.version}`,
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: `Restored to version ${version.version}`,
      intent: { source: 'documents', documentId: currentDocument.id, version: version.version },
      action: async () => {
        await restoreVersion(currentDocument.id, version.id)
        await getDocument(currentDocument.id)
      },
    })
  }, [currentDocument, execute, getDocument, restoreVersion])

  // ---- Comment handlers ----

  const handleToggleComments = useCallback(() => {
    if (!currentDocument) return
    return executeUI('Toggle comments', () => {
      const next = !showComments
      setShowComments(next)
      setShowVersions(false)
      if (next) fetchComments(currentDocument.id)
    })
  }, [currentDocument, executeUI, fetchComments, showComments])

  const handleAddComment = useCallback(async ({ text, quoted_text }) => {
    if (!currentDocument || !addComment) return
    return execute({
      type: InteractionType.CREATE,
      label: 'Add comment',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Comment added',
      intent: { source: 'documents', documentId: currentDocument.id },
      action: async () => {
        await addComment(currentDocument.id, { text, quoted_text })
        setSelectedText('')
      },
    })
  }, [addComment, currentDocument, execute])

  const handleResolveComment = useCallback(async (commentId) => {
    if (!currentDocument || !resolveComment) return
    return execute({
      type: InteractionType.UPDATE,
      label: 'Resolve comment',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Comment resolved',
      intent: { source: 'documents', documentId: currentDocument.id, commentId },
      action: async () => {
        await resolveComment(currentDocument.id, commentId)
      },
    })
  }, [currentDocument, execute, resolveComment])

  const handleReplyComment = useCallback(async (commentId, text) => {
    if (!currentDocument || !replyToComment) return
    return execute({
      type: InteractionType.CREATE,
      label: 'Reply to comment',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      successMessage: 'Reply added',
      intent: { source: 'documents', documentId: currentDocument.id, commentId },
      action: async () => {
        await replyToComment(currentDocument.id, commentId, { text })
      },
    })
  }, [currentDocument, execute, replyToComment])

  const handleDeleteComment = useCallback(async (commentId) => {
    if (!currentDocument || !deleteComment) return
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete comment',
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      successMessage: 'Comment deleted',
      intent: { source: 'documents', documentId: currentDocument.id, commentId },
      action: async () => {
        await deleteComment(currentDocument.id, commentId)
      },
    })
  }, [currentDocument, deleteComment, execute])

  const handleHighlightComment = useCallback((comment) => {
    setHighlightedCommentId(comment?.id || null)
  }, [])

  // ---- AI handlers ----

  const handleOpenAiMenu = useCallback((event) => {
    const anchor = event.currentTarget
    return executeUI('Open AI tools', () => setAiMenuAnchor(anchor))
  }, [executeUI])

  const handleCloseAiMenu = useCallback(() => {
    return executeUI('Close AI tools', () => setAiMenuAnchor(null))
  }, [executeUI])

  const handleAIAction = useCallback(async (action) => {
    setAiMenuAnchor(null)
    const text = selectedText || ''
    if (!text || !currentDocument) {
      toast.show('Select some text to use AI tools', 'warning')
      return
    }
    if (action === 'translate') { setTranslateDialogOpen(true); return }
    if (action === 'tone') { setToneDialogOpen(true); return }

    const actionLabels = {
      grammar: 'Check grammar', summarize: 'Summarize text',
      rewrite: 'Rewrite text', expand: 'Expand text',
    }
    return execute({
      type: InteractionType.ANALYZE,
      label: actionLabels[action] || 'Run AI action',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'documents', action, documentId: currentDocument.id },
      action: async () => {
        setAiLoading(true)
        try {
          switch (action) {
            case 'grammar': if (checkGrammar) await checkGrammar(currentDocument.id, text); break
            case 'summarize': if (summarize) await summarize(currentDocument.id, text); break
            case 'rewrite': if (rewrite) await rewrite(currentDocument.id, text); break
            case 'expand': if (expand) await expand(currentDocument.id, text); break
          }
          toast.show(`${actionLabels[action]} complete`, 'success')
        } finally { setAiLoading(false) }
      },
    })
  }, [checkGrammar, currentDocument, execute, expand, rewrite, selectedText, summarize, toast])

  const handleTranslate = useCallback(async () => {
    const text = selectedText || ''
    if (!text || !currentDocument) return
    setTranslateDialogOpen(false)
    return execute({
      type: InteractionType.ANALYZE,
      label: `Translate to ${selectedLanguage}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'documents', action: 'translate', documentId: currentDocument.id, language: selectedLanguage },
      action: async () => {
        setAiLoading(true)
        try {
          if (translate) await translate(currentDocument.id, text, selectedLanguage)
          toast.show(`Translated to ${selectedLanguage}`, 'success')
        } finally { setAiLoading(false) }
      },
    })
  }, [currentDocument, execute, selectedLanguage, selectedText, toast, translate])

  const handleAdjustTone = useCallback(async () => {
    const text = selectedText || ''
    if (!text || !currentDocument) return
    setToneDialogOpen(false)
    const toneLabel = TONE_OPTIONS.find(t => t.value === selectedTone)?.label || selectedTone
    return execute({
      type: InteractionType.ANALYZE,
      label: `Adjust tone to ${toneLabel}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'documents', action: 'tone', documentId: currentDocument.id, tone: selectedTone },
      action: async () => {
        setAiLoading(true)
        try {
          if (adjustTone) await adjustTone(currentDocument.id, text, selectedTone)
          toast.show(`Tone adjusted to ${toneLabel}`, 'success')
        } finally { setAiLoading(false) }
      },
    })
  }, [adjustTone, currentDocument, execute, selectedText, selectedTone, toast])

  const handleImport = useCallback(async (output) => {
    const doc = await createDocument({
      title: output.title || 'Imported',
      content: typeof output.data === 'string' ? output.data : JSON.stringify(output.data),
    })
    if (doc) getDocument(doc.id)
  }, [createDocument, getDocument])

  return {
    // Store data
    documents, currentDocument, versions, comments,
    loading, saving, error, aiResult, clearAiResult, reset,
    templates,
    // UI state
    showDocList, setShowDocList,
    editorContent, selectedText,
    aiLoading, aiMenuAnchor,
    showVersions, setShowVersions,
    showComments, setShowComments,
    selectedVersion, highlightedCommentId,
    // Dialog state
    createDialogOpen, newDocName, setNewDocName,
    selectedTemplateId, setSelectedTemplateId,
    deleteConfirmOpen, setDeleteConfirmOpen,
    docToDelete, setDocToDelete,
    translateDialogOpen, setTranslateDialogOpen,
    toneDialogOpen, setToneDialogOpen,
    selectedLanguage, setSelectedLanguage,
    selectedTone, setSelectedTone,
    // Auto-save
    autoSaveEnabled, lastSaved,
    // Handlers
    handleOpenCreateDialog, handleCloseCreateDialog, handleCreateDocument,
    handleSelectDocument, handleDeleteDocument, handleSave,
    handleEditorUpdate, handleSelectionChange,
    handleToggleVersions, handleSelectVersion, handleRestoreVersion,
    handleToggleComments, handleAddComment, handleResolveComment,
    handleReplyComment, handleDeleteComment, handleHighlightComment,
    handleOpenAiMenu, handleCloseAiMenu, handleAIAction,
    handleTranslate, handleAdjustTone, handleImport,
  }
}
