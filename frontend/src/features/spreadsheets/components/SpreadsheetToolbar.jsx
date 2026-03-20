import {
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  alpha,
} from '@mui/material'
import {
  Upload as UploadIcon,
  Download as DownloadIcon,
  AutoAwesome as AIIcon,
  Save as SaveIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { ToolbarContainer, ActionButton } from './styledComponents'

export default function SpreadsheetToolbar({
  spreadsheetName,
  hasUnsavedChanges,
  saving,
  onTriggerImport,
  onExportClick,
  onOpenAiDialog,
  onSave,
}) {
  return (
    <ToolbarContainer>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {spreadsheetName}
        </Typography>
        {hasUnsavedChanges && (
          <Chip
            label="Unsaved"
            size="small"
            sx={{ height: 20, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <Tooltip title="Undo">
          <IconButton size="small">
            <UndoIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Redo">
          <IconButton size="small">
            <RedoIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

        <ActionButton
          size="small"
          startIcon={<UploadIcon />}
          onClick={onTriggerImport}
        >
          Import
        </ActionButton>
        <ActionButton
          size="small"
          startIcon={<DownloadIcon />}
          onClick={onExportClick}
        >
          Export
        </ActionButton>
        <ActionButton
          size="small"
          startIcon={<AIIcon />}
          onClick={onOpenAiDialog}
        >
          AI Formula
        </ActionButton>
        <ActionButton
          variant="contained"
          size="small"
          startIcon={<SaveIcon />}
          onClick={onSave}
          disabled={saving || !hasUnsavedChanges}
        >
          {saving ? 'Saving...' : 'Save'}
        </ActionButton>
      </Box>
    </ToolbarContainer>
  )
}
