import { Box, Typography, Stack, Button, CircularProgress } from '@mui/material'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import SchemaIcon from '@mui/icons-material/Schema'
import { alpha } from '@mui/material/styles'
import { neutral, secondary } from '@/app/theme'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import LoadingState from '@/components/feedback/LoadingState.jsx'

export default function FidelityPreview({
  preview,
  file,
  verifying,
  selectedPage,
  pageCount,
  templateIframeSrc,
  templateIframeKey,
  startVerify,
}) {
  return (
    <Stack spacing={2.5} sx={{ mt: 3 }}>
      <Typography
        variant="subtitle2"
        sx={{ color: 'text.secondary', letterSpacing: '0.08em', textTransform: 'uppercase' }}
      >
        Fidelity Preview
      </Typography>
      {preview ? (
        <Box
          sx={{
            display: 'grid',
            gap: { xs: 2, md: 3 },
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          }}
        >
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">
              Reference (Page {selectedPage + 1}{pageCount > 1 ? ` of ${pageCount}` : ''})
            </Typography>
            <Box
              sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'hidden',
                aspectRatio: '210 / 297',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'background.paper',
                boxShadow: `0 16px 38px ${alpha(neutral[900], 0.08)}`,
              }}
            >
              <Box
                component="img"
                alt="Reference page preview"
                src={preview.pngUrl}
                loading="lazy"
                sx={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                  display: 'block',
                }}
              />
            </Box>
          </Stack>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">Generated HTML (preview)</Typography>
            <Box
              sx={{
                position: 'relative',
                aspectRatio: '210 / 297',
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'hidden',
                bgcolor: 'background.paper',
                boxShadow: `0 16px 38px ${alpha(neutral[900], 0.08)}`,
              }}
            >
              {templateIframeSrc ? (
                <>
                  <ScaledIframePreview
                    key={templateIframeKey}
                    src={templateIframeSrc}
                    title="template-preview"
                    frameAspectRatio="210 / 297"
                    loading="eager"
                    contentAlign="top"
                    pageChrome={false}
                    marginGuides={{ inset: 36, color: alpha(secondary.violet[500], 0.3) }}
                    sx={{ width: '100%', height: '100%' }}
                  />
                  {verifying && (
                    <Box
                      sx={{
                        position: 'absolute',
                        inset: 0,
                        zIndex: 1,
                        bgcolor: (theme) => alpha(neutral[900], 0.06),
                        backdropFilter: 'blur(1.5px)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        p: 2,
                      }}
                    >
                      <LoadingState
                        label="Generating preview..."
                        description="We are re-rendering the A4 layout to match the reference PDF."
                        inline
                        dense
                        sx={{ color: 'text.secondary' }}
                      />
                    </Box>
                  )}
                </>
              ) : (
                <Box
                  sx={{
                    height: '100%',
                    width: '100%',
                    borderRadius: 1,
                    border: '1px dashed',
                    borderColor: 'divider',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    px: 2,
                    bgcolor: 'background.paper',
                  }}
                >
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                    No preview yet
                  </Typography>
                </Box>
              )}
            </Box>
          </Stack>
        </Box>
      ) : (
        <EmptyState
          icon={SchemaIcon}
          size="large"
          title="Preview not ready"
          description={file ? 'Verify the design to generate the side-by-side A4 preview.' : 'Upload and verify a design to generate the preview.'}
          action={
            file ? (
              <Button
                variant="contained"
                size="small"
                onClick={startVerify}
                disabled={verifying}
                startIcon={verifying ? <CircularProgress size={16} /> : <TaskAltIcon />}
              >
                {verifying ? 'Verifying...' : 'Verify now'}
              </Button>
            ) : null
          }
          sx={{
            borderStyle: 'solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
            textAlign: 'left',
            alignItems: 'flex-start',
          }}
        />
      )}
    </Stack>
  )
}
