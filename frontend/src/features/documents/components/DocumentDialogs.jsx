/**
 * Dialogs for the Document Editor: Create, Delete, Translate, and Tone.
 */
import {
  Box, Typography, Button, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions,
} from '@mui/material'
import {
  Translate as TranslateIcon,
  FormatColorFill as ToneIcon,
} from '@mui/icons-material'
import TemplateSelector from '@/components/common/TemplateSelector'
import { LANGUAGE_OPTIONS, TONE_OPTIONS } from '../hooks/useDocumentEditor'

export function CreateDocumentDialog({
  open, onClose, newDocName, setNewDocName,
  selectedTemplateId, setSelectedTemplateId,
  onCreateDocument, loading,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 1 } }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Create New Document</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Document Name"
          value={newDocName}
          onChange={(e) => setNewDocName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onCreateDocument()}
          sx={{ mt: 2 }}
        />
        <TemplateSelector
          value={selectedTemplateId}
          onChange={setSelectedTemplateId}
          label="From Template (Optional)"
          size="small"
          showAll
        />
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} data-testid="doc-create-cancel">Cancel</Button>
        <Button
          variant="contained"
          onClick={onCreateDocument}
          disabled={!newDocName.trim() || loading}
          data-testid="doc-create-submit"
        >
          Create
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export function DeleteDocumentDialog({
  open, onClose, docToDelete, onDeleteDocument,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 1 } }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Delete Document</DialogTitle>
      <DialogContent>
        <Typography>
          Are you sure you want to delete "{docToDelete?.name}"? This action cannot be undone.
        </Typography>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} data-testid="doc-delete-cancel">Cancel</Button>
        <Button
          variant="contained"
          sx={{ color: 'text.secondary' }}
          onClick={onDeleteDocument}
          data-testid="doc-delete-confirm"
        >
          Delete
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export function TranslateDialog({
  open, onClose, selectedLanguage, setSelectedLanguage, onTranslate,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 1 } }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Translate Text</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Select the language you want to translate the selected text into.
        </Typography>
        <TextField
          select
          fullWidth
          label="Target Language"
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
        >
          {LANGUAGE_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} data-testid="translate-cancel">Cancel</Button>
        <Button
          variant="contained"
          onClick={onTranslate}
          startIcon={<TranslateIcon />}
          data-testid="translate-submit"
        >
          Translate
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export function ToneDialog({
  open, onClose, selectedTone, setSelectedTone, onAdjustTone,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      PaperProps={{ sx: { borderRadius: 1 } }}
    >
      <DialogTitle sx={{ fontWeight: 600 }}>Adjust Tone</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Select the tone you want to apply to the selected text.
        </Typography>
        <TextField
          select
          fullWidth
          label="Tone"
          value={selectedTone}
          onChange={(e) => setSelectedTone(e.target.value)}
        >
          {TONE_OPTIONS.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              <Box>
                <Typography variant="body2">{option.label}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {option.description}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </TextField>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} data-testid="tone-cancel">Cancel</Button>
        <Button
          variant="contained"
          onClick={onAdjustTone}
          startIcon={<ToneIcon />}
          data-testid="tone-submit"
        >
          Apply Tone
        </Button>
      </DialogActions>
    </Dialog>
  )
}
