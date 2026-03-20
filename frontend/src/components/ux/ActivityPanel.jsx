/**
 * Activity Panel
 * Shows recent operations, their status, and allows undo
 */
import { useMemo } from 'react'
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  Chip,
  Tooltip,
  useTheme,
  alpha,
  Fade,
} from '@mui/material'
import {
  Close as CloseIcon,
  History as HistoryIcon,
} from '@mui/icons-material'
import { useOperationHistory, OperationStatus } from './OperationHistoryProvider'
import { neutral } from '@/app/theme'
import OperationItem from './OperationItem'
import ActivityPanelSummary from './ActivityPanelSummary'

export default function ActivityPanel({ open, onClose }) {
  const theme = useTheme()
  const { operations, activeCount, hasActiveOperations, undoOperation, clearCompleted } = useOperationHistory()

  const completedCount = useMemo(() =>
    operations.filter((op) => op.status === OperationStatus.COMPLETED).length, [operations])
  const failedCount = useMemo(() =>
    operations.filter((op) => op.status === OperationStatus.FAILED).length, [operations])

  return (
    <Drawer
      anchor="right" open={open} onClose={onClose}
      PaperProps={{ sx: { width: 380, maxWidth: '100vw', bgcolor: alpha(theme.palette.background.default, 0.95), backdropFilter: 'blur(20px)' } }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 2, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <HistoryIcon sx={{ color: 'text.secondary' }} />
          <Typography variant="h6" fontWeight={600}>Activity</Typography>
          {hasActiveOperations && (
            <Chip size="small" label={`${activeCount} active`}
              sx={{ height: 22, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
          )}
        </Box>
        <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
      </Box>

      {operations.length > 0 && (
        <ActivityPanelSummary completedCount={completedCount} failedCount={failedCount} onClearCompleted={clearCompleted} />
      )}

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {operations.length === 0 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'text.secondary', textAlign: 'center', p: 4 }}>
            <HistoryIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
            <Typography variant="body1" fontWeight={500}>No recent activity</Typography>
            <Typography variant="body2" sx={{ mt: 1, opacity: 0.7 }}>Your actions will appear here</Typography>
          </Box>
        ) : (
          <List disablePadding>
            {operations.map((operation) => (
              <Fade in key={operation.id}>
                <div><OperationItem operation={operation} onUndo={undoOperation} /></div>
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
      <IconButton onClick={onClick} sx={{ position: 'relative', color: theme.palette.text.secondary }}>
        <HistoryIcon />
        {hasActiveOperations && (
          <Box sx={{
            position: 'absolute', top: 6, right: 6, width: 8, height: 8, borderRadius: '50%',
            bgcolor: theme.palette.text.secondary, animation: 'pulse 1.5s infinite',
            '@keyframes pulse': { '0%, 100%': { opacity: 1, transform: 'scale(1)' }, '50%': { opacity: 0.7, transform: 'scale(1.2)' } },
          }} />
        )}
      </IconButton>
    </Tooltip>
  )
}
