import { useState, useEffect } from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Collapse,
  alpha,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import ScaledIframePreview from '@/components/ScaledIframePreview'
import { neutral } from '@/app/theme'

export default function ProposedChangesPanel({ changes, proposedHtml, onApply, onReject, applying }) {
  const [showPreview, setShowPreview] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)

  useEffect(() => {
    if (!proposedHtml) {
      setPreviewUrl(null)
      return
    }
    const blob = new Blob([proposedHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    setPreviewUrl(url)
    return () => {
      URL.revokeObjectURL(url)
    }
  }, [proposedHtml])

  if (!changes || changes.length === 0) return null

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        mx: 2,
        mb: 2,
        borderRadius: 1,  // Figma spec: 8px
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.divider, 0.3),
        bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
      }}
    >
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <CheckCircleIcon sx={{ color: 'text.secondary' }} fontSize="small" />
          <Typography variant="subtitle2" fontWeight={600}>
            Ready to Apply Changes
          </Typography>
        </Stack>

        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Proposed modifications:
          </Typography>
          <Stack spacing={0.5}>
            {changes.map((change, idx) => (
              <Stack key={idx} direction="row" spacing={1} alignItems="flex-start">
                <Typography variant="body2" color="text.secondary">
                  •
                </Typography>
                <Typography variant="body2">
                  {change}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </Box>

        {proposedHtml && (
          <Box>
            <Button
              size="small"
              variant="text"
              onClick={() => setShowPreview(!showPreview)}
              endIcon={showPreview ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ mb: 1 }}
            >
              {showPreview ? 'Hide Preview' : 'Show Preview'}
            </Button>
            <Collapse in={showPreview}>
              <Box
                sx={{
                  borderRadius: 1,  // Figma spec: 8px
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'background.paper',
                  p: 1,
                  height: 300,
                  overflow: 'hidden',
                }}
              >
                {previewUrl && (
                  <ScaledIframePreview
                    src={previewUrl}
                    title="Proposed changes preview"
                    fit="contain"
                    pageShadow
                    frameAspectRatio="210 / 297"
                  />
                )}
              </Box>
            </Collapse>
          </Box>
        )}

        <Stack direction="row" spacing={1.5}>
          <Button
            variant="contained"
            onClick={onApply}
            disabled={applying}
            startIcon={applying ? <CircularProgress size={16} /> : <CheckCircleIcon />}
          >
            {applying ? 'Applying...' : 'Apply Changes'}
          </Button>
          <Button
            variant="outlined"
            color="inherit"
            onClick={onReject}
            disabled={applying}
          >
            Request Different Changes
          </Button>
        </Stack>
      </Stack>
    </Paper>
  )
}
