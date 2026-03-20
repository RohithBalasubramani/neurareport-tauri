/**
 * Save query dialog
 */
import {
  Button,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  useTheme,
  alpha,
  styled,
  Dialog,
} from '@mui/material'
import { PrimaryButton, StyledTextField } from './styledComponents'

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiBackdrop-root': {
    backgroundColor: alpha(theme.palette.common.black, 0.6),
    backdropFilter: 'blur(8px)',
  },
  '& .MuiDialog-paper': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    borderRadius: 8,
    boxShadow: `0 24px 64px ${alpha(theme.palette.common.black, 0.25)}`,
  },
}))

export default function SaveQueryDialog({
  open, saveName, saveDescription,
  onClose, onSaveNameChange, onSaveDescriptionChange, onSave,
}) {
  const theme = useTheme()

  return (
    <StyledDialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ color: theme.palette.text.primary }}>Save Query</DialogTitle>
      <DialogContent>
        <Stack spacing={2} mt={1}>
          <StyledTextField
            fullWidth label="Name" value={saveName}
            onChange={(e) => onSaveNameChange(e.target.value)}
            placeholder="e.g., Monthly Sales Report"
          />
          <StyledTextField
            fullWidth multiline rows={2} label="Description (optional)"
            value={saveDescription} onChange={(e) => onSaveDescriptionChange(e.target.value)}
            placeholder="What does this query do?"
          />
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 2.5 }}>
        <Button onClick={onClose} sx={{ borderRadius: 1, textTransform: 'none' }}>Cancel</Button>
        <PrimaryButton onClick={onSave} disabled={!saveName.trim()}>Save</PrimaryButton>
      </DialogActions>
    </StyledDialog>
  )
}
