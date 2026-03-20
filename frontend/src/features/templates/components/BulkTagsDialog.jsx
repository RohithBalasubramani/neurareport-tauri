/**
 * Bulk tags dialog
 */
import {
  Stack,
  Typography,
} from '@mui/material'
import {
  StyledDialog,
  DialogHeader,
  StyledDialogContent,
  StyledDialogActions,
  StyledTextField,
  PrimaryButton,
  SecondaryButton,
} from './TemplateStyledComponents'

export default function BulkTagsDialog({
  bulkTagsOpen,
  setBulkTagsOpen,
  selectedCount,
  bulkTags,
  setBulkTags,
  bulkActionLoading,
  handleBulkTagsApply,
}) {
  return (
    <StyledDialog open={bulkTagsOpen} onClose={() => setBulkTagsOpen(false)} maxWidth="sm" fullWidth>
      <DialogHeader>Add Tags</DialogHeader>
      <StyledDialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            Add tags to {selectedCount} design{selectedCount !== 1 ? 's' : ''}.
          </Typography>
          <StyledTextField
            label="Tags"
            value={bulkTags}
            onChange={(e) => setBulkTags(e.target.value)}
            helperText="Comma-separated (e.g. finance, monthly, ops)"
            fullWidth
          />
        </Stack>
      </StyledDialogContent>
      <StyledDialogActions>
        <SecondaryButton variant="outlined" onClick={() => setBulkTagsOpen(false)} disabled={bulkActionLoading}>Cancel</SecondaryButton>
        <PrimaryButton
          onClick={handleBulkTagsApply}
          disabled={bulkActionLoading}
        >
          {bulkActionLoading ? 'Updating...' : 'Add Tags'}
        </PrimaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}
