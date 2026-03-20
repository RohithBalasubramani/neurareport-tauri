import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import EnhancedDiffViewer from './EnhancedDiffViewer.jsx'
import KeyboardShortcutsPanel from './KeyboardShortcutsPanel.jsx'
import ConfirmModal from '@/components/modal/ConfirmModal'

export default function EditorDialogs({
  diffOpen,
  setDiffOpen,
  shortcutsOpen,
  setShortcutsOpen,
  modeSwitchConfirm,
  setModeSwitchConfirm,
  initialHtml,
  html,
  dirty,
  saving,
  handleSave,
  saveDraft,
  instructions,
  setEditMode,
  toast,
}) {
  return (
    <>
      {/* Enhanced Diff Dialog */}
      <Dialog
        open={diffOpen}
        onClose={() => setDiffOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '80vh', maxHeight: 800 },
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6">HTML Changes</Typography>
            <Typography variant="caption" color="text.secondary">
              Compare saved version with current edits
            </Typography>
          </Box>
          <Tooltip title="Close">
            <IconButton onClick={() => setDiffOpen(false)} aria-label="Close dialog">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </DialogTitle>
        <DialogContent dividers sx={{ p: 0, display: 'flex', flexDirection: 'column' }}>
          <EnhancedDiffViewer beforeText={initialHtml} afterText={html} contextLines={3} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiffOpen(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              handleSave()
              setDiffOpen(false)
            }}
            disabled={saving || !dirty}
          >
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Keyboard Shortcuts Dialog */}
      <Dialog
        open={shortcutsOpen}
        onClose={() => setShortcutsOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          Keyboard Shortcuts
          <Tooltip title="Close">
            <IconButton onClick={() => setShortcutsOpen(false)} aria-label="Close dialog">
              <CloseIcon />
            </IconButton>
          </Tooltip>
        </DialogTitle>
        <DialogContent>
          <KeyboardShortcutsPanel />
        </DialogContent>
      </Dialog>

      <ConfirmModal
        open={modeSwitchConfirm.open}
        onClose={() => setModeSwitchConfirm({ open: false, nextMode: null })}
        onConfirm={() => {
          if (dirty) {
            saveDraft(html, instructions)
          }
          setModeSwitchConfirm({ open: false, nextMode: null })
          setEditMode(modeSwitchConfirm.nextMode || 'chat')
          toast.show('Draft saved. Your current edits are still available in chat and manual modes.', 'info')
        }}
        title="Switch to Chat Mode"
        message="Switching to chat mode keeps your current edits and saves a draft for manual mode."
        confirmLabel="Switch"
        severity="warning"
      />
    </>
  )
}
