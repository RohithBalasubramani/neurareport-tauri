/**
 * Operation Item Main Row
 * Icon, label, status chip, and action buttons
 */
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Undo as UndoIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { OperationStatus } from './OperationHistoryProvider'
import { neutral } from '@/app/theme'

export default function OperationItemRow({
  operation,
  Icon,
  StatusIcon,
  statusConfig,
  timeAgo,
  expanded,
  onToggleExpand,
  onUndo,
}) {
  const theme = useTheme()
  const canUndo = operation.status === OperationStatus.COMPLETED && operation.canUndo

  return (
    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, width: '100%' }}>
      <Box
        sx={{
          width: 36, height: 36, borderRadius: 1,
          bgcolor: alpha(statusConfig.color, 0.1),
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}
      >
        <Icon sx={{ fontSize: 18, color: statusConfig.color }} />
      </Box>

      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Typography variant="body2" fontWeight={500} noWrap>{operation.label}</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
          <Chip
            size="small"
            icon={<StatusIcon sx={{ fontSize: '14px !important' }} />}
            label={statusConfig.label}
            sx={{
              height: 22, fontSize: '12px',
              bgcolor: alpha(statusConfig.color, 0.1), color: statusConfig.color,
              '& .MuiChip-icon': { color: statusConfig.color },
            }}
          />
          <Typography variant="caption" color="text.secondary">{timeAgo}</Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {canUndo && (
          <Tooltip title={operation.undoLabel || 'Undo'}>
            <IconButton size="small" onClick={() => onUndo(operation.id)}
              sx={{ color: theme.palette.text.secondary, '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] } }}>
              <UndoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
        {(operation.description || operation.error) && (
          <IconButton size="small" onClick={onToggleExpand}>
            {expanded ? <CollapseIcon fontSize="small" /> : <ExpandIcon fontSize="small" />}
          </IconButton>
        )}
      </Box>
    </Box>
  )
}
