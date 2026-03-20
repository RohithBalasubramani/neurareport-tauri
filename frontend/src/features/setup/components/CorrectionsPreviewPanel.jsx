import { Alert, Box, Button, CircularProgress, LinearProgress, Stack, TextField, Typography } from '@mui/material';

import InfoTooltip from '@/components/common/InfoTooltip.jsx';
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx';
import { useCorrectionsPreview } from '../hooks/useCorrectionsPreview';

export default function CorrectionsPreviewPanel(props) {
  const {
    instructions,
    setInstructions,
    running,
    errorMsg,
    result,
    acknowledged,
    handleRun,
    handleSaveAndClose,
  } = useCorrectionsPreview(props);

  const { disabled } = props;
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
