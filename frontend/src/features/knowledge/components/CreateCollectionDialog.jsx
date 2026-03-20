/**
 * Create Collection Dialog.
 */
import React from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button,
} from '@mui/material'

export default function CreateCollectionDialog({
  open, onClose, name, onNameChange, onCreate,
}) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Create Collection</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus fullWidth label="Collection Name"
          value={name} onChange={(e) => onNameChange(e.target.value)}
          sx={{ mt: 1 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onCreate}>Create</Button>
      </DialogActions>
    </Dialog>
  )
}
