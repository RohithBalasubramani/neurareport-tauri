/**
 * Validation Editor Dialog
 * Dialog for creating/editing data validation rules.
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
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
} from '@mui/material'
import {
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { ERROR_STYLES } from '../hooks/useDataValidation'
import ValidationCriteriaFields from './ValidationCriteriaFields'

const ERROR_ICON_MAP = { InfoIcon, WarningIcon, ErrorIcon }

export default function ValidationEditorDialog({ open, validation, onClose, onSave }) {
  const [localValidation, setLocalValidation] = useState(validation || {
    type: 'any',
    condition: 'between',
    value1: '',
    value2: '',
    formula: '',
    listValues: [],
    listSource: '',
    ignoreBlank: true,
    showDropdown: true,
    inputTitle: '',
    inputMessage: '',
    errorStyle: 'stop',
    errorTitle: 'Invalid Input',
    errorMessage: 'The value you entered is not valid.',
    range: 'A1:A100',
  })

  const [listInput, setListInput] = useState('')

  const handleChange = (key, value) => {
    setLocalValidation((prev) => ({ ...prev, [key]: value }))
  }

  const handleAddListItem = () => {
    if (listInput.trim()) {
      handleChange('listValues', [...(localValidation.listValues || []), listInput.trim()])
      setListInput('')
    }
  }

  const handleRemoveListItem = (index) => {
    handleChange('listValues', localValidation.listValues.filter((_, i) => i !== index))
  }

  const handleSave = () => {
    onSave?.(localValidation)
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {validation?.id ? 'Edit Validation Rule' : 'New Validation Rule'}
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2.5}>
          <TextField
            label="Apply to Range"
            size="small"
            fullWidth
            value={localValidation.range}
            onChange={(e) => handleChange('range', e.target.value)}
            placeholder="e.g., A1:A100"
          />
          <Divider />
          <ValidationCriteriaFields
            localValidation={localValidation}
            listInput={listInput}
            onListInputChange={setListInput}
            onChange={handleChange}
            onAddListItem={handleAddListItem}
            onRemoveListItem={handleRemoveListItem}
          />
          <Divider />
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Input Message (optional)
          </Typography>
          <TextField
            label="Title"
            size="small"
            fullWidth
            value={localValidation.inputTitle}
            onChange={(e) => handleChange('inputTitle', e.target.value)}
          />
          <TextField
            label="Message"
            size="small"
            fullWidth
            multiline
            rows={2}
            value={localValidation.inputMessage}
            onChange={(e) => handleChange('inputMessage', e.target.value)}
          />
          <Divider />
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Error Alert
          </Typography>
          <FormControl size="small" fullWidth>
            <InputLabel>Style</InputLabel>
            <Select
              value={localValidation.errorStyle}
              label="Style"
              onChange={(e) => handleChange('errorStyle', e.target.value)}
            >
              {ERROR_STYLES.map((style) => {
                const Icon = ERROR_ICON_MAP[style.icon]
                return (
                  <MenuItem key={style.value} value={style.value}>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Icon sx={{ fontSize: 18, color: `${style.color}.main` }} />
                      <span>{style.label}</span>
                    </Stack>
                  </MenuItem>
                )
              })}
            </Select>
          </FormControl>
          <TextField
            label="Error Title"
            size="small"
            fullWidth
            value={localValidation.errorTitle}
            onChange={(e) => handleChange('errorTitle', e.target.value)}
          />
          <TextField
            label="Error Message"
            size="small"
            fullWidth
            multiline
            rows={2}
            value={localValidation.errorMessage}
            onChange={(e) => handleChange('errorMessage', e.target.value)}
          />
          <Alert severity={localValidation.errorStyle === 'stop' ? 'error' : localValidation.errorStyle}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {localValidation.errorTitle}
            </Typography>
            {localValidation.errorMessage}
          </Alert>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          {validation?.id ? 'Save Changes' : 'Add Rule'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
