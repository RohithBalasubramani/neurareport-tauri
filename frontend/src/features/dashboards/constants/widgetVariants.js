/**
 * Complete widget variant metadata for all 24 scenarios and 71 variants.
 *
 * Maps every variant to its rendering configuration:
 * - chartType: ECharts chart type to use
 * - renderAs: which renderer component to use (chart, metric, text, list, domain)
 * - label: human-readable display name
 * - description: what this variant is good for
 * - defaultSize: { w, h } grid dimensions
 */

import { status, secondary } from '@/app/theme'

// ── Variant → Rendering Config ─────────────────────────────────────────────

export const VARIANT_CONFIG = {
  // ── KPI (5 variants) ──────────────────────────────────────────────────
  'kpi-live': {
    renderAs: 'metric',
    label: 'Live KPI',
    description: 'Real-time single metric with trend',
    defaultSize: { w: 3, h: 2 },
    metricFormat: 'number',
  },
  'kpi-alert': {
    renderAs: 'metric',
    label: 'Alert KPI',
    description: 'KPI with threshold alert indicator',
    defaultSize: { w: 3, h: 2 },
    metricFormat: 'number',
    showThreshold: true,
  },
  'kpi-accumulated': {
    renderAs: 'metric',
    label: 'Accumulated KPI',
    description: 'Cumulative total metric (kWh, counts)',
    defaultSize: { w: 3, h: 2 },
    metricFormat: 'compact',
  },
  'kpi-lifecycle': {
    renderAs: 'metric',
    label: 'Lifecycle KPI',
    description: 'Equipment age / remaining life',
    defaultSize: { w: 3, h: 2 },
    metricFormat: 'percent',
  },
  'kpi-status': {
    renderAs: 'metric',
    label: 'Status KPI',
    description: 'Binary on/off or status indicator',
    defaultSize: { w: 2, h: 2 },
    metricFormat: 'number',
    showStatus: true,
  },

  // ── Trend (6 variants) ────────────────────────────────────────────────
  'trend-line': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'Line Trend',
    description: 'Standard time-series line chart',
    defaultSize: { w: 6, h: 3 },
  },
  'trend-area': {
    renderAs: 'chart',
    chartType: 'area',
    label: 'Area Trend',
    description: 'Filled area time-series chart',
    defaultSize: { w: 6, h: 3 },
  },
  'trend-step-line': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'Step Line',
    description: 'Stepped line for discrete state changes',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { step: 'end' },
  },
  'trend-rgb-phase': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'RGB Phase',
    description: 'Three-phase R/Y/B overlay',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { multiSeries: true, colors: [status.destructive, status.warning, secondary.cyan[500]] },
  },
  'trend-alert-context': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'Alert Context',
    description: 'Trend line with alert markers',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { showAnnotations: true },
  },
  'trend-heatmap': {
    renderAs: 'chart',
    chartType: 'scatter',
    label: 'Trend Heatmap',
    description: 'Dense time-series as color intensity',
    defaultSize: { w: 6, h: 4 },
  },

  // ── Trend Multi-Line (1 variant) ──────────────────────────────────────
  'trend-multi-line': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'Multi-Line Trend',
    description: 'Multiple metrics overlaid for comparison',
    defaultSize: { w: 8, h: 3 },
    chartOptions: { multiSeries: true },
  },

  // ── Trends Cumulative (1 variant) ─────────────────────────────────────
  'trends-cumulative': {
    renderAs: 'chart',
    chartType: 'area',
    label: 'Cumulative Trend',
    description: 'Running total over time',
    defaultSize: { w: 6, h: 3 },
  },

  // ── Comparison (6 variants) ───────────────────────────────────────────
  'comparison-side-by-side': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Side-by-Side',
    description: 'Two items side by side comparison',
    defaultSize: { w: 6, h: 3 },
  },
  'comparison-delta-bar': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Delta Bar',
    description: 'Show differences as positive/negative bars',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { diverging: true },
  },
  'comparison-grouped-bar': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Grouped Bar',
    description: 'Multiple metrics grouped by entity',
    defaultSize: { w: 8, h: 3 },
    chartOptions: { grouped: true },
  },
  'comparison-waterfall': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Waterfall',
    description: 'Cumulative gains and losses',
    defaultSize: { w: 6, h: 3 },
  },
  'comparison-small-multiples': {
    renderAs: 'chart',
    chartType: 'line',
    label: 'Small Multiples',
    description: 'Grid of small charts for comparison',
    defaultSize: { w: 8, h: 4 },
  },
  'comparison-composition-split': {
    renderAs: 'chart',
    chartType: 'stacked',
    label: 'Composition Split',
    description: 'Split view showing composition differences',
    defaultSize: { w: 8, h: 3 },
  },

  // ── Distribution (6 variants) ─────────────────────────────────────────
  'distribution-donut': {
    renderAs: 'chart',
    chartType: 'donut',
    label: 'Donut',
    description: 'Donut chart with center metric',
    defaultSize: { w: 4, h: 3 },
  },
  'distribution-100-stacked-bar': {
    renderAs: 'chart',
    chartType: 'stacked',
    label: '100% Stacked',
    description: 'Normalized stacked bar (percentages)',
    defaultSize: { w: 6, h: 3 },
  },
  'distribution-horizontal-bar': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Horizontal Bar',
    description: 'Ranked horizontal bars',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { horizontal: true },
  },
  'distribution-pie': {
    renderAs: 'chart',
    chartType: 'pie',
    label: 'Pie',
    description: 'Classic pie chart for simple splits',
    defaultSize: { w: 4, h: 3 },
  },
  'distribution-grouped-bar': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Grouped Dist.',
    description: 'Distribution as grouped bar chart',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { grouped: true },
  },
  'distribution-pareto-bar': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Pareto',
    description: 'Pareto chart with 80/20 line',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { pareto: true },
  },

  // ── Composition (5 variants) ──────────────────────────────────────────
  'composition-stacked-bar': {
    renderAs: 'chart',
    chartType: 'stacked',
    label: 'Stacked Bar',
    description: 'Stacked bar showing parts of whole',
    defaultSize: { w: 6, h: 3 },
  },
  'composition-stacked-area': {
    renderAs: 'chart',
    chartType: 'area',
    label: 'Stacked Area',
    description: 'Stacked area over time',
    defaultSize: { w: 8, h: 3 },
    chartOptions: { stacked: true },
  },
  'composition-donut': {
    renderAs: 'chart',
    chartType: 'donut',
    label: 'Composition Donut',
    description: 'Donut showing composition breakdown',
    defaultSize: { w: 4, h: 3 },
  },
  'composition-waterfall': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Composition Waterfall',
    description: 'How parts build up to the total',
    defaultSize: { w: 6, h: 3 },
  },
  'composition-treemap': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Treemap',
    description: 'Hierarchical area-based composition',
    defaultSize: { w: 6, h: 4 },
  },

  // ── Category Bar (5 variants) ─────────────────────────────────────────
  'category-bar-vertical': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Vertical Bar',
    description: 'Standard vertical category bars',
    defaultSize: { w: 6, h: 3 },
  },
  'category-bar-horizontal': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Horizontal Bar',
    description: 'Horizontal bars for long labels',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { horizontal: true },
  },
  'category-bar-stacked': {
    renderAs: 'chart',
    chartType: 'stacked',
    label: 'Stacked Category',
    description: 'Stacked bar by category',
    defaultSize: { w: 6, h: 3 },
  },
  'category-bar-grouped': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Grouped Category',
    description: 'Grouped bar by category',
    defaultSize: { w: 8, h: 3 },
    chartOptions: { grouped: true },
  },
  'category-bar-diverging': {
    renderAs: 'chart',
    chartType: 'bar',
    label: 'Diverging Bar',
    description: 'Diverging bar from center axis',
    defaultSize: { w: 6, h: 3 },
    chartOptions: { diverging: true },
  },

  // ── Flow Sankey (5 variants) ──────────────────────────────────────────
  'flow-sankey-standard': {
    renderAs: 'domain',
    label: 'Sankey Flow',
    description: 'Standard energy/material flow',
    defaultSize: { w: 8, h: 4 },
    domainType: 'flow-sankey',
  },
  'flow-sankey-energy-balance': {
    renderAs: 'domain',
    label: 'Energy Balance',
    description: 'Energy input → output balance',
    defaultSize: { w: 8, h: 4 },
    domainType: 'flow-sankey',
  },
  'flow-sankey-multi-source': {
    renderAs: 'domain',
    label: 'Multi-Source Flow',
    description: 'Multiple source → destination flows',
    defaultSize: { w: 10, h: 4 },
    domainType: 'flow-sankey',
  },
  'flow-sankey-layered': {
    renderAs: 'domain',
    label: 'Layered Flow',
    description: 'Multi-layer flow diagram',
    defaultSize: { w: 10, h: 4 },
    domainType: 'flow-sankey',
  },
  'flow-sankey-time-sliced': {
    renderAs: 'domain',
    label: 'Time-Sliced Flow',
    description: 'Flow changes over time periods',
    defaultSize: { w: 10, h: 4 },
    domainType: 'flow-sankey',
  },

  // ── Matrix Heatmap (5 variants) ───────────────────────────────────────
  'matrix-heatmap-value': {
    renderAs: 'domain',
    label: 'Value Heatmap',
    description: 'Color-coded value matrix',
    defaultSize: { w: 8, h: 4 },
    domainType: 'matrix-heatmap',
  },
  'matrix-heatmap-correlation': {
    renderAs: 'domain',
    label: 'Correlation Matrix',
    description: 'Metric-to-metric correlation',
    defaultSize: { w: 8, h: 4 },
    domainType: 'matrix-heatmap',
  },
  'matrix-heatmap-calendar': {
    renderAs: 'domain',
    label: 'Calendar Heatmap',
    description: 'Day-of-week × hour pattern',
    defaultSize: { w: 8, h: 4 },
    domainType: 'matrix-heatmap',
  },
  'matrix-heatmap-status': {
    renderAs: 'domain',
    label: 'Status Matrix',
    description: 'Equipment × metric status grid',
    defaultSize: { w: 8, h: 4 },
    domainType: 'matrix-heatmap',
  },
  'matrix-heatmap-density': {
    renderAs: 'domain',
    label: 'Density Heatmap',
    description: 'Event density visualization',
    defaultSize: { w: 8, h: 4 },
    domainType: 'matrix-heatmap',
  },

  // ── Timeline (5 variants) ─────────────────────────────────────────────
  'timeline-linear': {
    renderAs: 'list',
    label: 'Linear Timeline',
    description: 'Chronological event sequence',
    defaultSize: { w: 6, h: 3 },
    listType: 'timeline',
  },
  'timeline-status': {
    renderAs: 'list',
    label: 'Status Timeline',
    description: 'Equipment status history',
    defaultSize: { w: 6, h: 3 },
    listType: 'timeline',
  },
  'timeline-multilane': {
    renderAs: 'list',
    label: 'Multi-Lane Timeline',
    description: 'Parallel timelines per entity',
    defaultSize: { w: 8, h: 4 },
    listType: 'timeline',
  },
  'timeline-forensic': {
    renderAs: 'list',
    label: 'Forensic Timeline',
    description: 'Detailed incident investigation',
    defaultSize: { w: 8, h: 4 },
    listType: 'timeline',
  },
  'timeline-dense': {
    renderAs: 'list',
    label: 'Dense Timeline',
    description: 'Compact high-frequency events',
    defaultSize: { w: 8, h: 3 },
    listType: 'timeline',
  },

  // ── Alerts (5 variants) ───────────────────────────────────────────────
  'alerts-banner': {
    renderAs: 'list',
    label: 'Alert Banner',
    description: 'Full-width alert notification',
    defaultSize: { w: 12, h: 1 },
    listType: 'alerts',
  },
  'alerts-toast': {
    renderAs: 'list',
    label: 'Alert Toast',
    description: 'Compact stacked notifications',
    defaultSize: { w: 3, h: 2 },
    listType: 'alerts',
  },
  'alerts-card': {
    renderAs: 'list',
    label: 'Alert Cards',
    description: 'Card-based alert display',
    defaultSize: { w: 4, h: 3 },
    listType: 'alerts',
  },
  'alerts-badge': {
    renderAs: 'list',
    label: 'Alert Badge',
    description: 'Compact count badge with summary',
    defaultSize: { w: 2, h: 2 },
    listType: 'alerts',
  },
  'alerts-modal': {
    renderAs: 'list',
    label: 'Alert Modal',
    description: 'Expandable alert detail panel',
    defaultSize: { w: 6, h: 3 },
    listType: 'alerts',
  },

  // ── Event Log Stream (5 variants) ─────────────────────────────────────
  'eventlogstream-chronological': {
    renderAs: 'list',
    label: 'Chronological Log',
    description: 'Time-ordered event stream',
    defaultSize: { w: 6, h: 4 },
    listType: 'eventlog',
  },
  'eventlogstream-compact-feed': {
    renderAs: 'list',
    label: 'Compact Feed',
    description: 'Dense scrolling event feed',
    defaultSize: { w: 4, h: 4 },
    listType: 'eventlog',
  },
  'eventlogstream-tabular': {
    renderAs: 'list',
    label: 'Tabular Log',
    description: 'Table-formatted event log',
    defaultSize: { w: 8, h: 4 },
    listType: 'eventlog',
  },
  'eventlogstream-correlation': {
    renderAs: 'list',
    label: 'Correlation Log',
    description: 'Events grouped by correlation',
    defaultSize: { w: 8, h: 4 },
    listType: 'eventlog',
  },
  'eventlogstream-grouped-asset': {
    renderAs: 'list',
    label: 'Asset-Grouped Log',
    description: 'Events grouped by equipment',
    defaultSize: { w: 8, h: 4 },
    listType: 'eventlog',
  },

  // ── Narrative (1 variant) ─────────────────────────────────────────────
  narrative: {
    renderAs: 'text',
    label: 'Narrative',
    description: 'Text-based insight summary',
    defaultSize: { w: 4, h: 2 },
  },

  // ── Single-variant domain scenarios ───────────────────────────────────
  peopleview: {
    renderAs: 'domain',
    label: 'People View',
    description: 'Personnel overview and assignments',
    defaultSize: { w: 6, h: 3 },
    domainType: 'peopleview',
  },
  peoplehexgrid: {
    renderAs: 'domain',
    label: 'People Hex Grid',
    description: 'Hexagonal personnel spatial map',
    defaultSize: { w: 8, h: 4 },
    domainType: 'peoplehexgrid',
  },
  peoplenetwork: {
    renderAs: 'domain',
    label: 'People Network',
    description: 'Organizational network graph',
    defaultSize: { w: 8, h: 4 },
    domainType: 'peoplenetwork',
  },
  supplychainglobe: {
    renderAs: 'domain',
    label: 'Supply Chain Globe',
    description: '3D globe with supply routes',
    defaultSize: { w: 12, h: 6 },
    domainType: 'supplychainglobe',
  },
  edgedevicepanel: {
    renderAs: 'domain',
    label: 'Edge Device Panel',
    description: 'IoT/edge device status panel',
    defaultSize: { w: 4, h: 2 },
    domainType: 'edgedevicepanel',
  },
  chatstream: {
    renderAs: 'domain',
    label: 'Chat Stream',
    description: 'Conversational message feed',
    defaultSize: { w: 4, h: 3 },
    domainType: 'chatstream',
  },
  diagnosticpanel: {
    renderAs: 'domain',
    label: 'Diagnostic Panel',
    description: 'Equipment diagnostics & health',
    defaultSize: { w: 6, h: 3 },
    domainType: 'diagnosticpanel',
  },
  uncertaintypanel: {
    renderAs: 'domain',
    label: 'Uncertainty Panel',
    description: 'Confidence intervals & data quality',
    defaultSize: { w: 4, h: 2 },
    domainType: 'uncertaintypanel',
  },
  agentsview: {
    renderAs: 'domain',
    label: 'Agents View',
    description: 'AI agent status & activity',
    defaultSize: { w: 6, h: 2 },
    domainType: 'agentsview',
  },
  vaultview: {
    renderAs: 'domain',
    label: 'Vault View',
    description: 'Secure data vault & archive',
    defaultSize: { w: 6, h: 2 },
    domainType: 'vaultview',
  },
}

// ── Scenario → Default Variant mapping ──────────────────────────────────────

export const DEFAULT_VARIANTS = {
  kpi: 'kpi-live',
  trend: 'trend-line',
  'trend-multi-line': 'trend-multi-line',
  'trends-cumulative': 'trends-cumulative',
  comparison: 'comparison-side-by-side',
  distribution: 'distribution-donut',
  composition: 'composition-stacked-bar',
  'category-bar': 'category-bar-vertical',
  'flow-sankey': 'flow-sankey-standard',
  'matrix-heatmap': 'matrix-heatmap-value',
  timeline: 'timeline-linear',
  alerts: 'alerts-card',
  eventlogstream: 'eventlogstream-chronological',
  narrative: 'narrative',
  peopleview: 'peopleview',
  peoplehexgrid: 'peoplehexgrid',
  peoplenetwork: 'peoplenetwork',
  supplychainglobe: 'supplychainglobe',
  edgedevicepanel: 'edgedevicepanel',
  chatstream: 'chatstream',
  diagnosticpanel: 'diagnosticpanel',
  uncertaintypanel: 'uncertaintypanel',
  agentsview: 'agentsview',
  vaultview: 'vaultview',
}

// ── Scenario → All Variants list ────────────────────────────────────────────

export const SCENARIO_VARIANTS = {
  kpi: ['kpi-live', 'kpi-alert', 'kpi-accumulated', 'kpi-lifecycle', 'kpi-status'],
  trend: ['trend-line', 'trend-area', 'trend-step-line', 'trend-rgb-phase', 'trend-alert-context', 'trend-heatmap'],
  'trend-multi-line': ['trend-multi-line'],
  'trends-cumulative': ['trends-cumulative'],
  comparison: ['comparison-side-by-side', 'comparison-delta-bar', 'comparison-grouped-bar', 'comparison-waterfall', 'comparison-small-multiples', 'comparison-composition-split'],
  distribution: ['distribution-donut', 'distribution-100-stacked-bar', 'distribution-horizontal-bar', 'distribution-pie', 'distribution-grouped-bar', 'distribution-pareto-bar'],
  composition: ['composition-stacked-bar', 'composition-stacked-area', 'composition-donut', 'composition-waterfall', 'composition-treemap'],
  'category-bar': ['category-bar-vertical', 'category-bar-horizontal', 'category-bar-stacked', 'category-bar-grouped', 'category-bar-diverging'],
  'flow-sankey': ['flow-sankey-standard', 'flow-sankey-energy-balance', 'flow-sankey-multi-source', 'flow-sankey-layered', 'flow-sankey-time-sliced'],
  'matrix-heatmap': ['matrix-heatmap-value', 'matrix-heatmap-correlation', 'matrix-heatmap-calendar', 'matrix-heatmap-status', 'matrix-heatmap-density'],
  timeline: ['timeline-linear', 'timeline-status', 'timeline-multilane', 'timeline-forensic', 'timeline-dense'],
  alerts: ['alerts-banner', 'alerts-toast', 'alerts-card', 'alerts-badge', 'alerts-modal'],
  eventlogstream: ['eventlogstream-chronological', 'eventlogstream-compact-feed', 'eventlogstream-tabular', 'eventlogstream-correlation', 'eventlogstream-grouped-asset'],
  narrative: ['narrative'],
  peopleview: ['peopleview'],
  peoplehexgrid: ['peoplehexgrid'],
  peoplenetwork: ['peoplenetwork'],
  supplychainglobe: ['supplychainglobe'],
  edgedevicepanel: ['edgedevicepanel'],
  chatstream: ['chatstream'],
  diagnosticpanel: ['diagnosticpanel'],
  uncertaintypanel: ['uncertaintypanel'],
  agentsview: ['agentsview'],
  vaultview: ['vaultview'],
}

/**
 * Get variant config, falling back to default variant for the scenario.
 */
export function getVariantConfig(variant, scenario) {
  if (VARIANT_CONFIG[variant]) return VARIANT_CONFIG[variant]
  const defaultVariant = DEFAULT_VARIANTS[scenario]
  if (defaultVariant && VARIANT_CONFIG[defaultVariant]) return VARIANT_CONFIG[defaultVariant]
  return null
}

/**
 * Get the default size for a variant or scenario.
 */
export function getVariantDefaultSize(variant, scenario) {
  const config = getVariantConfig(variant, scenario)
  return config?.defaultSize || { w: 4, h: 3 }
}
