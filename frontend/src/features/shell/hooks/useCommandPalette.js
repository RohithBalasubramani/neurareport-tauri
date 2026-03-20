import { useState, useEffect, useMemo, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import HistoryIcon from '@mui/icons-material/History'
import { useAppStore } from '@/stores'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { globalSearch } from '@/api/client'
import {
  COMMANDS,
  ICON_MAP,
  MAX_RECENT,
  SEARCH_TYPE_CONFIG,
  fuzzyScore,
  loadRecentCommands,
  persistRecentCommands,
} from '../components/command-palette/commandRegistry'

export function useCommandPalette({ open, onClose }) {
  const navigate = useNavigate()
  const { execute } = useInteraction()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  const [recentCommands, setRecentCommands] = useState([])
  const inputRef = useRef(null)
  const listRef = useRef(null)
  const searchTimeoutRef = useRef(null)

  const templates = useAppStore((s) => s.templates)
  const approvedTemplates = templates.filter((t) => t.status === 'approved')

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'command-palette', ...intent },
      action,
    })
  }, [execute])

  const handleClose = useCallback(() => {
    return executeUI('Close command palette', () => onClose?.())
  }, [executeUI, onClose])

  const updateRecentCommands = useCallback((entry) => {
    setRecentCommands((prev) => {
      const next = [entry, ...prev.filter((item) => item.id !== entry.id)].slice(0, MAX_RECENT)
      persistRecentCommands(next)
      return next
    })
  }, [])

  // Debounced search effect
  useEffect(() => {
    const trimmed = query.trim()
    if (!trimmed || trimmed.length < 2) {
      setSearchResults([])
      setIsSearching(false)
      return
    }
    const cappedQuery = trimmed.length > 200 ? trimmed.slice(0, 200) : trimmed
    setIsSearching(true)
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }
    searchTimeoutRef.current = setTimeout(() => {
      execute({
        type: InteractionType.EXECUTE,
        label: 'Search command palette',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: { source: 'command-palette', query: cappedQuery },
        action: async () => {
          try {
            const result = await globalSearch(cappedQuery, { limit: 10 })
            setSearchResults(result.results || [])
          } catch (err) {
            console.error('Search failed:', err)
            setSearchResults([])
          }
        },
      }).finally(() => setIsSearching(false))
    }, 200)
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [execute, query])

  // Build full command list
  const allCommands = useMemo(() => {
    const templateCommands = approvedTemplates.slice(0, 5).map((t) => ({
      id: `template-${t.id}`,
      label: t.name,
      description: 'Edit template',
      icon: DescriptionOutlinedIcon,
      iconKey: 'templates',
      action: 'navigate',
      path: `/templates/${t.id}/edit`,
      group: 'Recent Templates',
    }))
    const searchCommands = searchResults.map((result) => {
      const config = SEARCH_TYPE_CONFIG[result.type] || {
        icon: DescriptionOutlinedIcon,
        iconKey: 'templates',
        pathBuilder: () => '/',
        label: 'Item',
      }
      return {
        id: `search-${result.type}-${result.id}`,
        label: result.name,
        description: result.description || `${config.label}`,
        icon: config.icon,
        iconKey: config.iconKey,
        action: 'navigate',
        path: config.pathBuilder(result),
        group: 'Search Results',
        type: result.type,
        score: result.score,
      }
    })
    const recent = recentCommands.map((entry) => ({
      ...entry,
      icon: ICON_MAP[entry.iconKey] || HistoryIcon,
      action: 'navigate',
      group: 'Recent',
    }))
    return [...recent, ...searchCommands, ...COMMANDS, ...templateCommands]
  }, [approvedTemplates, searchResults, recentCommands])

  // Filter commands based on query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return allCommands
    const q = query.trim()
    const searchCommands = allCommands.filter((cmd) => cmd.group === 'Search Results')
    const otherCommands = allCommands.filter((cmd) => cmd.group !== 'Search Results')
    const rankedOthers = otherCommands
      .map((cmd) => {
        const labelScore = fuzzyScore(q, cmd.label || '')
        const descScore = fuzzyScore(q, cmd.description || '')
        const groupScore = fuzzyScore(q, cmd.group || '')
        const score = Math.max(labelScore, descScore, groupScore)
        return { cmd, score }
      })
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((item) => item.cmd)
    return searchCommands.length
      ? [...searchCommands, ...rankedOthers.slice(0, 8)]
      : rankedOthers
  }, [allCommands, query])

  // Group commands
  const groupedCommands = useMemo(() => {
    const groups = {}
    filteredCommands.forEach((cmd) => {
      const group = cmd.group || 'Other'
      if (!groups[group]) groups[group] = []
      groups[group].push(cmd)
    })
    return groups
  }, [filteredCommands])

  // Reset on open
  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedIndex(0)
      setSearchResults([])
      setIsSearching(false)
      setRecentCommands(loadRecentCommands())
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  // Keep selected index in bounds
  useEffect(() => {
    if (selectedIndex >= filteredCommands.length) {
      setSelectedIndex(Math.max(0, filteredCommands.length - 1))
    }
  }, [filteredCommands.length, selectedIndex])

  // Execute command
  const executeCommand = useCallback(
    (cmd) => {
      if (!cmd) return undefined
      return execute({
        type: cmd.action === 'navigate' ? InteractionType.NAVIGATE : InteractionType.EXECUTE,
        label: cmd.label || 'Run command',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: {
          source: 'command-palette',
          commandId: cmd.id,
          action: cmd.action,
          path: cmd.path,
          group: cmd.group,
        },
        action: async () => {
          if (cmd?.action === 'navigate' && cmd?.path) {
            updateRecentCommands({
              id: cmd.id,
              label: cmd.label,
              description: cmd.description,
              path: cmd.path,
              iconKey: cmd.iconKey || cmd.type || 'recent',
            })
            navigate(cmd.path)
          } else if (typeof cmd.action === 'function') {
            await cmd.action()
          }
          onClose?.()
        },
      })
    },
    [execute, navigate, onClose, updateRecentCommands]
  )

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex((prev) => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (filteredCommands[selectedIndex]) {
            executeCommand(filteredCommands[selectedIndex])
          }
          break
        case 'Escape':
          e.preventDefault()
          handleClose()
          break
      }
    },
    [filteredCommands, selectedIndex, executeCommand, handleClose]
  )

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedEl = listRef.current.querySelector(`[data-index="${selectedIndex}"]`)
      selectedEl?.scrollIntoView({ block: 'nearest' })
    }
  }, [selectedIndex])

  // Pre-compute flat index mapping
  const flatIndexMap = useMemo(() => {
    const map = new Map()
    let idx = 0
    Object.entries(groupedCommands).forEach(([, commands]) => {
      commands.forEach((cmd) => {
        map.set(cmd.id, idx++)
      })
    })
    return map
  }, [groupedCommands])

  return {
    query,
    setQuery,
    selectedIndex,
    setSelectedIndex,
    isSearching,
    filteredCommands,
    groupedCommands,
    flatIndexMap,
    inputRef,
    listRef,
    handleKeyDown,
    handleClose,
    executeCommand,
  }
}
