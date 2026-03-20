/**
 * Import template backup dialog
 */
import {
  Box,
  Stack,
  Typography,
} from '@mui/material'
import {
  StyledDialog,
  DialogHeader,
  StyledDialogContent,
  StyledDialogActions,
  StyledTextField,
  StyledLinearProgress,
  PrimaryButton,
  SecondaryButton,
} from './TemplateStyledComponents'

export default function ImportDialog({
  importOpen,
  setImportOpen,
  importFile,
  setImportFile,
  importName,
  setImportName,
  importing,
  importProgress,
  handleImport,
}) {
  return (
    <StyledDialog open={importOpen} onClose={() => !importing && setImportOpen(false)} maxWidth="sm" fullWidth>
      <DialogHeader>Import Design Backup</DialogHeader>
      <StyledDialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <SecondaryButton variant="outlined" component="label" disabled={importing}>
            {importFile ? importFile.name : 'Choose backup file (.zip)'}
            <input
              type="file"
              hidden
              accept=".zip"
              onChange={(e) => setImportFile(e.target.files?.[0] || null)}
            />
          </SecondaryButton>
          <StyledTextField
            label="Design Name (optional)"
            value={importName}
            onChange={(e) => setImportName(e.target.value)}
            fullWidth
            disabled={importing}
          />
          {importing && (
            <Box sx={{ width: '100%' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Uploading... {importProgress}%
              </Typography>
              <StyledLinearProgress variant="determinate" value={importProgress} />
            </Box>
          )}
        </Stack>
      </StyledDialogContent>
      <StyledDialogActions>
        <SecondaryButton variant="outlined" onClick={() => setImportOpen(false)} disabled={importing}>Cancel</SecondaryButton>
        <PrimaryButton onClick={handleImport} disabled={importing || !importFile}>
          {importing ? 'Importing...' : 'Import'}
        </PrimaryButton>
      </StyledDialogActions>
    </StyledDialog>
  )
}
