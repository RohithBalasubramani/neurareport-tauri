import {
  Box,
  Typography,
  Grid,
  useTheme,
  alpha,
} from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import ScheduleIcon from '@mui/icons-material/Schedule'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { neutral } from '@/app/theme'
import StatCard from './StatCard'
import ChartCard from './ChartCard'
import CustomTooltip from './CustomTooltip'

export default function TemplatesTab({ summary, templateBreakdown, handleNavigate }) {
  const theme = useTheme()

  return (
    <Grid container spacing={2}>
      {/* Template Stats */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Total Templates"
          value={summary.totalTemplates || 0}
          icon={DescriptionIcon}
          color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
          onClick={() => handleNavigate('/templates', 'Open templates')}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="PDF Templates"
          value={summary.pdfTemplates || 0}
          icon={DescriptionIcon}
          color={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
          onClick={() =>
            handleNavigate('/templates?kind=pdf', 'Open PDF templates', { kind: 'pdf' })
          }
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Excel Templates"
          value={summary.excelTemplates || 0}
          icon={DescriptionIcon}
          color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
          onClick={() =>
            handleNavigate('/templates?kind=excel', 'Open Excel templates', { kind: 'excel' })
          }
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Active Schedules"
          value={summary.activeSchedules || 0}
          icon={ScheduleIcon}
          color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
          onClick={() => handleNavigate('/schedules', 'Open schedules')}
        />
      </Grid>

      {/* Template Usage */}
      <Grid size={12}>
        <ChartCard title="Template Usage Breakdown" subtitle="Jobs per template" height={400}>
          {templateBreakdown.length === 0 ? (
            <Box sx={{ py: 8, textAlign: 'center' }}>
              <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 2 }} />
              <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
                No template usage data available
              </Typography>
            </Box>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={templateBreakdown} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                <XAxis
                  type="number"
                  tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                  axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                  axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                  width={120}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Jobs" fill={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>
      </Grid>
    </Grid>
  )
}
