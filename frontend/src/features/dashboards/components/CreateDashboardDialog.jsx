/**
 * Create Dashboard Dialog.
 */
import React from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button,
} from '@mui/material'
import ConnectionSelector from '@/components/common/ConnectionSelector'

export default function CreateDashboardDialog({
  open, onClose, loading,
  name, onNameChange,
  selectedConnectionId, onConnectionChange,
  onCreate,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Create New Dashboard</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Dashboard Name"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          sx={{ mt: 2 }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && name) onCreate()
          }}
        />
        <ConnectionSelector
          value={selectedConnectionId}
          onChange={onConnectionChange}
          label="Data Source (optional)"
          showStatus
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onCreate} disabled={!name || loading}>
          Create
        </Button>
      </DialogActions>
    </Dialog>
  )
}
