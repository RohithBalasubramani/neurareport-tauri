/**
 * Method-specific content panels for the Ingestion page.
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Chip,
  CircularProgress,
  LinearProgress,
  Paper,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Link as UrlIcon,
  ContentPaste as ClipIcon,
  Mic as MicIcon,
  PlayArrow as StartIcon,
  Storage as DatabaseImportIcon,
} from '@mui/icons-material'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { DropZone, ActionButton, UploadItem } from './IngestionStyledComponents'
import WatcherPanel from './WatcherPanel'

export default function IngestionMethodContent({
  activeMethod,
  isDragging,
  urlInput,
  setUrlInput,
  watchers,
  transcriptionJobs,
  loading,
  selectedConnectionId,
  setSelectedConnectionId,
  fileInputRef,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect,
  onUrlImport,
  onClipUrl,
  onToggleWatcher,
  onDeleteWatcher,
  onTranscribe,
  onOpenCreateWatcher,
}) {
  switch (activeMethod) {
    case 'upload':
      return (
        <Box>
          <DropZone
            isDragging={isDragging}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              onChange={onFileSelect}
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
            onClick={activeMethod === 'url' ? onUrlImport : onClipUrl}
            disabled={!urlInput.trim() || loading}
            startIcon={loading ? <CircularProgress size={20} /> : activeMethod === 'url' ? <UrlIcon /> : <ClipIcon />}
          >
            {activeMethod === 'url' ? 'Import' : 'Clip Page'}
          </ActionButton>
        </Paper>
      )

    case 'watcher':
      return (
        <WatcherPanel
          watchers={watchers}
          onToggleWatcher={onToggleWatcher}
          onDeleteWatcher={onDeleteWatcher}
          onOpenCreateWatcher={onOpenCreateWatcher}
        />
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
              onChange={onTranscribe}
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
