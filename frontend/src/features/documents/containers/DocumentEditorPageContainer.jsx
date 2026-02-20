/**
 * Document Editor Page Container
 * Rich text editor with TipTap, collaboration, comments, and AI writing features.
 */
import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Stack,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Description as DocIcon,
  Save as SaveIcon,
  History as HistoryIcon,
  Comment as CommentIcon,
  People as CollabIcon,
  Download as DownloadIcon,
  MoreVert as MoreIcon,
  AutoAwesome as AIIcon,
  Spellcheck as GrammarIcon,
  Summarize as SummarizeIcon,
  Edit as RewriteIcon,
  Translate as TranslateIcon,
  Expand as ExpandIcon,
  FormatColorFill as ToneIcon,
  Close as CloseIcon,
  FolderOpen as OpenIcon,
  NoteAdd as NewIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'
import useDocumentStore from '@/stores/documentStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import TemplateSelector from '@/components/common/TemplateSelector'
import TipTapEditor from '../components/TipTapEditor'
import TrackChangesPanel from '../components/TrackChangesPanel'
import CommentsPanel from '../components/CommentsPanel'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(10px)',
  gap: theme.spacing(2),
}))

const EditorArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

const EditorPane = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(3),
  backgroundColor: theme.palette.background.default,
}))

const DocumentsList = styled(Box)(({ theme }) => ({
  width: 300,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.5),
  display: 'flex',
  flexDirection: 'column',
}))

const DocumentsHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}))

const DocumentsContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(1),
}))

const DocumentItem = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isActive',
})(({ theme, isActive }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  cursor: 'pointer',
  border: `1px solid ${isActive ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'transparent'}`,
  backgroundColor: isActive ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50]) : 'transparent',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    borderColor: alpha(theme.palette.divider, 0.3),
  },
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
}))

const EmptyState = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}))

const AIResultCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.spacing(2),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  borderRadius: 8,  // Figma spec: 8px
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DocumentEditorPage() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const { templates } = useSharedData()

  // Cross-page: accept content from other features (Agents, Synthesis, Summary)
  useIncomingTransfer(FeatureKey.DOCUMENTS, {
    [TransferAction.CREATE_FROM]: async (payload) => {
      const doc = await createDocument({
        title: payload.title || 'Imported Document',
        content: typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content),
      })
      if (doc) getDocument(doc.id)
    },
  })

  const {
    documents,
    currentDocument,
    versions,
    comments,
    loading,
    saving,
    error,
    aiResult,
    fetchDocuments,
    createDocument,
    getDocument,
    updateDocument,
    deleteDocument,
    fetchVersions,
    restoreVersion,
    fetchComments,
    addComment,
    resolveComment,
    replyToComment,
    deleteComment,
    checkGrammar,
    summarize,
    rewrite,
    expand,
    translate,
    adjustTone,
    clearAiResult,
    reset,
  } = useDocumentStore()

  // UI State
  const [showDocList, setShowDocList] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newDocName, setNewDocName] = useState('')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')
  const [editorContent, setEditorContent] = useState(null)
  const [aiMenuAnchor, setAiMenuAnchor] = useState(null)
  const [selectedText, setSelectedText] = useState('')
  const [showVersions, setShowVersions] = useState(false)
  const [showComments, setShowComments] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState(null)
  const [highlightedCommentId, setHighlightedCommentId] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [docToDelete, setDocToDelete] = useState(null)

  // AI Tool Settings
  const [translateDialogOpen, setTranslateDialogOpen] = useState(false)
  const [toneDialogOpen, setToneDialogOpen] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('Spanish')
  const [selectedTone, setSelectedTone] = useState('professional')

  // Auto-save
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [lastSaved, setLastSaved] = useState(null)

  // Language and tone options
  const LANGUAGE_OPTIONS = [
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

  const TONE_OPTIONS = [
    { value: 'professional', label: 'Professional', description: 'Formal and business-appropriate' },
    { value: 'casual', label: 'Casual', description: 'Friendly and conversational' },
    { value: 'formal', label: 'Formal', description: 'Very formal and official' },
    { value: 'simplified', label: 'Simplified', description: 'Easy to understand, plain language' },
    { value: 'persuasive', label: 'Persuasive', description: 'Compelling and convincing' },
    { value: 'empathetic', label: 'Empathetic', description: 'Warm and understanding' },
  ]

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
    }, 2000) // Auto-save after 2 seconds of inactivity

    return () => clearTimeout(autoSaveTimer)
  }, [autoSaveEnabled, currentDocument, editorContent, hasUnsavedChanges, saving, updateDocument])

  // ==========================================================================
  // UX Governance helpers
  // ==========================================================================

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

  // ==========================================================================
  // Document handlers
  // ==========================================================================

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
          content: {
            type: 'doc',
            content: [{ type: 'paragraph', content: [] }],
          },
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

  // ==========================================================================
  // Version handlers
  // ==========================================================================

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

  // ==========================================================================
  // Comment handlers
  // ==========================================================================

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

  // ==========================================================================
  // AI handlers
  // ==========================================================================

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

    // For translate and tone, show a dialog to select options first
    if (action === 'translate') {
      setTranslateDialogOpen(true)
      return
    }
    if (action === 'tone') {
      setToneDialogOpen(true)
      return
    }

    const actionLabels = {
      grammar: 'Check grammar',
      summarize: 'Summarize text',
      rewrite: 'Rewrite text',
      expand: 'Expand text',
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
            case 'grammar':
              if (checkGrammar) await checkGrammar(currentDocument.id, text)
              break
            case 'summarize':
              if (summarize) await summarize(currentDocument.id, text)
              break
            case 'rewrite':
              if (rewrite) await rewrite(currentDocument.id, text)
              break
            case 'expand':
              if (expand) await expand(currentDocument.id, text)
              break
          }
          toast.show(`${actionLabels[action]} complete`, 'success')
        } finally {
          setAiLoading(false)
        }
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
        } finally {
          setAiLoading(false)
        }
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
        } finally {
          setAiLoading(false)
        }
      },
    })
  }, [adjustTone, currentDocument, execute, selectedText, selectedTone, toast])

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <PageContainer>
      {/* Toolbar */}
      <Toolbar>
        <Stack direction="row" alignItems="center" spacing={2}>
          <IconButton
            size="small"
            onClick={() => setShowDocList(!showDocList)}
            data-testid="toggle-doc-list"
            aria-label="Toggle documents list"
            sx={{ color: showDocList ? 'text.primary' : 'text.secondary' }}
          >
            <OpenIcon />
          </IconButton>
          <DocIcon sx={{ color: 'text.secondary' }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {currentDocument?.name || 'Documents'}
          </Typography>
          {currentDocument && (
            <>
              <Chip
                size="small"
                label={`v${currentDocument.version || 1}`}
                sx={{ borderRadius: 1 }}
              />
              {saving && (
                <Stack direction="row" alignItems="center" spacing={1}>
                  <CircularProgress size={14} />
                  <Typography variant="caption" color="text.secondary">
                    Saving...
                  </Typography>
                </Stack>
              )}
            </>
          )}
        </Stack>

        <Stack direction="row" spacing={1}>
          {currentDocument ? (
            <>
              <ActionButton
                variant="outlined"
                size="small"
                startIcon={<HistoryIcon />}
                onClick={handleToggleVersions}
                data-testid="doc-history-button"
                sx={{
                  bgcolor: showVersions ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
                }}
              >
                History
              </ActionButton>
              <ActionButton
                variant="outlined"
                size="small"
                startIcon={<CommentIcon />}
                onClick={handleToggleComments}
                data-testid="doc-comments-button"
                sx={{
                  bgcolor: showComments ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
                }}
              >
                Comments {comments.length > 0 && `(${comments.length})`}
              </ActionButton>
              <ActionButton
                variant="outlined"
                size="small"
                startIcon={aiLoading ? <CircularProgress size={16} /> : <AIIcon />}
                onClick={handleOpenAiMenu}
                disabled={aiLoading}
                data-testid="doc-ai-tools-button"
              >
                AI Tools
              </ActionButton>
              <ActionButton
                variant="contained"
                size="small"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={saving}
                data-testid="doc-save-button"
              >
                Save
              </ActionButton>
            </>
          ) : (
            <>
              <ImportFromMenu
                currentFeature={FeatureKey.DOCUMENTS}
                onImport={async (output) => {
                  const doc = await createDocument({
                    title: output.title || 'Imported',
                    content: typeof output.data === 'string' ? output.data : JSON.stringify(output.data),
                  })
                  if (doc) getDocument(doc.id)
                }}
                size="small"
              />
              <ActionButton
                variant="contained"
                size="small"
                startIcon={<AddIcon />}
                onClick={handleOpenCreateDialog}
                data-testid="doc-new-button"
              >
                New Document
              </ActionButton>
            </>
          )}
        </Stack>
      </Toolbar>

      {/* Editor Area */}
      <EditorArea>
        {/* Documents List Sidebar */}
        {showDocList && (
          <DocumentsList>
            <DocumentsHeader>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Documents
              </Typography>
              <Tooltip title="New Document">
                <IconButton size="small" onClick={handleOpenCreateDialog} data-testid="doc-sidebar-new-button" aria-label="New Document">
                  <NewIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </DocumentsHeader>
            <DocumentsContent>
              {loading && documents.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : documents.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No documents yet
                  </Typography>
                </Box>
              ) : (
                documents.map((doc) => (
                  <DocumentItem
                    key={doc.id}
                    elevation={0}
                    isActive={currentDocument?.id === doc.id}
                    onClick={() => handleSelectDocument(doc.id)}
                    data-testid={`doc-item-${doc.id}`}
                  >
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <DocIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {doc.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(doc.updated_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDocToDelete(doc)
                          setDeleteConfirmOpen(true)
                        }}
                        data-testid={`doc-delete-${doc.id}`}
                        aria-label={`Delete ${doc.name}`}
                        sx={{ opacity: 0, transition: 'opacity 0.15s ease', '.MuiPaper-root:hover &': { opacity: 0.5 }, '&:hover': { opacity: '1 !important' } }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Stack>
                  </DocumentItem>
                ))
              )}
            </DocumentsContent>
          </DocumentsList>
        )}

        {/* Main Editor */}
        {currentDocument ? (
          <EditorPane>
            <TipTapEditor
              content={editorContent}
              onUpdate={handleEditorUpdate}
              onSelectionChange={handleSelectionChange}
              placeholder="Start writing your document..."
            />

            {/* AI Result */}
            {aiResult && (
              <AIResultCard elevation={0}>
                <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <AIIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      AI Result
                    </Typography>
                  </Stack>
                  <IconButton size="small" onClick={() => clearAiResult && clearAiResult()}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Stack>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                  {aiResult.result_text}
                </Typography>
                {aiResult.suggestions?.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                      Suggestions:
                    </Typography>
                    {aiResult.suggestions.map((s, i) => (
                      <Typography key={i} variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                        • {s}
                      </Typography>
                    ))}
                  </Box>
                )}
                <Stack direction="row" spacing={1} mt={2}>
                  <ActionButton
                    size="small"
                    variant="outlined"
                    startIcon={<CopyIcon />}
                    onClick={() => {
                      navigator.clipboard.writeText(aiResult.result_text)
                        .then(() => toast.show('Copied to clipboard', 'success'))
                        .catch(() => toast.show('Failed to copy to clipboard', 'error'))
                    }}
                  >
                    Copy
                  </ActionButton>
                </Stack>
              </AIResultCard>
            )}
          </EditorPane>
        ) : (
          <EmptyState>
            <DocIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              No Document Selected
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Create a new document or select one from the list.
            </Typography>
            <ActionButton
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleOpenCreateDialog}
            >
              Create Document
            </ActionButton>
          </EmptyState>
        )}

        {/* Sidebars */}
        {showVersions && currentDocument && (
          <TrackChangesPanel
            versions={versions}
            loading={loading}
            selectedVersion={selectedVersion}
            onSelectVersion={handleSelectVersion}
            onRestoreVersion={handleRestoreVersion}
            onClose={() => setShowVersions(false)}
          />
        )}

        {showComments && currentDocument && (
          <CommentsPanel
            comments={comments}
            loading={loading}
            highlightedCommentId={highlightedCommentId}
            selectedText={selectedText}
            onAddComment={handleAddComment}
            onResolveComment={handleResolveComment}
            onReplyComment={handleReplyComment}
            onDeleteComment={handleDeleteComment}
            onHighlightComment={handleHighlightComment}
            onClose={() => setShowComments(false)}
          />
        )}
      </EditorArea>

      {/* AI Tools Menu */}
      <Menu
        anchorEl={aiMenuAnchor}
        open={Boolean(aiMenuAnchor)}
        onClose={handleCloseAiMenu}
        PaperProps={{
          sx: {
            borderRadius: 1,  // Figma spec: 8px
            minWidth: 200,
          },
        }}
      >
        <MenuItem onClick={() => handleAIAction('grammar')} data-testid="ai-grammar">
          <ListItemIcon><GrammarIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Check Grammar</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('summarize')} data-testid="ai-summarize">
          <ListItemIcon><SummarizeIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Summarize</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('rewrite')} data-testid="ai-rewrite">
          <ListItemIcon><RewriteIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Rewrite</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('expand')} data-testid="ai-expand">
          <ListItemIcon><ExpandIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Expand</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('translate')} data-testid="ai-translate">
          <ListItemIcon><TranslateIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Translate</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleAIAction('tone')} data-testid="ai-tone">
          <ListItemIcon><ToneIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Adjust Tone</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create Document Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={handleCloseCreateDialog}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Create New Document</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Document Name"
            value={newDocName}
            onChange={(e) => setNewDocName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreateDocument()}
            sx={{ mt: 2 }}
          />
          <TemplateSelector
            value={selectedTemplateId}
            onChange={setSelectedTemplateId}
            label="From Template (Optional)"
            size="small"
            showAll
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseCreateDialog} data-testid="doc-create-cancel">Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateDocument}
            disabled={!newDocName.trim() || loading}
            data-testid="doc-create-submit"
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Delete Document</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{docToDelete?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDeleteConfirmOpen(false)} data-testid="doc-delete-cancel">Cancel</Button>
          <Button
            variant="contained"
            sx={{ color: 'text.secondary' }}
            onClick={handleDeleteDocument}
            data-testid="doc-delete-confirm"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Translate Dialog */}
      <Dialog
        open={translateDialogOpen}
        onClose={() => setTranslateDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Translate Text</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select the language you want to translate the selected text into.
          </Typography>
          <TextField
            select
            fullWidth
            label="Target Language"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
          >
            {LANGUAGE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setTranslateDialogOpen(false)} data-testid="translate-cancel">Cancel</Button>
          <Button
            variant="contained"
            onClick={handleTranslate}
            startIcon={<TranslateIcon />}
            data-testid="translate-submit"
          >
            Translate
          </Button>
        </DialogActions>
      </Dialog>

      {/* Tone Dialog */}
      <Dialog
        open={toneDialogOpen}
        onClose={() => setToneDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { borderRadius: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Adjust Tone</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select the tone you want to apply to the selected text.
          </Typography>
          <TextField
            select
            fullWidth
            label="Tone"
            value={selectedTone}
            onChange={(e) => setSelectedTone(e.target.value)}
          >
            {TONE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                <Box>
                  <Typography variant="body2">{option.label}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {option.description}
                  </Typography>
                </Box>
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setToneDialogOpen(false)} data-testid="tone-cancel">Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAdjustTone}
            startIcon={<ToneIcon />}
            data-testid="tone-submit"
          >
            Apply Tone
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error Alert */}
      {error && (
        <Alert
          severity="error"
          onClose={() => reset()}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}

      {/* Auto-save indicator */}
      {autoSaveEnabled && lastSaved && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            position: 'fixed',
            bottom: 16,
            left: 16,
            opacity: 0.7,
          }}
        >
          Auto-saved {lastSaved.toLocaleTimeString()}
        </Typography>
      )}
    </PageContainer>
  )
}
