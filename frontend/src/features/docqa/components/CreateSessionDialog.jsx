/**
 * Create Q&A Session dialog.
 */
import React from 'react'
import {
  Typography,
  Button,
  TextField,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { GlassDialog, MAX_NAME_LENGTH } from './DocQAStyledComponents'

export default function CreateSessionDialog({
  open,
  onClose,
  newSessionName,
  setNewSessionName,
  handleCreateSession,
}) {
  const theme = useTheme()

  return (
    <GlassDialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Create Q&A Session
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Start a new document analysis workspace
        </Typography>
      </DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Session Name"
          placeholder="e.g., Research Papers Analysis"
          value={newSessionName}
          onChange={(e) => setNewSessionName(e.target.value)}
          sx={{ mt: 2 }}
          inputProps={{ maxLength: MAX_NAME_LENGTH }}
          InputProps={{ sx: { borderRadius: 1 } }}
        />
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} sx={{ borderRadius: 1, textTransform: 'none' }}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleCreateSession}
          disabled={!newSessionName}
          sx={{
            borderRadius: 1,
            textTransform: 'none',
            px: 3,
            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          }}
        >
          Create Session
        </Button>
      </DialogActions>
    </GlassDialog>
  )
}
