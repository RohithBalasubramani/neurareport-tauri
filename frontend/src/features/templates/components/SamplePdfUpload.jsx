/**
 * Sample PDF/Excel upload area for template creation.
 */
import React from 'react'
import {
  Box,
  Typography,
  Paper,
  Chip,
  IconButton,
} from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import CloseIcon from '@mui/icons-material/Close'

export default function SamplePdfUpload({
  samplePdf,
  templateKind,
  fileInputRef,
  onFileSelect,
  onDrop,
  onDragOver,
  onRemovePdf,
}) {
  if (samplePdf) {
    return (
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
        <IconButton size="small" onClick={onRemovePdf} title="Remove sample PDF">
          <CloseIcon fontSize="small" />
        </IconButton>
      </Paper>
    )
  }

  return (
    <Paper
      variant="outlined"
      onDrop={onDrop}
      onDragOver={onDragOver}
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
        onChange={(e) => onFileSelect(e.target.files?.[0])}
      />
    </Paper>
  )
}
