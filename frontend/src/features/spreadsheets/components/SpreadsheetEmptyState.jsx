import { Box, Typography } from '@mui/material'
import { Add as AddIcon, Upload as UploadIcon, TableChart as SpreadsheetIcon } from '@mui/icons-material'
import { EmptyStateContainer, ActionButton } from './styledComponents'

export default function SpreadsheetEmptyState({ onOpenCreateDialog, onTriggerImport }) {
  return (
    <EmptyStateContainer>
      <SpreadsheetIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
        No Spreadsheet Selected
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Create a new spreadsheet or select one from the sidebar.
      </Typography>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <ActionButton
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onOpenCreateDialog}
        >
          Create Spreadsheet
        </ActionButton>
        <ActionButton
          variant="outlined"
          startIcon={<UploadIcon />}
          onClick={onTriggerImport}
        >
          Import File
        </ActionButton>
      </Box>
    </EmptyStateContainer>
  )
}
