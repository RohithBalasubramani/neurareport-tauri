/**
 * GlobalSearch state and interaction hooks
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '../../api/client'

const SEARCH_ROUTE_BY_TYPE = {
  template: (result) => (result?.id ? `/templates/${result.id}/edit` : '/templates'),
  connection: () => '/connections',
  job: () => '/jobs',
}

export function useGlobalSearchState({ enableShortcut }) {
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { source: 'global-search', ...intent } }),
    [navigate]
  )

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'global-search', ...intent },
      action,
    })
  }, [execute])

  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [hasSearched, setHasSearched] = useState(false)
  const inputRef = useRef(null)
  const anchorRef = useRef(null)
  const debounceRef = useRef(null)

  // Keyboard shortcut to focus search (Ctrl/Cmd + K)
  useEffect(() => {
    if (!enableShortcut) return undefined
    const handleKeyDown = (e) => {
      if (e.defaultPrevented) return
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
      if (e.key === 'Escape' && open) {
        setOpen(false)
        inputRef.current?.blur()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [enableShortcut, open])

  // Handle result selection
  const handleSelect = useCallback((result) => {
    setOpen(false)
    setQuery('')
    setResults([])
    if (result?.url) {
      handleNavigate(result.url, `Open ${result.label}`, { resultType: result.type, resultId: result.id })
      return
    }
    const typeKey = result?.type ? String(result.type).toLowerCase() : ''
    const routeBuilder = SEARCH_ROUTE_BY_TYPE[typeKey]
    if (routeBuilder) {
      const nextPath = routeBuilder(result)
      if (nextPath) {
        handleNavigate(nextPath, `Open ${result.label}`, { resultType: result.type, resultId: result.id })
      }
    }
  }, [handleNavigate])

  // Handle arrow key navigation
  const handleKeyDown = useCallback((e) => {
    if (!open || results.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault()
      handleSelect(results[selectedIndex])
    }
  }, [open, results, selectedIndex, handleSelect])

  const handleSearch = useCallback((searchQuery) => {
    const normalizedQuery = searchQuery?.trim() || ''
    if (!normalizedQuery || normalizedQuery.length < 2) {
      setResults([])
      setOpen(false)
      setHasSearched(false)
      setSelectedIndex(-1)
      return
    }

    setLoading(true)
    setHasSearched(true)
    execute({
      type: InteractionType.EXECUTE,
      label: 'Search',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'global-search', query: normalizedQuery },
      action: async () => {
        try {
          const data = await api.globalSearch(normalizedQuery, { limit: 10 })
          const nextResults = data.results || []
          const isFocused =
            typeof document !== 'undefined' && document.activeElement === inputRef.current
          setResults(nextResults)
          setOpen(isFocused)
          setSelectedIndex(-1)
        } catch (err) {
          console.error('Search failed:', err)
          const isFocused =
            typeof document !== 'undefined' && document.activeElement === inputRef.current
          setResults([])
          setOpen(isFocused)
        }
      },
    }).finally(() => setLoading(false))
  }, [execute])

  const handleInputChange = useCallback((e) => {
    const value = e.target.value
    setQuery(value)

    // Debounce search
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      handleSearch(value)
    }, 300)
  }, [handleSearch])

  const handleFocus = useCallback(() => {
    if (hasSearched && query.trim().length >= 2) {
      executeUI('Open search results', () => setOpen(true))
    }
  }, [executeUI, hasSearched, query])

  const handleClickAway = useCallback(() => {
    executeUI('Close search results', () => setOpen(false))
  }, [executeUI])

  return {
    query, results, loading, open, selectedIndex,
    inputRef, anchorRef,
    handleSelect, handleKeyDown, handleInputChange,
    handleFocus, handleClickAway,
  }
}
