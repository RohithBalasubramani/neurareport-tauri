import Grid from '@mui/material/Grid2'
import { Box, Typography, Button, Divider, Alert } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import EditorSkeleton from './EditorSkeleton.jsx'
import TemplateChatEditor from '../containers/TemplateChatEditor.jsx'
import PreviewPanel from './PreviewPanel.jsx'
import ManualEditorPanel from './ManualEditorPanel.jsx'

export default function EditorContent({
  loading,
  error,
  html,
  setHtml,
  templateId,
  template,
  editMode,
  previewUrl,
  previewFullscreen,
  setPreviewFullscreen,
  instructions,
  setInstructions,
  dirty,
  hasInstructions,
  saving,
  aiBusy,
  undoBusy,
  history,
  referrer,
  handleSave,
  handleApplyAi,
  handleUndo,
  setDiffOpen,
  handleChatHtmlUpdate,
  handleChatApplySuccess,
}) {
  if (!loading && error && !html) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Template Not Found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          The template &ldquo;{templateId}&rdquo; could not be loaded. It may have been deleted or the ID is invalid.
        </Typography>
        <Button variant="contained" component={RouterLink} to="/templates">
          Go to Templates
        </Button>
      </Box>
    )
  }

  if (loading) {
    return (
      <>
        <Divider />
        <EditorSkeleton mode={editMode} />
      </>
    )
  }

  if (editMode === 'chat') {
    return (
      <>
        <Divider />
        <Grid container spacing={2.5} sx={{ alignItems: 'stretch' }}>
          <Grid size={{ xs: 12, md: previewFullscreen ? 12 : 5 }} sx={{ minWidth: 0 }}>
            <PreviewPanel
              previewUrl={previewUrl}
              templateId={templateId}
              previewFullscreen={previewFullscreen}
              setPreviewFullscreen={setPreviewFullscreen}
              minHeight={400}
              fullscreenMinHeight={600}
            />
          </Grid>
          {!previewFullscreen && (
            <Grid size={{ xs: 12, md: 7 }} sx={{ minWidth: 0 }}>
              <Box sx={{ height: 600 }}>
                <TemplateChatEditor
                  templateId={templateId}
                  templateName={template?.name || 'Template'}
                  currentHtml={html}
                  onHtmlUpdate={handleChatHtmlUpdate}
                  onApplySuccess={handleChatApplySuccess}
                />
              </Box>
            </Grid>
          )}
        </Grid>
      </>
    )
  }

  return (
    <>
      <Divider />
      <Grid container spacing={2.5} sx={{ alignItems: 'stretch' }}>
        <Grid size={{ xs: 12, md: previewFullscreen ? 12 : 6 }} sx={{ minWidth: 0 }}>
          <PreviewPanel
            previewUrl={previewUrl}
            templateId={templateId}
            previewFullscreen={previewFullscreen}
            setPreviewFullscreen={setPreviewFullscreen}
          />
        </Grid>
        {!previewFullscreen && (
          <Grid size={{ xs: 12, md: 6 }} sx={{ minWidth: 0 }}>
            <ManualEditorPanel
              html={html}
              setHtml={setHtml}
              instructions={instructions}
              setInstructions={setInstructions}
              dirty={dirty}
              hasInstructions={hasInstructions}
              saving={saving}
              aiBusy={aiBusy}
              undoBusy={undoBusy}
              loading={loading}
              history={history}
              onSave={handleSave}
              onApplyAi={handleApplyAi}
              onUndo={handleUndo}
              onDiffOpen={() => setDiffOpen(true)}
            />
          </Grid>
        )}
      </Grid>
    </>
  )
}
