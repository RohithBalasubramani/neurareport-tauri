/**
 * Bulk status update dialog
 */
import {
  Stack,
  Typography,
  MenuItem,
  InputLabel,
  Select,
} from '@mui/material'
import { StyledFormControl } from '@/styles'
import {
  StyledDialog,
  DialogHeader,
  StyledDialogContent,
  StyledDialogActions,
  PrimaryButton,
  SecondaryButton,
} from './TemplateStyledComponents'

export default function BulkStatusDialog({
  bulkStatusOpen,
  setBulkStatusOpen,
  selectedCount,
  bulkStatus,
  setBulkStatus,
  bulkActionLoading,
  handleBulkStatusApply,
}) {
  return (
    <StyledDialog open={bulkStatusOpen} onClose={() => setBulkStatusOpen(false)} maxWidth="xs" fullWidth>
      <DialogHeader>Update Status</DialogHeader>
      <StyledDialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Typography sx={{ fontSize: '14px', color: 'text.secondary' }}>
            Update {selectedCount} design{selectedCount !== 1 ? 's' : ''} to:
          </Typography>
          <StyledFormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={bulkStatus}
              label="Status"
              onChange={(e) => setBulkStatus(e.target.value)}
            >
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </Select>
          </StyledFormControl>
        </Stack>
      </StyledDialogContent>
      <StyledDialogActions>
        <SecondaryButton variant="outlined" onClick={() => setBulkStatusOpen(false)} disabled={bulkActionLoading}>Cancel</SecondaryButton>
        <PrimaryButton
          onClick={handleBulkStatusApply}
          disabled={bulkActionLoading}
        >
          {bulkActionLoading ? 'Updating...' : 'Update'}
        </PrimaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}
