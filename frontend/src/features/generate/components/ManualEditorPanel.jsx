import { forwardRef } from 'react'
import {
  Stack,
  Typography,
  Button,
  TextField,
  CircularProgress,
} from '@mui/material'
import SaveIcon from '@mui/icons-material/Save'
import UndoIcon from '@mui/icons-material/Undo'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import KeyboardShortcutsPanel from './KeyboardShortcutsPanel.jsx'
import EditHistoryTimeline from './EditHistoryTimeline.jsx'
import { getShortcutDisplay } from '../hooks/useTemplateEditor.js'

const FixedTextarea = forwardRef(function FixedTextarea(props, ref) {
  return <textarea {...props} ref={ref} />
})

export default function ManualEditorPanel({
  html,
  setHtml,
  instructions,
  setInstructions,
  dirty,
  hasInstructions,
  saving,
  aiBusy,
  undoBusy,
  loading,
  history,
  onSave,
  onApplyAi,
  onUndo,
  onDiffOpen,
}) {
  return (
    <Stack spacing={1.5} sx={{ height: '100%' }}>
      <Typography variant="subtitle1">HTML &amp; AI Guidance</Typography>

      <TextField
        label="Design HTML"
        value={html}
        onChange={(e) => setHtml(e.target.value)}
        inputProps={{ 'aria-label': 'Template HTML' }}
        multiline
        minRows={10}
        maxRows={24}
        fullWidth
        variant="outlined"
        size="small"
        error={dirty}
        helperText={
          dirty
            ? `Unsaved changes. Press ${getShortcutDisplay('save')} to save.`
            : 'HTML is in sync with the saved template.'
        }
        InputLabelProps={{ shrink: true }}
        sx={{
          '& .MuiInputBase-input': {
            fontFamily: 'monospace',
            fontSize: '14px',
          },
        }}
      />

      <TextField
        label="AI Instructions"
        value={instructions}
        onChange={(e) => setInstructions(e.target.value)}
        multiline
        rows={3}
        InputProps={{ inputComponent: FixedTextarea }}
        fullWidth
        variant="outlined"
        size="small"
        placeholder="Describe how the template should change. AI will preserve tokens and structure unless you ask otherwise."
        helperText={
          hasInstructions
            ? `Press ${getShortcutDisplay('applyAi')} or click Apply to run AI.`
            : 'Enter instructions to enable AI editing.'
        }
        InputLabelProps={{ shrink: true }}
      />

      <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={onSave}
          disabled={saving || loading || !dirty || aiBusy}
          startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
          sx={{ minWidth: 110 }}
        >
          {saving ? 'Saving...' : 'Save'}
        </Button>
        <Button
          variant="outlined"
          onClick={onApplyAi}
          disabled={aiBusy || loading || !hasInstructions}
          startIcon={aiBusy ? <CircularProgress size={16} /> : <AutoFixHighIcon />}
          sx={{ minWidth: 130, color: 'text.secondary', borderColor: 'divider' }}
        >
          {aiBusy ? 'Applying...' : 'Apply AI'}
        </Button>
        <Button
          variant="text"
          color="inherit"
          onClick={onUndo}
          disabled={undoBusy || loading}
          startIcon={undoBusy ? <CircularProgress size={16} /> : <UndoIcon />}
        >
          {undoBusy ? 'Undoing...' : 'Undo'}
        </Button>
        <Button
          variant="text"
          onClick={onDiffOpen}
          disabled={loading || !dirty}
          startIcon={<CompareArrowsIcon />}
          sx={{ color: 'text.secondary' }}
        >
          View Diff
        </Button>
      </Stack>

      <Typography variant="caption" color="text.secondary">
        AI edits are generated and may need review before use in production runs.
      </Typography>

      <KeyboardShortcutsPanel compact />

      <EditHistoryTimeline history={history} maxVisible={5} />
    </Stack>
  )
}
