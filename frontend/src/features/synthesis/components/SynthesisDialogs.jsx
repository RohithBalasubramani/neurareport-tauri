/**
 * All dialogs for SynthesisPage: create session, add document, preview, confirms
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Upload as UploadIcon } from '@mui/icons-material';
import { neutral } from '@/app/theme';
import ConfirmModal from '@/components/modal/ConfirmModal';

const MAX_NAME_LENGTH = 200;
const MAX_DOC_SIZE = 5 * 1024 * 1024;

export default function SynthesisDialogs({
  // Create session dialog
  createDialogOpen,
  onCloseCreateDialog,
  newSessionName,
  onNewSessionNameChange,
  onCreateSession,
  // Add document dialog
  addDocDialogOpen,
  onCloseAddDocDialog,
  docName,
  onDocNameChange,
  docContent,
  onDocContentChange,
  docType,
  onDocTypeChange,
  onFileUpload,
  onAddDocument,
  // Preview dialog
  previewOpen,
  previewDoc,
  onClosePreview,
  // Delete session confirm
  deleteSessionConfirm,
  onCloseDeleteSession,
  onConfirmDeleteSession,
  // Remove document confirm
  removeDocConfirm,
  onCloseRemoveDoc,
  onConfirmRemoveDoc,
}) {
  return (
    <>
      {/* Create Session Dialog */}
      <Dialog open={createDialogOpen} onClose={onCloseCreateDialog}>
        <DialogTitle>Create Synthesis Session</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Session Name"
            value={newSessionName}
            onChange={(e) => onNewSessionNameChange(e.target.value)}
            sx={{ mt: 2 }}
            inputProps={{ maxLength: MAX_NAME_LENGTH }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onCloseCreateDialog}>Cancel</Button>
          <Button variant="contained" onClick={onCreateSession} disabled={!newSessionName}>
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Document Dialog */}
      <Dialog open={addDocDialogOpen} onClose={onCloseAddDocDialog} maxWidth="md" fullWidth>
        <DialogTitle>Add Document</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 2, mb: 2, mt: 2 }}>
            <TextField
              fullWidth
              label="Document Name"
              value={docName}
              onChange={(e) => onDocNameChange(e.target.value)}
              inputProps={{ maxLength: MAX_NAME_LENGTH }}
            />
            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={docType}
                label="Type"
                onChange={(e) => onDocTypeChange(e.target.value)}
              >
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="word">Word</MenuItem>
                <MenuItem value="json">JSON</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadIcon />}
            sx={{ mb: 2 }}
          >
            Upload File
            <input type="file" hidden onChange={onFileUpload} />
          </Button>
          <TextField
            fullWidth
            multiline
            rows={10}
            label="Document Content"
            value={docContent}
            onChange={(e) => onDocContentChange(e.target.value)}
            placeholder="Paste document content or upload a file..."
            inputProps={{ maxLength: MAX_DOC_SIZE }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onCloseAddDocDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={onAddDocument}
            disabled={!docName || !docContent}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Document Dialog */}
      <Dialog open={previewOpen} onClose={onClosePreview} maxWidth="md" fullWidth>
        <DialogTitle>Document Preview</DialogTitle>
        <DialogContent dividers>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            {previewDoc?.name || 'Document'}
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            {previewDoc?.doc_type || previewDoc?.docType || 'text'}
          </Typography>
          <Paper sx={{ p: 2, bgcolor: neutral[50], maxHeight: 420, overflow: 'auto' }}>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {previewDoc?.content || 'No content available.'}
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClosePreview}>Close</Button>
        </DialogActions>
      </Dialog>

      <ConfirmModal
        open={deleteSessionConfirm.open}
        onClose={onCloseDeleteSession}
        onConfirm={onConfirmDeleteSession}
        title="Delete Session"
        message={`Are you sure you want to delete "${deleteSessionConfirm.sessionName}"? All documents and analysis data will be permanently removed.`}
        confirmLabel="Delete"
        severity="error"
      />

      <ConfirmModal
        open={removeDocConfirm.open}
        onClose={onCloseRemoveDoc}
        onConfirm={onConfirmRemoveDoc}
        title="Remove Document"
        message={`Are you sure you want to remove "${removeDocConfirm.docName}" from this session?`}
        confirmLabel="Remove"
        severity="warning"
      />
    </>
  );
}
