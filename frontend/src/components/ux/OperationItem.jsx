/**
 * Single Operation Item
 * Renders one operation entry in the Activity Panel
 */
import { useMemo, useState } from 'react'
import {
  Box,
  Typography,
  ListItem,
  LinearProgress,
  Collapse,
  useTheme,
  alpha,
} from '@mui/material'
import {
  History as HistoryIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
  Undo as UndoIcon,
  Delete as DeleteIcon,
  Add as CreateIcon,
  Edit as UpdateIcon,
  CloudUpload as UploadIcon,
  CloudDownload as DownloadIcon,
  Send as SendIcon,
  PlayArrow as ExecuteIcon,
  AutoAwesome as GenerateIcon,
} from '@mui/icons-material'
import { OperationStatus, OperationType } from './OperationHistoryProvider'
import { neutral } from '@/app/theme'
import OperationItemRow from './OperationItemRow'

export function formatTimeAgo(date) {
  const now = Date.now()
  const timestamp = date instanceof Date ? date.getTime() : new Date(date).getTime()
  const seconds = Math.floor((now - timestamp) / 1000)
  if (seconds < 5) return 'just now'
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const OPERATION_ICONS = {
  [OperationType.CREATE]: CreateIcon, [OperationType.UPDATE]: UpdateIcon,
  [OperationType.DELETE]: DeleteIcon, [OperationType.UPLOAD]: UploadIcon,
  [OperationType.DOWNLOAD]: DownloadIcon, [OperationType.GENERATE]: GenerateIcon,
  [OperationType.EXECUTE]: ExecuteIcon, [OperationType.SEND]: SendIcon,
}

export const getOperationIcon = (type) => OPERATION_ICONS[type] || HistoryIcon

export const getStatusConfig = (status, theme) => {
  const configs = {
    [OperationStatus.PENDING]: { icon: PendingIcon, color: neutral[500], label: 'Pending' },
    [OperationStatus.IN_PROGRESS]: { icon: PendingIcon, color: theme.palette.text.secondary, label: 'In progress', showProgress: true },
    [OperationStatus.COMPLETED]: { icon: SuccessIcon, color: theme.palette.text.secondary, label: 'Completed' },
    [OperationStatus.FAILED]: { icon: ErrorIcon, color: theme.palette.text.secondary, label: 'Failed' },
    [OperationStatus.UNDONE]: { icon: UndoIcon, color: theme.palette.text.secondary, label: 'Undone' },
  }
  return configs[status] || configs[OperationStatus.PENDING]
}

export default function OperationItem({ operation, onUndo }) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(false)
  const statusConfig = getStatusConfig(operation.status, theme)
  const Icon = getOperationIcon(operation.type)
  const StatusIcon = statusConfig.icon

  const timeAgo = useMemo(() => {
    const time = operation.completedAt || operation.startedAt
    return formatTimeAgo(time)
  }, [operation.completedAt, operation.startedAt])

  return (
    <ListItem sx={{
      flexDirection: 'column', alignItems: 'stretch', gap: 1, py: 1.5, px: 2,
      bgcolor: alpha(theme.palette.background.paper, 0.4), borderRadius: 1, mb: 1,
      '&:hover': { bgcolor: alpha(theme.palette.background.paper, 0.6) },
    }}>
      <OperationItemRow
        operation={operation} Icon={Icon} StatusIcon={StatusIcon}
        statusConfig={statusConfig} timeAgo={timeAgo} expanded={expanded}
        onToggleExpand={() => setExpanded(!expanded)} onUndo={onUndo}
      />
      {statusConfig.showProgress && (
        <LinearProgress
          variant={operation.progress > 0 ? 'determinate' : 'indeterminate'} value={operation.progress}
          sx={{ height: 4, borderRadius: 1, bgcolor: alpha(statusConfig.color, 0.1), '& .MuiLinearProgress-bar': { bgcolor: statusConfig.color } }}
        />
      )}
      <Collapse in={expanded}>
        <Box sx={{ mt: 1, p: 1.5, bgcolor: alpha(theme.palette.background.default, 0.5), borderRadius: 1 }}>
          {operation.description && <Typography variant="body2" color="text.secondary">{operation.description}</Typography>}
          {operation.error && <Typography variant="body2" color="text.secondary">Error: {operation.error}</Typography>}
        </Box>
      </Collapse>
    </ListItem>
  )
}
