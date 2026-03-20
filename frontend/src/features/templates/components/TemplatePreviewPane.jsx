/**
 * Template Preview pane — shows the HTML preview iframe or empty state.
 */
import React from 'react'
import {
  Box,
  Typography,
  Alert,
} from '@mui/material'

export default function TemplatePreviewPane({ previewUrl }) {
  return (
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
  )
}
