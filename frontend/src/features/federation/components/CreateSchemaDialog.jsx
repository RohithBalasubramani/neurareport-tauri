/**
 * Dialog for creating a new virtual schema
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  alpha,
} from '@mui/material'
import { Storage as DatabaseIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'

export default function CreateSchemaDialog({
  open,
  onClose,
  connections,
  newSchemaName,
  setNewSchemaName,
  newSchemaDescription,
  setNewSchemaDescription,
  selectedConnections,
  onToggleConnection,
  onCreateSchema,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create Virtual Schema</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Schema Name"
          value={newSchemaName}
          onChange={(e) => setNewSchemaName(e.target.value)}
          sx={{ mt: 2, mb: 2 }}
        />
        <TextField
          fullWidth
          label="Description"
          value={newSchemaDescription}
          onChange={(e) => setNewSchemaDescription(e.target.value)}
          multiline
          rows={2}
          sx={{ mb: 2 }}
        />
        <Typography variant="subtitle2" gutterBottom>
          Select Databases (minimum 2)
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {connections.map((conn) => (
            <Card
              key={conn.id}
              variant="outlined"
              sx={{
                cursor: 'pointer',
                borderColor: selectedConnections.includes(conn.id) ? 'text.secondary' : 'divider',
                bgcolor: selectedConnections.includes(conn.id) ? 'action.selected' : 'background.paper',
              }}
              onClick={() => onToggleConnection(conn.id)}
            >
              <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DatabaseIcon />
                    <Typography>{conn.name}</Typography>
                  </Box>
                  {selectedConnections.includes(conn.id) && (
                    <Chip label="Selected" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={onCreateSchema}
          disabled={!newSchemaName || selectedConnections.length < 2}
        >
          Create
        </Button>
      </DialogActions>
    </Dialog>
  )
}
