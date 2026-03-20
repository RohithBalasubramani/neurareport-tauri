import { Box, Dialog, DialogContent, DialogTitle } from '@mui/material'
import ScaledIframePreview from '@/components/ScaledIframePreview.jsx'

export default function TemplatePreviewDialog({ open, onClose, src, type, previewKey }) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      aria-labelledby="template-preview-title"
      PaperProps={{
        sx: {
          height: '90vh',
          bgcolor: 'background.default',
        },
      }}
    >
      <DialogTitle id="template-preview-title">Template Preview</DialogTitle>
      <DialogContent
        dividers
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-start',
          overflow: 'auto',
          bgcolor: 'background.default',
        }}
      >
        {src && type === 'html' ? (
          <Box
            sx={{
              width: '100%',
              maxWidth: 1120,
              mx: 'auto',
              bgcolor: 'background.paper',
              borderRadius: 1,
              boxShadow: 2,
              border: '1px solid',
              borderColor: 'divider',
              overflow: 'auto',
              p: 2,
            }}
          >
            <ScaledIframePreview key={previewKey || src} src={src} title="Template HTML preview" sx={{ width: '100%', height: '100%' }} loading="eager" />
          </Box>
        ) : src ? (
          <Box
            component="img"
            src={src}
            alt="Template preview"
            sx={{
              display: 'block',
              width: '100%',
              maxWidth: 1120,
              height: 'auto',
              mx: 'auto',
              borderRadius: 1,
              boxShadow: 2,
            }}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  )
}
