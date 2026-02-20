import { useState, useMemo } from 'react'
import {
  Box,
  Stack,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Collapse,
  ToggleButtonGroup,
  ToggleButton,
  alpha,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import HistoryIcon from '@mui/icons-material/History'
import EditIcon from '@mui/icons-material/Edit'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import UndoIcon from '@mui/icons-material/Undo'
import ChatIcon from '@mui/icons-material/Chat'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import FilterListIcon from '@mui/icons-material/FilterList'
import AccessTimeIcon from '@mui/icons-material/AccessTime'

const EDIT_TYPE_CONFIG = {
  manual: {
    icon: EditIcon,
    label: 'Manual',
    color: 'default',
  },
  ai: {
    icon: SmartToyIcon,
    label: 'AI',
    color: 'default',
  },
  chat: {
    icon: ChatIcon,
    label: 'Chat AI',
    color: 'default',
  },
  undo: {
    icon: UndoIcon,
    label: 'Undo',
    color: 'default',
  },
  default: {
    icon: HistoryIcon,
    label: 'Edit',
    color: 'default',
  },
}

function formatRelativeTime(timestamp) {
  if (!timestamp) return 'Unknown time'

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function HistoryEntry({ entry, isLatest }) {
  const config = EDIT_TYPE_CONFIG[entry.type] || EDIT_TYPE_CONFIG.default
  const Icon = config.icon

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        py: 1,
        px: 1.5,
        borderRadius: 1,
        bgcolor: isLatest ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
        '&:hover': {
          bgcolor: 'action.hover',
        },
      }}
    >
      {/* Timeline indicator */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          pt: 0.5,
        }}
      >
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon
            sx={{
              fontSize: 16,
              color: 'text.secondary',
            }}
          />
        </Box>
        <Box
          sx={{
            width: 2,
            flex: 1,
            mt: 0.5,
            bgcolor: 'divider',
            minHeight: 8,
          }}
        />
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.25 }}>
          <Chip
            label={config.label}
            size="small"
            variant="outlined"
            sx={{
              height: 20,
              fontSize: '12px',
              borderColor: (theme) => alpha(theme.palette.divider, 0.3),
              color: 'text.secondary',
            }}
          />
          {isLatest && (
            <Chip
              label="Latest"
              size="small"
              sx={{
                height: 20,
                fontSize: '12px',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                color: 'common.white',
              }}
            />
          )}
        </Stack>

        {entry.notes && (
          <Typography
            variant="body2"
            color="text.primary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: '100%',
            }}
          >
            {entry.notes}
          </Typography>
        )}

        <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
          <AccessTimeIcon sx={{ fontSize: 12, color: 'text.disabled' }} />
          <Typography variant="caption" color="text.disabled">
            {formatRelativeTime(entry.timestamp)}
          </Typography>
        </Stack>
      </Box>
    </Box>
  )
}

const MAX_HISTORY_ENTRIES = 500

export default function EditHistoryTimeline({ history = [], maxVisible = 5 }) {
  const [expanded, setExpanded] = useState(false)
  const [filter, setFilter] = useState('all')

  const filteredHistory = useMemo(() => {
    if (!Array.isArray(history)) return []
    // Cap to prevent rendering unbounded entries
    const capped = history.length > MAX_HISTORY_ENTRIES
      ? history.slice(-MAX_HISTORY_ENTRIES)
      : history
    let filtered = [...capped].reverse() // Most recent first
    if (filter !== 'all') {
      filtered = filtered.filter((entry) => entry.type === filter)
    }
    return filtered
  }, [history, filter])

  const visibleHistory = expanded
    ? filteredHistory
    : filteredHistory.slice(0, maxVisible)

  const hasMore = filteredHistory.length > maxVisible

  const editTypes = useMemo(() => {
    const types = new Set(['all'])
    history.forEach((entry) => {
      if (entry.type) types.add(entry.type)
    })
    return Array.from(types)
  }, [history])

  if (!history || history.length === 0) {
    return (
      <Box sx={{ py: 2, px: 1.5, textAlign: 'center' }}>
        <HistoryIcon sx={{ fontSize: 32, color: 'text.disabled', mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          No edit history yet
        </Typography>
        <Typography variant="caption" color="text.disabled">
          Your changes will appear here
        </Typography>
      </Box>
    )
  }

  return (
    <Box>
      {/* Header with filter */}
      <Stack
        direction="row"
        justifyContent="space-between"
        alignItems="center"
        sx={{ mb: 1 }}
      >
        <Stack direction="row" spacing={0.5} alignItems="center">
          <HistoryIcon fontSize="small" color="action" />
          <Typography variant="subtitle2">
            History
          </Typography>
          <Chip
            label={filteredHistory.length}
            size="small"
            sx={{ height: 18, fontSize: '12px' }}
          />
        </Stack>

        {editTypes.length > 2 && (
          <ToggleButtonGroup
            size="small"
            value={filter}
            exclusive
            onChange={(e, v) => v && setFilter(v)}
            sx={{
              '& .MuiToggleButton-root': {
                py: 0.25,
                px: 0.75,
                fontSize: '12px',
              },
            }}
          >
            <ToggleButton value="all">
              <Tooltip title="All edits">
                <FilterListIcon sx={{ fontSize: 14 }} />
              </Tooltip>
            </ToggleButton>
            {editTypes.filter((t) => t !== 'all').map((type) => {
              const config = EDIT_TYPE_CONFIG[type] || EDIT_TYPE_CONFIG.default
              const TypeIcon = config.icon
              return (
                <ToggleButton key={type} value={type}>
                  <Tooltip title={config.label}>
                    <TypeIcon sx={{ fontSize: 14 }} />
                  </Tooltip>
                </ToggleButton>
              )
            })}
          </ToggleButtonGroup>
        )}
      </Stack>

      {/* Timeline */}
      <Box
        sx={{
          borderRadius: 1.5,
          border: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
          overflow: 'hidden',
        }}
      >
        {visibleHistory.map((entry, idx) => (
          <HistoryEntry
            key={`${entry.timestamp}-${idx}`}
            entry={entry}
            isLatest={idx === 0}
          />
        ))}

        {/* Show more / less */}
        {hasMore && (
          <Box
            sx={{
              borderTop: '1px solid',
              borderColor: 'divider',
              py: 0.75,
              textAlign: 'center',
            }}
          >
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
              sx={{ fontSize: '12px' }}
            >
              {expanded ? (
                <>
                  <ExpandLessIcon fontSize="small" />
                  <Typography variant="caption" sx={{ ml: 0.5 }}>
                    Show less
                  </Typography>
                </>
              ) : (
                <>
                  <ExpandMoreIcon fontSize="small" />
                  <Typography variant="caption" sx={{ ml: 0.5 }}>
                    Show {filteredHistory.length - maxVisible} more
                  </Typography>
                </>
              )}
            </IconButton>
          </Box>
        )}
      </Box>
    </Box>
  )
}
