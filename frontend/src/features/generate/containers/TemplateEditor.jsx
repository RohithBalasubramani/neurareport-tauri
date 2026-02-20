import Grid from '@mui/material/Grid2'
import {
  Box,
  Stack,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Divider,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Breadcrumbs,
  Link,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  IconButton,
  Collapse,
} from '@mui/material'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CodeIcon from '@mui/icons-material/Code'
import ChatIcon from '@mui/icons-material/Chat'
import SaveIcon from '@mui/icons-material/Save'
import UndoIcon from '@mui/icons-material/Undo'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import FullscreenIcon from '@mui/icons-material/Fullscreen'
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import CloseIcon from '@mui/icons-material/Close'
import { forwardRef, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useLocation, Link as RouterLink, UNSAFE_NavigationContext } from 'react-router-dom'

import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import Surface from '@/components/layout/Surface.jsx'
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

// New components
import TemplateChatEditor from './TemplateChatEditor.jsx'
import EnhancedDiffViewer from '../components/EnhancedDiffViewer.jsx'
import EditHistoryTimeline from '../components/EditHistoryTimeline.jsx'
import EditorSkeleton from '../components/EditorSkeleton.jsx'
import KeyboardShortcutsPanel from '../components/KeyboardShortcutsPanel.jsx'
import DraftRecoveryBanner, { AutoSaveIndicator } from '../components/DraftRecoveryBanner.jsx'
import ConfirmModal from '@/components/Modal/ConfirmModal'
import AiUsageNotice from '@/components/ai/AiUsageNotice.jsx'

// Hooks
import { useEditorKeyboardShortcuts, getShortcutDisplay } from '../hooks/useEditorKeyboardShortcuts.js'
import { useEditorDraft } from '../hooks/useEditorDraft.js'

const surfaceStackSx = {
  gap: { xs: 2, md: 2.5 },
}

const FixedTextarea = forwardRef(function FixedTextarea(props, ref) {
  return <textarea {...props} ref={ref} />
})

export default function TemplateEditor() {
  const { templateId } = useParams()
  const navigate = useNavigateInteraction()
  const location = useLocation()
  const toast = useToast()
  const { execute } = useInteraction()
  const templates = useAppStore((state) => state.templates)
  const updateTemplateEntry = useAppStore((state) => state.updateTemplate)

  // Track where user came from for proper back navigation
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
  const [editMode, setEditMode] = useState('manual') // 'manual' | 'chat'
  const [diffOpen, setDiffOpen] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [previewFullscreen, setPreviewFullscreen] = useState(false)
  const [modeSwitchConfirm, setModeSwitchConfirm] = useState({ open: false, nextMode: null })

  const dirty = html !== initialHtml
  const hasInstructions = (instructions || '').trim().length > 0

  // Block in-app navigation when there are unsaved changes (BrowserRouter-compatible)
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

  // Auto-save when content changes
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

  return (
    <>
      {/* Breadcrumb Navigation */}
      <Box sx={{ mb: 2 }}>
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          aria-label="breadcrumb"
        >
          <Link
            component={RouterLink}
            to={referrer}
            underline="hover"
            color="text.secondary"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            {breadcrumbLabel}
          </Link>
            <Typography color="text.primary" fontWeight={600}>
              Edit Design
            </Typography>
        </Breadcrumbs>
      </Box>

      <Surface sx={surfaceStackSx}>
        {/* Header */}
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1.5} flexWrap="wrap">
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
              <Typography variant="h5" fontWeight={600}>
                {template?.name || 'Design Editor'}
              </Typography>
              <AutoSaveIndicator lastSaved={lastSaved} dirty={dirty} />
            </Stack>
            <Typography variant="body2" color="text.secondary">
              {templateId ? `ID: ${templateId}` : 'No template selected'}
            </Typography>
            {lastEditInfo && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                Last edit: {lastEditInfo.chipLabel}
              </Typography>
            )}
            {diffSummary && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                Recent change: {diffSummary}
              </Typography>
            )}
          </Box>

          <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap">
            {/* Edit mode toggle */}
            <ToggleButtonGroup
              value={editMode}
              exclusive
              onChange={handleEditModeChange}
              size="small"
              aria-label="Edit mode"
            >
              <ToggleButton value="manual" aria-label="Manual edit mode">
                <Tooltip title="Code Editor - Edit HTML directly with AI assistance">
                  <Stack direction="row" spacing={0.5} alignItems="center">
                    <CodeIcon fontSize="small" />
                    <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                      Code
                    </Typography>
                  </Stack>
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="chat" aria-label="Chat edit mode">
                <Tooltip title="Chat Editor - Conversational AI editing">
                  <Stack direction="row" spacing={0.5} alignItems="center">
                    <ChatIcon fontSize="small" />
                    <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                      Chat
                    </Typography>
                  </Stack>
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>

            {/* Keyboard shortcuts button */}
            <Tooltip title="Keyboard shortcuts">
              <IconButton size="small" onClick={() => setShortcutsOpen(true)} aria-label="Keyboard shortcuts">
                <KeyboardIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Button
              variant="outlined"
              onClick={handleBack}
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Back to {breadcrumbLabel}
            </Button>
          </Stack>
        </Stack>

        <AiUsageNotice
          dense
          title="AI editing"
          description="AI edits apply to this report design. Review changes before saving."
          chips={[
            { label: 'Source: Design + instructions', color: 'info', variant: 'outlined' },
            { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
            { label: 'Undo available', color: 'success', variant: 'outlined' },
          ]}
          sx={{ mb: 1 }}
        />

        {/* Draft recovery banner */}
        <DraftRecoveryBanner
          show={hasDraft && !loading && editMode === 'manual'}
          draftData={draftData}
          onRestore={handleRestoreDraft}
          onDiscard={discardDraft}
        />

        {/* Error display — show not-found with back link when template fails to load */}
        {error && (
          <Alert
            severity="error"
            action={
              <Button color="inherit" size="small" component={RouterLink} to={referrer}>
                Back
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {/* Main content — or not-found state when template fails to load */}
        {!loading && error && !html ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Template Not Found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              The template &ldquo;{templateId}&rdquo; could not be loaded. It may have been deleted or the ID is invalid.
            </Typography>
            <Button variant="contained" component={RouterLink} to="/templates">
              Go to Templates
            </Button>
          </Box>
        ) : loading ? (
          <>
            <Divider />
            <EditorSkeleton mode={editMode} />
          </>
        ) : editMode === 'chat' ? (
          <>
            <Divider />
            <Grid container spacing={2.5} sx={{ alignItems: 'stretch' }}>
              {/* Preview Panel */}
              <Grid size={{ xs: 12, md: previewFullscreen ? 12 : 5 }} sx={{ minWidth: 0 }}>
                <Stack spacing={1.5} sx={{ height: '100%' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle1">Preview</Typography>
                    <Tooltip title={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
                      <IconButton size="small" onClick={() => setPreviewFullscreen(!previewFullscreen)} aria-label={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
                        {previewFullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>
                  </Stack>
                  {previewUrl ? (
                    <Box
                      sx={{
                        borderRadius: 1.5,
                        border: '1px solid',
                        borderColor: 'divider',
                        bgcolor: 'background.paper',
                        p: 1.5,
                        minHeight: previewFullscreen ? 600 : 400,
                        transition: 'min-height 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                      }}
                    >
                      <ScaledIframePreview
                        src={previewUrl}
                        title={`Template preview for ${templateId}`}
                        fit="contain"
                        pageShadow
                        frameAspectRatio="210 / 297"
                        clampToParentHeight
                      />
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        borderRadius: 1.5,
                        border: '1px dashed',
                        borderColor: 'divider',
                        bgcolor: 'background.default',
                        p: 2,
                        minHeight: 400,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No HTML loaded yet.
                      </Typography>
                    </Box>
                  )}
                </Stack>
              </Grid>

              {/* Chat Editor */}
              {!previewFullscreen && (
                <Grid size={{ xs: 12, md: 7 }} sx={{ minWidth: 0 }}>
                  <Box sx={{ height: 600 }}>
                    <TemplateChatEditor
                      templateId={templateId}
                      templateName={template?.name || 'Template'}
                      currentHtml={html}
                      onHtmlUpdate={handleChatHtmlUpdate}
                      onApplySuccess={handleChatApplySuccess}
                    />
                  </Box>
                </Grid>
              )}
            </Grid>
          </>
        ) : (
          <>
            <Divider />
            <Grid container spacing={2.5} sx={{ alignItems: 'stretch' }}>
              {/* Preview Panel */}
              <Grid size={{ xs: 12, md: previewFullscreen ? 12 : 6 }} sx={{ minWidth: 0 }}>
                <Stack spacing={1.5} sx={{ height: '100%' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="subtitle1">Preview</Typography>
                    <Tooltip title={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
                      <IconButton size="small" onClick={() => setPreviewFullscreen(!previewFullscreen)} aria-label={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
                        {previewFullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
                      </IconButton>
                    </Tooltip>
                  </Stack>
                  {previewUrl ? (
                    <Box
                      sx={{
                        borderRadius: 1.5,
                        border: '1px solid',
                        borderColor: 'divider',
                        bgcolor: 'background.paper',
                        p: 1.5,
                        minHeight: previewFullscreen ? 500 : 200,
                        flex: 1,
                        transition: 'min-height 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                      }}
                    >
                      <ScaledIframePreview
                        src={previewUrl}
                        title={`Template preview for ${templateId}`}
                        fit="contain"
                        pageShadow
                        frameAspectRatio="210 / 297"
                        clampToParentHeight
                      />
                    </Box>
                  ) : (
                    <Box
                      sx={{
                        borderRadius: 1.5,
                        border: '1px dashed',
                        borderColor: 'divider',
                        bgcolor: 'background.default',
                        p: 2,
                        minHeight: 200,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        No HTML loaded yet.
                      </Typography>
                    </Box>
                  )}
                </Stack>
              </Grid>

              {/* Editor Panel */}
              {!previewFullscreen && (
                <Grid size={{ xs: 12, md: 6 }} sx={{ minWidth: 0 }}>
                  <Stack spacing={1.5} sx={{ height: '100%' }}>
                    <Typography variant="subtitle1">HTML &amp; AI Guidance</Typography>

                    {/* HTML Editor */}
                    <TextField
                      label="Design HTML"
                      value={html}
                      onChange={(e) => setHtml(e.target.value)}
                      inputProps={{ 'aria-label': 'Template HTML' }}
                      multiline
                      minRows={10}
                      maxRows={24}
                      fullWidth
                      variant="outlined"
                      size="small"
                      error={dirty}
                      helperText={
                        dirty
                          ? `Unsaved changes. Press ${getShortcutDisplay('save')} to save.`
                          : 'HTML is in sync with the saved template.'
                      }
                      InputLabelProps={{ shrink: true }}
                      sx={{
                        '& .MuiInputBase-input': {
                          fontFamily: 'monospace',
                          fontSize: '14px',
                        },
                      }}
                    />

                    {/* AI Instructions */}
                    <TextField
                      label="AI Instructions"
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      multiline
                      rows={3}
                      InputProps={{ inputComponent: FixedTextarea }}
                      fullWidth
                      variant="outlined"
                      size="small"
                      placeholder="Describe how the template should change. AI will preserve tokens and structure unless you ask otherwise."
                      helperText={
                        hasInstructions
                          ? `Press ${getShortcutDisplay('applyAi')} or click Apply to run AI.`
                          : 'Enter instructions to enable AI editing.'
                      }
                      InputLabelProps={{ shrink: true }}
                    />

                    {/* Action Buttons */}
                    <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        disabled={saving || loading || !dirty || aiBusy}
                        startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
                        sx={{ minWidth: 110 }}
                      >
                        {saving ? 'Saving...' : 'Save'}
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={handleApplyAi}
                        disabled={aiBusy || loading || !hasInstructions}
                        startIcon={aiBusy ? <CircularProgress size={16} /> : <AutoFixHighIcon />}
                        sx={{ minWidth: 130, color: 'text.secondary', borderColor: 'divider' }}
                      >
                        {aiBusy ? 'Applying...' : 'Apply AI'}
                      </Button>
                      <Button
                        variant="text"
                        color="inherit"
                        onClick={handleUndo}
                        disabled={undoBusy || loading}
                        startIcon={undoBusy ? <CircularProgress size={16} /> : <UndoIcon />}
                      >
                        {undoBusy ? 'Undoing...' : 'Undo'}
                      </Button>
                      <Button
                        variant="text"
                        onClick={() => setDiffOpen(true)}
                        disabled={loading || !dirty}
                        startIcon={<CompareArrowsIcon />}
                        sx={{ color: 'text.secondary' }}
                      >
                        View Diff
                      </Button>
                    </Stack>

                    <Typography variant="caption" color="text.secondary">
                      AI edits are generated and may need review before use in production runs.
                    </Typography>

                    {/* Keyboard shortcuts hint */}
                    <KeyboardShortcutsPanel compact />

                    {/* Edit History */}
                    <EditHistoryTimeline history={history} maxVisible={5} />
                  </Stack>
                </Grid>
              )}
            </Grid>
          </>
        )}
      </Surface>

      {/* Enhanced Diff Dialog */}
      <Dialog
        open={diffOpen}
        onClose={() => setDiffOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '80vh', maxHeight: 800 },
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6">HTML Changes</Typography>
            <Typography variant="caption" color="text.secondary">
              Compare saved version with current edits
            </Typography>
          </Box>
          <Tooltip title="Close">
            <IconButton onClick={() => setDiffOpen(false)} aria-label="Close dialog">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
          <EnhancedDiffViewer beforeText={initialHtml} afterText={html} contextLines={3} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiffOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              handleSave()
              setDiffOpen(false)
            }}
            disabled={saving || !dirty}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Keyboard Shortcuts Dialog */}
      <Dialog
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Keyboard Shortcuts
          <Tooltip title="Close">
            <IconButton onClick={() => setShortcutsOpen(false)} aria-label="Close dialog">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </DialogTitle>
        <DialogContent>
          <KeyboardShortcutsPanel />
        </DialogContent>
      </Dialog>

      <ConfirmModal
        open={modeSwitchConfirm.open}
        onClose={() => setModeSwitchConfirm({ open: false, nextMode: null })}
        onConfirm={() => {
          if (dirty) {
            saveDraft(html, instructions)
          }
          setModeSwitchConfirm({ open: false, nextMode: null })
          setEditMode(modeSwitchConfirm.nextMode || 'chat')
          toast.show('Draft saved. Your current edits are still available in chat and manual modes.', 'info')
        }}
        title="Switch to Chat Mode"
        message="Switching to chat mode keeps your current edits and saves a draft for manual mode."
        confirmLabel="Switch"
        severity="warning"
      />
    </>
  )
}
