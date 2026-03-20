/**
 * Validation Rule Card
 * Displays a single data validation rule with actions.
 */
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  Stack,
  Chip,
  alpha,
  styled,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Info as InfoIcon,
  Numbers as NumberIcon,
  TextFields as TextIcon,
  CalendarToday as DateIcon,
  List as ListIcon,
  Functions as FormulaIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import {
  VALIDATION_TYPES,
  ERROR_STYLES,
  getValidationDescription,
} from '../hooks/useDataValidation'

const ICON_MAP = {
  InfoIcon, NumberIcon, TextIcon, DateIcon, ListIcon, FormulaIcon,
  WarningIcon, ErrorIcon,
}

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

export default function ValidationRuleCard({ validation, onEdit, onDelete }) {
  const typeEntry = VALIDATION_TYPES.find((t) => t.value === validation.type)
  const TypeIcon = ICON_MAP[typeEntry?.icon] || InfoIcon
  const errorStyle = ERROR_STYLES.find((s) => s.value === validation.errorStyle)
  const ErrorStyleIcon = errorStyle ? ICON_MAP[errorStyle.icon] : null

  return (
    <RuleCard elevation={0}>
      <Stack direction="row" alignItems="flex-start" spacing={1.5}>
        <TypeIcon sx={{ color: 'text.secondary', fontSize: 20, mt: 0.25 }} />
        <Box sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
            <TypeChip
              label={typeEntry?.label}
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
            {errorStyle && ErrorStyleIcon && (
              <Chip
                icon={<ErrorStyleIcon sx={{ fontSize: 14 }} />}
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
            <IconButton size="small" onClick={() => onEdit(validation)}>
              <EditIcon sx={{ fontSize: 16 }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton
              size="small"
              onClick={() => onDelete(validation.id)}
            >
              <DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>
    </RuleCard>
  )
}
