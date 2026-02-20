/**
 * Data Validation Panel
 * UI for creating and managing data validation rules in spreadsheets.
 */
import { useState, useCallback } from 'react'
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
  Stack,
  Divider,
  Chip,
  Switch,
  FormControlLabel,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  VerifiedUser as ValidationIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Numbers as NumberIcon,
  TextFields as TextIcon,
  CalendarToday as DateIcon,
  List as ListIcon,
  Functions as FormulaIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 360,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const RuleCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const TypeChip = styled(Chip)(({ theme }) => ({
  borderRadius: 4,
  height: 24,
  fontSize: '12px',
  fontWeight: 600,
}))

// =============================================================================
// VALIDATION TYPES AND CONDITIONS
// =============================================================================

const VALIDATION_TYPES = [
  { value: 'any', label: 'Any Value', icon: InfoIcon },
  { value: 'whole_number', label: 'Whole Number', icon: NumberIcon },
  { value: 'decimal', label: 'Decimal', icon: NumberIcon },
  { value: 'list', label: 'List', icon: ListIcon },
  { value: 'date', label: 'Date', icon: DateIcon },
  { value: 'time', label: 'Time', icon: DateIcon },
  { value: 'text_length', label: 'Text Length', icon: TextIcon },
  { value: 'custom', label: 'Custom Formula', icon: FormulaIcon },
]

const NUMBER_CONDITIONS = [
  { value: 'between', label: 'between' },
  { value: 'not_between', label: 'not between' },
  { value: 'equal', label: 'equal to' },
  { value: 'not_equal', label: 'not equal to' },
  { value: 'greater', label: 'greater than' },
  { value: 'less', label: 'less than' },
  { value: 'greater_equal', label: 'greater than or equal to' },
  { value: 'less_equal', label: 'less than or equal to' },
]

const DATE_CONDITIONS = [
  { value: 'between', label: 'between' },
  { value: 'not_between', label: 'not between' },
  { value: 'equal', label: 'equal to' },
  { value: 'before', label: 'before' },
  { value: 'after', label: 'after' },
]

const ERROR_STYLES = [
  { value: 'stop', label: 'Stop', icon: ErrorIcon, color: 'error' },
  { value: 'warning', label: 'Warning', icon: WarningIcon, color: 'warning' },
  { value: 'info', label: 'Information', icon: InfoIcon, color: 'info' },
]

// =============================================================================
// VALIDATION EDITOR DIALOG
// =============================================================================

function ValidationEditorDialog({ open, validation, onClose, onSave }) {
  const theme = useTheme()
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

  const validationType = VALIDATION_TYPES.find((t) => t.value === localValidation.type)
  const needsCondition = ['whole_number', 'decimal', 'date', 'time', 'text_length'].includes(localValidation.type)
  const conditions = ['date', 'time'].includes(localValidation.type) ? DATE_CONDITIONS : NUMBER_CONDITIONS
  const needsTwoValues = ['between', 'not_between'].includes(localValidation.condition)

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {validation?.id ? 'Edit Validation Rule' : 'New Validation Rule'}
      </DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2.5}>
          {/* Range */}
          <TextField
            label="Apply to Range"
            size="small"
            fullWidth
            value={localValidation.range}
            onChange={(e) => handleChange('range', e.target.value)}
            placeholder="e.g., A1:A100"
          />

          <Divider />

          {/* Validation Type */}
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Criteria
          </Typography>

          <FormControl size="small" fullWidth>
            <InputLabel>Allow</InputLabel>
            <Select
              value={localValidation.type}
              label="Allow"
              onChange={(e) => handleChange('type', e.target.value)}
            >
              {VALIDATION_TYPES.map((type) => {
                const Icon = type.icon
                return (
                  <MenuItem key={type.value} value={type.value}>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Icon sx={{ fontSize: 18, color: 'text.secondary' }} />
                      <span>{type.label}</span>
                    </Stack>
                  </MenuItem>
                )
              })}
            </Select>
          </FormControl>

          {/* Condition for numeric/date types */}
          {needsCondition && (
            <FormControl size="small" fullWidth>
              <InputLabel>Data</InputLabel>
              <Select
                value={localValidation.condition}
                label="Data"
                onChange={(e) => handleChange('condition', e.target.value)}
              >
                {conditions.map((cond) => (
                  <MenuItem key={cond.value} value={cond.value}>
                    {cond.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          {/* Values for numeric/date types */}
          {needsCondition && (
            <Stack direction="row" spacing={1}>
              <TextField
                label={needsTwoValues ? 'Minimum' : 'Value'}
                size="small"
                fullWidth
                type={['date', 'time'].includes(localValidation.type) ? localValidation.type : 'number'}
                value={localValidation.value1}
                onChange={(e) => handleChange('value1', e.target.value)}
              />
              {needsTwoValues && (
                <TextField
                  label="Maximum"
                  size="small"
                  fullWidth
                  type={['date', 'time'].includes(localValidation.type) ? localValidation.type : 'number'}
                  value={localValidation.value2}
                  onChange={(e) => handleChange('value2', e.target.value)}
                />
              )}
            </Stack>
          )}

          {/* List values */}
          {localValidation.type === 'list' && (
            <>
              <TextField
                label="Source (optional)"
                size="small"
                fullWidth
                value={localValidation.listSource}
                onChange={(e) => handleChange('listSource', e.target.value)}
                placeholder="e.g., =Sheet2!A1:A10"
                helperText="Reference a range or enter values below"
              />

              <Stack direction="row" spacing={1}>
                <TextField
                  size="small"
                  fullWidth
                  placeholder="Add list item..."
                  value={listInput}
                  onChange={(e) => setListInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddListItem()}
                />
                <Button variant="outlined" onClick={handleAddListItem}>
                  <AddIcon />
                </Button>
              </Stack>

              <Stack direction="row" flexWrap="wrap" gap={0.5}>
                {(localValidation.listValues || []).map((item, i) => (
                  <Chip
                    key={i}
                    label={item}
                    size="small"
                    onDelete={() => handleRemoveListItem(i)}
                  />
                ))}
              </Stack>

              <FormControlLabel
                control={
                  <Switch
                    checked={localValidation.showDropdown}
                    onChange={(e) => handleChange('showDropdown', e.target.checked)}
                    size="small"
                  />
                }
                label="Show dropdown in cell"
              />
            </>
          )}

          {/* Custom formula */}
          {localValidation.type === 'custom' && (
            <TextField
              label="Formula"
              size="small"
              fullWidth
              value={localValidation.formula}
              onChange={(e) => handleChange('formula', e.target.value)}
              placeholder="=AND(A1>0, A1<100)"
              helperText="Formula must return TRUE for valid input"
            />
          )}

          <FormControlLabel
            control={
              <Switch
                checked={localValidation.ignoreBlank}
                onChange={(e) => handleChange('ignoreBlank', e.target.checked)}
                size="small"
              />
            }
            label="Ignore blank cells"
          />

          <Divider />

          {/* Input Message */}
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

          {/* Error Alert */}
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
                const Icon = style.icon
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

          {/* Preview */}
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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DataValidationPanel({
  validations = [],
  onValidationsChange,
  selectedRange = '',
  onClose,
}) {
  const theme = useTheme()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingValidation, setEditingValidation] = useState(null)

  // Get description for a validation rule
  const getValidationDescription = (validation) => {
    const type = VALIDATION_TYPES.find((t) => t.value === validation.type)
    if (validation.type === 'any') return 'Any value allowed'
    if (validation.type === 'list') {
      const count = validation.listValues?.length || 0
      return `List: ${count} items`
    }
    if (validation.type === 'custom') return 'Custom formula'

    const conditions = ['date', 'time'].includes(validation.type) ? DATE_CONDITIONS : NUMBER_CONDITIONS
    const cond = conditions.find((c) => c.value === validation.condition)

    if (['between', 'not_between'].includes(validation.condition)) {
      return `${type?.label} ${cond?.label} ${validation.value1} and ${validation.value2}`
    }
    return `${type?.label} ${cond?.label} ${validation.value1}`
  }

  // Add new validation
  const handleAddValidation = useCallback(() => {
    setEditingValidation(null)
    setDialogOpen(true)
  }, [])

  // Edit validation
  const handleEditValidation = useCallback((validation) => {
    setEditingValidation(validation)
    setDialogOpen(true)
  }, [])

  // Save validation
  const handleSaveValidation = useCallback((validation) => {
    if (validation.id) {
      onValidationsChange?.(validations.map((v) => (v.id === validation.id ? validation : v)))
    } else {
      onValidationsChange?.([...validations, { ...validation, id: `validation_${Date.now()}` }])
    }
    setDialogOpen(false)
  }, [validations, onValidationsChange])

  // Delete validation
  const handleDeleteValidation = useCallback((validationId) => {
    onValidationsChange?.(validations.filter((v) => v.id !== validationId))
  }, [validations, onValidationsChange])

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <ValidationIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Data Validation
          </Typography>
        </Stack>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </PanelHeader>

      <PanelContent>
        {/* Selected Range */}
        {selectedRange && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Selected Range:
            </Typography>
            <Chip
              label={selectedRange}
              size="small"
              sx={{ ml: 1, fontFamily: 'monospace' }}
            />
          </Box>
        )}

        {/* Add Rule Button */}
        <Button
          fullWidth
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={handleAddValidation}
          sx={{ mb: 2 }}
        >
          Add Validation Rule
        </Button>

        {/* Info */}
        <Alert severity="info" sx={{ mb: 2, fontSize: '0.75rem' }}>
          Data validation restricts the type of data that can be entered in cells.
        </Alert>

        {/* Validations List */}
        {validations.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <ValidationIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No validation rules yet
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Add rules to restrict cell input
            </Typography>
          </Box>
        ) : (
          validations.map((validation) => {
            const TypeIcon = VALIDATION_TYPES.find((t) => t.value === validation.type)?.icon || InfoIcon
            const errorStyle = ERROR_STYLES.find((s) => s.value === validation.errorStyle)

            return (
              <RuleCard key={validation.id} elevation={0}>
                <Stack direction="row" alignItems="flex-start" spacing={1.5}>
                  <TypeIcon sx={{ color: 'text.secondary', fontSize: 20, mt: 0.25 }} />
                  <Box sx={{ flex: 1 }}>
                    <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
                      <TypeChip
                        label={VALIDATION_TYPES.find((t) => t.value === validation.type)?.label}
                        size="small"
                        variant="outlined"
                        sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                      />
                      <Chip
                        label={validation.range}
                        size="small"
                        sx={{ fontFamily: 'monospace', fontSize: '10px' }}
                      />
                    </Stack>

                    <Typography variant="body2" sx={{ mb: 1 }}>
                      {getValidationDescription(validation)}
                    </Typography>

                    {validation.type === 'list' && validation.listValues?.length > 0 && (
                      <Stack direction="row" flexWrap="wrap" gap={0.5} mb={1}>
                        {validation.listValues.slice(0, 5).map((item, i) => (
                          <Chip key={i} label={item} size="small" variant="outlined" />
                        ))}
                        {validation.listValues.length > 5 && (
                          <Chip label={`+${validation.listValues.length - 5} more`} size="small" />
                        )}
                      </Stack>
                    )}

                    <Stack direction="row" alignItems="center" spacing={1}>
                      {errorStyle && (
                        <Chip
                          icon={<errorStyle.icon sx={{ fontSize: 14 }} />}
                          label={errorStyle.label}
                          size="small"
                          color={errorStyle.color}
                          variant="outlined"
                          sx={{ fontSize: '10px' }}
                        />
                      )}
                      {validation.ignoreBlank && (
                        <Chip
                          label="Ignore blank"
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: '10px' }}
                        />
                      )}
                    </Stack>
                  </Box>

                  <Stack direction="row" spacing={0.5}>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => handleEditValidation(validation)}>
                        <EditIcon sx={{ fontSize: 16 }} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteValidation(validation.id)}
                      >
                        <DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </Stack>
              </RuleCard>
            )
          })
        )}
      </PanelContent>

      {/* Validation Editor Dialog */}
      <ValidationEditorDialog
        open={dialogOpen}
        validation={editingValidation}
        onClose={() => setDialogOpen(false)}
        onSave={handleSaveValidation}
      />
    </PanelContainer>
  )
}
