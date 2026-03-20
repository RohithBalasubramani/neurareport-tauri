/**
 * Agent Configuration Form Component
 */
import {
  Box,
  Grid,
  CircularProgress,
  Paper,
  Typography,
  Divider,
} from '@mui/material'
import { PlayArrow as RunIcon } from '@mui/icons-material'
import { ActionButton } from './AgentsStyledComponents'
import AgentFieldRenderer from './AgentFieldRenderer'

export default function AgentForm({
  selectedAgent,
  formData,
  executing,
  recentRuns,
  runsLoading,
  selectedConnectionId,
  onFieldChange,
  onConnectionChange,
  onRun,
  isFormValid,
}) {
  if (!selectedAgent) return null

  return (
    <>
      <Divider sx={{ mb: 3 }} />
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
        {selectedAgent.name} Configuration
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Grid container spacing={2}>
          {selectedAgent.fields.map((field) => (
            <AgentFieldRenderer
              key={field.name}
              field={field}
              selectedAgent={selectedAgent}
              formData={formData}
              recentRuns={recentRuns}
              runsLoading={runsLoading}
              selectedConnectionId={selectedConnectionId}
              onFieldChange={onFieldChange}
              onConnectionChange={onConnectionChange}
            />
          ))}
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <ActionButton
            variant="contained"
            size="large"
            startIcon={executing ? <CircularProgress size={20} color="inherit" /> : <RunIcon />}
            onClick={onRun}
            disabled={!isFormValid || executing}
          >
            {executing ? 'Running...' : `Run ${selectedAgent.name}`}
          </ActionButton>
        </Box>
      </Paper>
    </>
  )
}
