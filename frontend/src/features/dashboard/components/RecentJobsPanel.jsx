import {
  Box,
  Typography,
  Stack,
  Button,
  Chip,
  Grow,
  alpha,
  useTheme,
} from '@mui/material'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import WorkIcon from '@mui/icons-material/Work'
import { neutral } from '@/app/theme'
import { shimmer, GlassCard } from '@/styles'
import { JobListItem } from './DashboardStyledComponents'

function getStatusIcon(status) {
  const iconProps = { sx: { fontSize: 18 } }
  switch (status) {
    case 'completed':
      return <CheckCircleOutlineIcon {...iconProps} sx={{ ...iconProps.sx, color: 'text.secondary' }} />
    case 'running':
      return <PlayArrowIcon {...iconProps} sx={{ ...iconProps.sx, color: 'text.secondary' }} />
    case 'pending':
      return <HourglassEmptyIcon {...iconProps} sx={{ ...iconProps.sx, color: 'text.secondary' }} />
    case 'failed':
      return <ErrorOutlineIcon {...iconProps} sx={{ ...iconProps.sx, color: 'text.secondary' }} />
    default:
      return <HourglassEmptyIcon {...iconProps} sx={{ ...iconProps.sx, color: 'text.secondary' }} />
  }
}

export default function RecentJobsPanel({ jobs, loading, handleNavigate }) {
  const theme = useTheme()

  return (
    <GlassCard sx={{ animationDelay: '250ms' }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="subtitle1" fontWeight={600}>
          Recent Jobs
        </Typography>
        <Button
          size="small"
          onClick={() => handleNavigate('/jobs', 'Open jobs')}
          sx={{ fontWeight: 600, fontSize: '0.75rem' }}
        >
          View All
        </Button>
      </Stack>

      {loading ? (
        <Stack spacing={1.5}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Box
              key={i}
              sx={{
                height: 48,
                borderRadius: 1.5,
                background: `linear-gradient(90deg, ${alpha(theme.palette.action.hover, 0.5)} 25%, ${alpha(theme.palette.action.hover, 0.8)} 50%, ${alpha(theme.palette.action.hover, 0.5)} 75%)`,
                backgroundSize: '200% 100%',
                animation: `${shimmer} 1.5s ease-in-out infinite`,
              }}
            />
          ))}
        </Stack>
      ) : jobs.length === 0 ? (
        <Box sx={{ py: 6, textAlign: 'center' }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: '50%',
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 2,
            }}
          >
            <WorkIcon sx={{ fontSize: 28, color: 'text.secondary' }} />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            No jobs yet. Run your first report to get started.
          </Typography>
          <Button
            variant="outlined"
            size="small"
            onClick={() => handleNavigate('/setup/wizard', 'Open setup wizard')}
            sx={{ borderRadius: 1 }}
          >
            Run First Report
          </Button>
        </Box>
      ) : (
        <Stack>
          {jobs.slice(0, 5).map((job, index) => (
            <Grow key={job.id} in timeout={300 + index * 100}>
              <JobListItem
                status={job.status}
                data-testid={`dashboard-job-${job.id}`}
                onClick={() =>
                  handleNavigate('/jobs', 'Open jobs', { jobId: job.id })
                }
              >
                <Box className="status-dot" />
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="body2" fontWeight={600} noWrap>
                    {job.template_name || job.templateName || job.template_id?.slice(0, 12)}
                  </Typography>
                  <Typography variant="caption" color="text.tertiary">
                    {new Date(job.created_at || job.createdAt).toLocaleString()}
                  </Typography>
                </Box>
                <Chip
                  label={job.status}
                  size="small"
                  data-testid={`job-status-${job.status}`}
                  sx={{
                    height: 24,
                    fontWeight: 600,
                    textTransform: 'capitalize',
                    fontSize: '12px',
                    bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                    color: 'text.secondary',
                  }}
                />
                <ArrowForwardIcon
                  className="job-arrow"
                  sx={{
                    fontSize: 16,
                    color: 'text.tertiary',
                    opacity: 0,
                    transform: 'translateX(-4px)',
                    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                  }}
                />
              </JobListItem>
            </Grow>
          ))}
        </Stack>
      )}
    </GlassCard>
  )
}
