import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  Switch,
  FormControlLabel,
  Stack,
  useTheme,
} from '@mui/material'
import {
  DragIndicator as DragIcon,
  TextFields as TextIcon,
  Upload as FileIcon,
  ContentCopy as DuplicateIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { RadioButtonChecked as RadioIcon } from '@mui/icons-material'
import { FieldCard, FIELD_TYPES } from './FormBuilder.styles'

function FieldInput({ field }) {
  switch (field.type) {
    case 'textarea':
      return (
        <TextField
          size="small"
          fullWidth
          multiline
          rows={3}
          placeholder={field.placeholder || 'Enter text...'}
          disabled
        />
      )
    case 'checkbox':
      return (
        <FormControlLabel
          control={<Switch disabled />}
          label={field.options?.[0] || 'Option'}
        />
      )
    case 'radio':
      return (
        <Stack spacing={0.5}>
          {(field.options || ['Option 1', 'Option 2']).slice(0, 3).map((opt, i) => (
            <FormControlLabel
              key={i}
              control={<RadioIcon sx={{ mr: 1, color: 'text.disabled' }} />}
              label={opt}
            />
          ))}
        </Stack>
      )
    case 'select':
    case 'multiselect':
      return (
        <FormControl size="small" fullWidth disabled>
          <Select value="">
            <MenuItem value="">Select...</MenuItem>
          </Select>
        </FormControl>
      )
    case 'file':
      return (
        <Button variant="outlined" startIcon={<FileIcon />} disabled size="small">
          Choose File
        </Button>
      )
    default:
      return (
        <TextField
          size="small"
          fullWidth
          type={field.type === 'number' ? 'number' : 'text'}
          placeholder={field.placeholder || `Enter ${field.type}...`}
          disabled
        />
      )
  }
}

export default function FieldPreview({ field, isSelected, onClick, onDelete, onDuplicate }) {
  const FieldIcon = FIELD_TYPES.find((f) => f.type === field.type)?.icon || TextIcon

  return (
    <FieldCard
      elevation={0}
      isSelected={isSelected}
      onClick={onClick}
    >
      <Stack direction="row" alignItems="flex-start" spacing={1}>
        <DragIcon sx={{ color: 'text.disabled', mt: 0.5, cursor: 'grab' }} />
        <Box sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1} mb={1}>
            <FieldIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {field.label || 'Untitled Field'}
              {field.required && (
                <Typography component="span" color="text.primary" sx={{ ml: 0.5 }}>
                  *
                </Typography>
              )}
            </Typography>
          </Stack>
          {field.description && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
              {field.description}
            </Typography>
          )}
          <FieldInput field={field} />
        </Box>
        <Stack direction="row" spacing={0.5} sx={{ opacity: isSelected ? 1 : 0.5 }}>
          <Tooltip title="Duplicate">
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); onDuplicate?.() }}>
              <DuplicateIcon sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); onDelete?.() }}>
              <DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>
    </FieldCard>
  )
}
