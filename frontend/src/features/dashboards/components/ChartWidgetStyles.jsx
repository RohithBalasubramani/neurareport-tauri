/**
 * Styled components and constants for ChartWidget.
 */
import {
  Box,
  alpha,
  styled,
} from '@mui/material'
import {
  BarChart as BarChartIcon,
  ShowChart as LineChartIcon,
  PieChart as PieChartIcon,
  DonutLarge as DonutIcon,
  ScatterPlot as ScatterIcon,
  BubbleChart as BubbleIcon,
  StackedBarChart as StackedIcon,
  AreaChart as AreaIcon,
} from '@mui/icons-material'

export const WidgetContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  overflow: 'hidden',
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

export const WidgetHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
  minHeight: 48,
}))

export const DragHandle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  cursor: 'grab',
  color: alpha(theme.palette.text.secondary, 0.4),
  marginRight: theme.spacing(1),
  '&:hover': {
    color: theme.palette.text.secondary,
  },
  '&:active': {
    cursor: 'grabbing',
  },
}))

export const WidgetContent = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(1),
  minHeight: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

export const ChartTypeIcon = {
  bar: BarChartIcon,
  line: LineChartIcon,
  pie: PieChartIcon,
  donut: DonutIcon,
  scatter: ScatterIcon,
  bubble: BubbleIcon,
  stacked: StackedIcon,
  area: AreaIcon,
}

export const SAMPLE_DATA = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    { label: 'Sales', data: [120, 200, 150, 80, 170, 250] },
    { label: 'Expenses', data: [90, 120, 100, 60, 110, 140] },
  ],
}

/**
 * Available chart types
 */
export const CHART_TYPES = [
  { type: 'bar', label: 'Bar Chart', icon: BarChartIcon },
  { type: 'line', label: 'Line Chart', icon: LineChartIcon },
  { type: 'area', label: 'Area Chart', icon: AreaIcon },
  { type: 'pie', label: 'Pie Chart', icon: PieChartIcon },
  { type: 'donut', label: 'Donut Chart', icon: DonutIcon },
  { type: 'scatter', label: 'Scatter Plot', icon: ScatterIcon },
  { type: 'stacked', label: 'Stacked Bar', icon: StackedIcon },
]
