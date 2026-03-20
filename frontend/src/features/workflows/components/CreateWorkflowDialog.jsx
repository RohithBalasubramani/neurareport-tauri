/**
 * Create workflow dialog
 */
import React from 'react'
import {
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'

export default function CreateWorkflowDialog({
  open,
  onClose,
  workflowName,
  onWorkflowNameChange,
  selectedConnectionId,
  onConnectionChange,
  selectedTemplateId,
  onTemplateChange,
  onCreateWorkflow,
  loading,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
    >
      <DialogTitle>Create New Workflow</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Workflow Name"
          value={workflowName}
          onChange={(e) => onWorkflowNameChange(e.target.value)}
          sx={{ mt: 2 }}
        />
        <ConnectionSelector
          value={selectedConnectionId}
          onChange={onConnectionChange}
          label="Database Connection"
          size="small"
          sx={{ mt: 2 }}
        />
        <TemplateSelector
          value={selectedTemplateId}
          onChange={onTemplateChange}
          label="Report Template"
          size="small"
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={onCreateWorkflow}
          disabled={!workflowName || loading}
        >
          Create
        </Button>
      </DialogActions>
    </Dialog>
  )
}
