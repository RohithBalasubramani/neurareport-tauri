/**
 * Executions sidebar for WorkflowBuilderPage
 */
import React from 'react'
import {
  Box,
  Typography,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Stop as StopIcon,
  Refresh as RetryIcon,
} from '@mui/icons-material'
import { SidebarContainer, ExecutionCard } from './WorkflowStyledComponents'

export default function ExecutionsSidebar({
  executions,
  onCancelExecution,
  onRetryExecution,
}) {
  const theme = useTheme()

  return (
    <SidebarContainer>
      <Box sx={{ p: 2, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Executions
        </Typography>
      </Box>
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {executions.length > 0 ? (
          executions.map((exec) => (
            <ExecutionCard key={exec.id} status={exec.status} variant="outlined">
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {exec.status}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(exec.started_at).toLocaleString()}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {exec.status === 'running' && (
                    <IconButton
                      size="small"
                      onClick={() => onCancelExecution(exec.id)}
                    >
                      <StopIcon fontSize="small" />
                    </IconButton>
                  )}
                  {exec.status === 'failed' && (
                    <IconButton
                      size="small"
                      onClick={() => onRetryExecution(exec.id)}
                    >
                      <RetryIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>
              </Box>
            </ExecutionCard>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
            No executions yet
          </Typography>
        )}
      </Box>
    </SidebarContainer>
  )
}
