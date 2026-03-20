/**
 * Background Operations Drawer
 *
 * Displays list of background operations with status, progress, and cancel controls.
 */
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Button,
  Drawer,
  List,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Notifications as NotifyIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { BackgroundOperationStatus } from './backgroundConstants'
import BackgroundOpItem from './BackgroundOpItem'

export default function BackgroundOpsDrawer({
  open,
  onClose,
  operations,
  activeCount,
  onCancelOperation,
  onClearCompleted,
}) {
  const theme = useTheme()

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: 400,
          maxWidth: '100vw',
          bgcolor: alpha(theme.palette.background.default, 0.95),
          backdropFilter: 'blur(20px)',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <NotifyIcon sx={{ color: 'text.secondary' }} />
          <Typography variant="h6" fontWeight={600}>
            Background Tasks
          </Typography>
          {activeCount > 0 && (
            <Chip
              size="small"
              label={`${activeCount} active`}
              sx={{
                height: 22,
                fontSize: '12px',
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                color: 'text.primary',
              }}
            />
          )}
        </Box>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Operations List */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
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
            <NotifyIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
            <Typography variant="body1" fontWeight={500}>
              No background tasks
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, opacity: 0.7 }}>
              Background operations will appear here
            </Typography>
          </Box>
        ) : (
          <List disablePadding>
            {operations.map((op) => (
              <BackgroundOpItem key={op.id} op={op} onCancel={onCancelOperation} />
            ))}
          </List>
        )}
      </Box>

      {/* Footer */}
      {operations.length > 0 && (
        <Box
          sx={{
            p: 2,
            borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          }}
        >
          <Button
            fullWidth
            size="small"
            onClick={onClearCompleted}
            disabled={
              !operations.some(
                (op) =>
                  op.status === BackgroundOperationStatus.COMPLETED ||
                  op.status === BackgroundOperationStatus.FAILED ||
                  op.status === BackgroundOperationStatus.CANCELLED
              )
            }
          >
            Clear Completed
          </Button>
        </Box>
      )}
    </Drawer>
  )
}
