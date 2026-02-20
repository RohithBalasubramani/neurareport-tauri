/**
 * AI Widget Suggestion Panel
 *
 * Allows users to describe what they want to see in natural language,
 * then uses the widget intelligence API to suggest optimal widgets.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  CircularProgress,
  Divider,
  alpha,
  styled,
} from '@mui/material'
import {
  AutoAwesome as AIIcon,
  Speed as KpiIcon,
  ShowChart as TrendIcon,
  CompareArrows as CompareIcon,
  PieChart as DistributionIcon,
  Warning as AlertsIcon,
  Timeline as TimelineIcon,
  Notes as NarrativeIcon,
  ViewList as EventLogIcon,
  BarChart as BarIcon,
  Layers as CompositionIcon,
  AccountTree as SankeyIcon,
  GridView as HeatmapIcon,
  Build as DiagnosticIcon,
  HelpOutline as UncertaintyIcon,
  People as PeopleIcon,
  Devices as DeviceIcon,
  Public as GlobeIcon,
  Chat as ChatIcon,
  SmartToy as AgentIcon,
  Lock as VaultIcon,
  Hexagon as HexIcon,
  Hub as NetworkIcon,
  AreaChart as CumulativeIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { selectWidgets, packGrid } from '../../../api/widgets'

// ── Scenario → Icon mapping ────────────────────────────────────────────────

const SCENARIO_ICONS = {
  kpi: KpiIcon,
  trend: TrendIcon,
  'trend-multi-line': TrendIcon,
  'trends-cumulative': CumulativeIcon,
  comparison: CompareIcon,
  distribution: DistributionIcon,
  composition: CompositionIcon,
  'category-bar': BarIcon,
  alerts: AlertsIcon,
  timeline: TimelineIcon,
  eventlogstream: EventLogIcon,
  narrative: NarrativeIcon,
  'flow-sankey': SankeyIcon,
  'matrix-heatmap': HeatmapIcon,
  diagnosticpanel: DiagnosticIcon,
  uncertaintypanel: UncertaintyIcon,
  peopleview: PeopleIcon,
  peoplehexgrid: HexIcon,
  peoplenetwork: NetworkIcon,
  edgedevicepanel: DeviceIcon,
  supplychainglobe: GlobeIcon,
  chatstream: ChatIcon,
  agentsview: AgentIcon,
  vaultview: VaultIcon,
}

// ── Styled Components ──────────────────────────────────────────────────────

const SuggestionContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1.5),
}))

const SuggestionItem = styled(ListItem)(({ theme }) => ({
  borderRadius: 8,
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(0.5),
  cursor: 'pointer',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha(theme.palette.primary.main, 0.12)
        : alpha(theme.palette.primary.main, 0.06),
    borderColor: theme.palette.primary.main,
  },
}))

// ── Main Component ─────────────────────────────────────────────────────────

export default function AIWidgetSuggestion({ onAddWidgets, onAddSingleWidget }) {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [error, setError] = useState(null)

  const handleSuggest = useCallback(async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await selectWidgets({ query: query.trim(), maxWidgets: 8 })
      setSuggestions(result.widgets || [])
    } catch (err) {
      setError(err.message || 'Failed to get suggestions')
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }, [query])

  const handleApplyAll = useCallback(async () => {
    if (!suggestions.length) return
    setLoading(true)
    try {
      const layout = await packGrid(suggestions)
      onAddWidgets?.(suggestions, layout)
      setSuggestions([])
      setQuery('')
    } catch (err) {
      setError(err.message || 'Failed to pack grid')
    } finally {
      setLoading(false)
    }
  }, [suggestions, onAddWidgets])

  const handleAddSingle = useCallback(
    (widget) => {
      onAddSingleWidget?.(widget.scenario, widget.variant || widget.scenario)
    },
    [onAddSingleWidget]
  )

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSuggest()
      }
    },
    [handleSuggest]
  )

  return (
    <SuggestionContainer>
      <Divider sx={{ my: 0.5 }} />

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AIIcon sx={{ fontSize: 18, color: 'primary.main' }} />
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          AI Suggest
        </Typography>
      </Box>

      <TextField
        size="small"
        placeholder="Describe your dashboard..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        multiline
        maxRows={3}
        fullWidth
        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
      />

      <Button
        variant="contained"
        size="small"
        onClick={handleSuggest}
        disabled={loading || !query.trim()}
        startIcon={loading ? <CircularProgress size={16} /> : <AIIcon />}
        sx={{ borderRadius: 2, textTransform: 'none' }}
      >
        {loading ? 'Thinking...' : 'Suggest Widgets'}
      </Button>

      {error && (
        <Typography variant="caption" color="error">
          {error}
        </Typography>
      )}

      {suggestions.length > 0 && (
        <>
          <Typography variant="caption" color="text.secondary">
            {suggestions.length} widget{suggestions.length !== 1 ? 's' : ''} suggested
          </Typography>

          <List dense disablePadding>
            {suggestions.map((widget, i) => {
              const IconComp = SCENARIO_ICONS[widget.scenario] || TrendIcon
              return (
                <SuggestionItem
                  key={widget.id || i}
                  disableGutters
                  sx={{ px: 1.5, py: 0.75 }}
                  onClick={() => handleAddSingle(widget)}
                >
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <IconComp sx={{ fontSize: 18, color: 'primary.main' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={widget.scenario}
                    secondary={widget.variant}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                  <Chip
                    label={`${Math.round((widget.relevance || 0) * 100)}%`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '12px' }}
                  />
                </SuggestionItem>
              )
            })}
          </List>

          <Button
            variant="outlined"
            size="small"
            onClick={handleApplyAll}
            disabled={loading}
            startIcon={<AddIcon />}
            sx={{ borderRadius: 2, textTransform: 'none' }}
          >
            Add All to Dashboard
          </Button>
        </>
      )}
    </SuggestionContainer>
  )
}
