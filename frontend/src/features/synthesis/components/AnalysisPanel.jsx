/**
 * Analysis actions panel for SynthesisPage
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  CircularProgress,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Warning as WarningIcon,
  AutoAwesome as SynthesizeIcon,
} from '@mui/icons-material';
import ConnectionSelector from '@/components/common/ConnectionSelector';
import DisabledTooltip from '@/components/ux/DisabledTooltip';

export default function AnalysisPanel({
  loading,
  currentSession,
  selectedConnectionId,
  onConnectionChange,
  outputFormat,
  onOutputFormatChange,
  focusTopics,
  onFocusTopicsChange,
  onFindInconsistencies,
  onSynthesize,
}) {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Analysis
      </Typography>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12 }}>
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={onConnectionChange}
            label="Enrich with Database (optional)"
            showStatus
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Output Format</InputLabel>
            <Select
              value={outputFormat}
              label="Output Format"
              onChange={(e) => onOutputFormatChange(e.target.value)}
            >
              <MenuItem value="structured">Structured</MenuItem>
              <MenuItem value="narrative">Narrative</MenuItem>
              <MenuItem value="comparison">Comparison</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            fullWidth
            size="small"
            label="Focus Topics (comma-separated)"
            value={focusTopics}
            onChange={(e) => onFocusTopicsChange(e.target.value)}
            placeholder="revenue, growth, risks"
          />
        </Grid>
      </Grid>
      <Box sx={{ display: 'flex', gap: 2 }}>
        {/* UX: DisabledTooltip explains WHY buttons are disabled */}
        <DisabledTooltip
          disabled={loading || !currentSession?.documents?.length}
          reason={
            loading
              ? 'Please wait for the current operation to complete'
              : !currentSession?.documents?.length
                ? 'Add at least one document first'
                : undefined
          }
        >
          <Button
            variant="outlined"
            startIcon={loading ? <CircularProgress size={20} /> : <WarningIcon />}
            onClick={onFindInconsistencies}
            disabled={loading || !currentSession?.documents?.length}
          >
            Find Inconsistencies
          </Button>
        </DisabledTooltip>
        <DisabledTooltip
          disabled={loading || !currentSession?.documents?.length}
          reason={
            loading
              ? 'Please wait for the current operation to complete'
              : !currentSession?.documents?.length
                ? 'Add at least two documents to synthesize'
                : undefined
          }
        >
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <SynthesizeIcon />}
            onClick={onSynthesize}
            disabled={loading || !currentSession?.documents?.length}
          >
            Synthesize
          </Button>
        </DisabledTooltip>
      </Box>
    </Paper>
  );
}
