import { Grid, useTheme, alpha } from '@mui/material'
import ScheduleIcon from '@mui/icons-material/Schedule'
import WorkIcon from '@mui/icons-material/Work'
import BarChartIcon from '@mui/icons-material/BarChart'
import ErrorIcon from '@mui/icons-material/Error'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { neutral } from '@/app/theme'
import StatCard from './StatCard'
import ChartCard from './ChartCard'
import CustomTooltip from './CustomTooltip'

export default function JobsTab({ historyByDay, metrics, summary, handleNavigate }) {
  const theme = useTheme()

  return (
    <Grid container spacing={2}>
      {/* Jobs Over Time */}
      <Grid size={12}>
        <ChartCard title="Jobs History" subtitle="Job executions over the past 2 weeks" height={320}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historyByDay}>
              <defs>
                <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
              <XAxis
                dataKey="date"
                tick={{ fill: theme.palette.text.secondary, fontSize: 10 }}
                axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="completed"
                name="Completed"
                stroke={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
                fill="url(#colorCompleted)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="failed"
                name="Failed"
                stroke={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
                fill="url(#colorFailed)"
                strokeWidth={2}
              />
              <Legend
                verticalAlign="top"
                height={36}
                formatter={(value) => (
                  <span style={{ color: theme.palette.text.secondary, fontSize: '0.75rem' }}>{value}</span>
                )}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>

      {/* Job Stats Cards */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Jobs Today"
          value={metrics.jobsToday || 0}
          icon={ScheduleIcon}
          color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
          onClick={() => handleNavigate('/jobs', 'Open jobs')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Jobs This Week"
          value={metrics.jobsThisWeek || 0}
          icon={WorkIcon}
          color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
          onClick={() => handleNavigate('/jobs', 'Open jobs')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Jobs This Month"
          value={metrics.jobsThisMonth || 0}
          icon={BarChartIcon}
          color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
          onClick={() => handleNavigate('/jobs', 'Open jobs')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Failed Jobs"
          value={summary.failedJobs || 0}
          icon={ErrorIcon}
          color={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
          onClick={() =>
            handleNavigate('/history?status=failed', 'Open failed history', { status: 'failed' })
          }
        />
      </Grid>
    </Grid>
  )
}
