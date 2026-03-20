import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Box, Typography, Stack, Button, TextField,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'
import HeaderMappingEditor from '@/features/setup/components/HeaderMappingEditor.jsx'

export default function MappingDialog({
  open,
  onClose,
  templateIframeSrc,
  templateIframeKey,
  previewKind,
  preview,
  connectionId,
  tplName,
  setTplName,
  tplDesc,
  setTplDesc,
  tplTags,
  setTplTags,
  onApprove,
  onCorrectionsComplete,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      aria-labelledby="mapping-dialog-title"
      aria-describedby="mapping-dialog-description"
    >
      <DialogTitle id="mapping-dialog-title">Map Fields</DialogTitle>
      <DialogContent dividers id="mapping-dialog-description">
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: 2,
            alignItems: 'stretch',
          }}
        >
          {/* LEFT: dedicated preview + template meta */}
          <Box
            sx={{
              width: { xs: '100%', md: '50%' },
              flexBasis: { md: '50%' },
              maxWidth: { md: '50%' },
              minWidth: { md: 360 },
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <Stack spacing={2} sx={{ flexGrow: 1, minHeight: 0 }}>
              <Typography variant="subtitle2">Design Preview</Typography>

              <Box
                sx={{
                  width: '100%',
                  alignSelf: 'stretch',
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 2,
                  mb: 2,
                }}
              >
                {templateIframeSrc ? (
                  <Box
                    sx={{
                      width: '100%',
                      maxWidth: { xs: 'min(100%, 620px)', md: 'min(100%, 960px)' },
                      aspectRatio: '210 / 297',
                      maxHeight: {
                        xs: 'min(1440px, calc(260vw), calc(175vh))',
                        md: 'min(2880px, calc(200vw), calc(175vh))',
                      },
                      flexShrink: 0,
                      margin: '0 auto',
                    }}
                  >
                    <ScaledIframePreview
                      key={`${templateIframeKey}-mapping`}
                      title="mapping-template-preview"
                      src={templateIframeSrc}
                      sx={{ width: '100%', height: '100%', overflow: 'hidden', borderRadius: 0 }}
                      frameAspectRatio="210 / 297"
                      fit="width"
                      loading="eager"
                      contentAlign="top"
                      pageShadow
                      pageBorderColor={alpha(neutral[900], 0.08)}
                      clampToParentHeight
                    />
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary" sx={{ px: 2, textAlign: 'center' }}>
                    Upload and verify a design to see the preview here.
                  </Typography>
                )}
              </Box>

              {/* Design Details */}
              <Typography variant="subtitle2">Design Details</Typography>
              <TextField
                label="Design Name"
                size="small"
                value={tplName}
                onChange={(e) => setTplName(e.target.value)}
                fullWidth
              />
              <TextField
                label="Description"
                size="small"
                value={tplDesc}
                onChange={(e) => setTplDesc(e.target.value)}
                fullWidth
              />
              <TextField
                label="Tags (comma separated)"
                size="small"
                value={tplTags}
                onChange={(e) => setTplTags(e.target.value)}
                fullWidth
              />
            </Stack>
          </Box>

          {/* RIGHT: Mapping editor */}
          <Box
            sx={{
              width: { xs: '100%', md: '50%' },
              flexBasis: { md: '50%' },
              maxWidth: { md: '50%' },
              minWidth: 0,
              display: 'flex',
              flexDirection: 'column',
              flexGrow: 1,
            }}
          >
            <Box
              sx={{
                flexGrow: 1,
                minHeight: 0,
                overflow: 'auto',
              }}
            >
              <HeaderMappingEditor
                templateId={preview?.templateId}
                connectionId={connectionId}
                templateKind={previewKind}
                onApproved={(resp) => {
                  onApprove(resp)
                }}
                onCorrectionsComplete={onCorrectionsComplete}
              />
            </Box>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  )
}
