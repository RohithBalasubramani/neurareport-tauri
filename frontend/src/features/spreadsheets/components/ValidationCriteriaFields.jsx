/**
 * Validation Criteria Fields
 * Form fields for validation criteria settings.
 */
import {
  Stack,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Switch,
  FormControlLabel,
  Typography,
} from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import {
  Info as InfoIcon,
  Numbers as NumberIcon,
  TextFields as TextIcon,
  CalendarToday as DateIcon,
  List as ListIcon,
  Functions as FormulaIcon,
} from '@mui/icons-material'
import {
  VALIDATION_TYPES,
  NUMBER_CONDITIONS,
  DATE_CONDITIONS,
} from '../hooks/useDataValidation'

const ICON_MAP = {
  InfoIcon, NumberIcon, TextIcon, DateIcon, ListIcon, FormulaIcon,
}

export default function ValidationCriteriaFields({
  localValidation,
  listInput,
  onListInputChange,
  onChange,
  onAddListItem,
  onRemoveListItem,
}) {
  const needsCondition = ['whole_number', 'decimal', 'date', 'time', 'text_length'].includes(localValidation.type)
  const conditions = ['date', 'time'].includes(localValidation.type) ? DATE_CONDITIONS : NUMBER_CONDITIONS
  const needsTwoValues = ['between', 'not_between'].includes(localValidation.condition)

  return (
    <>
      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
        Criteria
      </Typography>
      <FormControl size="small" fullWidth>
        <InputLabel>Allow</InputLabel>
        <Select
          value={localValidation.type}
          label="Allow"
          onChange={(e) => onChange('type', e.target.value)}
        >
          {VALIDATION_TYPES.map((type) => {
            const Icon = ICON_MAP[type.icon]
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
      {needsCondition && (
        <FormControl size="small" fullWidth>
          <InputLabel>Data</InputLabel>
          <Select
            value={localValidation.condition}
            label="Data"
            onChange={(e) => onChange('condition', e.target.value)}
          >
            {conditions.map((cond) => (
              <MenuItem key={cond.value} value={cond.value}>{cond.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {needsCondition && (
        <Stack direction="row" spacing={1}>
          <TextField
            label={needsTwoValues ? 'Minimum' : 'Value'}
            size="small"
            fullWidth
            type={['date', 'time'].includes(localValidation.type) ? localValidation.type : 'number'}
            value={localValidation.value1}
            onChange={(e) => onChange('value1', e.target.value)}
          />
          {needsTwoValues && (
            <TextField
              label="Maximum"
              size="small"
              fullWidth
              type={['date', 'time'].includes(localValidation.type) ? localValidation.type : 'number'}
              value={localValidation.value2}
              onChange={(e) => onChange('value2', e.target.value)}
            />
          )}
        </Stack>
      )}
      {localValidation.type === 'list' && (
        <>
          <TextField
            label="Source (optional)"
            size="small"
            fullWidth
            value={localValidation.listSource}
            onChange={(e) => onChange('listSource', e.target.value)}
            placeholder="e.g., =Sheet2!A1:A10"
            helperText="Reference a range or enter values below"
          />
          <Stack direction="row" spacing={1}>
            <TextField
              size="small"
              fullWidth
              placeholder="Add list item..."
              value={listInput}
              onChange={(e) => onListInputChange(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && onAddListItem()}
            />
            <Button variant="outlined" onClick={onAddListItem}>
              <AddIcon />
            </Button>
          </Stack>
          <Stack direction="row" flexWrap="wrap" gap={0.5}>
            {(localValidation.listValues || []).map((item, i) => (
              <Chip key={i} label={item} size="small" onDelete={() => onRemoveListItem(i)} />
            ))}
          </Stack>
          <FormControlLabel
            control={
              <Switch
                checked={localValidation.showDropdown}
                onChange={(e) => onChange('showDropdown', e.target.checked)}
                size="small"
              />
            }
            label="Show dropdown in cell"
          />
        </>
      )}
      {localValidation.type === 'custom' && (
        <TextField
          label="Formula"
          size="small"
          fullWidth
          value={localValidation.formula}
          onChange={(e) => onChange('formula', e.target.value)}
          placeholder="=AND(A1>0, A1<100)"
          helperText="Formula must return TRUE for valid input"
        />
      )}
      <FormControlLabel
        control={
          <Switch
            checked={localValidation.ignoreBlank}
            onChange={(e) => onChange('ignoreBlank', e.target.checked)}
            size="small"
          />
        }
        label="Ignore blank cells"
      />
    </>
  )
}
