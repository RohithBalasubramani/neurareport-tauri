import { Alert, Typography } from '@mui/material'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend as RechartsLegend,
} from 'recharts'

import { secondary } from '@/app/theme'

const palette = [
  secondary.violet[500],
  secondary.emerald[500],
  secondary.cyan[500],
  secondary.rose[500],
  secondary.teal[500],
  secondary.fuchsia[500],
  secondary.slate[500],
]

export default function SuggestedChartRenderer({ spec, data, source }) {
  if (!spec) {
    return (
      <Typography variant="body2" color="text.secondary">
        Select a suggestion to preview a chart.
      </Typography>
    )
  }
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No data available for this template and filters.
      </Typography>
    )
  }
  const sample = data[0] || {}
  const fieldNames = new Set(Object.keys(sample))
  const missingFields = []
  if (!fieldNames.has(spec.xField)) {
    missingFields.push(spec.xField)
  }
  const yFieldsArray = Array.isArray(spec.yFields) && spec.yFields.length ? spec.yFields : ['rows']
  yFieldsArray.forEach((field) => {
    if (!fieldNames.has(field)) {
      missingFields.push(field)
    }
  })
  if (spec.groupField && !fieldNames.has(spec.groupField)) {
    missingFields.push(spec.groupField)
  }
  if (missingFields.length) {
    return (
      <Alert severity="warning" sx={{ mt: 0.5 }}>
        {source === 'saved'
          ? `Saved chart references fields not present in current data (missing: ${missingFields.join(
              ', ',
            )}). Edit or delete this chart.`
          : `Cannot render this chart because the dataset is missing: ${missingFields.join(', ')}.`}
      </Alert>
    )
  }
  const type = (spec.type || '').toLowerCase()
  const xField = spec.xField
  const yKeys = yFieldsArray.length ? yFieldsArray : ['rows']

  if (type === 'pie') {
    const valueKey = yKeys[0]
    return (
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={xField}
            innerRadius="45%"
            outerRadius="80%"
            paddingAngle={2}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={palette[index % palette.length]} />
            ))}
          </Pie>
          <RechartsTooltip />
          <RechartsLegend />
        </PieChart>
      </ResponsiveContainer>
    )
  }
  if (type === 'scatter') {
    const yKey = yKeys[0]
    return (
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey={xField} name={xField} tick={{ fontSize: 12 }} />
          <YAxis type="number" dataKey={yKey} name={yKey} tick={{ fontSize: 12 }} />
          <RechartsTooltip />
          <RechartsLegend />
          <Scatter data={data} fill={secondary.emerald[500]} />
        </ScatterChart>
      </ResponsiveContainer>
    )
  }
  if (type === 'line') {
    return (
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <RechartsTooltip />
          <RechartsLegend />
          {yKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={palette[index % palette.length]}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    )
  }
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <RechartsTooltip />
        <RechartsLegend />
        {yKeys.map((key, index) => (
          <Bar key={key} dataKey={key} fill={palette[index % palette.length]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  )
}
