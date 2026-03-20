/**
 * Empty state when no workflow selected
 */
import React from 'react'
import {
  Box,
  Typography,
  Paper,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Add as AddIcon,
  AccountTree as WorkflowIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { EmptyState, ActionButton } from './WorkflowStyledComponents'

export default function WorkflowEmptyState({
  workflows,
  onOpenCreateDialog,
  onSelectWorkflow,
}) {
  const theme = useTheme()

  return (
    <EmptyState sx={{ width: '100%' }}>
      <WorkflowIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
        No Workflow Selected
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Create a new workflow to automate your processes.
      </Typography>
      <ActionButton
        variant="contained"
        startIcon={<AddIcon />}
        onClick={onOpenCreateDialog}
      >
        Create Workflow
      </ActionButton>

      {workflows.length > 0 && (
        <Box sx={{ mt: 4, width: '100%', maxWidth: 400 }}>
          <Typography variant="subtitle2" sx={{ mb: 2 }}>
            Recent Workflows
          </Typography>
          {workflows.slice(0, 5).map((wf) => (
            <Paper
              key={wf.id}
              sx={{
                p: 2,
                mb: 1,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50] },
              }}
              variant="outlined"
              onClick={() => onSelectWorkflow(wf.id)}
            >
              <WorkflowIcon sx={{ color: 'text.secondary' }} />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {wf.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {wf.nodes?.length || 0} nodes
                </Typography>
              </Box>
            </Paper>
          ))}
        </Box>
      )}
    </EmptyState>
  )
}
