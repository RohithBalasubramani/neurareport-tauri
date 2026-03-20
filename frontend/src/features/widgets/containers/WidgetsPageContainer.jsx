/**
 * WidgetsPageContainer — Dynamic Widget Intelligence dashboard.
 *
 * Renders Claude-recommended widgets in a proper 12-column CSS grid layout,
 * each widget at full size using the backend's grid packing coordinates.
 */
import {
  Box,
  Typography,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Storage as DbIcon,
} from '@mui/icons-material'
import PageHeader from '@/components/layout/PageHeader'
import { useWidgetRecommendations } from '../hooks/useWidgetRecommendations'
import { NoConnectionState, LoadingState, ErrorState } from '../components/WidgetEmptyStates'
import WidgetDashboardGrid from '../components/WidgetDashboardGrid'

export default function WidgetsPageContainer() {
  const state = useWidgetRecommendations()

  // ── No connection state ──────────────────────────────────────────────
  if (!state.connectionId) {
    return <NoConnectionState />
  }

  // ── Loading state ────────────────────────────────────────────────────
  if (state.loading && state.widgets.length === 0) {
    return <LoadingState connectionName={state.connectionName} />
  }

  // ── Error state ──────────────────────────────────────────────────────
  if (state.error && state.widgets.length === 0) {
    return (
      <ErrorState
        connectionName={state.connectionName}
        error={state.error}
        onRetry={state.loadRecommendations}
      />
    )
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader
        title="Widget Intelligence"
        description={`${state.widgets.length} widgets recommended for ${state.connectionName}`}
      />

      {/* Profile chips */}
      {state.profileChips.length > 0 && (
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip icon={<DbIcon />} label={state.connectionName} size="small" color="primary" variant="outlined" />
          {state.profileChips.map((label) => (
            <Chip key={label} label={label} size="small" variant="outlined" />
          ))}
        </Box>
      )}

      {/* Query bar */}
      <Box
        component="form"
        onSubmit={state.handleQuerySubmit}
        sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}
      >
        <TextField
          size="small"
          placeholder="Describe what you want to see... (e.g. 'show trends and alerts')"
          value={state.query}
          onChange={(e) => state.setQuery(e.target.value)}
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
          <IconButton onClick={state.loadRecommendations} disabled={state.loading} size="small">
            <RefreshIcon sx={{ animation: state.loading ? 'spin 1s linear infinite' : 'none' }} />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Dashboard Grid */}
      <WidgetDashboardGrid
        widgets={state.widgets}
        cellMap={state.cellMap}
        connectionId={state.connectionId}
        loading={state.loading}
        grid={state.grid}
      />
    </Box>
  )
}
