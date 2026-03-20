/**
 * Edit template metadata dialog
 */
import {
  Stack,
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
  StyledTextField,
  PrimaryButton,
  SecondaryButton,
} from './TemplateStyledComponents'

export default function MetadataDialog({
  metadataOpen,
  setMetadataOpen,
  metadataForm,
  setMetadataForm,
  metadataSaving,
  handleMetadataSave,
}) {
  return (
    <StyledDialog open={metadataOpen} onClose={() => setMetadataOpen(false)} maxWidth="sm" fullWidth>
      <DialogHeader>Edit Design Details</DialogHeader>
      <StyledDialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <StyledTextField
            label="Name"
            value={metadataForm.name}
            onChange={(e) => setMetadataForm((prev) => ({ ...prev, name: e.target.value }))}
            fullWidth
          />
          <StyledTextField
            label="Description"
            value={metadataForm.description}
            onChange={(e) => setMetadataForm((prev) => ({ ...prev, description: e.target.value }))}
            multiline
            minRows={2}
            fullWidth
          />
          <StyledTextField
            label="Tags"
            value={metadataForm.tags}
            onChange={(e) => setMetadataForm((prev) => ({ ...prev, tags: e.target.value }))}
            helperText="Comma-separated (e.g. finance, monthly, ops)"
            fullWidth
          />
          <StyledFormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={metadataForm.status}
              label="Status"
              onChange={(e) => setMetadataForm((prev) => ({ ...prev, status: e.target.value }))}
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
        <SecondaryButton variant="outlined" onClick={() => setMetadataOpen(false)} disabled={metadataSaving}>Cancel</SecondaryButton>
        <PrimaryButton
          onClick={handleMetadataSave}
          disabled={metadataSaving || !metadataForm.name.trim()}
        >
          {metadataSaving ? 'Saving...' : 'Save'}
        </PrimaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}
