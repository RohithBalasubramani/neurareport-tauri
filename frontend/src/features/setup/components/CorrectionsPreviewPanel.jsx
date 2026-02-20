import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Alert, Box, Button, CircularProgress, LinearProgress, Stack, TextField, Typography } from '@mui/material';

import { runCorrectionsPreview } from '@/api/client';
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance';
import InfoTooltip from '@/components/common/InfoTooltip.jsx';
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx';

export default function CorrectionsPreviewPanel({
  templateId,
  templateKind = 'pdf',
  disabled,
  onCompleted,
  onInstructionsChange = () => {},
  initialInstructions = '',
  mappingOverride = {},
  sampleTokens = [],
  onSaveAndClose = () => {},
}) {
  const { execute } = useInteraction();
  const [instructions, setInstructions] = useState(initialInstructions || '');
  const latestInstructionsRef = useRef(initialInstructions || '');
  const [running, setRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [result, setResult] = useState(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const abortRef = useRef(null);

  const mappingSnapshot = useMemo(() => {
    if (!mappingOverride || typeof mappingOverride !== 'object') return {};
    const snapshot = {};
    for (const [token, value] of Object.entries(mappingOverride)) {
      if (!token) continue;
      if (value === undefined || value === null) continue;
      snapshot[token] = typeof value === 'string' ? value : String(value);
    }
    return snapshot;
  }, [mappingOverride]);

  const sampleTokensSnapshot = useMemo(
    () =>
      Array.from(
        new Set(
          (sampleTokens || [])
            .filter((token) => typeof token === 'string')
            .map((token) => token.trim())
            .filter(Boolean)
        )
      ),
    [sampleTokens]
  );

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    latestInstructionsRef.current = instructions;
  }, [instructions]);

  const flushInstructions = useCallback(() => {
    if (typeof onInstructionsChange !== 'function') return;
    onInstructionsChange(latestInstructionsRef.current);
  }, [onInstructionsChange]);

  useEffect(() => () => {
    flushInstructions();
  }, [flushInstructions]);

  useEffect(() => {
    const next = initialInstructions || '';
    setInstructions((prev) => (prev === next ? prev : next));
  }, [initialInstructions]);

  useEffect(() => {
    setAcknowledged(false);
  }, [instructions]);

  const handleRun = async () => {
    if (!templateId) {
      setErrorMsg('Template is not ready. Verify and map the template first.');
      return;
    }
    latestInstructionsRef.current = instructions;
    flushInstructions();
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setRunning(true);
    setErrorMsg('');
    setAcknowledged(false);

    const outcome = await execute({
      type: InteractionType.GENERATE,
      label: 'Run corrections preview',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        templateKind,
        action: 'corrections_preview',
      },
      action: async () => {
        try {
          const finalEvent = await runCorrectionsPreview({
            templateId,
            userInput: instructions,
            mappingOverride: mappingSnapshot,
            sampleTokens: sampleTokensSnapshot,
            onEvent: () => {},
            signal: controller.signal,
            kind: templateKind,
          });
          setResult(finalEvent);
          onCompleted?.(finalEvent);
          return finalEvent;
        } catch (err) {
          if (err?.name === 'AbortError') {
            return null;
          }
          setErrorMsg(err?.message || 'Corrections preview failed.');
          throw err;
        } finally {
          if (abortRef.current === controller) {
            abortRef.current = null;
          }
          setRunning(false);
        }
      },
    });

    if (!outcome?.success) {
      return;
    }
  };

  const handleSaveAndClose = useCallback(() => {
    if (!result) return undefined;
    return execute({
      type: InteractionType.UPDATE,
      label: 'Acknowledge corrections preview',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        templateId,
        templateKind,
        action: 'corrections_acknowledge',
      },
      action: () => {
        latestInstructionsRef.current = instructions;
        flushInstructions();
        setAcknowledged(true);
        if (typeof onSaveAndClose === 'function') {
          onSaveAndClose();
        }
      },
    });
  }, [execute, flushInstructions, instructions, onSaveAndClose, result, templateId, templateKind]);

  const processed = result?.processed || {};
  const summary = result?.summary || {};
  const constantsInlined = summary.constants_inlined ?? 0;
  const pageSummaryChars = (processed.page_summary || '').length;

  return (
    <Box
      sx={{
        p: 2,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
        bgcolor: 'background.paper',
      }}
    >
      <Stack spacing={1.5}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="subtitle1">Corrections Assistant</Typography>
          <InfoTooltip
            content={TOOLTIP_COPY.llm35Corrections}
            ariaLabel="Corrections assistant guidance"
            placement="bottom-start"
          />
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Provide instructions to fix the template and inline constants. Each run updates the HTML and refreshes the page
          summary for the narrative step.
        </Typography>

        {errorMsg && <Alert severity="error">{errorMsg}</Alert>}

        <TextField
          label="Instructions (free-form)"
          multiline
          minRows={3}
          placeholder="Example: Fix spelling issues, inline the company name using the PDF, and note any footer signatures."
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          disabled={running || disabled}
        />

        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
          <Button
            variant="contained"
            onClick={handleRun}
            disabled={running || disabled}
            startIcon={running ? <CircularProgress size={18} /> : null}
          >
            {running ? 'Running...' : result ? 'Rerun Corrections' : 'Run Corrections'}
          </Button>
          <Button variant="outlined" onClick={handleSaveAndClose} disabled={!result || running}>
            Save &amp; Close
          </Button>
        </Stack>

        {acknowledged && result && (
          <Alert severity="success" variant="outlined">
            Latest run marked complete. You can close this panel or continue to the narrative step.
          </Alert>
        )}

        {running && <LinearProgress />}

        {result && (
          <Alert severity="info" variant="outlined">
            Latest run saved. Constants inlined: {constantsInlined}. Page summary length: {pageSummaryChars} characters.
            The updated template and narrative will be used for the final narrative step.
          </Alert>
        )}
      </Stack>
    </Box>
  );
}
