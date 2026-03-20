/**
 * Notification list content (loading, empty, and populated states)
 */
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  CircularProgress,
  alpha,
  useTheme,
} from '@mui/material'
import NotificationsIcon from '@mui/icons-material/Notifications'
import CloseIcon from '@mui/icons-material/Close'
import { neutral } from '@/app/theme'
import { getTypeConfig, formatTimeAgo } from './notificationHelpers'

export default function NotificationList({
  notifications,
  loading,
  onNotificationClick,
  onDeleteNotification,
}) {
  const theme = useTheme()

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={24} />
      </Box>
    )
  }

  if (notifications.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <NotificationsIcon
          sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 1 }}
        />
        <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
          No notifications yet
        </Typography>
      </Box>
    )
  }

  return (
    <List disablePadding>
      {notifications.map((notification, index) => {
        const typeConfig = getTypeConfig(theme, notification.type)
        const Icon = typeConfig.icon

        return (
          <Box key={notification.id}>
            {index > 0 && (
              <Divider sx={{ borderColor: alpha(theme.palette.divider, 0.06) }} />
            )}
            <ListItem
              disablePadding
              secondaryAction={
                <IconButton
                  size="small"
                  onClick={(e) => onDeleteNotification(e, notification.id)}
                  aria-label="Delete notification"
                  data-testid={`notification-delete-button-${notification.id}`}
                  sx={{
                    color: theme.palette.text.disabled,
                    opacity: 0,
                    transition: 'opacity 150ms',
                    '.MuiListItem-root:hover &': {
                      opacity: 1,
                    },
                    '&:hover': {
                      color: theme.palette.text.primary,
                    },
                  }}
                >
                  <CloseIcon sx={{ fontSize: 16 }} />
                </IconButton>
              }
            >
              <ListItemButton
                onClick={() => onNotificationClick(notification)}
                data-testid={`notification-item-${notification.id}`}
                sx={{
                  py: 1.5,
                  px: 2,
                  bgcolor: notification.read
                    ? 'transparent'
                    : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50]),
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <Icon
                    sx={{
                      fontSize: 20,
                      color: typeConfig.color,
                    }}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <Typography
                        sx={{
                          fontSize: '14px',
                          fontWeight: notification.read ? 400 : 600,
                          color: theme.palette.text.primary,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          maxWidth: 200,
                        }}
                      >
                        {notification.title}
                      </Typography>
                      <Typography
                        sx={{
                          fontSize: '12px',
                          color: theme.palette.text.disabled,
                          ml: 1,
                          flexShrink: 0,
                        }}
                      >
                        {formatTimeAgo(notification.created_at)}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Typography
                      sx={{
                        fontSize: '0.75rem',
                        color: theme.palette.text.secondary,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {notification.message}
                    </Typography>
                  }
                />
                {!notification.read && (
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                      ml: 1,
                      flexShrink: 0,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          </Box>
        )
      })}
    </List>
  )
}
