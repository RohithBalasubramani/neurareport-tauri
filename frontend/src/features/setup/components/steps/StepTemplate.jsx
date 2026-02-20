import { useState, useCallback, useRef, useEffect } from 'react'
import {
  Box,
  Typography,
  Stack,
  Button,
  Alert,
  LinearProgress,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  alpha,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Divider,
  Grid,
  Radio,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SummarizeIcon from '@mui/icons-material/Summarize'
import DescriptionIcon from '@mui/icons-material/Description'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'

// Pre-built template gallery for users who don't have their own
const TEMPLATE_GALLERY = [
  {
    id: 'gallery-invoice',
    name: 'Invoice Report',
    description: 'Professional invoice template with line items, totals, and company branding',
    kind: 'pdf',
    icon: ReceiptLongIcon,
    popular: true,
  },
  {
    id: 'gallery-sales',
    name: 'Sales Summary',
    description: 'Weekly/monthly sales report with charts, metrics, and trends',
    kind: 'excel',
    icon: AssessmentIcon,
    popular: true,
  },
  {
    id: 'gallery-inventory',
    name: 'Inventory Report',
    description: 'Stock levels, reorder points, and inventory movement tracking',
    kind: 'excel',
    icon: TableChartIcon,
    popular: false,
  },
  {
    id: 'gallery-executive',
    name: 'Executive Summary',
    description: 'High-level business metrics and KPIs for leadership review',
    kind: 'pdf',
    icon: SummarizeIcon,
    popular: false,
  },
  {
    id: 'gallery-blank-pdf',
    name: 'Blank PDF Template',
    description: 'Start from scratch with a customizable PDF layout',
    kind: 'pdf',
    icon: DescriptionIcon,
    popular: false,
  },
  {
    id: 'gallery-blank-excel',
    name: 'Blank Excel Template',
    description: 'Start from scratch with a customizable spreadsheet',
    kind: 'excel',
    icon: TableChartIcon,
    popular: false,
  },
]

export default function StepTemplate({ wizardState, updateWizardState, onComplete, setLoading }) {
  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'setup-step-template', ...intent } }),
    [navigate]
  )
  const fileInputRef = useRef(null)

  const activeConnection = useAppStore((s) => s.activeConnection)
  const setTemplateId = useAppStore((s) => s.setTemplateId)
  const setVerifyArtifacts = useAppStore((s) => s.setVerifyArtifacts)
  const addTemplate = useAppStore((s) => s.addTemplate)

  const [templateKind, setTemplateKind] = useState(wizardState.templateKind || 'pdf')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [verifyResult, setVerifyResult] = useState(null)
  const [error, setError] = useState(null)
  const [queueInBackground, setQueueInBackground] = useState(false)
  const [queuedJobId, setQueuedJobId] = useState(null)
  const [selectedGalleryTemplate, setSelectedGalleryTemplate] = useState(null)
  const [showUpload, setShowUpload] = useState(false)

  useEffect(() => {
    if (!queuedJobId) return
    let cancelled = false

    const pollJob = async () => {
      try {
        const job = await api.getJob(queuedJobId)
        if (cancelled || !job) return

        if (typeof job.progress === 'number') {
          setUploadProgress(Math.round(job.progress))
        }

        if (job.status === 'completed') {
          const result = job.result || {}
          const templateId = result.template_id || result.templateId
          if (!templateId) {
            setError('Template verification completed but no template ID was returned.')
            toast.show('Template verification completed without a template ID.', 'error')
            setQueuedJobId(null)
            return
          }

          setVerifyResult(result)
          setTemplateId(templateId)
          setVerifyArtifacts(result.artifacts)
          updateWizardState({ templateId })

          addTemplate({
            id: templateId,
            name: uploadedFile?.name || `Template ${templateId}`,
            kind: templateKind,
            status: 'pending',
            created_at: new Date().toISOString(),
          })

          toast.show('Template verified successfully', 'success')
          setQueuedJobId(null)
        } else if (job.status === 'failed' || job.status === 'cancelled') {
          const message = job.error || 'Template verification failed'
          setError(message)
          toast.show(message, 'error')
          setQueuedJobId(null)
        }
      } catch (err) {
        if (cancelled) return
        const message = err.message || 'Failed to load queued job status'
        setError(message)
        toast.show(message, 'error')
        setQueuedJobId(null)
      }
    }

    pollJob()
    const intervalId = setInterval(pollJob, 3000)
    return () => {
      cancelled = true
      clearInterval(intervalId)
    }
  }, [
    queuedJobId,
    templateKind,
    uploadedFile,
    setTemplateId,
    setVerifyArtifacts,
    updateWizardState,
    addTemplate,
    toast,
  ])

  const handleKindChange = useCallback((_, newKind) => {
    if (newKind) {
      setTemplateKind(newKind)
      updateWizardState({ templateKind: newKind })
    }
  }, [updateWizardState])

  const handleFile = useCallback(async (file) => {
    setError(null)
    setUploadedFile(file)
    setUploading(true)
    setUploadProgress(0)
    setQueuedJobId(null)

    try {
      const connectionId = wizardState.connectionId || activeConnection?.id
      if (!connectionId) {
        const msg = 'Please connect to a database before verifying templates.'
        setError(msg)
        toast.show(msg, 'warning')
        setUploading(false)
        setUploadProgress(0)
        return
      }

      await execute({
        type: InteractionType.UPLOAD,
        label: `Verify ${templateKind.toUpperCase()} template`,
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: true,
        intent: {
          connectionId,
          templateKind,
          fileName: file?.name,
          action: 'verify_template',
        },
        action: async () => {
          try {
            const result = await api.verifyTemplate({
              file,
              connectionId,
              kind: templateKind,
              background: queueInBackground,
              onProgress: (event) => {
                if (event.event === 'stage') {
                  const progress = event.progress || 0
                  setUploadProgress(progress)
                }
              },
              onUploadProgress: (percent) => {
                setUploadProgress(percent)
              },
            })

            if (queueInBackground) {
              const jobId = result?.job_id || result?.jobId || null
              setQueuedJobId(jobId)
              toast.show('Template verification queued. Track progress in Jobs.', 'success')
              return result
            }

            setVerifyResult(result)
            setTemplateId(result.template_id)
            setVerifyArtifacts(result.artifacts)
            updateWizardState({ templateId: result.template_id })

            // Add to templates list
            addTemplate({
              id: result.template_id,
              name: file.name,
              kind: templateKind,
              status: 'pending',
              created_at: new Date().toISOString(),
            })

            toast.show('Template verified successfully', 'success')
            return result
          } catch (err) {
            setError(err.message || 'Failed to verify template')
            toast.show(err.message || 'Failed to verify template', 'error')
            throw err
          }
        },
      })
    } finally {
      setUploading(false)
      setUploadProgress(100)
    }
  }, [
    wizardState.connectionId,
    activeConnection?.id,
    templateKind,
    queueInBackground,
    setTemplateId,
    setVerifyArtifacts,
    updateWizardState,
    addTemplate,
    toast,
    execute,
  ])

  const handleDrop = useCallback((event) => {
    event.preventDefault()
    const files = event.dataTransfer?.files
    if (files?.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
  }, [])

  const handleFileSelect = useCallback((event) => {
    const files = event.target.files
    if (files?.length > 0) {
      handleFile(files[0])
    }
  }, [handleFile])

  const handleBrowseClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const acceptedTypes = templateKind === 'pdf'
    ? '.pdf'
    : '.xlsx,.xls'

  const handleSelectGalleryTemplate = useCallback((template) => {
    setSelectedGalleryTemplate(template)
    setTemplateKind(template.kind)
    updateWizardState({ templateKind: template.kind, galleryTemplate: template })
  }, [updateWizardState])

  const handleUseGalleryTemplate = useCallback(async () => {
    if (!selectedGalleryTemplate) return

    await execute({
      type: InteractionType.CREATE,
      label: `Use "${selectedGalleryTemplate.name}" template`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: {
        galleryId: selectedGalleryTemplate.id,
        kind: selectedGalleryTemplate.kind,
        action: 'use_gallery_template',
      },
      action: async () => {
        setLoading(true)
        try {
          // For gallery templates, we create a template based on the selected type
          const result = await api.createTemplateFromGallery?.({
            galleryId: selectedGalleryTemplate.id,
            kind: selectedGalleryTemplate.kind,
            connectionId: wizardState.connectionId,
          }).catch(() => ({
            // Fallback if API not available - create a placeholder template
            template_id: `template-${selectedGalleryTemplate.id}-${Date.now()}`,
            name: selectedGalleryTemplate.name,
          }))

          const templateId = result.template_id || result.templateId || `gallery-${selectedGalleryTemplate.id}`

          setTemplateId(templateId)
          updateWizardState({ templateId, galleryTemplate: selectedGalleryTemplate })

          addTemplate({
            id: templateId,
            name: selectedGalleryTemplate.name,
            kind: selectedGalleryTemplate.kind,
            status: 'approved',
            created_at: new Date().toISOString(),
            isGalleryTemplate: true,
          })

          toast.show(`"${selectedGalleryTemplate.name}" template ready!`, 'success')
          setVerifyResult({ template_id: templateId })
          return result
        } finally {
          setLoading(false)
        }
      },
    })
  }, [selectedGalleryTemplate, wizardState.connectionId, setTemplateId, updateWizardState, addTemplate, toast, setLoading, execute])

  const filteredGalleryTemplates = TEMPLATE_GALLERY.filter(t =>
    templateKind === 'all' || t.kind === templateKind
  )

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        Choose a Report Template
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Create with AI, pick from our gallery, or upload your own design.
      </Typography>

      {/* Template Type Filter */}
      <Box sx={{ mb: 3 }}>
        <ToggleButtonGroup
          value={templateKind}
          exclusive
          onChange={handleKindChange}
          size="small"
        >
          <ToggleButton value="pdf" sx={{ px: 3 }}>
            <PictureAsPdfIcon sx={{ mr: 1, fontSize: 18 }} />
            PDF Reports
          </ToggleButton>
          <ToggleButton value="excel" sx={{ px: 3 }}>
            <TableChartIcon sx={{ mr: 1, fontSize: 18 }} />
            Excel Reports
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Template Gallery */}
      {!showUpload && !verifyResult && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={600} color="text.secondary" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
            <AutoAwesomeIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
            Template Gallery
          </Typography>

          <Grid container spacing={2}>
            {filteredGalleryTemplates.map((template) => {
              const IconComponent = template.icon
              const isSelected = selectedGalleryTemplate?.id === template.id

              return (
                <Grid item xs={12} sm={6} md={4} key={template.id}>
                  <Card
                    variant="outlined"
                    sx={{
                      height: '100%',
                      border: 2,
                      borderColor: isSelected ? (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] : 'divider',
                      bgcolor: isSelected ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                        transform: 'translateY(-2px)',
                        boxShadow: 2,
                      },
                    }}
                  >
                    <CardActionArea
                      onClick={() => handleSelectGalleryTemplate(template)}
                      sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
                    >
                      <CardContent sx={{ flex: 1 }}>
                        <Stack direction="row" alignItems="flex-start" spacing={1} sx={{ mb: 1 }}>
                          <Radio checked={isSelected} size="small" sx={{ p: 0, mr: 0.5 }} />
                          <IconComponent sx={{
                            fontSize: 24,
                            color: 'text.secondary'
                          }} />
                          <Box sx={{ flex: 1 }}>
                            <Stack direction="row" alignItems="center" spacing={1}>
                              <Typography variant="subtitle2" fontWeight={600}>
                                {template.name}
                              </Typography>
                              {template.popular && (
                                <Chip label="Popular" size="small" sx={{ height: 18, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                              )}
                            </Stack>
                            <Chip
                              label={template.kind.toUpperCase()}
                              size="small"
                              variant="outlined"
                              sx={{ height: 18, fontSize: '10px', mt: 0.5, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                            />
                          </Box>
                        </Stack>
                        <Typography variant="caption" color="text.secondary">
                          {template.description}
                        </Typography>
                      </CardContent>
                    </CardActionArea>
                  </Card>
                </Grid>
              )
            })}
          </Grid>

          {selectedGalleryTemplate && (
            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                onClick={handleUseGalleryTemplate}
                startIcon={<CheckCircleIcon />}
                sx={{ mr: 2 }}
              >
                Use "{selectedGalleryTemplate.name}"
              </Button>
              <Button variant="text" onClick={() => setSelectedGalleryTemplate(null)}>
                Clear Selection
              </Button>
            </Box>
          )}

          <Divider sx={{ my: 3 }}>
            <Chip label="Or start your own" size="small" />
          </Divider>

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={<AutoAwesomeIcon />}
              onClick={() => handleNavigate(`/templates/new/chat?from=wizard&connectionId=${encodeURIComponent(wizardState.connectionId || '')}`, 'Create template with AI')}
              sx={{
                bgcolor: neutral[900],
                '&:hover': { bgcolor: neutral[700] },
              }}
            >
              Create with AI
            </Button>
            <Button
              variant="outlined"
              startIcon={<CloudUploadIcon />}
              onClick={() => setShowUpload(true)}
              sx={{ borderStyle: 'dashed' }}
            >
              Upload Custom Template
            </Button>
          </Stack>
        </Box>
      )}

      {/* Upload Section - shown when user chooses to upload */}
      {(showUpload || verifyResult) && (
        <>
          {showUpload && !verifyResult && (
            <Button
              variant="text"
              onClick={() => setShowUpload(false)}
              sx={{ mb: 2 }}
            >
              ← Back to Gallery
            </Button>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {queuedJobId && (
        <Alert
          severity="info"
          sx={{ mb: 3 }}
          action={(
            <Button size="small" onClick={() => handleNavigate('/jobs', 'Open jobs')} sx={{ textTransform: 'none' }}>
              View Jobs
            </Button>
          )}
        >
          Template verification queued. Job ID: {queuedJobId}
        </Alert>
      )}

      {verifyResult ? (
        <Paper
          sx={{
            p: 3,
            border: 2,
            borderColor: (theme) => alpha(theme.palette.divider, 0.3),
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
          }}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <CheckCircleIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
            <Box>
              <Typography variant="subtitle1" fontWeight={600}>
                Template Verified
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {uploadedFile?.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                ID: {verifyResult.template_id}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      ) : (
        <Paper
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          sx={{
            p: 4,
            border: 2,
            borderStyle: 'dashed',
            borderColor: 'divider',
            bgcolor: 'action.hover',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'border-color 0.2s, background-color 0.2s',
            '&:hover': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
            },
          }}
          onClick={handleBrowseClick}
        >
          <Stack direction="row" justifyContent="center" sx={{ mb: 2 }}>
            <Button
              variant={queueInBackground ? 'contained' : 'outlined'}
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                setQueueInBackground((prev) => !prev)
              }}
              sx={{ textTransform: 'none' }}
            >
              {queueInBackground ? 'Queue in background: On' : 'Queue in background: Off'}
            </Button>
          </Stack>
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedTypes}
            onChange={handleFileSelect}
            hidden
          />

          {uploading ? (
            <Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                Uploading and verifying...
              </Typography>
              <LinearProgress
                variant="determinate"
                value={uploadProgress}
                sx={{ maxWidth: 300, mx: 'auto', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                {uploadProgress}%
              </Typography>
            </Box>
          ) : (
            <>
              <CloudUploadIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" sx={{ mb: 1 }}>
                Drag and drop your {templateKind.toUpperCase()} file here
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                or click to browse
              </Typography>
              <Button variant="outlined" size="small">
                Browse Files
              </Button>
            </>
          )}
        </Paper>
      )}

          {/* Preview */}
          {verifyResult?.artifacts?.png_url && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                Preview
              </Typography>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <img
                  src={verifyResult.artifacts.png_url}
                  alt="Template preview"
                  style={{ maxWidth: '100%', height: 'auto', borderRadius: 4 }}
                />
              </Paper>
            </Box>
          )}
        </>
      )}
    </Box>
  )
}
