/**
 * Widget Palette Component
 * Draggable widget options with variant sub-menus for AI widgets.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Collapse,
  IconButton,
  Tooltip,
  Popover,
  List,
  ListItemButton,
  ListItemText,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  BarChart as BarChartIcon,
  ShowChart as LineChartIcon,
  PieChart as PieChartIcon,
  DonutLarge as DonutIcon,
  StackedBarChart as StackedIcon,
  AreaChart as AreaIcon,
  ScatterPlot as ScatterIcon,
  TrendingUp as MetricIcon,
  TableChart as TableIcon,
  TextFields as TextIcon,
  FilterList as FilterIcon,
  Image as ImageIcon,
  Numbers as NumberIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  UnfoldMore as VariantIcon,
  // AI Widget icons
  Speed as KpiIcon,
  CompareArrows as CompareIcon,
  Equalizer as DistributionIcon,
  Layers as CompositionIcon,
  Warning as AlertsIcon,
  Timeline as TimelineIcon,
  ViewList as EventLogIcon,
  Notes as NarrativeIcon,
  AccountTree as SankeyIcon,
  GridView as HeatmapIcon,
  Build as DiagnosticIcon,
  HelpOutline as UncertaintyIcon,
  People as PeopleIcon,
  Hexagon as HexIcon,
  Hub as NetworkIcon,
  Devices as DeviceIcon,
  Public as GlobeIcon,
  Chat as ChatIcon,
  SmartToy as AgentIcon,
  Lock as VaultIcon,
} from '@mui/icons-material'
import { SCENARIO_VARIANTS, VARIANT_CONFIG, DEFAULT_VARIANTS } from '../constants/widgetVariants'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PaletteContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
}))

const CategoryHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  cursor: 'pointer',
  padding: theme.spacing(0.5, 0),
  '&:hover': {
    opacity: 0.8,
  },
}))

const WidgetCard = styled(Card)(({ theme }) => ({
  cursor: 'grab',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  position: 'relative',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 4px 12px ${theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : alpha(theme.palette.text.primary, 0.08)}`,
    borderColor: theme.palette.divider,
  },
  '&:active': {
    cursor: 'grabbing',
    transform: 'scale(0.98)',
  },
}))

const WidgetGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: theme.spacing(1),
}))

const VariantBadge = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 2,
  right: 2,
  width: 14,
  height: 14,
  borderRadius: '50%',
  backgroundColor: alpha(theme.palette.primary.main, 0.15),
  color: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '10px',
  fontWeight: 600,
}))

// =============================================================================
// WIDGET DEFINITIONS
// =============================================================================

const WIDGET_CATEGORIES = [
  {
    id: 'charts',
    label: 'Charts',
    widgets: [
      { type: 'chart:bar', label: 'Bar', icon: BarChartIcon, color: 'primary' },
      { type: 'chart:line', label: 'Line', icon: LineChartIcon, color: 'primary' },
      { type: 'chart:area', label: 'Area', icon: AreaIcon, color: 'primary' },
      { type: 'chart:pie', label: 'Pie', icon: PieChartIcon, color: 'primary' },
      { type: 'chart:donut', label: 'Donut', icon: DonutIcon, color: 'primary' },
      { type: 'chart:stacked', label: 'Stacked', icon: StackedIcon, color: 'primary' },
      { type: 'chart:scatter', label: 'Scatter', icon: ScatterIcon, color: 'primary' },
    ],
  },
  {
    id: 'metrics',
    label: 'Metrics',
    widgets: [
      { type: 'metric', label: 'KPI', icon: MetricIcon, color: 'success' },
      { type: 'metric:number', label: 'Number', icon: NumberIcon, color: 'success' },
      { type: 'metric:progress', label: 'Progress', icon: DonutIcon, color: 'success' },
    ],
  },
  {
    id: 'data',
    label: 'Data',
    widgets: [
      { type: 'table', label: 'Table', icon: TableIcon, color: 'info' },
      { type: 'filter', label: 'Filter', icon: FilterIcon, color: 'warning' },
    ],
  },
  {
    id: 'content',
    label: 'Content',
    widgets: [
      { type: 'text', label: 'Text', icon: TextIcon, color: 'secondary' },
      { type: 'image', label: 'Image', icon: ImageIcon, color: 'secondary' },
    ],
  },
  // ── AI Widget Scenarios ──────────────────────────────────────────────────
  {
    id: 'intelligent',
    label: 'AI Widgets',
    defaultCollapsed: true,
    widgets: [
      { type: 'kpi', label: 'KPI', icon: KpiIcon, color: 'success', hasVariants: true },
      { type: 'trend', label: 'Trend', icon: LineChartIcon, color: 'primary', hasVariants: true },
      { type: 'trend-multi-line', label: 'Multi-Line', icon: LineChartIcon, color: 'primary' },
      { type: 'trends-cumulative', label: 'Cumulative', icon: AreaIcon, color: 'primary' },
      { type: 'comparison', label: 'Compare', icon: CompareIcon, color: 'primary', hasVariants: true },
      { type: 'distribution', label: 'Distribution', icon: DistributionIcon, color: 'primary', hasVariants: true },
      { type: 'composition', label: 'Composition', icon: CompositionIcon, color: 'primary', hasVariants: true },
      { type: 'category-bar', label: 'Category Bar', icon: BarChartIcon, color: 'primary', hasVariants: true },
    ],
  },
  {
    id: 'context',
    label: 'Context & Events',
    defaultCollapsed: true,
    widgets: [
      { type: 'alerts', label: 'Alerts', icon: AlertsIcon, color: 'error', hasVariants: true },
      { type: 'timeline', label: 'Timeline', icon: TimelineIcon, color: 'info', hasVariants: true },
      { type: 'eventlogstream', label: 'Event Log', icon: EventLogIcon, color: 'info', hasVariants: true },
      { type: 'narrative', label: 'Narrative', icon: NarrativeIcon, color: 'secondary' },
    ],
  },
  {
    id: 'advanced',
    label: 'Advanced Viz',
    defaultCollapsed: true,
    widgets: [
      { type: 'flow-sankey', label: 'Flow Diagram', icon: SankeyIcon, color: 'warning', hasVariants: true },
      { type: 'matrix-heatmap', label: 'Heatmap', icon: HeatmapIcon, color: 'warning', hasVariants: true },
      { type: 'diagnosticpanel', label: 'Diagnostics', icon: DiagnosticIcon, color: 'warning' },
      { type: 'uncertaintypanel', label: 'Uncertainty', icon: UncertaintyIcon, color: 'warning' },
    ],
  },
  {
    id: 'domain',
    label: 'Domain-Specific',
    defaultCollapsed: true,
    widgets: [
      { type: 'peopleview', label: 'People', icon: PeopleIcon, color: 'secondary' },
      { type: 'peoplehexgrid', label: 'Hex Grid', icon: HexIcon, color: 'secondary' },
      { type: 'peoplenetwork', label: 'Network', icon: NetworkIcon, color: 'secondary' },
      { type: 'edgedevicepanel', label: 'IoT Device', icon: DeviceIcon, color: 'secondary' },
      { type: 'supplychainglobe', label: 'Globe', icon: GlobeIcon, color: 'secondary' },
      { type: 'chatstream', label: 'Chat', icon: ChatIcon, color: 'secondary' },
      { type: 'agentsview', label: 'Agents', icon: AgentIcon, color: 'secondary' },
      { type: 'vaultview', label: 'Vault', icon: VaultIcon, color: 'secondary' },
    ],
  },
]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function WidgetPalette({ onAddWidget }) {
  const theme = useTheme()
  const [expandedCategories, setExpandedCategories] = useState(
    WIDGET_CATEGORIES.reduce((acc, cat) => ({ ...acc, [cat.id]: !cat.defaultCollapsed }), {})
  )
  const [variantAnchor, setVariantAnchor] = useState(null)
  const [variantWidget, setVariantWidget] = useState(null)

  const toggleCategory = useCallback((categoryId) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [categoryId]: !prev[categoryId],
    }))
  }, [])

  const handleDragStart = useCallback((e, widget, variant) => {
    e.dataTransfer.setData('widget-type', widget.type)
    e.dataTransfer.setData('widget-label', widget.label)
    if (variant) {
      e.dataTransfer.setData('widget-variant', variant)
    }
    e.dataTransfer.effectAllowed = 'copy'
  }, [])

  const handleWidgetClick = useCallback((widget, e) => {
    // If widget has multiple variants, show variant picker
    const variants = SCENARIO_VARIANTS[widget.type]
    if (widget.hasVariants && variants && variants.length > 1) {
      setVariantAnchor(e.currentTarget)
      setVariantWidget(widget)
      return
    }
    // Single variant or legacy — add directly
    const defaultVariant = DEFAULT_VARIANTS[widget.type]
    onAddWidget?.(widget.type, widget.label, defaultVariant)
  }, [onAddWidget])

  const handleVariantSelect = useCallback((scenario, variant) => {
    const vConfig = VARIANT_CONFIG[variant]
    const label = vConfig?.label || variant
    onAddWidget?.(scenario, label, variant)
    setVariantAnchor(null)
    setVariantWidget(null)
  }, [onAddWidget])

  const handleCloseVariantPicker = useCallback(() => {
    setVariantAnchor(null)
    setVariantWidget(null)
  }, [])

  return (
    <PaletteContainer>
      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
        Add Widget
      </Typography>

      {WIDGET_CATEGORIES.map((category) => (
        <Box key={category.id}>
          <CategoryHeader onClick={() => toggleCategory(category.id)}>
            <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
              {category.label}
            </Typography>
            <IconButton size="small">
              {expandedCategories[category.id] ? (
                <CollapseIcon fontSize="small" />
              ) : (
                <ExpandIcon fontSize="small" />
              )}
            </IconButton>
          </CategoryHeader>

          <Collapse in={expandedCategories[category.id]}>
            <WidgetGrid>
              {category.widgets.map((widget) => {
                const variantCount = SCENARIO_VARIANTS[widget.type]?.length || 0
                return (
                  <WidgetCard
                    key={widget.type}
                    variant="outlined"
                    draggable
                    onDragStart={(e) => handleDragStart(e, widget)}
                    onClick={(e) => handleWidgetClick(widget, e)}
                  >
                    <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: 0.5,
                        }}
                      >
                        <widget.icon
                          sx={{
                            fontSize: 20,
                            color: 'text.secondary',
                          }}
                        />
                        <Typography
                          variant="caption"
                          sx={{ fontSize: '12px', textAlign: 'center' }}
                        >
                          {widget.label}
                        </Typography>
                      </Box>
                    </CardContent>
                    {widget.hasVariants && variantCount > 1 && (
                      <VariantBadge>{variantCount}</VariantBadge>
                    )}
                  </WidgetCard>
                )
              })}
            </WidgetGrid>
          </Collapse>
        </Box>
      ))}

      {/* Variant Picker Popover */}
      <Popover
        open={Boolean(variantAnchor)}
        anchorEl={variantAnchor}
        onClose={handleCloseVariantPicker}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
        slotProps={{
          paper: {
            sx: { maxHeight: 300, minWidth: 200, maxWidth: 260 },
          },
        }}
      >
        {variantWidget && (
          <Box sx={{ py: 0.5 }}>
            <Typography
              variant="caption"
              sx={{ fontWeight: 600, px: 2, py: 0.5, color: 'text.secondary', display: 'block' }}
            >
              {variantWidget.label} Variants
            </Typography>
            <List dense disablePadding>
              {(SCENARIO_VARIANTS[variantWidget.type] || []).map((v) => {
                const vConfig = VARIANT_CONFIG[v]
                return (
                  <ListItemButton
                    key={v}
                    onClick={() => handleVariantSelect(variantWidget.type, v)}
                    sx={{ py: 0.5, px: 2 }}
                  >
                    <ListItemText
                      primary={vConfig?.label || v}
                      secondary={vConfig?.description || ''}
                      primaryTypographyProps={{ variant: 'body2', fontSize: '14px' }}
                      secondaryTypographyProps={{ variant: 'caption', fontSize: '12px', noWrap: true }}
                    />
                  </ListItemButton>
                )
              })}
            </List>
          </Box>
        )}
      </Popover>
    </PaletteContainer>
  )
}

/**
 * Parse widget type to get category and subtype
 */
export function parseWidgetType(type) {
  const [category, subtype] = type.split(':')
  return { category, subtype: subtype || category }
}

/**
 * Get widget definition by type
 */
export function getWidgetDefinition(type) {
  for (const category of WIDGET_CATEGORIES) {
    const widget = category.widgets.find((w) => w.type === type)
    if (widget) return widget
  }
  return null
}

/**
 * All available widget types
 */
export const ALL_WIDGET_TYPES = WIDGET_CATEGORIES.flatMap((c) => c.widgets)
