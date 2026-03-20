import { useMemo } from 'react'
import {
  Alert,
  Box,
  Chip,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'

import { useTrackedJobs } from '@/hooks/useJobs'
import { JOB_STATUS_COLORS } from '../../utils/generateFeatureUtils'

export default function ProgressSection({ generation }) {
  const trackedJobIds = useMemo(
    () => generation.items.map((item) => item.jobId).filter(Boolean),
    [generation.items],
  )
  const { jobsById } = useTrackedJobs(trackedJobIds)

  return (
    <Box>
      <Divider sx={{ my: 2 }} />
      <Typography variant="subtitle1">Progress</Typography>
      {generation.items.length > 0 && (
        <Alert severity="info" sx={{ mt: 1 }}>
          Reports continue running in the background. Open the Jobs panel from Notifications in the header to monitor status and download results.
        </Alert>
      )}
      <Stack spacing={1.5} sx={{ mt: 1.5 }}>
        {generation.items.map((item) => {
          const jobDetails = item.jobId ? jobsById?.[item.jobId] : null
          const rawStatus = (jobDetails?.status || item.status || 'queued').toLowerCase()
          const statusLabel = rawStatus.charAt(0).toUpperCase() + rawStatus.slice(1)
          const jobProgress =
            typeof jobDetails?.progress === 'number'
              ? jobDetails.progress
              : typeof item.progress === 'number'
                ? item.progress
                : null
          const clampedProgress =
            typeof jobProgress === 'number' && Number.isFinite(jobProgress)
              ? Math.min(100, Math.max(0, jobProgress))
              : null
          const chipColor = JOB_STATUS_COLORS[rawStatus] || 'default'
          const progressVariant = clampedProgress == null ? 'indeterminate' : 'determinate'
          const errorMessage = jobDetails?.error || item.error
          return (
            <Box
              key={item.id}
              sx={{
                p: 1.5,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: 'background.paper',
              }}
            >
              <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={{ xs: 0.5, sm: 1 }}>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {item.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.jobId ? `Job ID: ${item.jobId}` : 'Preparing job...'}
                  </Typography>
                </Box>
                <Chip
                  size="small"
                  label={statusLabel}
                  color={chipColor === 'default' ? 'default' : chipColor}
                  variant={chipColor === 'default' ? 'outlined' : 'filled'}
                />
              </Stack>
              <LinearProgress
                variant={progressVariant}
                value={progressVariant === 'determinate' ? clampedProgress : undefined}
                sx={{ mt: 1 }}
                aria-label={`${item.name} progress`}
              />
              {errorMessage ? (
                <Alert severity="error" sx={{ mt: 1 }}>
                  {errorMessage}
                </Alert>
              ) : (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  Keep an eye on the Jobs panel to see when this run finishes and download the files.
                </Typography>
              )}
            </Box>
          )
        })}
        {!generation.items.length && <Typography variant="body2" color="text.secondary">No runs yet</Typography>}
      </Stack>
    </Box>
  )
}
