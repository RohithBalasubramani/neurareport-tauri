/**
 * Widget category definitions and utility functions for the Widget Palette.
 */
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

export const WIDGET_CATEGORIES = [
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
