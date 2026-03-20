import {
  Box,
  Stack,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import { neutral } from '@/app/theme'
import ChartCard from './ChartCard'
import CustomTooltip from './CustomTooltip'

export default function OverviewTab({
  jobsTrend,
  statusData,
  kindData,
  templateBreakdown,
  CHART_COLORS,
}) {
  const theme = useTheme()

  return (
    <Grid container spacing={2}>
      {/* Jobs Trend Chart */}
      <Grid size={{ xs: 12, lg: 8 }}>
        <ChartCard title="Jobs Trend" subtitle="Daily job completions over the past week">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={jobsTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
              <XAxis
                dataKey="label"
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
              />
              <YAxis
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="completed" name="Completed" fill={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} radius={[4, 4, 0, 0]} />
              <Bar dataKey="failed" name="Failed" fill={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>

      {/* Status Distribution */}
      <Grid size={{ xs: 12, lg: 4 }}>
        <ChartCard title="Job Status" subtitle="Distribution by status">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => (
                  <span style={{ color: theme.palette.text.secondary, fontSize: '0.75rem' }}>{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>

      {/* Template Type Distribution */}
      <Grid size={{ xs: 12, md: 6 }}>
        <ChartCard title="Template Types" subtitle="PDF vs Excel usage">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={kindData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={{ stroke: theme.palette.text.secondary }}
              >
                {kindData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>

      {/* Top Templates */}
      <Grid size={{ xs: 12, md: 6 }}>
        <ChartCard title="Top Templates" subtitle="Most used templates">
          {templateBreakdown.length === 0 ? (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
                No template usage data
              </Typography>
            </Box>
          ) : (
            <Stack spacing={1.5}>
              {templateBreakdown.map((template, index) => (
                <Box key={index}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <Typography sx={{ fontSize: '14px', color: theme.palette.text.primary }}>
                        {template.name}
                      </Typography>
                      <Chip
                        label={template.kind?.toUpperCase()}
                        size="small"
                        sx={{
                          height: 18,
                          fontSize: '10px',
                          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                          color: 'text.secondary',
                          borderRadius: 1,
                        }}
                      />
                    </Stack>
                    <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
                      {template.count} runs
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={
                      templateBreakdown[0]?.count
                        ? (template.count / templateBreakdown[0].count) * 100
                        : 0
                    }
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: alpha(theme.palette.divider, 0.15),
                      '& .MuiLinearProgress-bar': {
                        bgcolor: CHART_COLORS[index % CHART_COLORS.length],
                        borderRadius: 3,
                      },
                    }}
                  />
                </Box>
              ))}
            </Stack>
          )}
        </ChartCard>
      </Grid>
    </Grid>
  )
}
