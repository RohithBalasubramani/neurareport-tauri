/**
 * Notification popover header and footer
 */
import {
  Box,
  Typography,
  IconButton,
  Button,
  Tooltip,
  alpha,
  useTheme,
} from '@mui/material'
import DoneAllIcon from '@mui/icons-material/DoneAll'
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep'

export function NotificationHeader({ unreadCount, onMarkAllRead, onClearAll, notificationCount }) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        px: 2,
        py: 1.5,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
      }}
    >
      <Typography
        sx={{
          fontSize: '0.875rem',
          fontWeight: 600,
          color: theme.palette.text.primary,
        }}
      >
        Notifications
        {unreadCount > 0 && (
          <Typography
            component="span"
            sx={{
              ml: 1,
              fontSize: '0.75rem',
              color: theme.palette.text.secondary,
            }}
          >
            {unreadCount} unread
          </Typography>
        )}
      </Typography>
      <Box sx={{ display: 'flex', gap: 0.5 }}>
        <Tooltip title="Mark all as read">
          <IconButton
            size="small"
            onClick={onMarkAllRead}
            disabled={unreadCount === 0}
            aria-label="Mark all notifications as read"
            data-testid="notifications-mark-all-read-button"
            sx={{
              color: theme.palette.text.secondary,
              '&:hover': { color: theme.palette.text.primary },
            }}
          >
            <DoneAllIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Tooltip>
        <Tooltip title="Clear all">
          <IconButton
            size="small"
            onClick={onClearAll}
            disabled={notificationCount === 0}
            aria-label="Clear all notifications"
            data-testid="notifications-clear-all-button"
            sx={{
              color: theme.palette.text.secondary,
              '&:hover': { color: theme.palette.text.primary },
            }}
          >
            <DeleteSweepIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  )
}

export function NotificationFooter({ onViewActivity }) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        px: 2,
        py: 1,
        borderTop: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
        textAlign: 'center',
      }}
    >
      <Button
        size="small"
        onClick={onViewActivity}
        data-testid="notifications-view-activity-button"
        sx={{
          fontSize: '0.75rem',
          color: theme.palette.text.secondary,
          '&:hover': { color: theme.palette.text.primary },
        }}
      >
        View Activity Log
      </Button>
    </Box>
  )
}
