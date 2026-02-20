/**
 * Premium Global Search
 * Command palette style search with theme-based styling
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import {
  Box,
  TextField,
  InputAdornment,
  Popper,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  Chip,
  CircularProgress,
  useTheme,
  alpha,
  ClickAwayListener,
  keyframes,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import SearchIcon from '@mui/icons-material/Search'
import DescriptionIcon from '@mui/icons-material/Description'
import StorageIcon from '@mui/icons-material/Storage'
import WorkIcon from '@mui/icons-material/Work'
import KeyboardIcon from '@mui/icons-material/Keyboard'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '../api/client'

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
    template: { icon: DescriptionIcon, color: theme.palette.text.secondary, label: 'Template' },
    connection: { icon: StorageIcon, color: theme.palette.text.secondary, label: 'Connection' },
    job: { icon: WorkIcon, color: theme.palette.text.secondary, label: 'Job' },
  }
  return configs[type] || configs.template
}

const SEARCH_ROUTE_BY_TYPE = {
  template: (result) => (result?.id ? `/templates/${result.id}/edit` : '/templates'),
  connection: () => '/connections',
  job: () => '/jobs',
}

// =============================================================================
// SEARCH RESULT COMPONENT
// =============================================================================

function SearchResult({ result, onSelect, isSelected, theme }) {
  const config = getTypeConfig(theme, result.type)
  const Icon = config.icon

  return (
    <ListItem
      onClick={() => onSelect(result)}
      data-testid={`search-result-${result.type}-${result.id}`}
      sx={{
        px: 2,
        py: 1.5,
        cursor: 'pointer',
        bgcolor: isSelected ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
        transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
        '&:hover': {
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        },
      }}
    >
      <ListItemIcon sx={{ minWidth: 36 }}>
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '8px',
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon sx={{ fontSize: 14, color: 'text.secondary' }} />
        </Box>
      </ListItemIcon>
      <ListItemText
        primary={result.name}
        secondary={result.description}
        primaryTypographyProps={{
          fontSize: '14px',
          fontWeight: 500,
          color: theme.palette.text.primary,
        }}
        secondaryTypographyProps={{
          fontSize: '0.75rem',
          color: theme.palette.text.secondary,
        }}
      />
      <Chip
        label={config.label}
        size="small"
        sx={{
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
          color: 'text.secondary',
          fontSize: '0.625rem',
          height: 20,
          borderRadius: 1.5,
        }}
      />
    </ListItem>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function GlobalSearch({
  variant = 'compact',
  enableShortcut = true,
  showShortcutHint = true,
  placeholder,
}) {
  const theme = useTheme()
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
  const inputPlaceholder = placeholder || (enableShortcut ? 'Search... (Ctrl+K)' : 'Search...')

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

  const isCompact = variant === 'compact'

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box ref={anchorRef} sx={{ position: 'relative', width: isCompact ? 240 : 320 }}>
        <TextField
          inputRef={inputRef}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={inputPlaceholder}
          size="small"
          fullWidth
          data-testid="global-search-input"
          inputProps={{ 'aria-label': 'Search' }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                {loading ? (
                  <CircularProgress size={16} sx={{ color: theme.palette.text.secondary }} />
                ) : (
                  <SearchIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                )}
              </InputAdornment>
            ),
            endAdornment: isCompact && showShortcutHint && enableShortcut && (
              <InputAdornment position="end">
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.25,
                    px: 0.5,
                    py: 0.25,
                    bgcolor: alpha(theme.palette.text.primary, 0.08),
                    borderRadius: 1,  // Figma spec: 8px
                  }}
                >
                  <KeyboardIcon sx={{ fontSize: 12, color: theme.palette.text.disabled }} />
                  <Typography sx={{ fontSize: '0.625rem', color: theme.palette.text.disabled }}>K</Typography>
                </Box>
              </InputAdornment>
            ),
            sx: {
              bgcolor: alpha(theme.palette.background.paper, 0.5),
              borderRadius: 1,  // Figma spec: 8px
              transition: 'all 0.2s ease',
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.15),
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.3),
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              },
              '& input': {
                fontSize: '14px',
                color: theme.palette.text.primary,
                '&::placeholder': {
                  color: theme.palette.text.secondary,
                  opacity: 1,
                },
              },
            },
          }}
        />

        <Popper
          open={open}
          anchorEl={anchorRef.current}
          placement="bottom-start"
          style={{ width: anchorRef.current?.offsetWidth || 300, zIndex: 1300 }}
        >
          <Paper
            sx={{
              mt: 0.5,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.92) : 'rgba(255, 255, 255, 0.92)',
              backdropFilter: 'blur(12px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              borderRadius: 1,  // Figma spec: 8px
              boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`,
              maxHeight: 400,
              overflow: 'auto',
              animation: `${fadeInUp} 0.2s ease-out`,
            }}
          >
            {results.length === 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography sx={{ color: theme.palette.text.secondary, fontSize: '14px' }}>
                  No results found
                </Typography>
              </Box>
            ) : (
              <List disablePadding>
                {results.map((result, index) => (
                  <SearchResult
                    key={`${result.type}-${result.id}`}
                    result={result}
                    onSelect={handleSelect}
                    isSelected={index === selectedIndex}
                    theme={theme}
                  />
                ))}
              </List>
            )}
          </Paper>
        </Popper>
      </Box>
    </ClickAwayListener>
  )
}
