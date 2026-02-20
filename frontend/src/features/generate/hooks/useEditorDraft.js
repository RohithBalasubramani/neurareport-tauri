import { useState, useEffect, useCallback, useRef } from 'react'

const DRAFT_PREFIX = 'neura-template-draft-'
const DRAFT_EXPIRY_MS = 24 * 60 * 60 * 1000 // 24 hours

/**
 * Hook for auto-saving template drafts to localStorage.
 *
 * Features:
 * - Auto-saves drafts periodically when content changes
 * - Detects and restores unsaved drafts on load
 * - Cleans up old/expired drafts
 * - Provides manual save/discard controls
 */
export function useEditorDraft(templateId, { autoSaveInterval = 10000, enabled = true } = {}) {
  const [hasDraft, setHasDraft] = useState(false)
  const [draftData, setDraftData] = useState(null)
  const [lastSaved, setLastSaved] = useState(null)
  const autoSaveTimerRef = useRef(null)
  const pendingContentRef = useRef(null)

  const storageKey = `${DRAFT_PREFIX}${templateId}`

  // Load draft on mount
  useEffect(() => {
    if (!templateId || !enabled) return

    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const parsed = JSON.parse(stored)
        const age = Date.now() - (parsed.savedAt || 0)

        if (age < DRAFT_EXPIRY_MS) {
          setHasDraft(true)
          setDraftData(parsed)
        } else {
          // Expired draft, clean up
          localStorage.removeItem(storageKey)
        }
      }
    } catch (err) {
      console.warn('Failed to load draft:', err)
    }
  }, [templateId, storageKey, enabled])

  // Clean up old drafts on mount
  useEffect(() => {
    if (!enabled) return

    try {
      const keys = Object.keys(localStorage).filter((k) => k.startsWith(DRAFT_PREFIX))
      keys.forEach((key) => {
        try {
          const stored = localStorage.getItem(key)
          if (stored) {
            const parsed = JSON.parse(stored)
            const age = Date.now() - (parsed.savedAt || 0)
            if (age >= DRAFT_EXPIRY_MS) {
              localStorage.removeItem(key)
            }
          }
        } catch {
          // Invalid draft, remove it
          localStorage.removeItem(key)
        }
      })
    } catch (err) {
      console.warn('Failed to clean up drafts:', err)
    }
  }, [enabled])

  // Save draft to localStorage
  const saveDraft = useCallback(
    (html, instructions = '') => {
      if (!templateId || !enabled) return false

      try {
        const draft = {
          html,
          instructions,
          savedAt: Date.now(),
          templateId,
        }
        localStorage.setItem(storageKey, JSON.stringify(draft))
        setLastSaved(new Date())
        return true
      } catch (err) {
        console.warn('Failed to save draft:', err)
        return false
      }
    },
    [templateId, storageKey, enabled]
  )

  // Discard draft
  const discardDraft = useCallback(() => {
    if (!templateId) return

    try {
      localStorage.removeItem(storageKey)
      setHasDraft(false)
      setDraftData(null)
    } catch (err) {
      console.warn('Failed to discard draft:', err)
    }
  }, [templateId, storageKey])

  // Auto-save with debounce
  const scheduleAutoSave = useCallback(
    (html, instructions = '') => {
      if (!enabled) return

      pendingContentRef.current = { html, instructions }

      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }

      autoSaveTimerRef.current = setTimeout(() => {
        if (pendingContentRef.current) {
          saveDraft(pendingContentRef.current.html, pendingContentRef.current.instructions)
        }
      }, autoSaveInterval)
    },
    [enabled, autoSaveInterval, saveDraft]
  )

  // Flush pending draft and cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
      // Flush any pending content before unmount
      if (pendingContentRef.current) {
        try {
          const draft = {
            html: pendingContentRef.current.html,
            instructions: pendingContentRef.current.instructions,
            savedAt: Date.now(),
            templateId,
          }
          localStorage.setItem(storageKey, JSON.stringify(draft))
        } catch {
          // Best-effort flush on unmount
        }
      }
    }
  }, [templateId, storageKey])

  // Clear draft when it's been applied (i.e., saved to server)
  const clearDraftAfterSave = useCallback(() => {
    discardDraft()
  }, [discardDraft])

  return {
    // State
    hasDraft,
    draftData,
    lastSaved,

    // Actions
    saveDraft,
    discardDraft,
    scheduleAutoSave,
    clearDraftAfterSave,
  }
}

export default useEditorDraft
