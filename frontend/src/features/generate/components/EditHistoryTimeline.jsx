import { useState, useMemo } from 'react'
import {
  Box,
  Stack,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material'
import HistoryIcon from '@mui/icons-material/History'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import FilterListIcon from '@mui/icons-material/FilterList'
import { EDIT_TYPE_CONFIG, MAX_HISTORY_ENTRIES } from './editHistoryConfig'
import HistoryEntry from './HistoryEntry'

export default function EditHistoryTimeline({ history = [], maxVisible = 5 }) {
  const [expanded, setExpanded] = useState(false)
  const [filter, setFilter] = useState('all')

  const filteredHistory = useMemo(() => {
    if (!Array.isArray(history)) return []
    const capped = history.length > MAX_HISTORY_ENTRIES
      ? history.slice(-MAX_HISTORY_ENTRIES)
      : history
    let filtered = [...capped].reverse()
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
