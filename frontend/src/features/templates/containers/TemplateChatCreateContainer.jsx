import { useState, useCallback, useEffect, useRef } from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Breadcrumbs,
  Link,
  Alert,
  Paper,
  Chip,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import SaveIcon from '@mui/icons-material/Save'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import CloseIcon from '@mui/icons-material/Close'
import { Link as RouterLink, useSearchParams } from 'react-router-dom'

import Surface from '@/components/layout/Surface.jsx'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { useToast } from '@/components/ToastProvider.jsx'
import {
  useInteraction,
  InteractionType,
  Reversibility,
  useNavigateInteraction,
} from '@/components/ux/governance'
import { useAppStore } from '@/stores'
import { useTemplateChatStore } from '@/stores/templateChatStore'
import { chatTemplateCreate, createTemplateFromChat, mappingPreview, mappingApprove } from '@/api/client'
import TemplateChatEditor from '@/features/generate/containers/TemplateChatEditor.jsx'
import { neutral } from '@/app/theme'

const MAX_PDF_SIZE_MB = 10

const SESSION_KEY = '__chat_create__'

export default function TemplateChatCreateContainer() {
  const navigate = useNavigateInteraction()
  const toast = useToast()
  const { execute } = useInteraction()
  const addTemplate = useAppStore((s) => s.addTemplate)
  const setTemplateId = useAppStore((s) => s.setTemplateId)
  const lastUsedConnectionId = useAppStore((s) => s.lastUsed?.connectionId || null)
  const activeConnection = useAppStore((s) => s.activeConnection)
  const setActiveConnectionId = useAppStore((s) => s.setActiveConnectionId)
  const deleteSession = useTemplateChatStore((s) => s.deleteSession)
  const [searchParams] = useSearchParams()
  const fromWizard = searchParams.get('from') === 'wizard'
  const wizardConnectionId = searchParams.get('connectionId') || null
  const [selectedConnectionId, setSelectedConnectionId] = useState(
    wizardConnectionId || lastUsedConnectionId || activeConnection?.id || ''
  )

  const addAssistantMessage = useTemplateChatStore((s) => s.addAssistantMessage)

  const [currentHtml, setCurrentHtml] = useState('')
  const [previewUrl, setPreviewUrl] = useState(null)
  const [nameDialogOpen, setNameDialogOpen] = useState(false)
  const [templateName, setTemplateName] = useState('')
  const [creating, setCreating] = useState(false)
  const [samplePdf, setSamplePdf] = useState(null) // { file: File, name, size }
  const [templateKind, setTemplateKind] = useState('pdf')
  const fileInputRef = useRef(null)

  // Mapping phase state — shown after template save
  const [savedTemplateId, setSavedTemplateId] = useState(null)
  const [savedTemplateKind, setSavedTemplateKind] = useState('pdf')
  const [savedTemplateName, setSavedTemplateName] = useState('')
  const [mappingPreviewData, setMappingPreviewData] = useState(null)
  const [mappingApproving, setMappingApproving] = useState(false)

  const handleFileSelect = useCallback((file) => {
    if (!file) return
    const pdfTypes = ['application/pdf']
    const excelTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
    ]
    const allowedTypes = templateKind === 'excel' ? [...pdfTypes, ...excelTypes] : pdfTypes
    const isExcelExt = /\.(xlsx|xls)$/i.test(file.name)
    if (!allowedTypes.includes(file.type) && !(templateKind === 'excel' && isExcelExt)) {
      toast.show(templateKind === 'excel' ? 'Please upload a PDF or Excel file.' : 'Please upload a PDF file.', 'warning')
      return
    }
    if (file.size > MAX_PDF_SIZE_MB * 1024 * 1024) {
      toast.show(`File too large. Maximum size is ${MAX_PDF_SIZE_MB}MB.`, 'warning')
      return
    }
    setSamplePdf({ file, name: file.name, size: file.size })
    toast.show(`Sample file "${file.name}" attached. The AI will use this as a visual reference.`, 'info')
  }, [toast, templateKind])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const file = e.dataTransfer?.files?.[0]
    handleFileSelect(file)
  }, [handleFileSelect])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
  }, [])

  const handleRemovePdf = useCallback(() => {
    setSamplePdf(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [])

  // Update preview when HTML changes
  useEffect(() => {
    if (!currentHtml) {
      setPreviewUrl(null)
      return
    }
    const blob = new Blob([currentHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [currentHtml])

  // Clean up session on unmount
  useEffect(() => {
    return () => {
      // Don't clean up — let the user resume if they navigate back
    }
  }, [])

  const handleHtmlUpdate = useCallback((html) => {
    setCurrentHtml(html)
  }, [])

  const handleApplySuccess = useCallback((result) => {
    // In create mode, "apply" just updates local state (nothing persisted yet)
    if (result?.updated_html) {
      setCurrentHtml(result.updated_html)
    }
  }, [])

  const handleBack = useCallback(async () => {
    const backTo = fromWizard ? '/setup?step=template' : '/templates'
    await navigate(backTo, {
      interaction: {
        type: InteractionType.NAVIGATE,
        label: fromWizard ? 'Back to wizard' : 'Back to templates',
        reversibility: Reversibility.FULLY_REVERSIBLE,
      },
    })
  }, [navigate, fromWizard])

  const handleOpenNameDialog = useCallback(() => {
    setNameDialogOpen(true)
  }, [])

  const handleCloseNameDialog = useCallback(() => {
    setNameDialogOpen(false)
  }, [])

  const handleCreateTemplate = useCallback(async () => {
    const name = templateName.trim()
    if (!name) {
      toast.show('Please enter a template name.', 'warning')
      return
    }
    if (!currentHtml) {
      toast.show('No template HTML to save. Continue the conversation to generate a template first.', 'warning')
      return
    }

    await execute({
      type: InteractionType.CREATE,
      label: 'Create template from chat',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        action: 'create_template_from_chat',
        name,
      },
      action: async () => {
        setCreating(true)
        try {
          const result = await createTemplateFromChat(name, currentHtml, templateKind)
          const templateId = result?.template_id
          const kind = result?.kind || 'pdf'

          // Add to store and set as active template
          if (templateId) {
            addTemplate({
              id: templateId,
              name,
              kind,
              status: 'draft',
              artifacts: {},
              tags: [],
            })
            setTemplateId(templateId)
          }

          setNameDialogOpen(false)

          // Run mapping preview and show in chat for user review
          const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
          if (templateId && connId) {
            // Save template details for mapping phase
            setSavedTemplateId(templateId)
            setSavedTemplateKind(kind)
            setSavedTemplateName(name)

            toast.show(`Template "${name}" saved! Fetching data mapping suggestions...`, 'info')
            addAssistantMessage(
              SESSION_KEY,
              `Template "${name}" has been saved successfully! Now let's configure how your template fields map to your database columns. Fetching mapping suggestions...`
            )

            try {
              const preview = await mappingPreview(templateId, connId, { kind })
              const mapping = preview?.mapping || preview?.auto_mapping || {}

              if (Object.keys(mapping).length > 0) {
                // Show the mapping review panel in the chat
                setMappingPreviewData(preview)
                addAssistantMessage(
                  SESSION_KEY,
                  `I've auto-mapped ${Object.keys(mapping).length} template fields to your database columns. Review the mapping below — you can click any value to change it, or type in the chat to discuss changes.`
                )
              } else {
                toast.show(`Template "${name}" saved. No auto-mapping available — you can configure mapping later.`, 'info')
                addAssistantMessage(
                  SESSION_KEY,
                  `Template saved, but I couldn't generate auto-mapping suggestions. You can configure mapping manually from the template editor.`
                )
                // Navigate away since no mapping to review
                navigateToTemplate(templateId, name, kind)
              }
            } catch (mapErr) {
              console.warn('Mapping preview failed:', mapErr)
              toast.show(`Template "${name}" saved. Mapping preview failed — you can map manually later.`, 'warning')
              addAssistantMessage(
                SESSION_KEY,
                `Template saved! Auto-mapping encountered an issue, but you can configure it from the template editor.`
              )
              navigateToTemplate(templateId, name, kind)
            }
          } else {
            toast.show(`Template "${name}" created successfully.`, 'success')
            addAssistantMessage(
              SESSION_KEY,
              `Template "${name}" has been saved! Connect a database to enable field mapping.`
            )
            // No connection — navigate away
            deleteSession(SESSION_KEY)
            navigateToTemplate(templateId, name, kind)
          }
        } catch (err) {
          toast.show(String(err.message || err), 'error')
          throw err
        } finally {
          setCreating(false)
        }
      },
    })
  }, [templateName, currentHtml, execute, addTemplate, setTemplateId, deleteSession, toast, navigate, fromWizard, wizardConnectionId, lastUsedConnectionId, addAssistantMessage])

  // Navigate to template editor (after save or after mapping)
  const navigateToTemplate = useCallback(async (templateId, name, kind) => {
    deleteSession(SESSION_KEY)
    if (fromWizard) {
      try {
        const wizardRaw = sessionStorage.getItem('neurareport_wizard_state')
        const wizardData = wizardRaw ? JSON.parse(wizardRaw) : {}
        wizardData.templateId = templateId
        wizardData.templateKind = kind
        wizardData.templateName = name
        sessionStorage.setItem('neurareport_wizard_state', JSON.stringify(wizardData))
      } catch (_) { /* ignore storage errors */ }

      await navigate('/setup?step=mapping', {
        interaction: {
          type: InteractionType.NAVIGATE,
          label: 'Continue to mapping',
          reversibility: Reversibility.FULLY_REVERSIBLE,
        },
      })
    } else {
      await navigate(`/templates/${templateId}/edit`, {
        state: { from: '/templates', editMode: 'chat' },
        interaction: {
          type: InteractionType.NAVIGATE,
          label: 'Open new template editor',
          reversibility: Reversibility.FULLY_REVERSIBLE,
        },
      })
    }
  }, [deleteSession, fromWizard, navigate])

  // Handle mapping approval from the chat panel
  const handleMappingApprove = useCallback(async (finalMapping) => {
    if (!savedTemplateId) return
    setMappingApproving(true)
    try {
      const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
      addAssistantMessage(SESSION_KEY, 'Building contract and generator assets... This may take a moment.')
      toast.show('Approving mapping and building contract...', 'info')
      await mappingApprove(savedTemplateId, finalMapping, {
        connectionId: connId,
        kind: savedTemplateKind,
      })
      toast.show(`Template "${savedTemplateName}" is report-ready!`, 'success')
      addAssistantMessage(SESSION_KEY, `Mapping approved and contract built! Template "${savedTemplateName}" is now report-ready. Redirecting...`)
      // Short delay so user sees the success message
      setTimeout(() => {
        navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
      }, 1500)
    } catch (err) {
      console.error('Mapping approve failed:', err)
      toast.show('Mapping approval failed. You can retry or map later from the editor.', 'error')
      addAssistantMessage(SESSION_KEY, `Mapping approval encountered an error: ${err.message || err}. You can try again or skip to map later.`)
    } finally {
      setMappingApproving(false)
    }
  }, [savedTemplateId, savedTemplateKind, savedTemplateName, wizardConnectionId, lastUsedConnectionId, toast, addAssistantMessage, navigateToTemplate])

  // Handle "Skip — Map Later"
  const handleMappingSkip = useCallback(() => {
    if (!savedTemplateId) return
    toast.show(`Template "${savedTemplateName}" saved. You can configure mapping from the editor.`, 'info')
    navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
  }, [savedTemplateId, savedTemplateName, savedTemplateKind, toast, navigateToTemplate])

  // Handle "Queue & Continue" — fire-and-forget the approval and navigate away
  const handleMappingQueue = useCallback(() => {
    if (!savedTemplateId) return
    const connId = selectedConnectionId || wizardConnectionId || lastUsedConnectionId
    // Fire the approval in the background — don't await
    mappingApprove(savedTemplateId, mappingPreviewData?.mapping || {}, {
      connectionId: connId,
      kind: savedTemplateKind,
    }).then(() => {
      // Silently succeeds in background
    }).catch((err) => {
      console.warn('Background mapping approval failed:', err)
    })
    toast.show(`Mapping approval queued for "${savedTemplateName}". You can check progress from the template editor.`, 'info')
    navigateToTemplate(savedTemplateId, savedTemplateName, savedTemplateKind)
  }, [savedTemplateId, savedTemplateName, savedTemplateKind, wizardConnectionId, lastUsedConnectionId, mappingPreviewData, toast, navigateToTemplate])

  // Wrap the chatApi to match (messages, html) signature, passing sample PDF and kind
  const chatApi = useCallback((messages, html) => {
    return chatTemplateCreate(messages, html, samplePdf?.file || null, templateKind)
  }, [samplePdf, templateKind])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', flex: '1 1 0', minHeight: 0, overflow: 'hidden' }}>
      {/* Breadcrumb */}
      <Box sx={{ mb: 1, flexShrink: 0 }}>
        <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} aria-label="breadcrumb">
          <Link
            component={RouterLink}
            to="/templates"
            underline="hover"
            color="text.secondary"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            Templates
          </Link>
          <Typography color="text.primary" fontWeight={600}>
            Create with AI
          </Typography>
        </Breadcrumbs>
      </Box>

      <Surface sx={{ gap: { xs: 1.5, md: 2 }, flex: '1 1 0', minHeight: 0, overflow: 'hidden' }}>
        {/* Header */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1.5} sx={{ flexShrink: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
            <AutoAwesomeIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
            <Typography variant="h6" fontWeight={600}>
              Create Template with AI
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1.5} alignItems="center">
            <ConnectionSelector
              value={selectedConnectionId}
              onChange={(connId) => {
                setSelectedConnectionId(connId)
                setActiveConnectionId(connId)
              }}
              label="Data Source"
              size="small"
              fullWidth={false}
              sx={{ minWidth: 200 }}
            />
            <Button
              variant="contained"
              onClick={handleOpenNameDialog}
              disabled={!currentHtml}
              startIcon={<SaveIcon />}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                bgcolor: neutral[900],
                '&:hover': { bgcolor: neutral[700] },
                '&.Mui-disabled': { bgcolor: neutral[300], color: neutral[500] },
              }}
            >
              Save Template
            </Button>
            <Button
              variant="outlined"
              onClick={handleBack}
              startIcon={<ArrowBackIcon />}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Back
            </Button>
          </Stack>
        </Stack>

        {/* Sample PDF Upload — compact */}
        {samplePdf ? (
          <Paper
            variant="outlined"
            sx={{
              px: 1.5, py: 0.75,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              borderColor: 'primary.main',
              bgcolor: 'primary.50',
              flexShrink: 0,
            }}
          >
            <PictureAsPdfIcon sx={{ color: 'error.main', fontSize: 20 }} />
            <Typography variant="body2" fontWeight={600} noWrap sx={{ flex: 1, minWidth: 0 }}>
              {samplePdf.name}
            </Typography>
            <Chip label="Sample PDF" size="small" color="primary" variant="outlined" />
            <IconButton size="small" onClick={handleRemovePdf} title="Remove sample PDF">
              <CloseIcon fontSize="small" />
            </IconButton>
          </Paper>
        ) : (
          <Paper
            variant="outlined"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              px: 1.5, py: 0.75,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              cursor: 'pointer',
              borderStyle: 'dashed',
              borderColor: 'divider',
              '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' },
              transition: 'all 0.15s',
              flexShrink: 0,
            }}
          >
            <UploadFileIcon sx={{ color: 'text.secondary' }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" fontWeight={600}>
                {templateKind === 'excel' ? 'Have a sample PDF or Excel file?' : 'Have a sample PDF?'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {templateKind === 'excel'
                  ? 'Drop a PDF or Excel file here or click to upload. The AI will use it as a visual reference.'
                  : 'Drop a PDF here or click to upload. The AI will use it as a visual reference for layout and styling.'}
              </Typography>
            </Box>
            <Chip label="Optional" size="small" variant="outlined" />
            <input
              ref={fileInputRef}
              type="file"
              accept={templateKind === 'excel' ? 'application/pdf,.xlsx,.xls' : 'application/pdf'}
              hidden
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
            />
          </Paper>
        )}

        {/* Main content: Preview + Chat — fills remaining Surface space */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '7fr 5fr' },
            gap: 2,
            flex: 1,
            minHeight: 0,      /* allow shrinking within flex parent */
          }}
        >
          {/* Left: Preview — full-width iframe with vertical scroll */}
          <Box
            sx={{
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              overflow: 'hidden',
              bgcolor: 'background.paper',
              display: 'flex',
              flexDirection: 'column',
              minHeight: 0,
            }}
          >
            <Box
              sx={{
                p: 1.5,
                borderBottom: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.default',
                flexShrink: 0,
              }}
            >
              <Typography variant="caption" fontWeight={600} color="text.secondary">
                Template Preview
              </Typography>
            </Box>
            <Box sx={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
              {previewUrl ? (
                <iframe
                  src={previewUrl}
                  title="Template Preview"
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    display: 'block',
                    minHeight: 600,
                  }}
                />
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '100%',
                    p: 4,
                  }}
                >
                  <Alert severity="info" variant="outlined" sx={{ maxWidth: 400 }}>
                    Start a conversation to generate a template. The preview will appear here as the AI creates your template.
                  </Alert>
                </Box>
              )}
            </Box>
          </Box>

          {/* Right: Chat — only this panel scrolls internally */}
          <TemplateChatEditor
            templateId={SESSION_KEY}
            templateName="New Template"
            currentHtml={currentHtml}
            onHtmlUpdate={handleHtmlUpdate}
            onApplySuccess={handleApplySuccess}
            onRequestSave={handleOpenNameDialog}
            mappingPreviewData={mappingPreviewData}
            mappingApproving={mappingApproving}
            onMappingApprove={handleMappingApprove}
            onMappingSkip={handleMappingSkip}
            onMappingQueue={handleMappingQueue}
            mode="create"
            chatApi={chatApi}
          />
        </Box>
      </Surface>

      {/* Name Dialog */}
      <Dialog
        open={nameDialogOpen}
        onClose={handleCloseNameDialog}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: 2 } }}
      >
        <DialogTitle sx={{ fontWeight: 600 }}>
          Name Your Template
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Give your template a descriptive name. You can change this later.
          </Typography>
          <ToggleButtonGroup
            value={templateKind}
            exclusive
            onChange={(_, newKind) => newKind && setTemplateKind(newKind)}
            size="small"
            sx={{ mb: 2 }}
          >
            <ToggleButton value="pdf">
              <PictureAsPdfIcon sx={{ mr: 1, fontSize: 18 }} /> PDF Report
            </ToggleButton>
            <ToggleButton value="excel">
              <TableChartIcon sx={{ mr: 1, fontSize: 18 }} /> Excel Report
            </ToggleButton>
          </ToggleButtonGroup>
          <TextField
            autoFocus
            fullWidth
            label="Template Name"
            placeholder="e.g., Monthly Sales Invoice"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && templateName.trim()) {
                handleCreateTemplate()
              }
            }}
            disabled={creating}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={handleCloseNameDialog} disabled={creating}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateTemplate}
            disabled={!templateName.trim() || creating}
            sx={{
              bgcolor: neutral[900],
              '&:hover': { bgcolor: neutral[700] },
            }}
          >
            {creating ? 'Creating...' : 'Create Template'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
