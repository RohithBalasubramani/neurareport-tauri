/**
 * Executive Summary Generation Page
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  Divider,
  Slider,
  Tooltip,
  Collapse,
  Stack,
  alpha,
} from '@mui/material';
import {
  AutoAwesome as SummaryIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import useSummaryStore from '@/stores/summaryStore';
import useSharedData from '@/hooks/useSharedData';
import useCrossPageActions from '@/hooks/useCrossPageActions';
import SendToMenu from '@/components/common/SendToMenu';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';
import { useToast } from '@/components/ToastProvider.jsx';
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance';
import ConfirmModal from '@/components/Modal/ConfirmModal';
import AiUsageNotice from '@/components/ai/AiUsageNotice';
import ConnectionSelector from '@/components/common/ConnectionSelector';
import { neutral, palette } from '@/app/theme';
import { getReportHistory } from '@/api/client';

const TONE_OPTIONS = [
  { value: 'formal', label: 'Formal', description: 'Professional, business-appropriate tone' },
  { value: 'conversational', label: 'Conversational', description: 'Friendly, easy-to-read tone' },
  { value: 'technical', label: 'Technical', description: 'Detailed, precise terminology' },
];

const FOCUS_SUGGESTIONS = [
  'Key findings',
  'Financial metrics',
  'Trends',
  'Recommendations',
  'Risks',
  'Opportunities',
  'Performance',
  'Growth',
];

export default function SummaryPage() {
  const {
    summary,
    history,
    loading,
    error,
    generateSummary,
    queueSummary,
    clearSummary,
    clearHistory,
    reset,
  } = useSummaryStore();

  const { connections, activeConnectionId } = useSharedData();
  const { registerOutput } = useCrossPageActions(FeatureKey.SUMMARY);

  const [content, setContent] = useState('');
  const [selectedConnectionId, setSelectedConnectionId] = useState('');
  const [tone, setTone] = useState('formal');
  const [maxSentences, setMaxSentences] = useState(5);
  const [focusAreas, setFocusAreas] = useState([]);
  const [customFocus, setCustomFocus] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [copied, setCopied] = useState(false);
  const [queueing, setQueueing] = useState(false);
  const [queuedJobId, setQueuedJobId] = useState(null);
  const [clearHistoryConfirmOpen, setClearHistoryConfirmOpen] = useState(false);
  const [reportRuns, setReportRuns] = useState([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const toast = useToast();
  const navigate = useNavigateInteraction();
  const { execute } = useInteraction();
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'summary', ...intent } }),
    [navigate]
  );
  const executeUI = useCallback(
    (label, action, intent = {}) =>
      execute({
        type: InteractionType.EXECUTE,
        label,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: { source: 'summary', ...intent },
        action,
      }),
    [execute]
  );

  useEffect(() => {
    return () => reset();
  }, [reset]);

  // Fetch recent report runs for "Load from Report" feature
  useEffect(() => {
    let cancelled = false;
    const fetchRuns = async () => {
      setLoadingReports(true);
      try {
        const result = await getReportHistory({ limit: 20, status: 'succeeded' });
        if (!cancelled) {
          setReportRuns(result?.history || []);
        }
      } catch (err) {
        console.error('Failed to fetch report runs:', err);
      } finally {
        if (!cancelled) setLoadingReports(false);
      }
    };
    fetchRuns();
    return () => { cancelled = true; };
  }, []);

  const handleGenerate = async () => {
    if (!content.trim()) return;
    setQueuedJobId(null);
    // Validate content length
    const trimmedContent = content.trim();
    if (trimmedContent.length < 50) {
      toast.show('Content is too short. Please provide at least 50 characters.', 'error');
      return;
    }
    if (trimmedContent.length > 50000) {
      toast.show('Content exceeds maximum length of 50,000 characters.', 'error');
      return;
    }
    await execute({
      type: InteractionType.GENERATE,
      label: 'Generate summary',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        action: 'generate_summary',
      },
      action: async () => {
        const result = await generateSummary({
          content: trimmedContent,
          tone,
          maxSentences,
          focusAreas: focusAreas.length > 0 ? focusAreas : undefined,
        });
        if (!result) {
          throw new Error('Summary generation failed');
        }
        registerOutput({
          type: OutputType.TEXT,
          title: `Executive Summary (${tone})`,
          summary: (typeof result === 'string' ? result : '').substring(0, 200),
          data: typeof result === 'string' ? result : JSON.stringify(result),
          format: 'text',
        });
        return result;
      },
    });
  };

  const handleQueue = async () => {
    if (!content.trim()) return;
    setQueuedJobId(null);
    // Validate content length
    const trimmedContent = content.trim();
    if (trimmedContent.length < 50) {
      toast.show('Content is too short. Please provide at least 50 characters.', 'error');
      return;
    }
    if (trimmedContent.length > 50000) {
      toast.show('Content exceeds maximum length of 50,000 characters.', 'error');
      return;
    }
    await execute({
      type: InteractionType.GENERATE,
      label: 'Queue summary',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        action: 'queue_summary',
      },
      action: async () => {
        setQueueing(true);
        try {
          const response = await queueSummary({
            content: trimmedContent,
            tone,
            maxSentences,
            focusAreas: focusAreas.length > 0 ? focusAreas : undefined,
          });
          if (response?.job_id) {
            setQueuedJobId(response.job_id);
            toast.show('Summary queued. Track progress in Jobs.', 'success');
          } else {
            toast.show('Failed to queue summary job.', 'error');
            throw new Error('Failed to queue summary job');
          }
          return response;
        } finally {
          setQueueing(false);
        }
      },
    });
  };

  const handleToggleHistory = useCallback(
    () =>
      executeUI('Toggle summary history', () => {
        setShowHistory((prev) => !prev);
      }),
    [executeUI]
  );

  const handleOpenClearHistory = useCallback(
    () =>
      executeUI('Open clear history confirmation', () => {
        setClearHistoryConfirmOpen(true);
      }),
    [executeUI]
  );

  const handleCloseClearHistory = useCallback(
    () =>
      executeUI('Close clear history confirmation', () => {
        setClearHistoryConfirmOpen(false);
      }),
    [executeUI]
  );

  const handleAddFocus = useCallback(
    (focus) =>
      executeUI(
        'Add focus area',
        () => {
          if (focusAreas.length < 5 && !focusAreas.includes(focus)) {
            setFocusAreas([...focusAreas, focus]);
          }
        },
        { focus }
      ),
    [executeUI, focusAreas]
  );

  const handleRemoveFocus = useCallback(
    (focus) =>
      executeUI(
        'Remove focus area',
        () => {
          setFocusAreas(focusAreas.filter((f) => f !== focus));
        },
        { focus }
      ),
    [executeUI, focusAreas]
  );

  const handleAddCustomFocus = useCallback(
    () =>
      executeUI('Add custom focus area', () => {
        const trimmed = customFocus.trim();
        if (trimmed && focusAreas.length < 5 && !focusAreas.includes(trimmed)) {
          setFocusAreas([...focusAreas, trimmed]);
          setCustomFocus('');
        }
      }),
    [customFocus, executeUI, focusAreas]
  );

  const handleCopy = useCallback(
    () =>
      executeUI('Copy summary to clipboard', async () => {
        if (summary) {
          await navigator.clipboard.writeText(summary);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }
      }),
    [executeUI, summary]
  );

  const handleClearSummary = useCallback(
    () =>
      execute({
        type: InteractionType.DELETE,
        label: 'Clear summary output',
        reversibility: Reversibility.PARTIALLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: { source: 'summary', action: 'clear_summary' },
        action: () => clearSummary(),
      }),
    [clearSummary, execute]
  );

  const handleLoadFromHistory = useCallback(
    (item) =>
      executeUI(
        'Load summary from history',
        () => {
          setContent(item.contentPreview.replace('...', ''));
          setTone(item.tone);
          setMaxSentences(item.maxSentences);
          setFocusAreas(item.focusAreas || []);
        },
        { historyId: item.id }
      ),
    [executeUI]
  );

  const handleClearHistory = useCallback(
    () =>
      execute({
        type: InteractionType.DELETE,
        label: 'Clear summary history',
        reversibility: Reversibility.IRREVERSIBLE,
        requiresConfirmation: true,
        intent: { source: 'summary', action: 'clear_history' },
        action: () => {
          clearHistory();
          setClearHistoryConfirmOpen(false);
        },
      }),
    [clearHistory, execute]
  );

  const handleDismissError = useCallback(
    () =>
      executeUI('Dismiss summary error', () => {
        reset();
      }),
    [executeUI, reset]
  );

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

      {/* History Panel */}
      <Collapse in={showHistory}>
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Summaries</Typography>
            <Button size="small" onClick={handleOpenClearHistory} sx={{ color: 'text.secondary' }}>
              Clear All
            </Button>
          </Box>
          <Grid container spacing={2}>
            {history.map((item) => (
              <Grid size={{ xs: 12, md: 6 }} key={item.id}>
                <Card variant="outlined" sx={{ cursor: 'pointer' }} onClick={() => handleLoadFromHistory(item)}>
                  <CardContent sx={{ py: 1.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(item.createdAt).toLocaleString()} - {item.tone}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }} noWrap>
                      {item.summary?.substring(0, 150)}...
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Collapse>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Content to Summarize
            </Typography>

            {/* Load from existing report runs */}
            {reportRuns.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Load from Report Run</InputLabel>
                  <Select
                    value=""
                    label="Load from Report Run"
                    onChange={(e) => {
                      const run = reportRuns.find((r) => r.id === e.target.value);
                      if (run) {
                        const parts = [
                          `Report: ${run.templateName || 'Unknown'}`,
                          run.startDate && run.endDate ? `Period: ${run.startDate} to ${run.endDate}` : null,
                          run.connectionName ? `Connection: ${run.connectionName}` : null,
                          run.keyValues && Object.keys(run.keyValues).length > 0
                            ? `Parameters: ${Object.entries(run.keyValues).map(([k, v]) => `${k}=${v}`).join(', ')}`
                            : null,
                          run.artifacts?.html_url ? `\nReport content available at: ${run.artifacts.html_url}` : null,
                        ].filter(Boolean);
                        setContent(parts.join('\n'));
                        toast.show(`Loaded report "${run.templateName}" context`, 'success');
                      }
                    }}
                  >
                    {reportRuns.map((run) => (
                      <MenuItem key={run.id} value={run.id}>
                        <Box>
                          <Typography variant="body2">{run.templateName || 'Unknown Report'}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {run.createdAt ? new Date(run.createdAt).toLocaleDateString() : ''}
                            {run.connectionName ? ` \u2022 ${run.connectionName}` : ''}
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            )}

            <ConnectionSelector
              value={selectedConnectionId}
              onChange={setSelectedConnectionId}
              label="Pull from Connection (Optional)"
              size="small"
              showStatus
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={12}
              placeholder="Paste your document content, report text, or any content you want to summarize..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Typography variant="caption" color="text.secondary">
              {content.length} / 50,000 characters
            </Typography>

            <Divider sx={{ my: 2 }} />

            {/* Options */}
            <Typography variant="subtitle2" gutterBottom>
              Summary Options
            </Typography>

            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>Tone</InputLabel>
              <Select value={tone} label="Tone" onChange={(e) => setTone(e.target.value)}>
                {TONE_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    <Box>
                      <Typography variant="body2">{opt.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {opt.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Summary Length: {maxSentences} sentences
              </Typography>
              <Slider
                value={maxSentences}
                onChange={(e, val) => setMaxSentences(val)}
                min={2}
                max={15}
                marks={[
                  { value: 2, label: '2' },
                  { value: 5, label: '5' },
                  { value: 10, label: '10' },
                  { value: 15, label: '15' },
                ]}
                valueLabelDisplay="auto"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Focus Areas (optional, max 5)
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                {focusAreas.map((focus) => (
                  <Chip
                    key={focus}
                    label={focus}
                    size="small"
                    onDelete={() => handleRemoveFocus(focus)}
                    sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                {FOCUS_SUGGESTIONS.filter((f) => !focusAreas.includes(f)).map((focus) => (
                  <Chip
                    key={focus}
                    label={focus}
                    size="small"
                    variant="outlined"
                    onClick={() => handleAddFocus(focus)}
                    disabled={focusAreas.length >= 5}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  size="small"
                  placeholder="Add custom focus..."
                  value={customFocus}
                  onChange={(e) => setCustomFocus(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddCustomFocus()}
                  disabled={focusAreas.length >= 5}
                  sx={{ flex: 1 }}
                />
                <Button
                  variant="outlined"
                  size="small"
                  onClick={handleAddCustomFocus}
                  disabled={!customFocus.trim() || focusAreas.length >= 5}
                >
                  Add
                </Button>
              </Box>
            </Box>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SummaryIcon />}
                onClick={handleGenerate}
                disabled={!content.trim() || content.length < 10 || loading || queueing}
              >
                {loading ? 'Generating...' : 'Generate Summary'}
              </Button>
              <Button
                variant="outlined"
                fullWidth
                size="large"
                startIcon={queueing ? <CircularProgress size={20} color="inherit" /> : <ScheduleIcon />}
                onClick={handleQueue}
                disabled={!content.trim() || content.length < 10 || loading || queueing}
              >
                {queueing ? 'Queueing...' : 'Queue in Background'}
              </Button>
            </Stack>
          </Paper>
        </Grid>

        {/* Output Section */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Generated Summary</Typography>
              {summary && (
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                  <SendToMenu
                    outputType={OutputType.TEXT}
                    payload={{
                      title: `Executive Summary (${tone})`,
                      content: summary,
                    }}
                    sourceFeature={FeatureKey.SUMMARY}
                  />
                  <Tooltip title={copied ? 'Copied!' : 'Copy to clipboard'}>
                    <IconButton size="small" onClick={handleCopy} aria-label="Copy to clipboard">
                      <CopyIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Clear">
                    <IconButton size="small" onClick={handleClearSummary} aria-label="Clear summary">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              )}
            </Box>

            {summary ? (
              <Box sx={{ flex: 1 }}>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    bgcolor: neutral[50],
                    minHeight: 200,
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  <Typography variant="body1">{summary}</Typography>
                </Paper>
                <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label={`Tone: ${tone}`} size="small" variant="outlined" />
                  <Chip label={`${maxSentences} sentences`} size="small" variant="outlined" />
                  {focusAreas.map((f) => (
                    <Chip key={f} label={f} size="small" variant="outlined" sx={{ borderColor: 'divider', color: 'text.secondary' }} />
                  ))}
                </Box>
              </Box>
            ) : (
              <Box
                sx={{
                  flex: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: 300,
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <SummaryIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography color="text.secondary">
                    Enter your content and click "Generate Summary" to create an executive summary
                  </Typography>
                </Box>
              </Box>
            )}
          </Paper>
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
