/**
 * WidgetsPageContainer — Dynamic Widget Intelligence dashboard.
 *
 * Renders Claude-recommended widgets in a proper 12-column CSS grid layout,
 * each widget at full size using the backend's grid packing coordinates.
 */
import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Box,
  Typography,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
  IconButton,
  Tooltip,
  alpha,
  styled,
} from '@mui/material'
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Storage as DbIcon,
  LinkOff as NoConnectionIcon,
  Cable as ConnectionsIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { Button } from '@mui/material'
import PageHeader from '@/components/layout/PageHeader'
import WidgetRenderer from '@/features/dashboards/components/WidgetRenderer'
import { recommendWidgets } from '@/api/widgets'
import { useAppStore } from '@/stores'
import { VARIANT_CONFIG } from '@/features/dashboards/constants/widgetVariants'

// ── Constants ────────────────────────────────────────────────────────────

const ROW_HEIGHT = 80 // px per grid row unit

// ── Styled ───────────────────────────────────────────────────────────────

const DashboardGrid = styled(Box)({
  display: 'grid',
  gridTemplateColumns: 'repeat(12, 1fr)',
  gridAutoRows: ROW_HEIGHT,
  gap: 12,
  width: '100%',
})

const WidgetCell = styled(Box)(({ theme }) => ({
  position: 'relative',
  borderRadius: 10,
  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 24px ${alpha(theme.palette.common.black, 0.08)}`,
    borderColor: alpha(theme.palette.primary.main, 0.3),
  },
}))

const WidgetOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: 0,
  left: 0,
  right: 0,
  padding: theme.spacing(0.75, 1.5),
  background: `linear-gradient(transparent, ${alpha(theme.palette.background.paper, 0.92)})`,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  opacity: 0,
  transition: 'opacity 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '.MuiBox-root:hover > &': {
    opacity: 1,
  },
}))

// ── Component ────────────────────────────────────────────────────────────

export default function WidgetsPageContainer() {
  const navigate = useNavigate()
  const [widgets, setWidgets] = useState([])
  const [grid, setGrid] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('overview')

  const connectionId = useAppStore((s) => s.activeConnectionId)
  const activeConnection = useAppStore((s) => s.activeConnection)
  const connectionName = activeConnection?.name || connectionId || ''

  const loadRecommendations = useCallback(() => {
    if (!connectionId) return
    setLoading(true)
    setError(null)
    recommendWidgets({ connectionId, query, maxWidgets: 12 })
      .then((res) => {
        setWidgets(res.widgets || [])
        setGrid(res.grid || null)
        setProfile(res.profile || null)
      })
      .catch((err) => {
        console.error('[WidgetsPage] Recommendation failed:', err)
        setError(err.userMessage || err.message || 'Failed to get widget recommendations')
      })
      .finally(() => {
        setLoading(false)
      })
  }, [connectionId, query])

  useEffect(() => {
    loadRecommendations()
  }, [loadRecommendations])

  const handleQuerySubmit = useCallback(
    (e) => {
      e.preventDefault()
      loadRecommendations()
    },
    [loadRecommendations],
  )

  // Build a lookup: widget_id → grid cell placement
  const cellMap = useMemo(() => {
    const map = {}
    if (grid?.cells) {
      for (const c of grid.cells) {
        map[c.widget_id] = c
      }
    }
    return map
  }, [grid])

  // ── No connection state ──────────────────────────────────────────────

  if (!connectionId) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <PageHeader
          title="Widget Intelligence"
          description="Dynamic data-driven widget recommendations"
        />
        <Box
          sx={{
            py: 10,
            textAlign: 'center',
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
            borderStyle: 'dashed',
          }}
        >
          <NoConnectionIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No database connected
          </Typography>
          <Typography variant="body2" color="text.disabled" sx={{ mb: 2 }}>
            Connect a database from the Connections page to see intelligent widget
            recommendations tailored to your data.
          </Typography>
          <Button
            variant="contained"
            startIcon={<ConnectionsIcon />}
            onClick={() => navigate('/connections')}
            sx={{ textTransform: 'none' }}
          >
            Go to Connections
          </Button>
        </Box>
      </Box>
    )
  }

  // ── Loading state ────────────────────────────────────────────────────

  if (loading && widgets.length === 0) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <PageHeader title="Widget Intelligence" description={`Analyzing ${connectionName}...`} />
        <Box
          sx={{ py: 8, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}
        >
          <CircularProgress />
          <Typography variant="body2" color="text.secondary">
            Analyzing database schema and recommending widgets...
          </Typography>
        </Box>
      </Box>
    )
  }

  // ── Error state ──────────────────────────────────────────────────────

  if (error && widgets.length === 0) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <PageHeader title="Widget Intelligence" description={connectionName} />
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography variant="h6" color="error" gutterBottom>
            Recommendation failed
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {error}
          </Typography>
          <Chip label="Retry" onClick={loadRecommendations} color="primary" clickable />
        </Box>
      </Box>
    )
  }

  // ── Profile chips ────────────────────────────────────────────────────

  const profileChips = profile
    ? [
        `${profile.table_count} tables`,
        `${profile.numeric_columns} numeric cols`,
        profile.has_timeseries ? 'timeseries' : 'no timeseries',
      ]
    : []

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader
        title="Widget Intelligence"
        description={`${widgets.length} widgets recommended for ${connectionName}`}
      />

      {/* Profile chips */}
      {profileChips.length > 0 && (
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip icon={<DbIcon />} label={connectionName} size="small" color="primary" variant="outlined" />
          {profileChips.map((label) => (
            <Chip key={label} label={label} size="small" variant="outlined" />
          ))}
        </Box>
      )}

      {/* Query bar */}
      <Box
        component="form"
        onSubmit={handleQuerySubmit}
        sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}
      >
        <TextField
          size="small"
          placeholder="Describe what you want to see... (e.g. 'show trends and alerts')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ fontSize: 18 }} />
                </InputAdornment>
              ),
            },
          }}
          sx={{ flex: 1, minWidth: 240 }}
        />
        <Tooltip title="Refresh recommendations">
          <IconButton onClick={loadRecommendations} disabled={loading} size="small">
            <RefreshIcon sx={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Dashboard Grid — full-size widgets positioned by backend grid packer */}
      <DashboardGrid>
        {widgets.map((widget) => {
          const { id, scenario, variant, question, relevance, size } = widget
          const cell = cellMap[id]
          const vConfig = VARIANT_CONFIG[variant]
          const label = vConfig?.label || variant || scenario

          // Use backend grid packing if available, else auto-size by widget size
          const sizeSpans = { compact: 3, normal: 4, expanded: 6, hero: 12 }
          const rowSpans = { compact: 3, normal: 4, expanded: 4, hero: 5 }
          const colSpan = cell
            ? `${cell.col_start} / ${cell.col_end}`
            : `span ${sizeSpans[size] || 4}`
          const rowSpan = cell
            ? `${cell.row_start} / ${cell.row_end}`
            : `span ${rowSpans[size] || 4}`

          return (
            <WidgetCell
              key={id}
              sx={{
                gridColumn: colSpan,
                gridRow: rowSpan,
              }}
            >
              <Box sx={{ height: '100%', width: '100%' }}>
                <WidgetRenderer
                  scenario={scenario}
                  variant={variant}
                  connectionId={connectionId}
                  showSourceBadge
                />
              </Box>
              <WidgetOverlay>
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 600, flex: 1 }}
                  noWrap
                >
                  {question || label}
                </Typography>
                <Chip
                  label={`${Math.round(relevance * 100)}%`}
                  size="small"
                  color={relevance > 0.8 ? 'success' : 'default'}
                  variant="outlined"
                  sx={{ height: 18, fontSize: '10px' }}
                />
              </WidgetOverlay>
            </WidgetCell>
          )
        })}
      </DashboardGrid>

      {widgets.length === 0 && !loading && (
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No widgets recommended for this database.
          </Typography>
          <Typography variant="caption" color="text.disabled">
            Try a different query or check your database connection.
          </Typography>
        </Box>
      )}

      {/* Grid utilization */}
      {grid && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Typography variant="caption" color="text.disabled">
            {grid.total_cols}&times;{grid.total_rows} grid &middot; {grid.utilization_pct}%
            utilization
          </Typography>
        </Box>
      )}
    </Box>
  )
}
