/**
 * Premium Notification Center
 * Real-time notifications with theme-based styling
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  CircularProgress,
  Tooltip,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import NotificationsIcon from '@mui/icons-material/Notifications'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import NotificationsOffIcon from '@mui/icons-material/NotificationsOff'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import DoneAllIcon from '@mui/icons-material/DoneAll'
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep'
import CloseIcon from '@mui/icons-material/Close'
import { readPreferences, subscribePreferences } from '@/utils/preferences'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
  clearAllNotifications,
} from '@/api/client'

// =============================================================================
// ANIMATIONS
// =============================================================================

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

// =============================================================================
// HELPERS
// =============================================================================

const getTypeConfig = (theme, type) => {
  const configs = {
    info: {
      icon: InfoOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    success: {
      icon: CheckCircleOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    warning: {
      icon: WarningAmberOutlinedIcon,
      color: theme.palette.text.secondary,
    },
    error: {
      icon: ErrorOutlineIcon,
      color: theme.palette.text.secondary,
    },
  }
  return configs[type] || configs.info
}

const ENTITY_ROUTES = {
  template: (id) => (id ? `/templates/${id}/edit` : '/templates'),
  connection: () => '/connections',
  job: () => '/jobs',
  schedule: () => '/schedules',
  report: () => '/history',
}

function formatTimeAgo(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const seconds = Math.floor((now - date) / 1000)

  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`
  return date.toLocaleDateString()
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function NotificationCenter() {
  const theme = useTheme()
  const navigate = useNavigate()
  const { execute } = useInteraction()
  const [anchorEl, setAnchorEl] = useState(null)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [polling, setPolling] = useState(false)
  const pollingRef = useRef(false)
  const [notificationsEnabled, setNotificationsEnabled] = useState(
    () => readPreferences().showNotifications ?? true
  )

  const open = Boolean(anchorEl)

  const runUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'notifications', ...intent },
      action,
    })
  }, [execute])

  const runNavigate = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.NAVIGATE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'notifications', ...intent },
      action,
    })
  }, [execute])

  const runUpdate = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.UPDATE,
      label,
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'notifications', ...intent },
      action,
    })
  }, [execute])

  const runDelete = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.DELETE,
      label,
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'notifications', ...intent },
      action,
    })
  }, [execute])

  useEffect(() => {
    const unsubscribe = subscribePreferences((prefs) => {
      const enabled = prefs?.showNotifications ?? true
      setNotificationsEnabled(enabled)
      if (!enabled) {
        setAnchorEl(null)
      }
    })
    return unsubscribe
  }, [])

  const fetchNotifications = useCallback(async (showLoading = true) => {
    if (showLoading) setLoading(true)
    try {
      const data = await getNotifications({ limit: 20 })
      setNotifications(data.notifications || [])
      setUnreadCount(data.unreadCount || 0)
    } catch (err) {
      console.error('Failed to fetch notifications:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial fetch and visibility-aware polling
  useEffect(() => {
    if (!notificationsEnabled) return undefined
    fetchNotifications()

    let interval = null
    let isVisible = !document.hidden

    const startPolling = () => {
      if (interval) return
      interval = setInterval(() => {
        if (!pollingRef.current && isVisible) {
          pollingRef.current = true
          setPolling(true)
          fetchNotifications(false).finally(() => {
            pollingRef.current = false
            setPolling(false)
          })
        }
      }, 30000)
    }

    const stopPolling = () => {
      if (interval) {
        clearInterval(interval)
        interval = null
      }
    }

    const handleVisibilityChange = () => {
      isVisible = !document.hidden
      if (isVisible) {
        fetchNotifications(false)
        startPolling()
      } else {
        stopPolling()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    startPolling()

    return () => {
      stopPolling()
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [fetchNotifications, notificationsEnabled])

  const handleClick = useCallback((event) => {
    if (!notificationsEnabled) return undefined
    const anchor = event.currentTarget
    return runUI('Open notifications', () => {
      setAnchorEl(anchor)
      return fetchNotifications()
    })
  }, [fetchNotifications, notificationsEnabled, runUI])

  const handleClose = useCallback(() => {
    return runUI('Close notifications', () => setAnchorEl(null))
  }, [runUI])

  const handleNotificationClick = useCallback((notification) => {
    const entityTypeRaw = notification.entity_type || notification.entityType
    const entityId = notification.entity_id || notification.entityId
    const normalizedType = entityTypeRaw ? String(entityTypeRaw).toLowerCase().replace(/s$/, '') : ''
    const fallbackRoute =
      normalizedType && ENTITY_ROUTES[normalizedType]
        ? ENTITY_ROUTES[normalizedType](entityId)
        : '/activity'
    const targetRoute = notification.link || fallbackRoute
    return runNavigate('Open notification', async () => {
      let readError = null
      if (!notification.read) {
        try {
          await markNotificationRead(notification.id)
          setNotifications((prev) =>
            prev.map((n) => (n.id === notification.id ? { ...n, read: true } : n))
          )
          setUnreadCount((prev) => Math.max(0, prev - 1))
        } catch (err) {
          readError = err
          console.error('Failed to mark notification as read:', err)
        }
      }

      if (targetRoute) {
        navigate(targetRoute)
      }
      setAnchorEl(null)

      if (readError) {
        throw readError
      }
    }, {
      notificationId: notification.id,
      entityType: normalizedType,
      targetRoute,
    })
  }, [navigate, runNavigate])

  const handleMarkAllRead = useCallback(() => {
    return runUpdate('Mark all notifications read', async () => {
      await markAllNotificationsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
      setUnreadCount(0)
    }, { unreadCount })
  }, [runUpdate, unreadCount])

  const handleDeleteNotification = useCallback((event, notificationId) => {
    event.stopPropagation()
    return runDelete('Delete notification', async () => {
      await deleteNotification(notificationId)
      setNotifications((prev) => {
        const removed = prev.find((n) => n.id === notificationId)
        if (removed && !removed.read) {
          setUnreadCount((count) => Math.max(0, count - 1))
        }
        return prev.filter((n) => n.id !== notificationId)
      })
    }, { notificationId })
  }, [runDelete])

  const handleClearAll = useCallback(() => {
    return runDelete('Clear notifications', async () => {
      await clearAllNotifications()
      setNotifications([])
      setUnreadCount(0)
    }, { count: notifications.length })
  }, [runDelete, notifications.length])

  const handleViewActivity = useCallback(() => {
    return runNavigate('Open activity log', () => {
      navigate('/activity')
      setAnchorEl(null)
    }, { targetRoute: '/activity' })
  }, [navigate, runNavigate])

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
          onClick={handleClick}
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
            badgeContent={unreadCount}
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
            {unreadCount > 0 ? (
              <NotificationsActiveIcon sx={{ fontSize: 20 }} />
            ) : (
              <NotificationsIcon sx={{ fontSize: 20 }} />
            )}
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
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
        {/* Header */}
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
                onClick={handleMarkAllRead}
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
                onClick={handleClearAll}
                disabled={notifications.length === 0}
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

        {/* Content */}
        <Box sx={{ maxHeight: 380, overflow: 'auto' }}>
          {loading ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <CircularProgress size={24} />
            </Box>
          ) : notifications.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <NotificationsIcon
                sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 1 }}
              />
              <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
                No notifications yet
              </Typography>
            </Box>
          ) : (
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
                          onClick={(e) => handleDeleteNotification(e, notification.id)}
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
                        onClick={() => handleNotificationClick(notification)}
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
          )}
        </Box>

        {/* Footer */}
        {notifications.length > 0 && (
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
              onClick={handleViewActivity}
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
        )}
      </Popover>
    </>
  )
}
