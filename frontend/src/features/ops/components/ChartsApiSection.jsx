import { Stack, Typography, TextField, Button, Grid } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import { parseJsonInput, splitList } from '../hooks/useOpsConsole'

export default function ChartsApiSection({ state, busy, toast, runRequest }) {
  const {
    chartData, setChartData,
    chartType, setChartType,
    chartXField, setChartXField,
    chartYFields, setChartYFields,
    chartTitle, setChartTitle,
    chartMaxSuggestions, setChartMaxSuggestions,
  } = state

  return (
    <Surface>
      <SectionHeader
        title="Charts API"
        subtitle="Request chart analysis and generation directly."
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">Analyze Data</Typography>
            <TextField
              fullWidth
              label="Data (JSON array)"
              value={chartData}
              onChange={(event) => setChartData(event.target.value)}
              size="small"
              multiline
              minRows={4}
            />
            <TextField
              fullWidth
              label="Max Suggestions"
              type="number"
              value={chartMaxSuggestions}
              onChange={(event) => setChartMaxSuggestions(Number(event.target.value) || 0)}
              size="small"
              inputProps={{ min: 1, max: 10 }}
            />
            <Button
              variant="outlined"
              disabled={busy}
              onClick={() => {
                const data = parseJsonInput(chartData, toast, 'chart data')
                if (data === null) return
                runRequest({
                  method: 'post',
                  url: '/charts/analyze?background=true',
                  data: {
                    data,
                    max_suggestions: chartMaxSuggestions || 3,
                  },
                })
              }}
            >
              Analyze Charts
            </Button>
          </Stack>
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">Generate Chart</Typography>
            <TextField
              fullWidth
              label="Chart Type"
              value={chartType}
              onChange={(event) => setChartType(event.target.value)}
              size="small"
            />
            <TextField
              fullWidth
              label="X Field"
              value={chartXField}
              onChange={(event) => setChartXField(event.target.value)}
              size="small"
            />
            <TextField
              fullWidth
              label="Y Fields (comma separated)"
              value={chartYFields}
              onChange={(event) => setChartYFields(event.target.value)}
              size="small"
            />
            <TextField
              fullWidth
              label="Title (optional)"
              value={chartTitle}
              onChange={(event) => setChartTitle(event.target.value)}
              size="small"
            />
            <Button
              variant="contained"
              disabled={busy}
              onClick={() => {
                const data = parseJsonInput(chartData, toast, 'chart data')
                if (data === null) return
                runRequest({
                  method: 'post',
                  url: '/charts/generate?background=true',
                  data: {
                    data,
                    chart_type: chartType || 'bar',
                    x_field: chartXField,
                    y_fields: splitList(chartYFields),
                    title: chartTitle || undefined,
                  },
                })
              }}
            >
              Generate Chart
            </Button>
          </Stack>
        </Grid>
      </Grid>
    </Surface>
  )
}
