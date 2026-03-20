/**
 * Reports Page — Clean workflow for report generation
 * Single-column layout: Design & Source -> Time Period -> Generate -> Recent Runs
 */
import { useCallback } from 'react'
import { Box, Container, Stack } from '@mui/material'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { useToast } from '@/components/ToastProvider'
import { useNavigateInteraction } from '@/components/ux/governance'
import PageHeader from '@/components/layout/PageHeader'
import SuccessCelebration, { useCelebration } from '@/components/SuccessCelebration'

// Hooks
import useReportConfig from '../hooks/useReportConfig'
import useReportDateRange from '../hooks/useReportDateRange'
import useReportDiscovery from '../hooks/useReportDiscovery'
import useReportGeneration from '../hooks/useReportGeneration'
import useReportHistory from '../hooks/useReportHistory'

// Components
import DesignSourceCard from '../components/DesignSourceCard'
import TimePeriodCard from '../components/TimePeriodCard'
import ActionBar from '../components/ActionBar'
import BatchDiscoverySection from '../components/BatchDiscoverySection'
import RecentRunsSection from '../components/RecentRunsSection'
import { SecondaryButton } from '../components/ReportsStyledComponents'

export default function ReportsPage() {
  const navigate = useNavigateInteraction()
  const toast = useToast()

  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'reports', ...intent } }),
    [navigate]
  )

  // Success celebration
  const { celebrating, celebrate, onComplete: onCelebrationComplete } = useCelebration()

  // Date range state (initialized first so key options can filter by dates)
  const dateRange = useReportDateRange()

  // Config: templates, connection, key filters (date-aware)
  const config = useReportConfig({
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
  })

  // Batch discovery
  const disc = useReportDiscovery({
    selectedTemplate: config.selectedTemplate,
    activeConnection: config.activeConnection,
    templates: config.templates,
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
    startTime: dateRange.startTime,
    endTime: dateRange.endTime,
    keyValues: config.keyValues,
  })

  // Report generation
  const gen = useReportGeneration({
    selectedTemplate: config.selectedTemplate,
    activeConnection: config.activeConnection,
    templates: config.templates,
    startDate: dateRange.startDate,
    endDate: dateRange.endDate,
    startTime: dateRange.startTime,
    endTime: dateRange.endTime,
    keyValues: config.keyValues,
    discovery: disc.discovery,
    selectedBatches: disc.selectedBatches,
    celebrate,
  })

  // Run history
  const history = useReportHistory()

  // Clear generation-related state on template change
  const handleTemplateChange = useCallback((event) => {
    config.handleTemplateChange(event)
    gen.setResult(null)
    disc.resetDiscovery()
  }, [config, gen, disc])

  return (
    <Box sx={{ minHeight: '100vh', p: 3, bgcolor: 'background.default' }}>
      <SuccessCelebration trigger={celebrating} onComplete={onCelebrationComplete} />
      <Container maxWidth="lg">
        <PageHeader
          title="Run a Report"
          description="Choose a design, set your date range, and generate a report."
          actions={
            <SecondaryButton
              variant="outlined"
              startIcon={<ScheduleIcon />}
              disabled={!config.selectedTemplate || gen.generating}
              onClick={() =>
                handleNavigate(`/schedules?template=${config.selectedTemplate}`, 'Open schedules', {
                  templateId: config.selectedTemplate,
                })
              }
            >
              Schedule
            </SecondaryButton>
          }
        />

        <Stack spacing={3}>
          <DesignSourceCard
            templates={config.templates}
            selectedTemplate={config.selectedTemplate}
            activeConnection={config.activeConnection}
            onTemplateChange={handleTemplateChange}
            onAiSelectTemplate={config.handleAiSelectTemplate}
            onConnectionChange={config.setActiveConnectionId}
            onNavigate={handleNavigate}
          />

          <TimePeriodCard
            startDate={dateRange.startDate}
            setStartDate={dateRange.setStartDate}
            endDate={dateRange.endDate}
            setEndDate={dateRange.setEndDate}
            startTime={dateRange.startTime}
            setStartTime={dateRange.setStartTime}
            endTime={dateRange.endTime}
            setEndTime={dateRange.setEndTime}
            datePreset={dateRange.datePreset}
            setDatePreset={dateRange.setDatePreset}
            handleDatePreset={dateRange.handleDatePreset}
            keyFields={config.keyFields}
            keyValues={config.keyValues}
            keyOptions={config.keyOptions}
            onKeyValueChange={config.handleKeyValueChange}
          />

          <ActionBar
            error={gen.error}
            generating={gen.generating}
            result={gen.result}
            selectedTemplate={config.selectedTemplate}
            activeConnection={config.activeConnection}
            onGenerate={gen.handleGenerate}
            onClearError={() => gen.setError(null)}
            onNavigate={handleNavigate}
          />

          <BatchDiscoverySection
            batchDiscoveryOpen={disc.batchDiscoveryOpen}
            onToggleOpen={() => disc.setBatchDiscoveryOpen((prev) => !prev)}
            discovering={disc.discovering}
            discovery={disc.discovery}
            selectedBatches={disc.selectedBatches}
            selectedTemplate={config.selectedTemplate}
            activeConnection={config.activeConnection}
            onDiscover={disc.handleDiscover}
            onToggleBatch={disc.toggleBatch}
            onSelectAll={disc.handleSelectAllBatches}
            onClear={disc.handleClearBatches}
          />

          <RecentRunsSection
            runHistory={history.runHistory}
            historyLoading={history.historyLoading}
            selectedRun={history.selectedRun}
            expandedRunId={history.expandedRunId}
            summaryLoading={history.summaryLoading}
            runSummary={history.runSummary}
            queueingSummary={history.queueingSummary}
            generatingDocx={gen.generatingDocx}
            onRefresh={history.fetchRunHistory}
            onSelectRun={history.handleSelectRun}
            onQueueSummary={history.handleQueueSummary}
            onGenerateDocx={(runId) => gen.handleGenerateDocx(runId, history.fetchRunHistory)}
            onNavigate={handleNavigate}
            toast={toast}
          />
        </Stack>
      </Container>
    </Box>
  )
}
