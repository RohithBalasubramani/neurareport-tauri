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
import { createContext, useContext, useCallback, useMemo, useState } from 'react'
import { useBeforeUnload } from 'react-router-dom'
import NavigationBlockedDialog from './NavigationBlockedDialog'

// Re-export constants and hooks for backwards compatibility
export { BlockerType } from './navigationConstants'
export { useOperationBlocker, useUnsavedChangesBlocker } from './hooks/useNavigationBlockers'
export { default as RouteBlocker } from './RouteBlocker'

// ============================================================================
// CONTEXT
// ============================================================================

const NavigationSafetyContext = createContext(null)

// ============================================================================
// PROVIDER
// ============================================================================

export function NavigationSafetyProvider({ children }) {
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
      type: config.type || 'custom',
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

      <NavigationBlockedDialog
        open={dialogOpen}
        activeBlockers={getActiveBlockers()}
        onCancel={cancelNavigation}
        onForceNavigate={forceNavigation}
      />
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
