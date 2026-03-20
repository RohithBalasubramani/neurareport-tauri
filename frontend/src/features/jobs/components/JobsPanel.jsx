import {
  Drawer,
  Box,
  Stack,
  Typography,
  IconButton,
  Chip,
  LinearProgress,
  Divider,
  Tooltip,
  Button,
  Alert,
} from '@mui/material'
import { alpha } from '@mui/material'
import { neutral } from '@/app/theme'
import CloseIcon from '@mui/icons-material/Close'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import { useJobsPanel } from '../hooks/useJobsPanel'
import JobCard from './JobCard'

const STATUS_FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
]

export default function JobsPanel({ open, onClose }) {
  const {
    statusFilter,
    filteredJobs,
    activeCount,
    showEmptyState,
    connectionLookup,
    isLoading,
    isFetching,
    error,
    handleClosePanel,
    handleFilterChange,
    handleRetry,
    onJobNavigate,
    onSetupNavigate,
    handleCancelJob,
    handleForceCancelJob,
  } = useJobsPanel({ onClose })

  const emptyDescription =
    statusFilter === 'all'
      ? 'Jobs launched from the Reports page will appear here so you can check progress without leaving your work.'
      : 'No jobs match the selected filter. Try another status or start a new run.'

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={handleClosePanel}
      PaperProps={{
        sx: {
          backgroundColor: (theme) => theme.palette.mode === 'dark' ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(12px)',
        },
      }}
    >
      <Box
        sx={{
          width: { xs: '100vw', sm: 420 },
          maxWidth: '100vw',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        <Stack spacing={2}>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Box>
              <Typography variant="h6">Background Jobs</Typography>
              <Typography variant="body2" color="text.secondary">
                {activeCount ? `${activeCount} active` : 'No active jobs'}
              </Typography>
            </Box>
            <IconButton onClick={handleClosePanel} aria-label="Close jobs panel">
              <CloseIcon />
            </IconButton>
          </Stack>
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            flexWrap="wrap"
            data-testid="jobs-filter-group"
          >
            <Typography variant="body2" color="text.secondary">
              Status:
            </Typography>
            {STATUS_FILTERS.map((filter) => (
              <Chip
                key={filter.value}
                size="small"
                label={filter.label}
                sx={statusFilter === filter.value ? { bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' } : undefined}
                variant={statusFilter === filter.value ? 'filled' : 'outlined'}
                onClick={() => handleFilterChange(filter.value)}
                data-testid={`jobs-filter-${filter.value}`}
              />
            ))}
          </Stack>
          {error && (
            <Alert
              severity="error"
              action={
                <Button color="inherit" size="small" onClick={handleRetry}>
                  Retry
                </Button>
              }
            >
              Failed to load jobs: {error.message || String(error)}
            </Alert>
          )}
          {(isLoading || isFetching) && <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }} aria-label="Loading jobs" />}
        </Stack>
        <Divider />
        {showEmptyState ? (
          <EmptyState
            title="No jobs to display"
            description={emptyDescription}
            action={
              statusFilter !== 'all' ? (
                <Button size="small" variant="outlined" onClick={() => handleFilterChange('all')}>
                  Clear filters
                </Button>
              ) : null
            }
          />
        ) : (
          <Stack
            spacing={2}
            sx={{ flex: 1, overflowY: 'auto', pr: 1 }}
            data-testid="jobs-list"
          >
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onNavigate={onJobNavigate}
                onSetupNavigate={onSetupNavigate}
                connectionName={connectionLookup.get(job.connectionId)}
                onCancel={handleCancelJob}
                onForceCancel={handleForceCancelJob}
              />
            ))}
            {!filteredJobs.length && (
              <Tooltip title="Jobs refresh automatically every few seconds" arrow>
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  No jobs yet. Run a report to see progress here.
                </Typography>
              </Tooltip>
            )}
          </Stack>
        )}
      </Box>
    </Drawer>
  )
}
