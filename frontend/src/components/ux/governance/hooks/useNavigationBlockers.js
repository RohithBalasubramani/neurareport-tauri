/**
 * Navigation Blocker Hooks
 *
 * Hooks for blocking navigation during operations or unsaved changes.
 */
import { useCallback, useRef, useEffect } from 'react'
import { useNavigationSafety } from '../NavigationSafety'
import { BlockerType } from '../navigationConstants'

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
