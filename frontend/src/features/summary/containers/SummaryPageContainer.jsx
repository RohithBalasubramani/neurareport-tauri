/**
 * Executive Summary Generation Page
 */
import React from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Grid,
} from '@mui/material';
import {
  AutoAwesome as SummaryIcon,
  History as HistoryIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import AiUsageNotice from '@/components/ai/AiUsageNotice';
import ConfirmModal from '@/components/modal/ConfirmModal';
import { useSummaryPage } from '../hooks/useSummaryPage';
import SummaryHistoryPanel from '../components/SummaryHistoryPanel';
import SummaryInputPanel from '../components/SummaryInputPanel';
import SummaryOutputPanel from '../components/SummaryOutputPanel';

export default function SummaryPage() {
  const {
    summary,
    history,
    loading,
    error,
    content,
    setContent,
    selectedConnectionId,
    setSelectedConnectionId,
    tone,
    setTone,
    maxSentences,
    setMaxSentences,
    focusAreas,
    customFocus,
    setCustomFocus,
    showHistory,
    copied,
    queueing,
    queuedJobId,
    clearHistoryConfirmOpen,
    reportRuns,
    handleNavigate,
    handleGenerate,
    handleQueue,
    handleToggleHistory,
    handleOpenClearHistory,
    handleCloseClearHistory,
    handleAddFocus,
    handleRemoveFocus,
    handleAddCustomFocus,
    handleCopy,
    handleClearSummary,
    handleLoadFromHistory,
    handleClearHistory,
    handleDismissError,
    handleLoadReportRun,
  } = useSummaryPage();

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SummaryIcon /> Executive Summary Generator
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Generate concise executive summaries from your content using AI
          </Typography>
        </Box>
        {history.length > 0 && (
          <Button
            variant="outlined"
            startIcon={showHistory ? <ExpandLessIcon /> : <HistoryIcon />}
            onClick={handleToggleHistory}
          >
            History ({history.length})
          </Button>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={handleDismissError}>
          {error}
        </Alert>
      )}

      {queuedJobId && (
        <Alert
          severity="info"
          sx={{ mb: 2 }}
          action={(
            <Button size="small" onClick={() => handleNavigate('/jobs', 'Open jobs')} sx={{ textTransform: 'none' }}>
              View Jobs
            </Button>
          )}
        >
          Summary queued in background. Job ID: {queuedJobId}
        </Alert>
      )}

      <AiUsageNotice
        title="AI summary"
        description="Summaries are generated from the text you provide. Review for accuracy before sharing."
        chips={[
          { label: 'Source: Pasted content', color: 'info', variant: 'outlined' },
          { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
          { label: 'Reversible: Output only', color: 'success', variant: 'outlined' },
        ]}
        dense
        sx={{ mb: 2 }}
      />

      <SummaryHistoryPanel
        showHistory={showHistory}
        history={history}
        onLoadFromHistory={handleLoadFromHistory}
        onOpenClearHistory={handleOpenClearHistory}
      />

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <SummaryInputPanel
            content={content}
            setContent={setContent}
            selectedConnectionId={selectedConnectionId}
            setSelectedConnectionId={setSelectedConnectionId}
            tone={tone}
            setTone={setTone}
            maxSentences={maxSentences}
            setMaxSentences={setMaxSentences}
            focusAreas={focusAreas}
            customFocus={customFocus}
            setCustomFocus={setCustomFocus}
            loading={loading}
            queueing={queueing}
            reportRuns={reportRuns}
            onGenerate={handleGenerate}
            onQueue={handleQueue}
            onAddFocus={handleAddFocus}
            onRemoveFocus={handleRemoveFocus}
            onAddCustomFocus={handleAddCustomFocus}
            onLoadReportRun={handleLoadReportRun}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <SummaryOutputPanel
            summary={summary}
            tone={tone}
            maxSentences={maxSentences}
            focusAreas={focusAreas}
            copied={copied}
            onCopy={handleCopy}
            onClear={handleClearSummary}
          />
        </Grid>
      </Grid>

      <ConfirmModal
        open={clearHistoryConfirmOpen}
        onClose={handleCloseClearHistory}
        onConfirm={handleClearHistory}
        title="Clear History"
        message="Are you sure you want to clear all summary history? This action cannot be undone."
        confirmLabel="Clear All"
        severity="warning"
      />
    </Box>
  );
}
