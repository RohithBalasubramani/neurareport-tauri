/**
 * Ingestion Page Container
 * Document ingestion and import interface.
 */
import React, { useState, useEffect, useCallback, useRef } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  IconButton,
  TextField,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Link as UrlIcon,
  Folder as FolderIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  ContentPaste as ClipIcon,
  Description as DocIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as SyncIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  FolderOpen as WatcherIcon,
  Storage as DatabaseImportIcon,
} from '@mui/icons-material'
import useIngestionStore from '@/stores/ingestionStore'
import useSharedData from '@/hooks/useSharedData'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { neutral, palette } from '@/app/theme'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

const DropZone = styled(Paper)(({ theme, isDragging }) => ({
  padding: theme.spacing(6),
  border: `2px dashed ${isDragging ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.3)}`,
  backgroundColor: isDragging ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : 'transparent',
  borderRadius: 8,  // Figma spec: 8px
  textAlign: 'center',
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
  },
}))

const MethodCard = styled(Card)(({ theme, selected }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  border: selected ? `2px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[900]}` : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

const UploadItem = styled(Paper)(({ theme, status }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1),
  borderLeft: `4px solid ${
    status === 'completed'
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
      : status === 'error'
      ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
      : (theme.palette.mode === 'dark' ? neutral[500] : neutral[500])
  }`,
}))

const WatcherCard = styled(Paper)(({ theme, isRunning }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1),
  border: `1px solid ${isRunning ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.2)}`,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

// =============================================================================
// INGESTION METHODS
// =============================================================================

const INGESTION_METHODS = [
  { id: 'upload', name: 'File Upload', description: 'Upload files from your computer', icon: UploadIcon, color: 'primary' },
  { id: 'url', name: 'URL Import', description: 'Import from a web URL', icon: UrlIcon, color: 'info' },
  { id: 'clip', name: 'Web Clipper', description: 'Clip content from web pages', icon: ClipIcon, color: 'secondary' },
  { id: 'watcher', name: 'Folder Watcher', description: 'Auto-import from folders', icon: WatcherIcon, color: 'warning' },
  { id: 'email', name: 'Email Import', description: 'Import from email accounts', icon: EmailIcon, color: 'error' },
  { id: 'transcribe', name: 'Transcription', description: 'Transcribe audio/video', icon: MicIcon, color: 'success' },
  { id: 'database', name: 'Database Import', description: 'Import from a database connection', icon: DatabaseImportIcon, color: 'primary' },
]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function IngestionPageContainer() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const fileInputRef = useRef(null)
  const { connections, activeConnectionId } = useSharedData()
  const {
    uploads,
    watchers,
    transcriptionJobs,
    imapAccounts,
    uploadProgress,
    loading,
    uploading,
    error,
    uploadFile,
    uploadBulk,
    uploadZip,
    importFromUrl,
    clipUrl,
    createWatcher,
    fetchWatchers,
    startWatcher,
    stopWatcher,
    deleteWatcher,
    transcribeFile,
    connectImapAccount,
    fetchImapAccounts,
    syncImapAccount,
    reset,
  } = useIngestionStore()

  const [activeMethod, setActiveMethod] = useState('upload')
  const [isDragging, setIsDragging] = useState(false)
  const [urlInput, setUrlInput] = useState('')
  const [watcherPath, setWatcherPath] = useState('')
  const [createWatcherOpen, setCreateWatcherOpen] = useState(false)
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId || '')

  useEffect(() => {
    fetchWatchers()
    fetchImapAccounts()
    return () => reset()
  }, [fetchImapAccounts, fetchWatchers, reset])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length === 0) return

    return execute({
      type: InteractionType.CREATE,
      label: `Upload ${files.length} file(s)`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', fileCount: files.length },
      action: async () => {
        if (files.length === 1) {
          await uploadFile(files[0])
        } else {
          await uploadBulk(files)
        }
        toast.show(`${files.length} file(s) uploaded`, 'success')
      },
    })
  }, [execute, toast, uploadBulk, uploadFile])

  const handleFileSelect = useCallback(async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    return execute({
      type: InteractionType.CREATE,
      label: `Upload ${files.length} file(s)`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', fileCount: files.length },
      action: async () => {
        if (files.length === 1) {
          const isZip = files[0].name.endsWith('.zip')
          if (isZip) {
            await uploadZip(files[0])
          } else {
            await uploadFile(files[0])
          }
        } else {
          await uploadBulk(files)
        }
        toast.show(`${files.length} file(s) uploaded`, 'success')
      },
    })
  }, [execute, toast, uploadBulk, uploadFile, uploadZip])

  const handleUrlImport = useCallback(async () => {
    if (!urlInput.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Import from URL',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', url: urlInput },
      action: async () => {
        await importFromUrl(urlInput)
        toast.show('URL imported', 'success')
        setUrlInput('')
      },
    })
  }, [execute, importFromUrl, toast, urlInput])

  const handleClipUrl = useCallback(async () => {
    if (!urlInput.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Clip web page',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', url: urlInput },
      action: async () => {
        await clipUrl(urlInput)
        toast.show('Page clipped', 'success')
        setUrlInput('')
      },
    })
  }, [clipUrl, execute, toast, urlInput])

  const handleCreateWatcher = useCallback(async () => {
    if (!watcherPath.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Create folder watcher',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'ingestion', path: watcherPath },
      action: async () => {
        await createWatcher(watcherPath)
        toast.show('Watcher created', 'success')
        setWatcherPath('')
        setCreateWatcherOpen(false)
      },
    })
  }, [createWatcher, execute, toast, watcherPath])

  const handleToggleWatcher = useCallback(async (watcher) => {
    const isRunning = watcher.status === 'running'
    return execute({
      type: InteractionType.UPDATE,
      label: isRunning ? 'Stop watcher' : 'Start watcher',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'ingestion', watcherId: watcher.id },
      action: async () => {
        if (isRunning) {
          await stopWatcher(watcher.id)
          toast.show('Watcher stopped', 'info')
        } else {
          await startWatcher(watcher.id)
          toast.show('Watcher started', 'success')
        }
      },
    })
  }, [execute, startWatcher, stopWatcher, toast])

  const handleDeleteWatcher = useCallback(async (watcherId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete watcher',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'ingestion', watcherId },
      action: async () => {
        await deleteWatcher(watcherId)
        toast.show('Watcher deleted', 'success')
      },
    })
  }, [deleteWatcher, execute, toast])

  const handleTranscribe = useCallback(async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Transcribe file',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', filename: file.name },
      action: async () => {
        await transcribeFile(file)
        toast.show('Transcription started', 'success')
      },
    })
  }, [execute, toast, transcribeFile])

  const renderMethodContent = () => {
    switch (activeMethod) {
      case 'upload':
        return (
          <Box>
            <DropZone
              isDragging={isDragging}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                hidden
                onChange={handleFileSelect}
              />
              <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                Drag & drop files here
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or click to browse (PDF, DOCX, XLSX, TXT, ZIP)
              </Typography>
            </DropZone>
          </Box>
        )

      case 'url':
      case 'clip':
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              {activeMethod === 'url' ? 'Import from URL' : 'Clip Web Page'}
            </Typography>
            <TextField
              fullWidth
              placeholder="https://example.com/document"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              sx={{ mb: 2 }}
            />
            <ActionButton
              variant="contained"
              onClick={activeMethod === 'url' ? handleUrlImport : handleClipUrl}
              disabled={!urlInput.trim() || loading}
              startIcon={loading ? <CircularProgress size={20} /> : activeMethod === 'url' ? <UrlIcon /> : <ClipIcon />}
            >
              {activeMethod === 'url' ? 'Import' : 'Clip Page'}
            </ActionButton>
          </Paper>
        )

      case 'watcher':
        return (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Folder Watchers
              </Typography>
              <ActionButton
                variant="contained"
                size="small"
                startIcon={<WatcherIcon />}
                onClick={() => setCreateWatcherOpen(true)}
              >
                Add Watcher
              </ActionButton>
            </Box>
            {watchers.length > 0 ? (
              watchers.map((watcher) => (
                <WatcherCard key={watcher.id} isRunning={watcher.status === 'running'}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <FolderIcon color={watcher.status === 'running' ? 'success' : 'action'} />
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {watcher.folder_path}
                        </Typography>
                        <Chip
                          size="small"
                          label={watcher.status}
                          color={watcher.status === 'running' ? 'success' : 'default'}
                        />
                      </Box>
                    </Box>
                    <Box>
                      <IconButton onClick={() => handleToggleWatcher(watcher)}>
                        {watcher.status === 'running' ? <StopIcon /> : <StartIcon />}
                      </IconButton>
                      <IconButton onClick={() => handleDeleteWatcher(watcher.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </WatcherCard>
              ))
            ) : (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                No folder watchers configured
              </Typography>
            )}
          </Box>
        )

      case 'transcribe':
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Audio/Video Transcription
            </Typography>
            <DropZone
              onClick={() => document.getElementById('transcribe-input')?.click()}
            >
              <input
                id="transcribe-input"
                type="file"
                accept="audio/*,video/*"
                hidden
                onChange={handleTranscribe}
              />
              <MicIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                Upload audio or video file
              </Typography>
              <Typography variant="body2" color="text.secondary">
                MP3, WAV, MP4, WebM supported
              </Typography>
            </DropZone>

            {transcriptionJobs.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Transcription Jobs
                </Typography>
                {transcriptionJobs.map((job) => (
                  <UploadItem key={job.id} status={job.status}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography variant="body2">{job.filename}</Typography>
                      <Chip size="small" label={job.status} />
                    </Box>
                    {job.status === 'processing' && <LinearProgress sx={{ mt: 1 }} />}
                  </UploadItem>
                ))}
              </Box>
            )}
          </Paper>
        )

      case 'database':
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Import from Database
            </Typography>
            <ConnectionSelector
              value={selectedConnectionId}
              onChange={setSelectedConnectionId}
              label="Select Connection"
              showStatus
              sx={{ mb: 2 }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Select a database connection to import tables and data.
            </Typography>
            <ActionButton
              variant="contained"
              disabled={!selectedConnectionId || loading}
              startIcon={loading ? <CircularProgress size={20} /> : <StartIcon />}
            >
              Import Data
            </ActionButton>
          </Paper>
        )

      default:
        return null
    }
  }

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <UploadIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Document Ingestion
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Import documents from various sources
            </Typography>
          </Box>
        </Box>
      </Header>

      <ContentArea>
        {/* Method Selection */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {INGESTION_METHODS.map((method) => (
            <Grid item xs={6} sm={4} md={2} key={method.id}>
              <MethodCard
                selected={activeMethod === method.id}
                onClick={() => setActiveMethod(method.id)}
              >
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 1,  // Figma spec: 8px
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                      mx: 'auto',
                      mb: 1,
                    }}
                  >
                    <method.icon sx={{ color: 'text.secondary' }} />
                  </Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {method.name}
                  </Typography>
                </CardContent>
              </MethodCard>
            </Grid>
          ))}
        </Grid>

        <Divider sx={{ mb: 3 }} />

        {/* Method Content */}
        {renderMethodContent()}

        {/* Recent Uploads */}
        {uploads.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Recent Uploads
            </Typography>
            {uploads.slice(0, 10).map((upload) => (
              <UploadItem key={upload.id} status={upload.status || 'completed'}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <DocIcon sx={{ color: 'text.secondary' }} />
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {upload.filename || upload.title || 'Untitled'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {upload.file_type?.toUpperCase()} - {new Date(upload.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                  {upload.status === 'completed' && <SuccessIcon sx={{ color: 'text.secondary' }} />}
                  {upload.status === 'error' && <ErrorIcon sx={{ color: 'text.secondary' }} />}
                  {upload.status === 'processing' && <CircularProgress size={20} />}
                </Box>
                {uploadProgress[upload.id] !== undefined && uploadProgress[upload.id] < 100 && (
                  <LinearProgress
                    variant="determinate"
                    value={uploadProgress[upload.id]}
                    sx={{ mt: 1 }}
                  />
                )}
              </UploadItem>
            ))}
          </Box>
        )}
      </ContentArea>

      {/* Create Watcher Dialog */}
      <Dialog open={createWatcherOpen} onClose={() => setCreateWatcherOpen(false)}>
        <DialogTitle>Add Folder Watcher</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Folder Path"
            placeholder="/path/to/folder"
            value={watcherPath}
            onChange={(e) => setWatcherPath(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateWatcherOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateWatcher}>Create</Button>
        </DialogActions>
      </Dialog>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}
