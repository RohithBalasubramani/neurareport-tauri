import { Box, Typography, Stack, Button, List, ListItem, ListItemText, LinearProgress, Alert } from '@mui/material'
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined'
import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { useTemplateUpload } from '../hooks/useTemplateUpload'

export default function UploadTemplate() {
  const state = useTemplateUpload()

  return (
    <Surface>
      <Stack direction="row" alignItems="center" spacing={0.75} sx={{ mb: 2 }}>
        <Typography variant="h6">Upload & Verify Template</Typography>
        <InfoTooltip
          content={TOOLTIP_COPY.uploadTemplate}
          ariaLabel="Upload and verify guidance"
        />
      </Stack>
      <Stack spacing={2}>
        <Box
          onDrop={state.handleDrop}
          onDragOver={state.handleDragOver}
          onDragEnter={state.handleDragEnter}
          onDragLeave={state.handleDragLeave}
          role="button"
          tabIndex={0}
          onClick={() => state.inputRef.current?.click()}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault()
              state.inputRef.current?.click()
            }
          }}
          sx={{
            border: '1px dashed',
            borderColor: state.isDragging ? 'text.secondary' : 'divider',
            borderRadius: 1,  // Figma spec: 8px
            p: 3,
            textAlign: 'center',
            bgcolor: state.isDragging ? 'action.hover' : 'transparent',
            cursor: 'pointer',
            transition: 'all 160ms cubic-bezier(0.22, 1, 0.36, 1)',
          }}
        >
          <CloudUploadOutlinedIcon sx={{ mb: 1, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            Drag & drop a PDF or Excel template here, or click to browse
          </Typography>
          <input
            ref={state.inputRef}
            hidden
            accept=".pdf,.xls,.xlsx"
            type="file"
            onChange={state.onFileChange}
          />
        </Box>

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems="center">
          <Button
            variant="contained"
            onClick={state.handleUpload}
            disabled={!state.files.length || state.uploading}
          >
            {state.uploading ? 'Uploading...' : 'Upload & Verify'}
          </Button>
          {state.uploading && (
            <Box sx={{ flex: 1, width: '100%' }}>
              <LinearProgress variant="determinate" value={state.uploadProgress} />
            </Box>
          )}
        </Stack>

        {state.error && <Alert severity="error">{state.error}</Alert>}
        {state.result?.template_id && (
          <Alert severity="success">
            Verified template ID: {state.result.template_id}
          </Alert>
        )}
      </Stack>
      {!!state.files.length && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Selected</Typography>
          <List dense>
            {state.files.map((f) => (
              <ListItem key={f.name} disableGutters>
                <ListItemText primary={f.name} secondary={`${(f.size/1024).toFixed(1)} KB`} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Surface>
  )
}
