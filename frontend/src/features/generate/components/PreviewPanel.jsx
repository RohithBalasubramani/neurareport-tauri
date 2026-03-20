import {
  Box,
  Stack,
  Typography,
  Tooltip,
  IconButton,
} from '@mui/material'
import FullscreenIcon from '@mui/icons-material/Fullscreen'
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'

export default function PreviewPanel({
  previewUrl,
  templateId,
  previewFullscreen,
  setPreviewFullscreen,
  minHeight = 200,
  fullscreenMinHeight = 500,
}) {
  return (
    <Stack spacing={1.5} sx={{ height: '100%' }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="subtitle1">Preview</Typography>
        <Tooltip title={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
          <IconButton size="small" onClick={() => setPreviewFullscreen(!previewFullscreen)} aria-label={previewFullscreen ? 'Exit fullscreen' : 'Fullscreen preview'}>
            {previewFullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
          </IconButton>
        </Tooltip>
      </Stack>
      {previewUrl ? (
        <Box
          sx={{
            borderRadius: 1.5,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
            p: 1.5,
            minHeight: previewFullscreen ? fullscreenMinHeight : minHeight,
            flex: 1,
            transition: 'min-height 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
          }}
        >
          <ScaledIframePreview
            src={previewUrl}
            title={`Template preview for ${templateId}`}
            fit="contain"
            pageShadow
            frameAspectRatio="210 / 297"
            clampToParentHeight
          />
        </Box>
      ) : (
        <Box
          sx={{
            borderRadius: 1.5,
            border: '1px dashed',
            borderColor: 'divider',
            bgcolor: 'background.default',
            p: 2,
            minHeight,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            No HTML loaded yet.
          </Typography>
        </Box>
      )}
    </Stack>
  )
}
