import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Brush,
  Cell,
  ReferenceArea,
} from 'recharts'
import { Box, Typography } from '@mui/material'
import { neutral, secondary } from '@/app/theme'

const CHART_COLORS = [
  secondary.violet[500],
  secondary.emerald[500],
  secondary.cyan[500],
  secondary.rose[500],
  secondary.teal[500],
  secondary.fuchsia[500],
  secondary.slate[500],
  secondary.zinc[500],
]

const CHART_MARGINS = { top: 8, right: 16, bottom: 24, left: 8 }

export { CHART_COLORS, CHART_MARGINS }

export default function ChartRenderer({
  type = 'bar',
  xField,
  yFields = [],
  displayData,
  data,
  height,
  showBrush,
  zoomState,
  handleMouseDown,
  handleMouseMove,
  handleMouseUp,
  handleBrushChange,
}) {
  if (!xField || yFields.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height }}>
        <Typography color="text.secondary">Invalid chart configuration</Typography>
      </Box>
    )
  }

  if (!displayData || displayData.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height }}>
        <Typography color="text.secondary">No data available</Typography>
      </Box>
    )
  }

  const commonProps = {
    data: displayData,
    margin: CHART_MARGINS,
    onMouseDown: type !== 'pie' ? handleMouseDown : undefined,
    onMouseMove: type !== 'pie' ? handleMouseMove : undefined,
    onMouseUp: type !== 'pie' ? handleMouseUp : undefined,
  }

  const zoomArea =
    zoomState.refAreaLeft && zoomState.refAreaRight ? (
      <ReferenceArea
        x1={zoomState.refAreaLeft}
        x2={zoomState.refAreaRight}
        strokeOpacity={0.3}
        fill={secondary.violet[500]}
        fillOpacity={0.3}
      />
    ) : null

  const brush = showBrush && type !== 'pie' && data.length > 10 ? (
    <Brush
      dataKey={xField}
      height={24}
      stroke={secondary.violet[500]}
      travellerWidth={8}
      onChange={handleBrushChange}
      startIndex={zoomState.startIndex}
      endIndex={zoomState.endIndex ?? data.length - 1}
    />
  ) : null

  switch (type) {
    case 'line':
      return (
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {yFields.map((field, idx) => (
            <Line
              key={field}
              type="monotone"
              dataKey={field}
              stroke={CHART_COLORS[idx % CHART_COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
          {zoomArea}
          {brush}
        </LineChart>
      )

    case 'pie':
      return (
        <PieChart>
          <Pie
            data={displayData}
            dataKey={yFields[0]}
            nameKey={xField}
            cx="50%"
            cy="50%"
            innerRadius="40%"
            outerRadius="75%"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            labelLine={{ stroke: neutral[500], strokeWidth: 1 }}
          >
            {displayData.map((entry, idx) => (
              <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      )

    case 'scatter':
      return (
        <ScatterChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} name={xField} tick={{ fontSize: 12 }} />
          <YAxis dataKey={yFields[0]} name={yFields[0]} tick={{ fontSize: 12 }} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter
            name={yFields[0]}
            data={displayData}
            fill={CHART_COLORS[0]}
          />
          {zoomArea}
          {brush}
        </ScatterChart>
      )

    case 'bar':
    default:
      return (
        <BarChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {yFields.map((field, idx) => (
            <Bar
              key={field}
              dataKey={field}
              fill={CHART_COLORS[idx % CHART_COLORS.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
          {zoomArea}
          {brush}
        </BarChart>
      )
  }
}
