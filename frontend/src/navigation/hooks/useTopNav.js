/**
 * TopNav state and interaction hooks
 */
import { useState, useCallback, useMemo } from 'react'
import { useNavigateInteraction, useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { useAppStore } from '../../stores'
import { useJobsList } from '../../hooks/useJobs'
import { withBase } from '../../api/client'

export function useTopNavInteractions(onMenuClick) {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'topnav', ...intent },
      action,
    })
  }, [execute])

  const handleNavigate = useCallback((path, label) => {
    navigate(path, {
      label: label || `Open ${path}`,
      intent: { source: 'topnav', path },
    })
  }, [navigate])

  const handleMenuButtonClick = useCallback(() => {
    return executeUI('Open navigation menu', () => onMenuClick?.(), { target: 'sidebar' })
  }, [executeUI, onMenuClick])

  const handleOpenCommandPalette = useCallback(() => {
    return executeUI('Open command palette', () => {
      if (typeof window === 'undefined') return
      window.dispatchEvent(new CustomEvent('neura:open-command-palette'))
    })
  }, [executeUI])

  return { execute, executeUI, handleNavigate, handleMenuButtonClick, handleOpenCommandPalette }
}

export function useTopNavMenus(executeUI, handleNavigate) {
  const [anchorEl, setAnchorEl] = useState(null)
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState(null)

  const openMenu = useCallback((anchor) => {
    setAnchorEl(anchor)
  }, [])

  const closeMenu = useCallback(() => {
    setAnchorEl(null)
  }, [])

  const handleOpenMenu = useCallback((event) => {
    const anchor = event.currentTarget
    return executeUI('Open user menu', () => openMenu(anchor))
  }, [executeUI, openMenu])

  const handleCloseMenu = useCallback(() => {
    return executeUI('Close user menu', () => closeMenu())
  }, [executeUI, closeMenu])

  const handleNavigateAndClose = useCallback((path, label) => {
    handleNavigate(path, label)
    closeMenu()
  }, [handleNavigate, closeMenu])

  const closeNotifications = useCallback(() => {
    setNotificationsAnchorEl(null)
  }, [])

  const handleOpenNotifications = useCallback((event) => {
    const anchor = event.currentTarget
    return executeUI('Open notifications', () => setNotificationsAnchorEl(anchor))
  }, [executeUI])

  const handleCloseNotifications = useCallback(() => {
    return executeUI('Close notifications', () => closeNotifications())
  }, [executeUI, closeNotifications])

  const handleOpenJobsPanel = useCallback(() => {
    return executeUI('Open jobs panel', () => {
      if (typeof window === 'undefined') return
      window.dispatchEvent(new CustomEvent('neura:open-jobs-panel'))
      closeNotifications()
    })
  }, [executeUI, closeNotifications])

  const handleOpenDownload = useCallback((download) => {
    return executeUI('Open download', () => {
      const rawUrl = download?.pdfUrl || download?.docxUrl || download?.xlsxUrl || download?.htmlUrl || download?.url
      if (!rawUrl || typeof window === 'undefined') return
      const href = typeof rawUrl === 'string' ? withBase(rawUrl) : rawUrl
      window.open(href, '_blank', 'noopener')
      closeNotifications()
    }, { downloadId: download?.id })
  }, [executeUI, closeNotifications])

  return {
    anchorEl, notificationsAnchorEl,
    closeMenu,
    handleOpenMenu, handleCloseMenu,
    handleNavigateAndClose,
    handleOpenNotifications, handleCloseNotifications,
    handleOpenJobsPanel, handleOpenDownload,
  }
}

export function useTopNavDialogs(executeUI) {
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  const handleOpenShortcuts = useCallback(() => executeUI('Open shortcuts', () => setShortcutsOpen(true)), [executeUI])
  const handleCloseShortcuts = useCallback(() => executeUI('Close shortcuts', () => setShortcutsOpen(false)), [executeUI])

  const handleOpenHelp = useCallback(() => executeUI('Open help', () => setHelpOpen(true)), [executeUI])
  const handleCloseHelp = useCallback(() => executeUI('Close help', () => setHelpOpen(false)), [executeUI])

  return {
    shortcutsOpen, helpOpen,
    handleOpenShortcuts, handleCloseShortcuts,
    handleOpenHelp, handleCloseHelp,
  }
}

export function useTopNavSignOut(execute, closeMenu) {
  const clearAppStorage = useCallback(() => {
    if (typeof window === 'undefined') return
    try {
      Object.keys(window.localStorage).forEach((key) => {
        if (key.startsWith('neura') || key.startsWith('neurareport')) {
          window.localStorage.removeItem(key)
        }
      })
    } catch {
      // Ignore storage cleanup failures
    }
  }, [])

  const handleSignOut = useCallback(() => {
    return execute({
      type: InteractionType.LOGOUT,
      label: 'Sign out',
      reversibility: Reversibility.PARTIALLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'topnav' },
      action: () => {
        closeMenu()
        clearAppStorage()
        if (typeof window !== 'undefined') {
          window.location.assign('/')
        }
      },
    })
  }, [execute, closeMenu, clearAppStorage])

  return { handleSignOut }
}

export function useTopNavNotificationData() {
  const downloads = useAppStore((state) => state.downloads)
  const jobsQuery = useJobsList({ limit: 5 })
  const jobs = jobsQuery?.data?.jobs || []

  const jobNotifications = useMemo(() => (
    Array.isArray(jobs) ? jobs.slice(0, 3) : []
  ), [jobs])

  const downloadNotifications = useMemo(() => (
    Array.isArray(downloads) ? downloads.slice(0, 3) : []
  ), [downloads])

  const notificationsCount = jobNotifications.length + downloadNotifications.length

  return { jobNotifications, downloadNotifications, notificationsCount }
}
