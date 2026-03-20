/**
 * Formula Bar Component
 * Excel-style formula bar with cell reference and autocomplete.
 */
import {
  Box,
  TextField,
  IconButton,
  Tooltip,
  Typography,
  Stack,
  alpha,
  styled,
} from '@mui/material'
import {
  Functions as FormulaIcon,
  Check as ApplyIcon,
  Close as CancelIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { useFormulaBar } from '../hooks/useFormulaBar'
import FunctionMenuPopover, { AutocompletePopover } from './FunctionMenuPopover'

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
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  cursor: 'pointer',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const FormulaInput = styled(TextField)(({ theme }) => ({
  flex: 1,
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,
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
  const {
    inputRef,
    localValue,
    isEditing,
    setIsEditing,
    functionMenuAnchor,
    setFunctionMenuAnchor,
    autocompleteAnchor,
    setAutocompleteAnchor,
    filteredFunctions,
    handleChange,
    handleApply,
    handleCancel,
    handleKeyDown,
    handleInsertFunction,
    handleSelectFunction,
  } = useFormulaBar({ value, formula, onChange, onApply, onCancel })

  return (
    <FormulaBarContainer>
      <CellReferenceBox onClick={onCellRefClick}>
        <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
          {cellRef || 'A1'}
        </Typography>
      </CellReferenceBox>

      <Tooltip title="Insert Function">
        <IconButton
          size="small"
          onClick={(e) => setFunctionMenuAnchor(e.currentTarget)}
          disabled={disabled}
          sx={{ color: 'text.secondary' }}
        >
          <FormulaIcon fontSize="small" />
        </IconButton>
      </Tooltip>

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
        InputProps={{ sx: { color: 'text.primary' } }}
      />

      {isEditing && (
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Apply (Enter)">
            <IconButton size="small" onClick={handleApply} sx={{ color: 'text.secondary' }}>
              <ApplyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Cancel (Esc)">
            <IconButton size="small" onClick={handleCancel} sx={{ color: 'text.secondary' }}>
              <CancelIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      )}

      <FunctionMenuPopover
        anchorEl={functionMenuAnchor}
        onClose={() => setFunctionMenuAnchor(null)}
        onSelect={handleSelectFunction}
      />

      <AutocompletePopover
        anchorEl={autocompleteAnchor}
        filteredFunctions={filteredFunctions}
        onClose={() => setAutocompleteAnchor(null)}
        onInsert={handleInsertFunction}
      />
    </FormulaBarContainer>
  )
}
