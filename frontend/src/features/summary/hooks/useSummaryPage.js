/**
 * Custom hook for Summary Page state and actions.
 */
import { useState, useEffect, useCallback } from 'react';
import useSummaryStore from '@/stores/summaryStore';
import useSharedData from '@/hooks/useSharedData';
import useCrossPageActions from '@/hooks/useCrossPageActions';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';
import { useToast } from '@/components/ToastProvider.jsx';
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance';
import { getReportHistory } from '@/api/client';

export function useSummaryPage() {
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
      intent: { action: 'generate_summary' },
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
      intent: { action: 'queue_summary' },
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

  const handleLoadReportRun = useCallback(
    (run) => {
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
    },
    [toast]
  );

  return {
    // Store state
    summary,
    history,
    loading,
    error,
    // Local state
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
    loadingReports,
    // Handlers
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
  };
}
