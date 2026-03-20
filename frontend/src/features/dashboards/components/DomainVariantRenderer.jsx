/**
 * Domain variant sub-renderer for WidgetRenderer (heatmap, sankey, placeholders).
 */
import { Typography, Chip } from '@mui/material'
import {
  TrendingUp as TrendIcon,
  Devices as DeviceIcon,
  Public as GlobeIcon,
  Lock as VaultIcon,
  People as PeopleIcon,
  Chat as ChatIcon,
  Build as BuildIcon,
  HelpOutline as UncertaintyIcon,
  Hexagon as HexIcon,
  Hub as NetworkIcon,
  AccountTree as SankeyIcon,
  GridView as HeatmapIcon,
  SmartToy as AgentIcon,
} from '@mui/icons-material'
import ChartWidget from './ChartWidget'
import { PlaceholderCard } from './WidgetRendererStyles'

const DOMAIN_ICONS = {
  'flow-sankey': SankeyIcon,
  'matrix-heatmap': HeatmapIcon,
  diagnosticpanel: BuildIcon,
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

export default function DomainVariantRenderer({ variantKey, vConfig, data, config, ...props }) {
  const domainType = vConfig.domainType || variantKey
  const title = config?.title || vConfig.label

  // Route heatmap and sankey through ChartWidget for actual ECharts rendering
  if (domainType === 'matrix-heatmap' && data && Object.keys(data).length > 0) {
    return (
      <ChartWidget
        title={title}
        chartType="heatmap"
        data={data}
        config={{ ...config, title }}
        editable={false}
        {...props}
      />
    )
  }

  if (domainType === 'flow-sankey' && data && Object.keys(data).length > 0) {
    return (
      <ChartWidget
        title={title}
        chartType="sankey"
        data={data}
        config={{ ...config, title }}
        editable={false}
        {...props}
      />
    )
  }

  // Fallback placeholder for other domain types
  const IconComponent = DOMAIN_ICONS[domainType] || TrendIcon
  return (
    <PlaceholderCard>
      <IconComponent sx={{ fontSize: 40, color: 'primary.main', opacity: 0.6 }} />
      <Typography variant="subtitle2" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="caption" color="text.disabled">
        {vConfig.description || variantKey}
      </Typography>
      {data && Object.keys(data).length > 0 && (
        <Chip label="Data loaded" size="small" color="success" variant="outlined" sx={{ mt: 0.5 }} />
      )}
    </PlaceholderCard>
  )
}
