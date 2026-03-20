/**
 * Rule Editor Dialog
 * Dialog for creating/editing conditional formatting rules.
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
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { secondary } from '@/app/theme'
import { RULE_TYPES, CONDITIONS } from '../hooks/useConditionalFormat'
import RuleFormatSettings from './RuleFormatSettings'

export default function RuleEditorDialog({ open, rule, onClose, onSave }) {
  const [localRule, setLocalRule] = useState(rule || {
    type: 'cell_value',
    condition: 'greater_than',
    value1: '',
    value2: '',
    format: {
      fill: secondary.rose[100],
      text: secondary.rose[700],
      bold: false,
      italic: false,
    },
    range: 'A1:Z100',
    priority: 1,
    enabled: true,
  })

  const handleChange = (key, value) => {
    setLocalRule((prev) => ({ ...prev, [key]: value }))
  }

  const handleFormatChange = (key, value) => {
    setLocalRule((prev) => ({
      ...prev,
      format: { ...prev.format, [key]: value },
    }))
  }

  const handleSave = () => {
    onSave?.(localRule)
    onClose()
  }

  const conditions = CONDITIONS[localRule.type] || []
  const needsValue = !['duplicate', 'unique', 'above_below_avg', 'color_scale', 'data_bar', 'icon_set'].includes(localRule.type) &&
    !['yesterday', 'today', 'tomorrow', 'is_blank', 'not_blank'].includes(localRule.condition)
  const needsTwoValues = ['between', 'not_between'].includes(localRule.condition)

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {rule?.id ? 'Edit Formatting Rule' : 'New Formatting Rule'}
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2.5}>
          <TextField
            label="Apply to Range"
            size="small"
            fullWidth
            value={localRule.range}
            onChange={(e) => handleChange('range', e.target.value)}
            placeholder="e.g., A1:Z100"
          />
          <FormControl size="small" fullWidth>
            <InputLabel>Rule Type</InputLabel>
            <Select
              value={localRule.type}
              label="Rule Type"
              onChange={(e) => handleChange('type', e.target.value)}
            >
              {RULE_TYPES.map((type) => (
                <MenuItem key={type.value} value={type.value}>{type.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          {conditions.length > 0 && (
            <FormControl size="small" fullWidth>
              <InputLabel>Condition</InputLabel>
              <Select
                value={localRule.condition}
                label="Condition"
                onChange={(e) => handleChange('condition', e.target.value)}
              >
                {conditions.map((cond) => (
                  <MenuItem key={cond.value} value={cond.value}>{cond.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
          {needsValue && (
            <Stack direction="row" spacing={1}>
              <TextField
                label={needsTwoValues ? 'From' : 'Value'}
                size="small"
                fullWidth
                value={localRule.value1}
                onChange={(e) => handleChange('value1', e.target.value)}
              />
              {needsTwoValues && (
                <TextField
                  label="To"
                  size="small"
                  fullWidth
                  value={localRule.value2}
                  onChange={(e) => handleChange('value2', e.target.value)}
                />
              )}
            </Stack>
          )}
          {localRule.type === 'formula' && (
            <TextField
              label="Formula"
              size="small"
              fullWidth
              value={localRule.formula || ''}
              onChange={(e) => handleChange('formula', e.target.value)}
              placeholder="=$A1>100"
              helperText="Use cell references relative to the first cell in range"
            />
          )}
          <Divider />
          <RuleFormatSettings
            format={localRule.format}
            onFormatChange={handleFormatChange}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          {rule?.id ? 'Save Changes' : 'Add Rule'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
