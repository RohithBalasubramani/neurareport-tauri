/**
 * Upload Document Dialog with dropzone and title input.
 */
import React from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Typography, TextField, Button, Alert, CircularProgress,
} from '@mui/material'
import { CloudUpload as UploadIcon } from '@mui/icons-material'
import { UploadDropzone } from './KnowledgeStyles'

export default function UploadDocumentDialog({
  open, onClose, uploading,
  uploadFile, uploadTitle, onTitleChange,
  onFileSelect, onUpload, selectedCollection,
}) {
  return (
    <Dialog open={open} onClose={() => !uploading && onClose()} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Document</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Upload a document to add it to your knowledge library. Supported formats: PDF, DOCX, TXT, MD, HTML
        </Typography>

        <UploadDropzone
          onClick={() => document.getElementById('document-upload-input')?.click()}
          sx={{ mb: 3 }}
        >
          <input
            id="document-upload-input"
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md,.html"
            onChange={onFileSelect}
            style={{ display: 'none' }}
          />
          <UploadIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
          {uploadFile ? (
            <>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {uploadFile.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {(uploadFile.size / 1024 / 1024).toFixed(2)} MB - Click to change
              </Typography>
            </>
          ) : (
            <>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Click to select a file
              </Typography>
              <Typography variant="body2" color="text.secondary">
                or drag and drop here
              </Typography>
            </>
          )}
        </UploadDropzone>

        <TextField
          fullWidth label="Document Title"
          value={uploadTitle} onChange={(e) => onTitleChange(e.target.value)}
          placeholder="Enter a title for this document" sx={{ mb: 2 }}
        />

        {selectedCollection && (
          <Alert severity="info">
            This document will be added to the &quot;{selectedCollection.name}&quot; collection.
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={uploading}>Cancel</Button>
        <Button
          variant="contained" onClick={onUpload}
          disabled={!uploadFile || uploading}
          startIcon={uploading ? <CircularProgress size={16} /> : <UploadIcon />}
        >
          {uploading ? 'Uploading...' : 'Upload'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
