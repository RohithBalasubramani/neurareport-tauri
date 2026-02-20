import { useState, useCallback } from 'react'
import {
  Box, Typography, CircularProgress, Chip, IconButton, Collapse,
  Table, TableHead, TableRow, TableCell, TableBody,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import WorkIcon from '@mui/icons-material/Work'
import { GlassCard } from '@/styles/components'
import { getLoggerJobRuns } from '@/api/client'

const statusConfig = {
  running: { color: 'success', label: 'Running' },
  stopped: { color: 'default', label: 'Stopped' },
  paused: { color: 'warning', label: 'Paused' },
  error: { color: 'error', label: 'Error' },
}

const typeLabels = {
  continuous: 'Continuous',
  trigger: 'Trigger-based',
}

function formatMs(ms) {
  if (ms == null) return '—'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function formatInterval(ms) {
  if (ms == null) return '—'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(0)}s`
  return `${(ms / 60000).toFixed(1)}min`
}

export default function JobMonitor({ jobs = [], connectionId, loading }) {
  const [expandedJob, setExpandedJob] = useState(null)
  const [jobRuns, setJobRuns] = useState({})
  const [loadingRuns, setLoadingRuns] = useState(null)

  const toggleExpand = useCallback(async (jobId) => {
    if (expandedJob === jobId) {
      setExpandedJob(null)
      return
    }
    setExpandedJob(jobId)
    if (!jobRuns[jobId] && connectionId) {
      setLoadingRuns(jobId)
      try {
        const result = await getLoggerJobRuns(connectionId, jobId, 20)
        setJobRuns((prev) => ({ ...prev, [jobId]: result?.runs || [] }))
      } catch {
        setJobRuns((prev) => ({ ...prev, [jobId]: [] }))
      } finally {
        setLoadingRuns(null)
      }
    }
  }, [expandedJob, jobRuns, connectionId])

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (jobs.length === 0) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <WorkIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">No jobs found</Typography>
        <Typography variant="body2" color="text.secondary">
          This Logger database has no configured logging jobs.
        </Typography>
      </GlassCard>
    )
  }

  return (
    <Box>
      {jobs.map((job) => {
        const status = statusConfig[job.status] || statusConfig.stopped
        const runs = jobRuns[job.id] || []
        const isExpanded = expandedJob === job.id

        return (
          <GlassCard key={job.id} sx={{ mb: 2, '&:hover': { transform: 'none' } }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton
                  size="small"
                  onClick={() => toggleExpand(job.id)}
                  sx={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: '0.2s' }}
                >
                  <ExpandMoreIcon />
                </IconButton>
                <Box>
                  <Typography variant="subtitle1" fontWeight={600}>{job.name}</Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                    <Chip
                      label={typeLabels[job.job_type] || job.job_type}
                      size="small"
                      variant="outlined"
                    />
                    {job.interval_ms && (
                      <Chip label={`Every ${formatInterval(job.interval_ms)}`} size="small" variant="outlined" />
                    )}
                    {job.batch_size && (
                      <Chip label={`Batch: ${job.batch_size}`} size="small" variant="outlined" />
                    )}
                  </Box>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip label={status.label} color={status.color} size="small" />
                {job.enabled === false && <Chip label="Disabled" size="small" color="default" />}
              </Box>
            </Box>

            <Collapse in={isExpanded}>
              <Box sx={{ mt: 2, pl: 6 }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                  Recent Runs
                </Typography>
                {loadingRuns === job.id ? (
                  <CircularProgress size={20} />
                ) : runs.length > 0 ? (
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 600 }}>Started</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Duration</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Rows</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Reads</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Errors</TableCell>
                        <TableCell sx={{ fontWeight: 600 }}>Avg Latency</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {runs.map((run, i) => (
                        <TableRow key={i}>
                          <TableCell>{run.started_at ? new Date(run.started_at).toLocaleString() : '—'}</TableCell>
                          <TableCell>{formatMs(run.duration_ms)}</TableCell>
                          <TableCell>{run.rows_written ?? '—'}</TableCell>
                          <TableCell>{run.reads_count ?? '—'}</TableCell>
                          <TableCell>
                            {(run.read_errors || 0) + (run.write_errors || 0) > 0 ? (
                              <Chip
                                label={`${(run.read_errors || 0) + (run.write_errors || 0)}`}
                                size="small"
                                color="error"
                                variant="outlined"
                              />
                            ) : '0'}
                          </TableCell>
                          <TableCell>{run.avg_latency_ms != null ? `${run.avg_latency_ms}ms` : '—'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <Typography variant="body2" color="text.secondary">No runs recorded</Typography>
                )}
              </Box>
            </Collapse>
          </GlassCard>
        )
      })}
    </Box>
  )
}
