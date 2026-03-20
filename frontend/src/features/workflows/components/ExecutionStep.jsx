/**
 * ExecutionStep — single step card within the execution viewer.
 */
import { useState } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Button,
  Stack,
  Chip,
  Collapse,
  CircularProgress,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Replay as ReplayIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Timer as TimerIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import {
  StepCard,
  LogContainer,
  LogLine,
  StatusChip,
  TimelineConnector,
  STATUS_CONFIG,
  formatDuration,
  formatTimestamp,
} from './ExecutionViewerStyles'

export default function ExecutionStep({ step, isLast, onRetry }) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(step.status === 'error')
  const statusConfig = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending
  const StatusIcon = statusConfig.icon

  return (
    <Box sx={{ position: 'relative' }}>
      {!isLast && <TimelineConnector />}

      <StepCard elevation={0} status={step.status}>
        <Stack direction="row" alignItems="flex-start" spacing={1.5}>
          {/* Status Icon */}
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: alpha(theme.palette[statusConfig.color]?.main || neutral[500], 0.15),
            }}
          >
            {step.status === 'running' ? (
              <CircularProgress size={16} color={statusConfig.color} />
            ) : (
              <StatusIcon
                sx={{
                  fontSize: 18,
                  color: `${statusConfig.color}.main`,
                }}
              />
            )}
          </Box>

          {/* Step Info */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {step.name}
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1}>
                {step.duration && (
                  <Chip
                    icon={<TimerIcon sx={{ fontSize: 12 }} />}
                    label={formatDuration(step.duration)}
                    size="small"
                    variant="outlined"
                    sx={{ height: 20, fontSize: '10px' }}
                  />
                )}
                <StatusChip
                  label={statusConfig.label}
                  size="small"
                  sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                />
              </Stack>
            </Stack>

            <Typography variant="caption" color="text.secondary">
              {step.nodeType} • Started: {formatTimestamp(step.startedAt)}
            </Typography>

            {step.error && (
              <Alert severity="error" sx={{ mt: 1, py: 0, fontSize: '0.75rem' }}>
                {step.error}
              </Alert>
            )}

            {(step.logs?.length > 0 || step.output) && (
              <Button
                size="small"
                onClick={() => setExpanded(!expanded)}
                endIcon={expanded ? <CollapseIcon /> : <ExpandIcon />}
                sx={{ mt: 1, fontSize: '12px', textTransform: 'none' }}
              >
                {expanded ? 'Hide Details' : 'Show Details'}
              </Button>
            )}

            <Collapse in={expanded}>
              {step.logs?.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, mb: 0.5, display: 'block' }}>
                    Logs
                  </Typography>
                  <LogContainer>
                    {step.logs.map((log, i) => (
                      <LogLine key={i} level={log.level}>
                        <span style={{ opacity: 0.5 }}>[{formatTimestamp(log.timestamp)}]</span>{' '}
                        {log.message}
                      </LogLine>
                    ))}
                  </LogContainer>
                </Box>
              )}

              {step.output && (
                <Box sx={{ mt: 1.5 }}>
                  <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      Output
                    </Typography>
                    <Tooltip title="Copy output">
                      <IconButton
                        size="small"
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(step.output, null, 2))}
                      >
                        <CopyIcon sx={{ fontSize: 14 }} />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                  <LogContainer>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(step.output, null, 2)}
                    </pre>
                  </LogContainer>
                </Box>
              )}

              {step.status === 'error' && onRetry && (
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<ReplayIcon />}
                  onClick={() => onRetry(step.id)}
                  sx={{ mt: 1.5 }}
                >
                  Retry This Step
                </Button>
              )}
            </Collapse>
          </Box>
        </Stack>
      </StepCard>
    </Box>
  )
}
