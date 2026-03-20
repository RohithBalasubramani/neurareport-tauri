/**
 * NotificationCenter state and interaction hooks
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
  clearAllNotifications,
} from '@/api/client'

export function useNotificationInteractions() {
  const { execute } = useInteraction()

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

  return { runUI, runNavigate, runUpdate, runDelete }
}

export function useNotificationData(notificationsEnabled) {
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [polling, setPolling] = useState(false)
  const pollingRef = useRef(false)

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

  return { notifications, setNotifications, unreadCount, setUnreadCount, loading, polling, fetchNotifications }
}

const ENTITY_ROUTES = {
  template: (id) => (id ? `/templates/${id}/edit` : '/templates'),
  connection: () => '/connections',
  job: () => '/jobs',
  schedule: () => '/schedules',
  report: () => '/history',
}

export function useNotificationActions(
  { runUI, runNavigate, runUpdate, runDelete },
  { notifications, setNotifications, unreadCount, setUnreadCount, fetchNotifications },
  notificationsEnabled = true
) {
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState(null)
  const open = Boolean(anchorEl)

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
  }, [navigate, runNavigate, setNotifications, setUnreadCount])

  const handleMarkAllRead = useCallback(() => {
    return runUpdate('Mark all notifications read', async () => {
      await markAllNotificationsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
      setUnreadCount(0)
    }, { unreadCount })
  }, [runUpdate, unreadCount, setNotifications, setUnreadCount])

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
  }, [runDelete, setNotifications, setUnreadCount])

  const handleClearAll = useCallback(() => {
    return runDelete('Clear notifications', async () => {
      await clearAllNotifications()
      setNotifications([])
      setUnreadCount(0)
    }, { count: notifications.length })
  }, [runDelete, notifications.length, setNotifications, setUnreadCount])

  const handleViewActivity = useCallback(() => {
    return runNavigate('Open activity log', () => {
      navigate('/activity')
      setAnchorEl(null)
    }, { targetRoute: '/activity' })
  }, [navigate, runNavigate])

  return {
    anchorEl, open,
    handleClick, handleClose,
    handleNotificationClick, handleMarkAllRead,
    handleDeleteNotification, handleClearAll,
    handleViewActivity,
  }
}
