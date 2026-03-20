/**
 * Dialog for naming a new template before saving.
 */
import React from 'react'
import {
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import { neutral } from '@/app/theme'

export default function TemplateNameDialog({
  open,
  templateName,
  setTemplateName,
  templateKind,
  setTemplateKind,
  creating,
  onClose,
  onCreate,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{ sx: { borderRadius: 2 } }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>
        Name Your Template
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Give your template a descriptive name. You can change this later.
        </Typography>
        <ToggleButtonGroup
          value={templateKind}
          exclusive
          onChange={(_, newKind) => newKind && setTemplateKind(newKind)}
          size="small"
          sx={{ mb: 2 }}
        >
          <ToggleButton value="pdf">
            <PictureAsPdfIcon sx={{ mr: 1, fontSize: 18 }} /> PDF Report
          </ToggleButton>
          <ToggleButton value="excel">
            <TableChartIcon sx={{ mr: 1, fontSize: 18 }} /> Excel Report
          </ToggleButton>
        </ToggleButtonGroup>
        <TextField
          autoFocus
          fullWidth
          label="Template Name"
          placeholder="e.g., Monthly Sales Invoice"
          value={templateName}
          onChange={(e) => setTemplateName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && templateName.trim()) {
              onCreate()
            }
          }}
          disabled={creating}
        />
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={creating}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={onCreate}
          disabled={!templateName.trim() || creating}
          sx={{
            bgcolor: neutral[900],
            '&:hover': { bgcolor: neutral[700] },
          }}
        >
          {creating ? 'Creating...' : 'Create Template'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
