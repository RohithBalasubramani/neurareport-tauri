/**
 * Agent History Sidebar Component
 */
import {
  Box,
  Chip,
  Typography,
  List,
  ListItem,
  ListItemText,
  alpha,
  useTheme,
} from '@mui/material'
import { Sidebar, AGENTS } from './AgentsStyledComponents'

export default function AgentHistorySidebar({
  tasks,
  result,
  resultRef,
  onSelectAgent,
  onSelectResult,
}) {
  const theme = useTheme()

  return (
    <Sidebar>
      <Box sx={{ p: 2, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Task History
        </Typography>
      </Box>
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {tasks.length > 0 ? (
          <List>
            {tasks.map((task) => {
              const taskId = task.id || task.task_id
              const isSelected = (result?.id || result?.task_id) === taskId
              return (
                <ListItem
                  key={taskId}
                  divider
                  onClick={() => {
                    const agentDef = AGENTS.find((a) => a.type === task.agent_type)
                    if (agentDef) onSelectAgent(agentDef)
                    onSelectResult(task)
                    setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100)
                  }}
                  sx={{
                    cursor: 'pointer',
                    bgcolor: isSelected ? alpha(theme.palette.primary.main, 0.08) : 'transparent',
                    borderLeft: isSelected ? `3px solid ${theme.palette.primary.main}` : '3px solid transparent',
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.04),
                    },
                    transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
                  }}
                >
                  <ListItemText
                    primary={task.agent_type?.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    secondary={
                      <>
                        <Chip
                          size="small"
                          label={task.status}
                          color={task.status === 'completed' ? 'success' : task.status === 'failed' ? 'error' : 'default'}
                          sx={{ mr: 1 }}
                        />
                        {new Date(task.created_at).toLocaleString()}
                      </>
                    }
                  />
                </ListItem>
              )
            })}
          </List>
        ) : (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="text.secondary">No tasks yet</Typography>
          </Box>
        )}
      </Box>
    </Sidebar>
  )
}
