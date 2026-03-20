/**
 * Recent Uploads list for the Ingestion page.
 */
import React from 'react'
import {
  Box,
  Typography,
  CircularProgress,
  LinearProgress,
} from '@mui/material'
import {
  Description as DocIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { UploadItem } from './IngestionStyledComponents'

export default function RecentUploads({ uploads, uploadProgress }) {
  if (uploads.length === 0) return null

  return (
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
  )
}
