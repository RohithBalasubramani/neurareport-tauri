/**
 * Toolbar for WorkflowBuilderPage
 */
import React from 'react'
import {
  Box,
  Typography,
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  AccountTree as WorkflowIcon,
  Save as SaveIcon,
  PlayArrow as RunIcon,
  Stop as StopIcon,
  History as HistoryIcon,
} from '@mui/icons-material'
import { Toolbar, ActionButton } from './WorkflowStyledComponents'

export default function WorkflowToolbar({
  currentWorkflow,
  workflowNodes,
  executing,
  onToggleExecutions,
  onExecute,
  onSave,
  onOpenCreateDialog,
}) {
  return (
    <Toolbar>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <WorkflowIcon sx={{ color: 'text.secondary' }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          {currentWorkflow?.name || 'Workflows'}
        </Typography>
        {currentWorkflow && (
          <Chip
            size="small"
            label={`${workflowNodes.length} nodes`}
            sx={{ borderRadius: 1 }}
          />
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 1 }}>
        {currentWorkflow ? (
          <>
            <ActionButton
              size="small"
              startIcon={<HistoryIcon />}
              onClick={onToggleExecutions}
            >
              Executions
            </ActionButton>
            <ActionButton
              size="small"
              variant="outlined"
              sx={{ color: 'text.secondary' }}
              startIcon={executing ? <StopIcon /> : <RunIcon />}
              onClick={onExecute}
              disabled={executing || workflowNodes.length === 0}
            >
              {executing ? 'Running...' : 'Run'}
            </ActionButton>
            <ActionButton
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              onClick={onSave}
            >
              Save
            </ActionButton>
          </>
        ) : (
          <ActionButton
            variant="contained"
            size="small"
            startIcon={<AddIcon />}
            onClick={onOpenCreateDialog}
          >
            New Workflow
          </ActionButton>
        )}
      </Box>
    </Toolbar>
  )
}
