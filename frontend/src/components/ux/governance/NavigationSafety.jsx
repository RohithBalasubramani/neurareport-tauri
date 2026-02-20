/**
 * UX Governance: Navigation Safety System
 *
 * Prevents accidental data loss by:
 * - Blocking navigation during active operations
 * - Warning about unsaved changes
 * - Requiring confirmation for destructive navigation
 *
 * RULE: Every background action MUST communicate whether it's safe to navigate away.
 */
import { createContext, useContext, useCallback, useMemo, useRef, useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Box,
  Typography,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Warning as WarningIcon,
  HourglassEmpty as PendingIcon,
  Edit as UnsavedIcon,
} from '@mui/icons-material'
import { useBlocker, useBeforeUnload } from 'react-router-dom'

// ============================================================================
// NAVIGATION BLOCKER TYPES
// ============================================================================

export const BlockerType = {
  // Active operation in progress
  OPERATION_IN_PROGRESS: 'operation_in_progress',

  // Unsaved form changes
  UNSAVED_CHANGES: 'unsaved_changes',

  // Custom blocker
  CUSTOM: 'custom',
}

// ============================================================================
// CONTEXT
// ============================================================================

const NavigationSafetyContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function NavigationSafetyProvider({ children }) {
  const theme = useTheme()

  // Active blockers
  const [blockers, setBlockers] = useState(new Map())

  // Pending navigation (when blocked)
  const [pendingNavigation, setPendingNavigation] = useState(null)

  // Confirmation dialog state
  const [dialogOpen, setDialogOpen] = useState(false)

  /**
   * Register a navigation blocker
   * @returns {string} Blocker ID for cleanup
   */
  const registerBlocker = useCallback((config) => {
    const blockerId = `blocker_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

    const blocker = {
      id: blockerId,
      type: config.type || BlockerType.CUSTOM,
      label: config.label,
      description: config.description,
      canForceNavigate: config.canForceNavigate ?? true,
      priority: config.priority || 0,
      createdAt: Date.now(),
    }

    setBlockers((prev) => {
      const updated = new Map(prev)
      updated.set(blockerId, blocker)
      return updated
    })

    return blockerId
  }, [])

  /**
   * Unregister a navigation blocker
   */
  const unregisterBlocker = useCallback((blockerId) => {
    setBlockers((prev) => {
      const updated = new Map(prev)
      updated.delete(blockerId)
      return updated
    })
  }, [])

  /**
   * Check if navigation is safe
   */
  const isNavigationSafe = useCallback(() => {
    return blockers.size === 0
  }, [blockers.size])

  /**
   * Get all active blockers
   */
  const getActiveBlockers = useCallback(() => {
    return Array.from(blockers.values()).sort((a, b) => b.priority - a.priority)
  }, [blockers])

  /**
   * Attempt to navigate (shows confirmation if blocked)
   */
  const attemptNavigation = useCallback((callback) => {
    if (isNavigationSafe()) {
      callback()
      return
    }

    setPendingNavigation(() => callback)
    setDialogOpen(true)
  }, [isNavigationSafe])

  /**
   * Force navigation (bypasses blockers)
   */
  const forceNavigation = useCallback(() => {
    try {
      if (pendingNavigation) {
        pendingNavigation()
      }
    } catch (err) {
      console.error('[NavigationSafety] forceNavigation callback failed:', err)
    } finally {
      setPendingNavigation(null)
      setDialogOpen(false)
    }
  }, [pendingNavigation])

  /**
   * Cancel pending navigation
   */
  const cancelNavigation = useCallback(() => {
    setPendingNavigation(null)
    setDialogOpen(false)
  }, [])

  // Handle browser beforeunload
  useBeforeUnload(
    useCallback(
      (event) => {
        if (!isNavigationSafe()) {
          event.preventDefault()
          return (event.returnValue = 'You have unsaved changes. Are you sure you want to leave?')
        }
      },
      [isNavigationSafe]
    )
  )

  const contextValue = useMemo(() => ({
    registerBlocker,
    unregisterBlocker,
    isNavigationSafe,
    getActiveBlockers,
    attemptNavigation,
    forceNavigation,
    cancelNavigation,
    hasBlockers: blockers.size > 0,
    blockerCount: blockers.size,
  }), [
    registerBlocker,
    unregisterBlocker,
    isNavigationSafe,
    getActiveBlockers,
    attemptNavigation,
    forceNavigation,
    cancelNavigation,
    blockers.size,
  ])

  return (
    <NavigationSafetyContext.Provider value={contextValue}>
      {children}

      {/* Navigation Blocked Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={cancelNavigation}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: alpha(theme.palette.background.paper, 0.95),
            backdropFilter: 'blur(10px)',
            borderRadius: 1,  // Figma spec: 8px
          },
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <WarningIcon sx={{ color: 'text.secondary' }} />
          <Typography variant="h6" fontWeight={600}>
            Wait! You have unsaved work
          </Typography>
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Leaving this page will interrupt the following:
          </DialogContentText>
          <List dense>
            {getActiveBlockers().map((blocker) => (
              <ListItem key={blocker.id}>
                <ListItemIcon>
                  {blocker.type === BlockerType.OPERATION_IN_PROGRESS ? (
                    <CircularProgress size={20} />
                  ) : blocker.type === BlockerType.UNSAVED_CHANGES ? (
                    <UnsavedIcon sx={{ color: 'text.secondary' }} />
                  ) : (
                    <PendingIcon sx={{ color: 'text.secondary' }} />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={blocker.label}
                  secondary={blocker.description}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={cancelNavigation} variant="contained">
            Stay on this page
          </Button>
          <Button onClick={forceNavigation} sx={{ color: 'text.secondary' }}>
            Leave anyway
          </Button>
        </DialogActions>
      </Dialog>
    </NavigationSafetyContext.Provider>
  )
}

// ============================================================================
// HOOKS
// ============================================================================

export function useNavigationSafety() {
  const context = useContext(NavigationSafetyContext)
  if (!context) {
    throw new Error('useNavigationSafety must be used within NavigationSafetyProvider')
  }
  return context
}

/**
 * Hook to block navigation during an operation
 * Auto-registers and unregisters blocker
 */
export function useOperationBlocker(isActive, label, description) {
  const { registerBlocker, unregisterBlocker } = useNavigationSafety()
  const blockerIdRef = useRef(null)

  useEffect(() => {
    if (isActive) {
      blockerIdRef.current = registerBlocker({
        type: BlockerType.OPERATION_IN_PROGRESS,
        label,
        description,
      })
    } else if (blockerIdRef.current) {
      unregisterBlocker(blockerIdRef.current)
      blockerIdRef.current = null
    }

    return () => {
      if (blockerIdRef.current) {
        unregisterBlocker(blockerIdRef.current)
      }
    }
  }, [isActive, label, description, registerBlocker, unregisterBlocker])
}

/**
 * Hook to block navigation when form has unsaved changes
 */
export function useUnsavedChangesBlocker(hasChanges, formName = 'form') {
  const { registerBlocker, unregisterBlocker } = useNavigationSafety()
  const blockerIdRef = useRef(null)

  useEffect(() => {
    if (hasChanges) {
      blockerIdRef.current = registerBlocker({
        type: BlockerType.UNSAVED_CHANGES,
        label: `Unsaved changes in ${formName}`,
        description: 'Your changes will be lost if you leave',
      })
    } else if (blockerIdRef.current) {
      unregisterBlocker(blockerIdRef.current)
      blockerIdRef.current = null
    }

    return () => {
      if (blockerIdRef.current) {
        unregisterBlocker(blockerIdRef.current)
      }
    }
  }, [hasChanges, formName, registerBlocker, unregisterBlocker])
}

/**
 * Route blocker component using react-router-dom
 */
export function RouteBlocker() {
  const { isNavigationSafe, getActiveBlockers } = useNavigationSafety()
  const [dialogOpen, setDialogOpen] = useState(false)

  // Use react-router's useBlocker to prevent route changes
  const blocker = useBlocker(
    useCallback(() => !isNavigationSafe(), [isNavigationSafe])
  )

  useEffect(() => {
    if (blocker.state === 'blocked') {
      setDialogOpen(true)
    } else {
      setDialogOpen(false)
    }
  }, [blocker.state])

  const handleProceed = useCallback(() => {
    blocker.proceed?.()
  }, [blocker])

  const handleCancel = useCallback(() => {
    blocker.reset?.()
  }, [blocker])

  const activeBlockers = getActiveBlockers()

  return (
    <Dialog open={dialogOpen} onClose={handleCancel}>
      <DialogTitle>Unsaved Changes</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Leaving this page may discard unsaved changes or interrupt active operations.
        </DialogContentText>
        {activeBlockers.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Active blockers: {activeBlockers.map((b) => b.reason).join(', ')}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel} variant="contained">Stay on this page</Button>
        <Button onClick={handleProceed}>Leave anyway</Button>
      </DialogActions>
    </Dialog>
  )
}
