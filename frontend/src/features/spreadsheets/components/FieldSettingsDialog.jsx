/**
 * Field Settings Dialog
 * Dialog for configuring pivot table field settings.
 */
import { useState } from 'react'
import {
  Stack,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { AGGREGATIONS, SORT_OPTIONS } from '../hooks/usePivotTableBuilder'

export default function FieldSettingsDialog({ open, field, zone, onClose, onSave }) {
  const [localField, setLocalField] = useState(field || {})

  const handleChange = (key, value) => {
    setLocalField((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    onSave?.(localField)
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>Field Settings: {field?.name}</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2}>
          {zone === 'values' && (
            <>
              <FormControl size="small" fullWidth>
                <InputLabel>Summarize by</InputLabel>
                <Select
                  value={localField.aggregation || 'sum'}
                  label="Summarize by"
                  onChange={(e) => handleChange('aggregation', e.target.value)}
                >
                  {AGGREGATIONS.map((agg) => (
                    <MenuItem key={agg.value} value={agg.value}>
                      {agg.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Custom Name"
                size="small"
                fullWidth
                value={localField.customName || ''}
                onChange={(e) => handleChange('customName', e.target.value)}
                placeholder={`${localField.aggregation || 'Sum'} of ${localField.name}`}
              />

              <FormControl size="small" fullWidth>
                <InputLabel>Number Format</InputLabel>
                <Select
                  value={localField.format || 'general'}
                  label="Number Format"
                  onChange={(e) => handleChange('format', e.target.value)}
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="number">Number (1,234.56)</MenuItem>
                  <MenuItem value="currency">Currency ($1,234.56)</MenuItem>
                  <MenuItem value="percent">Percentage (12.34%)</MenuItem>
                  <MenuItem value="scientific">Scientific (1.23E+03)</MenuItem>
                </Select>
              </FormControl>
            </>
          )}

          {(zone === 'rows' || zone === 'columns') && (
            <>
              <FormControl size="small" fullWidth>
                <InputLabel>Sort</InputLabel>
                <Select
                  value={localField.sort || 'none'}
                  label="Sort"
                  onChange={(e) => handleChange('sort', e.target.value)}
                >
                  {SORT_OPTIONS.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <TextField
                label="Custom Name"
                size="small"
                fullWidth
                value={localField.customName || ''}
                onChange={(e) => handleChange('customName', e.target.value)}
              />
            </>
          )}

          {zone === 'filters' && (
            <>
              <Typography variant="body2" color="text.secondary">
                Select values to include:
              </Typography>
              <Alert severity="info">
                Filter configuration coming soon
              </Alert>
            </>
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  )
}
