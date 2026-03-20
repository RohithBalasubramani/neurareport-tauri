/**
 * Dialog for creating a custom enrichment source.
 */
import React from 'react';
import {
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { SOURCE_TYPES } from '../hooks/useEnrichmentConfig';

export default function CreateSourceDialog({
  open,
  onClose,
  newSourceName,
  setNewSourceName,
  newSourceType,
  setNewSourceType,
  newSourceDescription,
  setNewSourceDescription,
  newSourceCacheTtl,
  setNewSourceCacheTtl,
  onCreateSource,
  loading,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create Custom Enrichment Source</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Source Name"
          value={newSourceName}
          onChange={(e) => setNewSourceName(e.target.value)}
          sx={{ mt: 2, mb: 2 }}
        />
        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Source Type</InputLabel>
          <Select
            value={newSourceType}
            label="Source Type"
            onChange={(e) => setNewSourceType(e.target.value)}
          >
            {SOURCE_TYPES.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          fullWidth
          label="Description"
          value={newSourceDescription}
          onChange={(e) => setNewSourceDescription(e.target.value)}
          multiline
          rows={2}
          sx={{ mb: 2 }}
        />
        <TextField
          fullWidth
          label="Cache TTL (hours)"
          type="number"
          value={newSourceCacheTtl}
          onChange={(e) => setNewSourceCacheTtl(parseInt(e.target.value) || 24)}
          inputProps={{ min: 1, max: 720 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={onCreateSource}
          disabled={!newSourceName.trim() || loading}
        >
          Create
        </Button>
      </DialogActions>
    </Dialog>
  );
}
