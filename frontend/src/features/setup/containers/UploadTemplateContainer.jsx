import { useCallback, useRef, useState } from 'react'
import { Box, Typography, Stack, Button, List, ListItem, ListItemText, LinearProgress, Alert } from '@mui/material'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { verifyTemplate as apiVerifyTemplate } from '@/api/client'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

const getTemplateKind = (file) => {
  const name = file?.name?.toLowerCase() || ''
  if (name.endsWith('.pdf')) return 'pdf'
  if (name.endsWith('.xls') || name.endsWith('.xlsx')) return 'excel'
  return null
}

export default function UploadTemplate() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)
  const toast = useToast()
  const { execute } = useInteraction()
  const {
    activeConnectionId,
    setTemplateId,
    setVerifyArtifacts,
    setTemplateKind,
  } = useAppStore()

  const onFileChange = useCallback((e) => {
    const selected = Array.from(e.target.files || [])
    if (selected.length && !getTemplateKind(selected[0])) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    setFiles(selected)
    setResult(null)
    setError(null)
    if (selected.length) {
      setTemplateKind(getTemplateKind(selected[0]) || 'pdf')
    }
  }, [setTemplateKind, toast])

  const handleDrop = useCallback((event) => {
    event.preventDefault()
    setIsDragging(false)
    const dropped = Array.from(event.dataTransfer?.files || [])
    if (!dropped.length) return
    if (!getTemplateKind(dropped[0])) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    setFiles(dropped)
    setResult(null)
    setError(null)
    setTemplateKind(getTemplateKind(dropped[0]) || 'pdf')
  }, [setTemplateKind, toast])

  const handleDragOver = useCallback((event) => {
    event.preventDefault()
  }, [])

  const handleDragEnter = useCallback((event) => {
    event.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleUpload = useCallback(async () => {
    const file = files[0]
    if (!file || uploading) return
    const kind = getTemplateKind(file)
    if (!kind) {
      toast.show('Unsupported file type. Please upload a PDF or Excel template.', 'warning')
      return
    }
    if (!activeConnectionId) {
      toast.show('Connect to a database before verifying templates.', 'warning')
      return
    }

    await execute({
      type: InteractionType.UPLOAD,
      label: 'Verify template',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: activeConnectionId,
        templateKind: kind,
        fileName: file?.name,
        action: 'verify_template',
      },
      action: async () => {
        setUploading(true)
        setUploadProgress(0)
        setError(null)
        setResult(null)

        try {
          const response = await apiVerifyTemplate({
            file,
            connectionId: activeConnectionId,
            kind,
            onUploadProgress: (percent) => setUploadProgress(percent),
          })
          setResult(response)
          setTemplateId(response?.template_id || null)
          setVerifyArtifacts(response?.artifacts || null)
          setTemplateKind(kind)
          toast.show('Template uploaded and verified', 'success')
          return response
        } catch (err) {
          const message = err?.message || 'Failed to upload template'
          setError(message)
          toast.show(message, 'error')
          throw err
        } finally {
          setUploading(false)
        }
      },
    })
  }, [activeConnectionId, execute, files, setTemplateId, setTemplateKind, setVerifyArtifacts, toast, uploading])

  return (
    <Surface>
      <Stack direction="row" alignItems="center" spacing={0.75} sx={{ mb: 2 }}>
        <Typography variant="h6">Upload & Verify Template</Typography>
        <InfoTooltip
          content={TOOLTIP_COPY.uploadTemplate}
          ariaLabel="Upload and verify guidance"
        />
      </Stack>
      <Stack spacing={2}>
        <Box
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          role="button"
          tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault()
              inputRef.current?.click()
            }
          }}
          sx={{
            border: '1px dashed',
            borderColor: isDragging ? 'text.secondary' : 'divider',
            borderRadius: 1,  // Figma spec: 8px
            p: 3,
            textAlign: 'center',
            bgcolor: isDragging ? 'action.hover' : 'transparent',
            cursor: 'pointer',
            transition: 'all 160ms cubic-bezier(0.22, 1, 0.36, 1)',
          }}
        >
          <CloudUploadOutlinedIcon sx={{ mb: 1, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            Drag & drop a PDF or Excel template here, or click to browse
          </Typography>
          <input
            ref={inputRef}
            hidden
            accept=".pdf,.xls,.xlsx"
            type="file"
            onChange={onFileChange}
          />
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems="center">
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!files.length || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload & Verify'}
          </Button>
          {uploading && (
            <Box sx={{ flex: 1, width: '100%' }}>
              <LinearProgress variant="determinate" value={uploadProgress} />
            </Box>
          )}
        </Stack>

        {error && <Alert severity="error">{error}</Alert>}
        {result?.template_id && (
          <Alert severity="success">
            Verified template ID: {result.template_id}
          </Alert>
        )}
      </Stack>
      {!!files.length && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Selected</Typography>
          <List dense>
            {files.map((f) => (
              <ListItem key={f.name} disableGutters>
                <ListItemText primary={f.name} secondary={`${(f.size/1024).toFixed(1)} KB`} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Surface>
  )
}
