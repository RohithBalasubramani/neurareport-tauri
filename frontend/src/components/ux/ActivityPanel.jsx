/**
 * Activity Panel
 * Shows recent operations, their status, and allows undo
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Make every action reversible where possible
 * - What just happened / what will happen next
 */
import { useMemo, useState } from 'react'
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Chip,
  Divider,
  LinearProgress,
  Tooltip,
  useTheme,
  alpha,
  Fade,
  Collapse,
} from '@mui/material'
import {
  Close as CloseIcon,
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
  ClearAll as ClearIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { useOperationHistory, OperationStatus, OperationType } from './OperationHistoryProvider'
import { neutral, palette } from '@/app/theme'

// Simple time ago formatter (no external dependency)
function formatTimeAgo(date) {
  const now = Date.now()
  const timestamp = date instanceof Date ? date.getTime() : new Date(date).getTime()
  const seconds = Math.floor((now - timestamp) / 1000)

  if (seconds < 5) return 'just now'
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// Operation type icons
const getOperationIcon = (type) => {
  const icons = {
    [OperationType.CREATE]: CreateIcon,
    [OperationType.UPDATE]: UpdateIcon,
    [OperationType.DELETE]: DeleteIcon,
    [OperationType.UPLOAD]: UploadIcon,
    [OperationType.DOWNLOAD]: DownloadIcon,
    [OperationType.GENERATE]: GenerateIcon,
    [OperationType.EXECUTE]: ExecuteIcon,
    [OperationType.SEND]: SendIcon,
  }
  return icons[type] || HistoryIcon
}

// Status configurations
const getStatusConfig = (status, theme) => {
  const configs = {
    [OperationStatus.PENDING]: {
      icon: PendingIcon,
      color: neutral[500],
      label: 'Pending',
    },
    [OperationStatus.IN_PROGRESS]: {
      icon: PendingIcon,
      color: theme.palette.text.secondary,
      label: 'In progress',
      showProgress: true,
    },
    [OperationStatus.COMPLETED]: {
      icon: SuccessIcon,
      color: theme.palette.text.secondary,
      label: 'Completed',
    },
    [OperationStatus.FAILED]: {
      icon: ErrorIcon,
      color: theme.palette.text.secondary,
      label: 'Failed',
    },
    [OperationStatus.UNDONE]: {
      icon: UndoIcon,
      color: theme.palette.text.secondary,
      label: 'Undone',
    },
  }
  return configs[status] || configs[OperationStatus.PENDING]
}

/**
 * Single Operation Item
 */
function OperationItem({ operation, onUndo }) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(false)
  const statusConfig = getStatusConfig(operation.status, theme)
  const Icon = getOperationIcon(operation.type)
  const StatusIcon = statusConfig.icon

  const timeAgo = useMemo(() => {
    const time = operation.completedAt || operation.startedAt
    return formatTimeAgo(time)
  }, [operation.completedAt, operation.startedAt])

  const canUndo = operation.status === OperationStatus.COMPLETED && operation.canUndo

  return (
    <ListItem
      sx={{
        flexDirection: 'column',
        alignItems: 'stretch',
        gap: 1,
        py: 1.5,
        px: 2,
        bgcolor: alpha(theme.palette.background.paper, 0.4),
        borderRadius: 1,  // Figma spec: 8px
        mb: 1,
        '&:hover': {
          bgcolor: alpha(theme.palette.background.paper, 0.6),
        },
      }}
    >
      {/* Main row */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, width: '100%' }}>
        {/* Type icon */}
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: alpha(statusConfig.color, 0.1),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Icon sx={{ fontSize: 18, color: statusConfig.color }} />
        </Box>

        {/* Content */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body2" fontWeight={500} noWrap>
            {operation.label}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            <Chip
              size="small"
              icon={<StatusIcon sx={{ fontSize: '14px !important' }} />}
              label={statusConfig.label}
              sx={{
                height: 22,
                fontSize: '12px',
                bgcolor: alpha(statusConfig.color, 0.1),
                color: statusConfig.color,
                '& .MuiChip-icon': {
                  color: statusConfig.color,
                },
              }}
            />
            <Typography variant="caption" color="text.secondary">
              {timeAgo}
            </Typography>
          </Box>
        </Box>

        {/* Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {canUndo && (
            <Tooltip title={operation.undoLabel || 'Undo'}>
              <IconButton
                size="small"
                onClick={() => onUndo(operation.id)}
                sx={{
                  color: theme.palette.text.secondary,
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                  },
                }}
              >
                <UndoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          {(operation.description || operation.error) && (
            <IconButton size="small" onClick={() => setExpanded(!expanded)}>
              {expanded ? <CollapseIcon fontSize="small" /> : <ExpandIcon fontSize="small" />}
            </IconButton>
          )}
        </Box>
      </Box>

      {/* Progress bar for in-progress operations */}
      {statusConfig.showProgress && (
        <LinearProgress
          variant={operation.progress > 0 ? 'determinate' : 'indeterminate'}
          value={operation.progress}
          sx={{
            height: 4,
            borderRadius: 1,  // Figma spec: 8px
            bgcolor: alpha(statusConfig.color, 0.1),
            '& .MuiLinearProgress-bar': {
              bgcolor: statusConfig.color,
            },
          }}
        />
      )}

      {/* Expanded details */}
      <Collapse in={expanded}>
        <Box
          sx={{
            mt: 1,
            p: 1.5,
            bgcolor: alpha(theme.palette.background.default, 0.5),
            borderRadius: 1,
          }}
        >
          {operation.description && (
            <Typography variant="body2" color="text.secondary">
              {operation.description}
            </Typography>
          )}
          {operation.error && (
            <Typography variant="body2" color="text.secondary">
              Error: {operation.error}
            </Typography>
          )}
        </Box>
      </Collapse>
    </ListItem>
  )
}

/**
 * Activity Panel Component
 */
export default function ActivityPanel({ open, onClose }) {
  const theme = useTheme()
  const {
    operations,
    activeCount,
    hasActiveOperations,
    undoOperation,
    clearCompleted,
  } = useOperationHistory()

  const completedCount = useMemo(() =>
    operations.filter((op) => op.status === OperationStatus.COMPLETED).length,
    [operations]
  )

  const failedCount = useMemo(() =>
    operations.filter((op) => op.status === OperationStatus.FAILED).length,
    [operations]
  )

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 380,
          maxWidth: '100vw',
          bgcolor: alpha(theme.palette.background.default, 0.95),
          backdropFilter: 'blur(20px)',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <HistoryIcon sx={{ color: 'text.secondary' }} />
          <Typography variant="h6" fontWeight={600}>
            Activity
          </Typography>
          {hasActiveOperations && (
            <Chip
              size="small"
              label={`${activeCount} active`}
              sx={{ height: 22, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
            />
          )}
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Summary bar */}
      {operations.length > 0 && (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 2,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50],
            borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          }}
        >
          <Box sx={{ flex: 1, display: 'flex', gap: 2 }}>
            <Typography variant="body2">
              <Box component="span" fontWeight={600}>{completedCount}</Box> completed
            </Typography>
            {failedCount > 0 && (
              <Typography variant="body2" color="text.secondary">
                <Box component="span" fontWeight={600}>{failedCount}</Box> failed
              </Typography>
            )}
          </Box>
          {completedCount > 0 && (
            <Button
              size="small"
              startIcon={<ClearIcon />}
              onClick={clearCompleted}
              sx={{ textTransform: 'none' }}
            >
              Clear completed
            </Button>
          )}
        </Box>
      )}

      {/* Operations list */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
        }}
      >
        {operations.length === 0 ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary',
              textAlign: 'center',
              p: 4,
            }}
          >
            <HistoryIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
            <Typography variant="body1" fontWeight={500}>
              No recent activity
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, opacity: 0.7 }}>
              Your actions will appear here
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {operations.map((operation) => (
              <Fade in key={operation.id}>
                <div>
                  <OperationItem
                    operation={operation}
                    onUndo={undoOperation}
                  />
                </div>
              </Fade>
            ))}
          </List>
        )}
      </Box>
    </Drawer>
  )
}

/**
 * Activity Button - Shows in header to indicate active operations
 */
export function ActivityButton({ onClick }) {
  const theme = useTheme()
  const { activeCount, hasActiveOperations } = useOperationHistory()

  return (
    <Tooltip title={hasActiveOperations ? `${activeCount} operations in progress` : 'Activity'}>
      <IconButton
        onClick={onClick}
        sx={{
          position: 'relative',
          color: theme.palette.text.secondary,
        }}
      >
        <HistoryIcon />
        {hasActiveOperations && (
          <Box
            sx={{
              position: 'absolute',
              top: 6,
              right: 6,
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: theme.palette.text.secondary,
              animation: 'pulse 1.5s infinite',
              '@keyframes pulse': {
                '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                '50%': { opacity: 0.7, transform: 'scale(1.2)' },
              },
            }}
          />
        )}
      </IconButton>
    </Tooltip>
  )
}
