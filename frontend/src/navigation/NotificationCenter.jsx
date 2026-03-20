/**
 * Premium Notification Center
 * Real-time notifications with theme-based styling
 */
import { useState, useEffect } from 'react'
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import NotificationsIcon from '@mui/icons-material/Notifications'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import NotificationsOffIcon from '@mui/icons-material/NotificationsOff'
import { readPreferences, subscribePreferences } from '@/utils/preferences'
import { useNotificationInteractions, useNotificationData, useNotificationActions } from './hooks/useNotifications'
import { fadeInUp } from './components/notificationHelpers'
import { NotificationHeader, NotificationFooter } from './components/NotificationPopover'
import NotificationList from './components/NotificationList'

export default function NotificationCenter() {
  const theme = useTheme()
  const [notificationsEnabled, setNotificationsEnabled] = useState(
    () => readPreferences().showNotifications ?? true
  )

  useEffect(() => {
    const unsubscribe = subscribePreferences((prefs) => {
      setNotificationsEnabled(prefs?.showNotifications ?? true)
    })
    return unsubscribe
  }, [])

  const interactions = useNotificationInteractions()
  const data = useNotificationData(notificationsEnabled)
  const actions = useNotificationActions(interactions, data, notificationsEnabled)

  if (!notificationsEnabled) {
    return (
      <Tooltip title="Notifications disabled in Settings">
        <span>
          <IconButton
            disabled
            data-testid="notifications-disabled-button"
            sx={{
              color: theme.palette.text.disabled,
            }}
          >
            <NotificationsOffIcon sx={{ fontSize: 20 }} />
          </IconButton>
        </span>
      </Tooltip>
    )
  }

  return (
    <>
      <Tooltip title="Notifications">
        <IconButton
          onClick={actions.handleClick}
          aria-label="Open notifications center"
          data-testid="notification-center-button"
          sx={{
            color: theme.palette.text.secondary,
            transition: 'all 0.2s ease',
            '&:hover': {
              color: theme.palette.text.primary,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            },
          }}
        >
          <Badge
            badgeContent={data.unreadCount}
            max={99}
            sx={{
              '& .MuiBadge-badge': {
                bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                color: 'common.white',
                fontSize: '10px',
                fontWeight: 600,
                minWidth: 16,
                height: 16,
              },
            }}
          >
            {data.unreadCount > 0 ? (
              <NotificationsActiveIcon sx={{ fontSize: 20 }} />
            ) : (
              <NotificationsIcon sx={{ fontSize: 20 }} />
            )}
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={actions.open}
        anchorEl={actions.anchorEl}
        onClose={actions.handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: 380,
            maxHeight: 480,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.92) : 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(12px)',
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            borderRadius: 1,  // Figma spec: 8px
            overflow: 'hidden',
            boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`,
            animation: `${fadeInUp} 0.2s ease-out`,
          },
        }}
      >
        <NotificationHeader
          unreadCount={data.unreadCount}
          onMarkAllRead={actions.handleMarkAllRead}
          onClearAll={actions.handleClearAll}
          notificationCount={data.notifications.length}
        />

        <Box sx={{ maxHeight: 380, overflow: 'auto' }}>
          <NotificationList
            notifications={data.notifications}
            loading={data.loading}
            onNotificationClick={actions.handleNotificationClick}
            onDeleteNotification={actions.handleDeleteNotification}
          />
        </Box>

        {data.notifications.length > 0 && (
          <NotificationFooter onViewActivity={actions.handleViewActivity} />
        )}
      </Popover>
    </>
  )
}
