/**
 * Conditional Format Rule Card
 * Displays a single conditional formatting rule with actions.
 */
import {
  Box,
  Typography,
  IconButton,
  Stack,
  Chip,
  Switch,
  Button,
  Divider,
  Collapse,
  alpha,
  Paper,
  styled,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  DragIndicator as DragIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { RULE_TYPES, getRuleDescription } from '../hooks/useConditionalFormat'

const RuleCard = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isActive',
})(({ theme, isActive }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  backgroundColor: isActive ? 'transparent' : alpha(theme.palette.action.disabled, 0.05),
  opacity: isActive ? 1 : 0.7,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const ColorPreview = styled(Box)(({ theme, bgcolor, textcolor }) => ({
  width: 60,
  height: 28,
  borderRadius: 4,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: bgcolor || theme.palette.background.default,
  color: textcolor || theme.palette.text.primary,
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  fontSize: '0.75rem',
  fontWeight: 600,
}))

export default function ConditionalFormatRuleCard({
  rule,
  index,
  isExpanded,
  onToggleExpansion,
  onToggleEnabled,
  onEdit,
  onDelete,
}) {
  return (
    <RuleCard elevation={0} isActive={rule.enabled}>
      <Stack direction="row" alignItems="flex-start" spacing={1}>
        <DragIcon sx={{ color: 'text.disabled', mt: 0.5, cursor: 'grab' }} />

        <Box sx={{ flex: 1 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Stack direction="row" alignItems="center" spacing={1}>
              <Chip
                label={index + 1}
                size="small"
                sx={{
                  width: 24,
                  height: 24,
                  fontSize: '12px',
                  '& .MuiChip-label': { px: 0 },
                }}
              />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {RULE_TYPES.find((t) => t.value === rule.type)?.label || rule.type}
              </Typography>
            </Stack>
            <Stack direction="row" spacing={0.5}>
              <Switch
                size="small"
                checked={rule.enabled}
                onChange={() => onToggleEnabled(rule.id)}
              />
              <IconButton
                size="small"
                onClick={() => onToggleExpansion(rule.id)}
              >
                {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
              </IconButton>
            </Stack>
          </Stack>

          <Typography variant="caption" color="text.secondary">
            {getRuleDescription(rule)}
          </Typography>

          <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
            <ColorPreview
              bgcolor={rule.format?.fill}
              textcolor={rule.format?.text}
              sx={{
                fontWeight: rule.format?.bold ? 600 : 400,
                fontStyle: rule.format?.italic ? 'italic' : 'normal',
              }}
            >
              Abc
            </ColorPreview>
            <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
              {rule.range}
            </Typography>
          </Stack>

          <Collapse in={isExpanded}>
            <Divider sx={{ my: 1.5 }} />
            <Stack direction="row" spacing={1}>
              <Button
                size="small"
                startIcon={<EditIcon />}
                onClick={() => onEdit(rule)}
              >
                Edit
              </Button>
              <Button
                size="small"
                sx={{ color: 'text.secondary' }}
                startIcon={<DeleteIcon />}
                onClick={() => onDelete(rule.id)}
              >
                Delete
              </Button>
            </Stack>
          </Collapse>
        </Box>
      </Stack>
    </RuleCard>
  )
}
