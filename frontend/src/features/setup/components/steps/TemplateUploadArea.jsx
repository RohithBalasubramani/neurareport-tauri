import {
  Box, Typography, Stack, Button, Alert, LinearProgress, Paper, alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

export default function TemplateUploadArea({
  showUpload,
  verifyResult,
  error,
  setError,
  queuedJobId,
  uploading,
  uploadProgress,
  uploadedFile,
  queueInBackground,
  setQueueInBackground,
  templateKind,
  acceptedTypes,
  fileInputRef,
  handleNavigate,
  handleDrop,
  handleDragOver,
  handleFileSelect,
  handleBrowseClick,
  setShowUpload,
}) {
  return (
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
  )
}
