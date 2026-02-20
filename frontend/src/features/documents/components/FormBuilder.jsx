/**
 * Form Builder Component
 * Drag-and-drop form field builder for creating interactive document forms.
 */
import { useState, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Chip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  DragIndicator as DragIcon,
  TextFields as TextIcon,
  Numbers as NumberIcon,
  CalendarToday as DateIcon,
  CheckBox as CheckboxIcon,
  RadioButtonChecked as RadioIcon,
  ArrowDropDownCircle as SelectIcon,
  Upload as FileIcon,
  TextSnippet as TextAreaIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Link as UrlIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  ContentCopy as DuplicateIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Preview as PreviewIcon,
  Save as SaveIcon,
} from '@mui/icons-material'
import { neutral, palette, status } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const BuilderContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: '100%',
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const FieldPalette = styled(Box)(({ theme }) => ({
  width: 280,
  padding: theme.spacing(2),
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

const FormCanvas = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflowY: 'auto',
}))

const PropertyPanel = styled(Box)(({ theme }) => ({
  width: 320,
  padding: theme.spacing(2),
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  overflowY: 'auto',
}))

const FieldCard = styled(Paper, {
  shouldForwardProp: (prop) => !['isSelected', 'isDragging'].includes(prop),
})(({ theme, isSelected, isDragging }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${
    isSelected
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[900])
      : alpha(theme.palette.divider, 0.2)
  }`,
  backgroundColor: isDragging
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50])
    : theme.palette.background.paper,
  cursor: 'grab',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, 0.1)}`,
  },
}))

const PaletteItem = styled(ListItemButton)(({ theme }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const SectionHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 0),
  marginBottom: theme.spacing(1),
}))

// =============================================================================
// FIELD TYPES CONFIGURATION
// =============================================================================

const FIELD_TYPES = [
  { type: 'text', label: 'Text Input', icon: TextIcon, category: 'basic' },
  { type: 'textarea', label: 'Text Area', icon: TextAreaIcon, category: 'basic' },
  { type: 'number', label: 'Number', icon: NumberIcon, category: 'basic' },
  { type: 'email', label: 'Email', icon: EmailIcon, category: 'basic' },
  { type: 'phone', label: 'Phone', icon: PhoneIcon, category: 'basic' },
  { type: 'url', label: 'URL', icon: UrlIcon, category: 'basic' },
  { type: 'date', label: 'Date', icon: DateIcon, category: 'datetime' },
  { type: 'time', label: 'Time', icon: DateIcon, category: 'datetime' },
  { type: 'datetime', label: 'Date & Time', icon: DateIcon, category: 'datetime' },
  { type: 'checkbox', label: 'Checkbox', icon: CheckboxIcon, category: 'choice' },
  { type: 'radio', label: 'Radio Group', icon: RadioIcon, category: 'choice' },
  { type: 'select', label: 'Dropdown', icon: SelectIcon, category: 'choice' },
  { type: 'multiselect', label: 'Multi-Select', icon: SelectIcon, category: 'choice' },
  { type: 'file', label: 'File Upload', icon: FileIcon, category: 'advanced' },
  { type: 'signature', label: 'Signature', icon: EditIcon, category: 'advanced' },
]

const FIELD_CATEGORIES = [
  { id: 'basic', label: 'Basic Fields' },
  { id: 'datetime', label: 'Date & Time' },
  { id: 'choice', label: 'Choice Fields' },
  { id: 'advanced', label: 'Advanced' },
]

// =============================================================================
// FIELD PREVIEW COMPONENT
// =============================================================================

function FieldPreview({ field, isSelected, onClick, onDelete, onDuplicate }) {
  const theme = useTheme()
  const FieldIcon = FIELD_TYPES.find((f) => f.type === field.type)?.icon || TextIcon

  const renderFieldInput = () => {
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
          {renderFieldInput()}
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

// =============================================================================
// FIELD PROPERTIES PANEL
// =============================================================================

function FieldPropertiesPanel({ field, onChange }) {
  const theme = useTheme()
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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function FormBuilder({
  fields = [],
  onFieldsChange,
  onSave,
  formTitle = 'Untitled Form',
  onTitleChange,
  readOnly = false,
}) {
  const theme = useTheme()
  const [selectedFieldId, setSelectedFieldId] = useState(null)
  const [expandedCategories, setExpandedCategories] = useState(['basic', 'choice'])
  const [previewOpen, setPreviewOpen] = useState(false)

  const selectedField = useMemo(
    () => fields.find((f) => f.id === selectedFieldId),
    [fields, selectedFieldId]
  )

  // Toggle category expansion
  const toggleCategory = useCallback((categoryId) => {
    setExpandedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((c) => c !== categoryId)
        : [...prev, categoryId]
    )
  }, [])

  // Add new field
  const handleAddField = useCallback((fieldType) => {
    const newField = {
      id: `field_${Date.now()}`,
      type: fieldType.type,
      label: `New ${fieldType.label}`,
      name: `field_${Date.now()}`,
      required: false,
      options: ['radio', 'select', 'multiselect'].includes(fieldType.type)
        ? ['Option 1', 'Option 2']
        : undefined,
    }
    onFieldsChange?.([...fields, newField])
    setSelectedFieldId(newField.id)
  }, [fields, onFieldsChange])

  // Update field
  const handleUpdateField = useCallback((updatedField) => {
    onFieldsChange?.(
      fields.map((f) => (f.id === updatedField.id ? updatedField : f))
    )
  }, [fields, onFieldsChange])

  // Delete field
  const handleDeleteField = useCallback((fieldId) => {
    onFieldsChange?.(fields.filter((f) => f.id !== fieldId))
    if (selectedFieldId === fieldId) {
      setSelectedFieldId(null)
    }
  }, [fields, onFieldsChange, selectedFieldId])

  // Duplicate field
  const handleDuplicateField = useCallback((fieldId) => {
    const field = fields.find((f) => f.id === fieldId)
    if (field) {
      const newField = {
        ...field,
        id: `field_${Date.now()}`,
        name: `${field.name}_copy`,
        label: `${field.label} (Copy)`,
      }
      const index = fields.findIndex((f) => f.id === fieldId)
      const newFields = [...fields]
      newFields.splice(index + 1, 0, newField)
      onFieldsChange?.(newFields)
      setSelectedFieldId(newField.id)
    }
  }, [fields, onFieldsChange])

  return (
    <BuilderContainer>
      {/* Field Palette */}
      <FieldPalette>
        <SectionHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Form Fields
          </Typography>
        </SectionHeader>

        {FIELD_CATEGORIES.map((category) => {
          const categoryFields = FIELD_TYPES.filter((f) => f.category === category.id)
          const isExpanded = expandedCategories.includes(category.id)

          return (
            <Box key={category.id} sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => toggleCategory(category.id)}
                sx={{ borderRadius: 1, py: 0.5, px: 1 }}
              >
                <ListItemText
                  primary={category.label}
                  primaryTypographyProps={{ variant: 'body2', fontWeight: 600 }}
                />
                {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
              </ListItemButton>

              <Collapse in={isExpanded}>
                <List dense disablePadding sx={{ pl: 1, pr: 0.5 }}>
                  {categoryFields.map((fieldType) => {
                    const Icon = fieldType.icon
                    return (
                      <PaletteItem
                        key={fieldType.type}
                        onClick={() => !readOnly && handleAddField(fieldType)}
                        disabled={readOnly}
                      >
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={fieldType.label}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </PaletteItem>
                    )
                  })}
                </List>
              </Collapse>
            </Box>
          )
        })}
      </FieldPalette>

      {/* Form Canvas */}
      <FormCanvas>
        <Paper
          elevation={0}
          sx={{
            maxWidth: 720,
            mx: 'auto',
            p: 3,
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            borderRadius: 1,  // Figma spec: 8px
          }}
        >
          {/* Form Header */}
          <Stack direction="row" alignItems="center" justifyContent="space-between" mb={3}>
            <TextField
              value={formTitle}
              onChange={(e) => onTitleChange?.(e.target.value)}
              variant="standard"
              disabled={readOnly}
              InputProps={{
                sx: { fontSize: '1.5rem', fontWeight: 600 },
                disableUnderline: readOnly,
              }}
            />
            <Stack direction="row" spacing={1}>
              <Tooltip title="Preview">
                <IconButton onClick={() => setPreviewOpen(true)}>
                  <PreviewIcon />
                </IconButton>
              </Tooltip>
              {!readOnly && (
                <Tooltip title="Save">
                  <IconButton onClick={onSave} sx={{ color: 'text.secondary' }}>
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Stack>
          </Stack>

          <Divider sx={{ mb: 3 }} />

          {/* Form Fields */}
          {fields.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <AddIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Drag fields from the palette to build your form
              </Typography>
              <Typography variant="body2" color="text.disabled">
                or click a field type to add it
              </Typography>
            </Box>
          ) : (
            fields.map((field) => (
              <FieldPreview
                key={field.id}
                field={field}
                isSelected={selectedFieldId === field.id}
                onClick={() => setSelectedFieldId(field.id)}
                onDelete={() => handleDeleteField(field.id)}
                onDuplicate={() => handleDuplicateField(field.id)}
              />
            ))
          )}
        </Paper>
      </FormCanvas>

      {/* Properties Panel */}
      <PropertyPanel>
        <SectionHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Properties
          </Typography>
        </SectionHeader>

        <FieldPropertiesPanel
          field={selectedField}
          onChange={handleUpdateField}
        />
      </PropertyPanel>

      {/* Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{formTitle}</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2}>
            {fields.map((field) => (
              <Box key={field.id}>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  {field.label}
                  {field.required && <span style={{ color: status.destructive }}> *</span>}
                </Typography>
                {field.description && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    {field.description}
                  </Typography>
                )}
                {field.type === 'textarea' ? (
                  <TextField fullWidth multiline rows={3} size="small" placeholder={field.placeholder} />
                ) : field.type === 'select' ? (
                  <FormControl fullWidth size="small">
                    <Select defaultValue="">
                      <MenuItem value="">Select...</MenuItem>
                      {(field.options || []).map((opt, i) => (
                        <MenuItem key={i} value={opt}>{opt}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ) : field.type === 'checkbox' ? (
                  <FormControlLabel control={<Switch />} label={field.options?.[0] || 'Enable'} />
                ) : (
                  <TextField fullWidth size="small" type={field.type} placeholder={field.placeholder} />
                )}
              </Box>
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>Close</Button>
          <Button variant="contained">Submit</Button>
        </DialogActions>
      </Dialog>
    </BuilderContainer>
  )
}
