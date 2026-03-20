/**
 * Summary Output Panel — displays the generated summary or empty state.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  AutoAwesome as SummaryIcon,
  ContentCopy as CopyIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import SendToMenu from '@/components/common/SendToMenu';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';
import { neutral } from '@/app/theme';

export default function SummaryOutputPanel({
  summary,
  tone,
  maxSentences,
  focusAreas,
  copied,
  onCopy,
  onClear,
}) {
  return (
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
              <IconButton size="small" onClick={onCopy} aria-label="Copy to clipboard">
                <CopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Clear">
              <IconButton size="small" onClick={onClear} aria-label="Clear summary">
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
  );
}
