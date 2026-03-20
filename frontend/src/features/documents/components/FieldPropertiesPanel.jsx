import { useState } from 'react'
import {
  Box, Typography, TextField, Button, Switch,
  FormControlLabel, Chip, Stack, Divider, alpha,
} from '@mui/material'
import { Add as AddIcon, Settings as SettingsIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { FIELD_TYPES } from './FormBuilder.styles'

export default function FieldPropertiesPanel({ field, onChange }) {
  const hasOptions = ['radio', 'select', 'multiselect', 'checkbox'].includes(field?.type)
  const [optionInput, setOptionInput] = useState('')

  const handleChange = (key, value) => {
    onChange?.({ ...field, [key]: value })
  }

  const handleAddOption = () => {
    if (optionInput.trim()) {
      const options = [...(field.options || []), optionInput.trim()]
      handleChange('options', options)
      setOptionInput('')
    }
  }

  const handleRemoveOption = (index) => {
    const options = field.options.filter((_, i) => i !== index)
    handleChange('options', options)
  }

  if (!field) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <SettingsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          Select a field to edit its properties
        </Typography>
      </Box>
    )
  }

  return (
    <Stack spacing={2.5}>
      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1.5 }}>
          Field Properties
        </Typography>
        <Chip
          label={FIELD_TYPES.find((f) => f.type === field.type)?.label || field.type}
          size="small"
          sx={{ borderRadius: 1, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
        />
      </Box>
      <TextField
        label="Label"
        size="small"
        fullWidth
        value={field.label || ''}
        onChange={(e) => handleChange('label', e.target.value)}
      />

      <TextField
        label="Placeholder"
        size="small"
        fullWidth
        value={field.placeholder || ''}
        onChange={(e) => handleChange('placeholder', e.target.value)}
      />

      <TextField
        label="Description"
        size="small"
        fullWidth
        multiline
        rows={2}
        value={field.description || ''}
        onChange={(e) => handleChange('description', e.target.value)}
      />

      <TextField
        label="Field Name (ID)"
        size="small"
        fullWidth
        value={field.name || ''}
        onChange={(e) => handleChange('name', e.target.value.replace(/\s+/g, '_').toLowerCase())}
        helperText="Used for form submission"
      />

      <Divider />

      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
        Validation
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={field.required || false}
            onChange={(e) => handleChange('required', e.target.checked)}
            size="small"
          />
        }
        label="Required"
      />

      {field.type === 'text' && (
        <>
          <TextField
            label="Min Length"
            size="small"
            type="number"
            value={field.minLength || ''}
            onChange={(e) => handleChange('minLength', parseInt(e.target.value) || undefined)}
          />
          <TextField
            label="Max Length"
            size="small"
            type="number"
            value={field.maxLength || ''}
            onChange={(e) => handleChange('maxLength', parseInt(e.target.value) || undefined)}
          />
          <TextField
            label="Pattern (Regex)"
            size="small"
            fullWidth
            value={field.pattern || ''}
            onChange={(e) => handleChange('pattern', e.target.value)}
            placeholder="e.g., ^[A-Za-z]+$"
          />
        </>
      )}

      {field.type === 'number' && (
        <>
          <TextField
            label="Min Value"
            size="small"
            type="number"
            value={field.min ?? ''}
            onChange={(e) => handleChange('min', parseFloat(e.target.value) || undefined)}
          />
          <TextField
            label="Max Value"
            size="small"
            type="number"
            value={field.max ?? ''}
            onChange={(e) => handleChange('max', parseFloat(e.target.value) || undefined)}
          />
        </>
      )}

      {hasOptions && (
        <>
          <Divider />
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Options
          </Typography>
          <Stack direction="row" spacing={1}>
            <TextField
              size="small"
              fullWidth
              placeholder="Add option..."
              value={optionInput}
              onChange={(e) => setOptionInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddOption()}
            />
            <Button variant="outlined" onClick={handleAddOption} sx={{ minWidth: 40 }}>
              <AddIcon />
            </Button>
          </Stack>
          <Stack spacing={0.5}>
            {(field.options || []).map((opt, i) => (
              <Chip
                key={i}
                label={opt}
                size="small"
                onDelete={() => handleRemoveOption(i)}
                sx={{ justifyContent: 'space-between' }}
              />
            ))}
          </Stack>
        </>
      )}

      <Divider />

      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
        Default Value
      </Typography>

      <TextField
        label="Default Value"
        size="small"
        fullWidth
        value={field.defaultValue || ''}
        onChange={(e) => handleChange('defaultValue', e.target.value)}
      />
    </Stack>
  )
}
