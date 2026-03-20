/**
 * Summary Input Panel — content entry, report loader, and action buttons.
 */
import React from 'react';
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
  CircularProgress,
  Divider,
  Stack,
} from '@mui/material';
import {
  AutoAwesome as SummaryIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import ConnectionSelector from '@/components/common/ConnectionSelector';
import SummaryOptionsPanel from './SummaryOptionsPanel';

export default function SummaryInputPanel({
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
  loading,
  queueing,
  reportRuns,
  onGenerate,
  onQueue,
  onAddFocus,
  onRemoveFocus,
  onAddCustomFocus,
  onLoadReportRun,
}) {
  return (
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
                if (run) onLoadReportRun(run);
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

      <SummaryOptionsPanel
        tone={tone}
        setTone={setTone}
        maxSentences={maxSentences}
        setMaxSentences={setMaxSentences}
        focusAreas={focusAreas}
        customFocus={customFocus}
        setCustomFocus={setCustomFocus}
        onAddFocus={onAddFocus}
        onRemoveFocus={onRemoveFocus}
        onAddCustomFocus={onAddCustomFocus}
      />

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
        <Button
          variant="contained"
          fullWidth
          size="large"
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SummaryIcon />}
          onClick={onGenerate}
          disabled={!content.trim() || content.length < 10 || loading || queueing}
        >
          {loading ? 'Generating...' : 'Generate Summary'}
        </Button>
        <Button
          variant="outlined"
          fullWidth
          size="large"
          startIcon={queueing ? <CircularProgress size={20} color="inherit" /> : <ScheduleIcon />}
          onClick={onQueue}
          disabled={!content.trim() || content.length < 10 || loading || queueing}
        >
          {queueing ? 'Queueing...' : 'Queue in Background'}
        </Button>
      </Stack>
    </Paper>
  );
}
