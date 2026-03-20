/**
 * Add Document dialog.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Divider,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
} from '@mui/material'
import { CloudUpload as UploadIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { GlassDialog, MAX_DOC_SIZE, MAX_NAME_LENGTH } from './DocQAStyledComponents'

export default function AddDocumentDialog({
  open,
  onClose,
  docName,
  setDocName,
  docContent,
  setDocContent,
  handleAddDocument,
  handleFileUpload,
}) {
  const theme = useTheme()

  return (
    <GlassDialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>Add Document</Typography>
        <Typography variant="body2" color="text.secondary">
          Upload or paste document content for analysis
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box
          sx={{
            mt: 2, p: 4,
            border: `2px dashed ${alpha(theme.palette.divider, 0.4)}`,
            borderRadius: 1, textAlign: 'center', cursor: 'pointer',
            transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
            '&:hover': {
              borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
            },
          }}
          component="label"
        >
          <UploadIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body1" sx={{ fontWeight: 500, mb: 0.5 }}>
            Drop your file here or click to browse
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Supports TXT, MD, JSON, CSV (max 5MB)
          </Typography>
          <input type="file" hidden onChange={handleFileUpload} accept=".txt,.md,.json,.csv" />
        </Box>
        <Divider sx={{ my: 3 }}>
          <Typography variant="caption" color="text.secondary">OR</Typography>
        </Divider>
        <TextField
          fullWidth label="Document Name" value={docName}
          onChange={(e) => setDocName(e.target.value)} sx={{ mb: 2 }}
          inputProps={{ maxLength: MAX_NAME_LENGTH }}
          InputProps={{ sx: { borderRadius: 1 } }}
        />
        <TextField
          fullWidth multiline rows={10} label="Document Content"
          value={docContent} onChange={(e) => setDocContent(e.target.value)}
          placeholder="Paste your document content here..."
          inputProps={{ maxLength: MAX_DOC_SIZE }}
          InputProps={{ sx: { borderRadius: 1 } }}
        />
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} sx={{ borderRadius: 1, textTransform: 'none' }}>Cancel</Button>
        <Button
          variant="contained" onClick={handleAddDocument} disabled={!docName || !docContent}
          sx={{
            borderRadius: 1, textTransform: 'none', px: 3,
            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          }}
        >
          Add Document
        </Button>
      </DialogActions>
    </GlassDialog>
  )
}
