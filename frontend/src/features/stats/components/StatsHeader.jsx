import {
  Box,
  Typography,
  Stack,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Grid,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import DescriptionIcon from '@mui/icons-material/Description'
import WorkIcon from '@mui/icons-material/Work'
import StorageIcon from '@mui/icons-material/Storage'
import DownloadIcon from '@mui/icons-material/Download'
import { StyledFormControl, RefreshButton, ExportButton } from '@/styles'
import { neutral } from '@/app/theme'
import StatCard from './StatCard'

const PERIOD_OPTIONS = [
  { value: 'day', label: 'Last 24 hours' },
  { value: 'week', label: 'Last 7 days' },
  { value: 'month', label: 'Last 30 days' },
]

export default function StatsHeader({
  theme,
  period,
  loading,
  summary,
  metrics,
  handleNavigate,
  handleRefresh,
  handleExportStats,
  handlePeriodChange,
  HeaderContainer,
}) {
  return (
    <>
      <HeaderContainer direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h5" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
            Usage Statistics
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Detailed analytics and insights for your workspace
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <StyledFormControl size="small">
            <InputLabel>Time Period</InputLabel>
            <Select
              value={period}
              onChange={(e) => handlePeriodChange(e.target.value)}
              label="Time Period"
            >
              {PERIOD_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
          <ExportButton
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon sx={{ fontSize: 16 }} />}
            onClick={handleExportStats}
          >
            Export
          </ExportButton>
          <RefreshButton
            onClick={handleRefresh}
            disabled={loading}
            sx={{ color: theme.palette.text.secondary }}
          >
            {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          </RefreshButton>
        </Stack>
      </HeaderContainer>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Total Jobs"
            value={summary.totalJobs || 0}
            subtitle={`${metrics.jobsThisWeek || 0} this week`}
            icon={WorkIcon}
            color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
            onClick={() => handleNavigate('/jobs', 'Open jobs')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Success Rate"
            value={`${(metrics.successRate || 0).toFixed(1)}%`}
            subtitle={`${summary.completedJobs || 0} completed`}
            icon={CheckCircleIcon}
            color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
            onClick={() => handleNavigate('/history', 'Open history')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Templates"
            value={summary.totalTemplates || 0}
            subtitle={`${summary.approvedTemplates || 0} approved`}
            icon={DescriptionIcon}
            color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
            onClick={() => handleNavigate('/templates', 'Open templates')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Connections"
            value={summary.totalConnections || 0}
            subtitle={`${summary.activeConnections || 0} active`}
            icon={StorageIcon}
            color={theme.palette.mode === 'dark' ? neutral[300] : neutral[300]}
            onClick={() => handleNavigate('/connections', 'Open connections')}
          />
        </Grid>
      </Grid>
    </>
  )
}
