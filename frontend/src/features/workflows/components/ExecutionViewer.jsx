/**
 * Execution Viewer Component
 * Real-time workflow execution monitoring with logs and status tracking.
 */
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Stack,
  LinearProgress,
  Alert,
} from '@mui/material'
import {
  Close as CloseIcon,
  Loop as RunningIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
} from '@mui/icons-material'
import {
  ViewerContainer,
  ViewerHeader,
  ViewerContent,
  STATUS_CONFIG,
  formatDuration,
} from './ExecutionViewerStyles'
import ExecutionStep from './ExecutionStep'
import ExecutionStatusBar from './ExecutionStatusBar'
import { useExecutionViewer } from '../hooks/useExecutionViewer'

export default function ExecutionViewer({
  execution = null,
  onStop, onPause, onResume, onRetry, onRetryStep,
  onDownloadLogs, onClose, onFullscreen,
}) {
  const { logsEndRef, progress, stats } = useExecutionViewer(execution)

  if (!execution) {
    return (
      <ViewerContainer>
        <ViewerHeader>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Execution Viewer</Typography>
          <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
        </ViewerHeader>
        <ViewerContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <RunningIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">No execution selected</Typography>
            <Typography variant="caption" color="text.disabled">Run a workflow to see execution details</Typography>
          </Box>
        </ViewerContent>
      </ViewerContainer>
    )
  }

  const overallStatus = STATUS_CONFIG[execution.status] || STATUS_CONFIG.pending
  const OverallIcon = overallStatus.icon

  return (
    <ViewerContainer>
      <ViewerHeader>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <OverallIcon sx={{ color: `${overallStatus.color}.main`, fontSize: 24 }} />
          <Box>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              {execution.workflowName || 'Workflow Execution'}
            </Typography>
            <Typography variant="caption" color="text.secondary">ID: {execution.id}</Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title="Download logs">
            <IconButton size="small" onClick={onDownloadLogs}><DownloadIcon fontSize="small" /></IconButton>
          </Tooltip>
          {onFullscreen && (
            <Tooltip title="Fullscreen">
              <IconButton size="small" onClick={onFullscreen}><FullscreenIcon fontSize="small" /></IconButton>
            </Tooltip>
          )}
          <IconButton size="small" onClick={onClose}><CloseIcon fontSize="small" /></IconButton>
        </Stack>
      </ViewerHeader>

      {execution.status === 'running' && <LinearProgress variant="determinate" value={progress} />}

      <ExecutionStatusBar
        execution={execution}
        overallStatus={overallStatus}
        stats={stats}
        onStop={onStop}
        onPause={onPause}
        onResume={onResume}
        onRetry={onRetry}
      />

      <ViewerContent>
        {execution.steps?.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">Waiting for execution to start...</Typography>
          </Box>
        ) : (
          <>
            {execution.steps.map((step, index) => (
              <ExecutionStep
                key={step.id}
                step={step}
                isLast={index === execution.steps.length - 1}
                onRetry={onRetryStep}
              />
            ))}
            <div ref={logsEndRef} />
          </>
        )}

        {execution.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Execution Error</Typography>
            {execution.error}
          </Alert>
        )}

        {execution.status === 'success' && (
          <Alert severity="success" sx={{ mt: 2 }}>
            Workflow completed successfully in {formatDuration(execution.duration)}
          </Alert>
        )}
      </ViewerContent>
    </ViewerContainer>
  )
}
