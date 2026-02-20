/**
 * Formula Bar Component
 * Excel-style formula bar with cell reference and autocomplete.
 */
import { useState, useCallback, useMemo, useEffect, useRef } from 'react'
import {
  Box,
  TextField,
  IconButton,
  Tooltip,
  Popover,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Chip,
  Stack,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Functions as FormulaIcon,
  Check as ApplyIcon,
  Close as CancelIcon,
  KeyboardArrowDown as DropdownIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const FormulaBarContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(1, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: theme.palette.background.paper,
  gap: theme.spacing(1),
}))

const CellReferenceBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  minWidth: 80,
  padding: theme.spacing(0.5, 1),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  cursor: 'pointer',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const FormulaInput = styled(TextField)(({ theme }) => ({
  flex: 1,
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,  // Figma spec: 8px
    fontSize: '14px',
    fontFamily: 'monospace',
    '& fieldset': {
      borderColor: alpha(theme.palette.divider, 0.2),
    },
    '&:hover fieldset': {
      borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[300],
    },
    '&.Mui-focused fieldset': {
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    },
  },
}))

const FunctionChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  height: 24,
  fontSize: '0.75rem',
  fontFamily: 'monospace',
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  color: 'text.secondary',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],
  },
}))

// =============================================================================
// FORMULA FUNCTIONS LIST
// =============================================================================

const FORMULA_FUNCTIONS = [
  { name: 'SUM', syntax: 'SUM(range)', description: 'Sum of values' },
  { name: 'AVERAGE', syntax: 'AVERAGE(range)', description: 'Average of values' },
  { name: 'COUNT', syntax: 'COUNT(range)', description: 'Count of numbers' },
  { name: 'COUNTA', syntax: 'COUNTA(range)', description: 'Count of non-empty cells' },
  { name: 'MAX', syntax: 'MAX(range)', description: 'Maximum value' },
  { name: 'MIN', syntax: 'MIN(range)', description: 'Minimum value' },
  { name: 'IF', syntax: 'IF(condition, true_val, false_val)', description: 'Conditional logic' },
  { name: 'VLOOKUP', syntax: 'VLOOKUP(value, range, col, exact)', description: 'Vertical lookup' },
  { name: 'HLOOKUP', syntax: 'HLOOKUP(value, range, row, exact)', description: 'Horizontal lookup' },
  { name: 'SUMIF', syntax: 'SUMIF(range, criteria, sum_range)', description: 'Conditional sum' },
  { name: 'COUNTIF', syntax: 'COUNTIF(range, criteria)', description: 'Conditional count' },
  { name: 'CONCATENATE', syntax: 'CONCATENATE(text1, text2, ...)', description: 'Join text' },
  { name: 'LEFT', syntax: 'LEFT(text, num_chars)', description: 'Left characters' },
  { name: 'RIGHT', syntax: 'RIGHT(text, num_chars)', description: 'Right characters' },
  { name: 'MID', syntax: 'MID(text, start, length)', description: 'Middle characters' },
  { name: 'LEN', syntax: 'LEN(text)', description: 'Text length' },
  { name: 'TRIM', syntax: 'TRIM(text)', description: 'Remove extra spaces' },
  { name: 'ROUND', syntax: 'ROUND(number, decimals)', description: 'Round number' },
  { name: 'ABS', syntax: 'ABS(number)', description: 'Absolute value' },
  { name: 'TODAY', syntax: 'TODAY()', description: 'Current date' },
  { name: 'NOW', syntax: 'NOW()', description: 'Current date and time' },
  { name: 'YEAR', syntax: 'YEAR(date)', description: 'Year from date' },
  { name: 'MONTH', syntax: 'MONTH(date)', description: 'Month from date' },
  { name: 'DAY', syntax: 'DAY(date)', description: 'Day from date' },
]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function FormulaBar({
  cellRef = '',
  value = '',
  formula = null,
  onChange,
  onApply,
  onCancel,
  onCellRefClick,
  disabled = false,
}) {
  const theme = useTheme()
  const inputRef = useRef(null)
  const [localValue, setLocalValue] = useState(value)
  const [isEditing, setIsEditing] = useState(false)
  const [functionMenuAnchor, setFunctionMenuAnchor] = useState(null)
  const [autocompleteAnchor, setAutocompleteAnchor] = useState(null)
  const [filteredFunctions, setFilteredFunctions] = useState([])

  // Sync value from props
  useEffect(() => {
    setLocalValue(formula || value)
  }, [value, formula])

  // Check if value is a formula
  const isFormula = localValue.startsWith('=')

  // Handle input change
  const handleChange = useCallback((e) => {
    const newValue = e.target.value
    setLocalValue(newValue)
    setIsEditing(true)
    onChange?.(newValue)

    // Check for function autocomplete
    if (newValue.startsWith('=')) {
      const match = newValue.match(/=([A-Z]+)$/i)
      if (match) {
        const searchTerm = match[1].toUpperCase()
        const matches = FORMULA_FUNCTIONS.filter((f) =>
          f.name.startsWith(searchTerm)
        )
        if (matches.length > 0) {
          setFilteredFunctions(matches)
          setAutocompleteAnchor(inputRef.current)
        } else {
          setAutocompleteAnchor(null)
        }
      } else {
        setAutocompleteAnchor(null)
      }
    } else {
      setAutocompleteAnchor(null)
    }
  }, [onChange])

  // Handle apply (Enter key)
  const handleApply = useCallback(() => {
    setIsEditing(false)
    setAutocompleteAnchor(null)
    onApply?.(localValue)
  }, [localValue, onApply])

  // Handle cancel (Escape key)
  const handleCancel = useCallback(() => {
    setLocalValue(formula || value)
    setIsEditing(false)
    setAutocompleteAnchor(null)
    onCancel?.()
  }, [formula, onCancel, value])

  // Handle key press
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      handleApply()
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }, [handleApply, handleCancel])

  // Insert function from autocomplete
  const handleInsertFunction = useCallback((func) => {
    const currentValue = localValue
    const match = currentValue.match(/=([A-Z]+)$/i)
    if (match) {
      const newValue = currentValue.slice(0, -match[1].length) + func.name + '('
      setLocalValue(newValue)
      onChange?.(newValue)
    }
    setAutocompleteAnchor(null)
    inputRef.current?.focus()
  }, [localValue, onChange])

  // Open function menu
  const handleOpenFunctionMenu = useCallback((e) => {
    setFunctionMenuAnchor(e.currentTarget)
  }, [])

  // Close function menu
  const handleCloseFunctionMenu = useCallback(() => {
    setFunctionMenuAnchor(null)
  }, [])

  // Insert function from menu
  const handleSelectFunction = useCallback((func) => {
    const newValue = `=${func.name}(`
    setLocalValue(newValue)
    onChange?.(newValue)
    handleCloseFunctionMenu()
    inputRef.current?.focus()
  }, [handleCloseFunctionMenu, onChange])

  return (
    <FormulaBarContainer>
      {/* Cell Reference */}
      <CellReferenceBox onClick={onCellRefClick}>
        <Typography
          variant="body2"
          sx={{ fontWeight: 600, fontFamily: 'monospace' }}
        >
          {cellRef || 'A1'}
        </Typography>
      </CellReferenceBox>

      {/* Function Button */}
      <Tooltip title="Insert Function">
        <IconButton
          size="small"
          onClick={handleOpenFunctionMenu}
          disabled={disabled}
          sx={{ color: 'text.secondary' }}
        >
          <FormulaIcon fontSize="small" />
        </IconButton>
      </Tooltip>

      {/* Formula Input */}
      <FormulaInput
        ref={inputRef}
        size="small"
        fullWidth
        value={localValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsEditing(true)}
        placeholder="Enter value or formula (start with =)"
        disabled={disabled}
        InputProps={{
          sx: {
            color: 'text.primary',
          },
        }}
      />

      {/* Apply/Cancel Buttons (visible when editing) */}
      {isEditing && (
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Apply (Enter)">
            <IconButton
              size="small"
              onClick={handleApply}
              sx={{ color: 'text.secondary' }}
            >
              <ApplyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Cancel (Esc)">
            <IconButton
              size="small"
              onClick={handleCancel}
              sx={{ color: 'text.secondary' }}
            >
              <CancelIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      )}

      {/* Function Menu */}
      <Popover
        open={Boolean(functionMenuAnchor)}
        anchorEl={functionMenuAnchor}
        onClose={handleCloseFunctionMenu}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        PaperProps={{
          sx: { width: 320, maxHeight: 400, borderRadius: 1 },  // Figma spec: 8px
        }}
      >
        <Box sx={{ p: 1.5 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Insert Function
          </Typography>
          <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
            {FORMULA_FUNCTIONS.map((func) => (
              <ListItem key={func.name} disablePadding>
                <ListItemButton
                  onClick={() => handleSelectFunction(func)}
                  sx={{ borderRadius: 1, py: 0.5 }}
                >
                  <ListItemText
                    primary={
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <FunctionChip label={func.name} size="small" />
                      </Stack>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {func.description}
                      </Typography>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Popover>

      {/* Autocomplete Popover */}
      <Popover
        open={Boolean(autocompleteAnchor) && filteredFunctions.length > 0}
        anchorEl={autocompleteAnchor}
        onClose={() => setAutocompleteAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        disableAutoFocus
        disableEnforceFocus
        PaperProps={{
          sx: { width: 250, maxHeight: 200, borderRadius: 1 },  // Figma spec: 8px
        }}
      >
        <List dense>
          {filteredFunctions.slice(0, 8).map((func) => (
            <ListItem key={func.name} disablePadding>
              <ListItemButton
                onClick={() => handleInsertFunction(func)}
                sx={{ py: 0.5 }}
              >
                <FunctionChip label={func.name} size="small" sx={{ mr: 1 }} />
                <Typography variant="caption" color="text.secondary" noWrap>
                  {func.description}
                </Typography>
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Popover>
    </FormulaBarContainer>
  )
}
