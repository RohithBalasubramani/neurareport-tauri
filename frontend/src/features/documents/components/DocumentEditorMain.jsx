/**
 * Main editor pane with TipTap editor and AI result display.
 */
import {
  Box, Typography, IconButton, Stack,
} from '@mui/material'
import {
  Add as AddIcon, AutoAwesome as AIIcon, Close as CloseIcon,
  Description as DocIcon, ContentCopy as CopyIcon,
} from '@mui/icons-material'
import { useToast } from '@/components/ToastProvider'
import TipTapEditor from './TipTapEditor'
import { EditorPane, EmptyState, AIResultCard, ActionButton } from './DocumentEditorStyles'

export default function DocumentEditorMain({
  currentDocument, editorContent, aiResult, clearAiResult,
  onEditorUpdate, onSelectionChange, onOpenCreateDialog,
}) {
  const toast = useToast()

  if (!currentDocument) {
    return (
      <EmptyState>
        <DocIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
          No Document Selected
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 3 }}>
          Create a new document or select one from the list.
        </Typography>
        <ActionButton
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onOpenCreateDialog}
        >
          Create Document
        </ActionButton>
      </EmptyState>
    )
  }

  return (
    <EditorPane>
      <TipTapEditor
        content={editorContent}
        onUpdate={onEditorUpdate}
        onSelectionChange={onSelectionChange}
        placeholder="Start writing your document..."
      />

      {aiResult && (
        <AIResultCard elevation={0}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
            <Stack direction="row" alignItems="center" spacing={1}>
              <AIIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                AI Result
              </Typography>
            </Stack>
            <IconButton size="small" onClick={() => clearAiResult && clearAiResult()}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Stack>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
            {aiResult.result_text}
          </Typography>
          {aiResult.suggestions?.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                Suggestions:
              </Typography>
              {aiResult.suggestions.map((s, i) => (
                <Typography key={i} variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                  • {s}
                </Typography>
              ))}
            </Box>
          )}
          <Stack direction="row" spacing={1} mt={2}>
            <ActionButton
              size="small"
              variant="outlined"
              startIcon={<CopyIcon />}
              onClick={() => {
                navigator.clipboard.writeText(aiResult.result_text)
                  .then(() => toast.show('Copied to clipboard', 'success'))
                  .catch(() => toast.show('Failed to copy to clipboard', 'error'))
              }}
            >
              Copy
            </ActionButton>
          </Stack>
        </AIResultCard>
      )}
    </EditorPane>
  )
}
