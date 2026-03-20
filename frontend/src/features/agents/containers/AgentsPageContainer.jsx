/**
 * AI Agents Page Container
 * Interface for running AI agents (research, data analysis, email, content, proofreading, report analyst).
 */
import {
  Box,
  Typography,
  CardContent,
  Grid,
  Alert,
  useTheme,
  alpha,
} from '@mui/material'
import {
  History as HistoryIcon,
  SmartToy as AgentIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { useAgentsData } from '../hooks/useAgentsData'
import {
  PageContainer,
  Header,
  ContentArea,
  MainPanel,
  AgentCard,
  ActionButton,
  AGENTS,
} from '../components/AgentsStyledComponents'
import AgentForm from '../components/AgentForm'
import AgentResultPanel from '../components/AgentResultPanel'
import AgentHistorySidebar from '../components/AgentHistorySidebar'
import GenerateReportDialog from '../components/GenerateReportDialog'

export default function AgentsPageContainer() {
  const theme = useTheme()
  const {
    tasks,
    executing,
    error,
    connections,
    templates,
    selectedConnectionId,
    selectedAgent,
    formData,
    showHistory,
    result,
    recentRuns,
    runsLoading,
    generateDialogOpen,
    resultRef,
    handleSelectAgent,
    handleFieldChange,
    handleRun,
    handleCopyResult,
    handleToggleHistory,
    isFormValid,
    setSelectedConnectionId,
    setResult,
    setSelectedAgent,
    setGenerateDialogOpen,
    handleGenerateReport,
  } = useAgentsData()

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <AgentIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI Agents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Specialized AI agents for research, analysis, writing, and more
              </Typography>
            </Box>
          </Box>
          <ActionButton
            startIcon={<HistoryIcon />}
            onClick={handleToggleHistory}
            variant={showHistory ? 'contained' : 'outlined'}
          >
            History ({tasks.length})
          </ActionButton>
        </Box>
      </Header>

      <ContentArea>
        <MainPanel>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
            Select Agent
          </Typography>
          <Grid container spacing={2} sx={{ mb: 4 }}>
            {AGENTS.map((agent) => (
              <Grid item xs={12} sm={6} md={4} key={agent.type}>
                <AgentCard
                  selected={selectedAgent?.type === agent.type}
                  onClick={() => handleSelectAgent(agent)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                        }}
                      >
                        <agent.icon color="inherit" sx={{ color: 'text.secondary' }} />
                      </Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {agent.name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {agent.description}
                    </Typography>
                  </CardContent>
                </AgentCard>
              </Grid>
            ))}
          </Grid>

          {selectedAgent && (
            <>
              <AgentForm
                selectedAgent={selectedAgent}
                formData={formData}
                executing={executing}
                recentRuns={recentRuns}
                runsLoading={runsLoading}
                selectedConnectionId={selectedConnectionId}
                onFieldChange={handleFieldChange}
                onConnectionChange={setSelectedConnectionId}
                onRun={handleRun}
                isFormValid={isFormValid()}
              />

              <AgentResultPanel
                result={result}
                selectedAgent={selectedAgent}
                resultRef={resultRef}
                onCopyResult={handleCopyResult}
                onGenerateReport={() => setGenerateDialogOpen(true)}
              />
            </>
          )}
        </MainPanel>

        {showHistory && (
          <AgentHistorySidebar
            tasks={tasks}
            result={result}
            resultRef={resultRef}
            onSelectAgent={setSelectedAgent}
            onSelectResult={setResult}
          />
        )}
      </ContentArea>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      <GenerateReportDialog
        open={generateDialogOpen}
        onClose={() => setGenerateDialogOpen(false)}
        taskId={result?.task_id}
        templates={templates}
        connections={connections}
        onGenerate={handleGenerateReport}
      />
    </PageContainer>
  )
}
