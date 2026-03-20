/**
 * Ingestion Page Container
 * Document ingestion and import interface.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  CardContent,
  Alert,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Link as UrlIcon,
  ContentPaste as ClipIcon,
  FolderOpen as WatcherIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  Storage as DatabaseImportIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { useIngestionPage } from '../hooks/useIngestionPage'
import { PageContainer, Header, ContentArea, MethodCard } from '../components/IngestionStyledComponents'
import IngestionMethodContent from '../components/IngestionMethodContent'
import RecentUploads from '../components/RecentUploads'

const INGESTION_METHODS = [
  { id: 'upload', name: 'File Upload', icon: UploadIcon },
  { id: 'url', name: 'URL Import', icon: UrlIcon },
  { id: 'clip', name: 'Web Clipper', icon: ClipIcon },
  { id: 'watcher', name: 'Folder Watcher', icon: WatcherIcon },
  { id: 'email', name: 'Email Import', icon: EmailIcon },
  { id: 'transcribe', name: 'Transcription', icon: MicIcon },
  { id: 'database', name: 'Database Import', icon: DatabaseImportIcon },
]

export default function IngestionPageContainer() {
  const theme = useTheme()
  const {
    uploads,
    watchers,
    transcriptionJobs,
    uploadProgress,
    loading,
    error,
    fileInputRef,
    activeMethod,
    setActiveMethod,
    isDragging,
    urlInput,
    setUrlInput,
    watcherPath,
    setWatcherPath,
    createWatcherOpen,
    setCreateWatcherOpen,
    selectedConnectionId,
    setSelectedConnectionId,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    handleUrlImport,
    handleClipUrl,
    handleCreateWatcher,
    handleToggleWatcher,
    handleDeleteWatcher,
    handleTranscribe,
  } = useIngestionPage()

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
                      borderRadius: 1,
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
        <IngestionMethodContent
          activeMethod={activeMethod}
          isDragging={isDragging}
          urlInput={urlInput}
          setUrlInput={setUrlInput}
          watchers={watchers}
          transcriptionJobs={transcriptionJobs}
          loading={loading}
          selectedConnectionId={selectedConnectionId}
          setSelectedConnectionId={setSelectedConnectionId}
          fileInputRef={fileInputRef}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onFileSelect={handleFileSelect}
          onUrlImport={handleUrlImport}
          onClipUrl={handleClipUrl}
          onToggleWatcher={handleToggleWatcher}
          onDeleteWatcher={handleDeleteWatcher}
          onTranscribe={handleTranscribe}
          onOpenCreateWatcher={() => setCreateWatcherOpen(true)}
        />

        {/* Recent Uploads */}
        <RecentUploads uploads={uploads} uploadProgress={uploadProgress} />
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
