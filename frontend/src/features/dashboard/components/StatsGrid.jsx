import { Box } from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import DescriptionIcon from '@mui/icons-material/Description'
import WorkIcon from '@mui/icons-material/Work'
import ScheduleIcon from '@mui/icons-material/Schedule'
import SpeedIcon from '@mui/icons-material/Speed'
import StatCard from './StatCard'

export default function StatsGrid({ summary, metrics, savedConnections, templates, handleNavigate }) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)',
          lg: 'repeat(5, 1fr)',
        },
        gap: 2.5,
        mb: 4,
      }}
    >
      <StatCard
        title="Connections"
        value={summary.totalConnections ?? savedConnections.length}
        subtitle={`${summary.activeConnections ?? 0} active`}
        icon={StorageIcon}
        onClick={() => handleNavigate('/connections', 'Open connections')}
        delay={0}
      />
      <StatCard
        title="Templates"
        value={summary.totalTemplates ?? templates.length}
        subtitle={`${summary.pdfTemplates ?? 0} PDF, ${summary.excelTemplates ?? 0} Excel`}
        icon={DescriptionIcon}
        onClick={() => handleNavigate('/templates', 'Open templates')}
        delay={50}
      />
      <StatCard
        title="Jobs Today"
        value={metrics.jobsToday ?? 0}
        subtitle={`${metrics.jobsThisWeek ?? 0} this week`}
        icon={WorkIcon}
        onClick={() => handleNavigate('/jobs', 'Open jobs')}
        delay={100}
      />
      <StatCard
        title="Success Rate"
        value={`${metrics.successRate ?? 0}%`}
        subtitle={`${summary.completedJobs ?? 0} completed`}
        icon={SpeedIcon}
        onClick={() => handleNavigate('/stats', 'Open usage stats')}
        trend={metrics.successRateTrend}
        delay={150}
      />
      <StatCard
        title="Schedules"
        value={summary.totalSchedules ?? 0}
        subtitle={`${summary.activeSchedules ?? 0} active`}
        icon={ScheduleIcon}
        onClick={() => handleNavigate('/schedules', 'Open schedules')}
        delay={200}
      />
    </Box>
  )
}
