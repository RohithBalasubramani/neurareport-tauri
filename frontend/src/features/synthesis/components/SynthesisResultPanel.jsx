/**
 * Synthesis result display for SynthesisPage
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
} from '@mui/material';
import { neutral } from '@/app/theme';
import SendToMenu from '@/components/common/SendToMenu';
import { OutputType, FeatureKey } from '@/utils/crossPageTypes';

export default function SynthesisResultPanel({ synthesisResult, currentSession }) {
  if (!synthesisResult) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6">
          Synthesis Result
        </Typography>
        <SendToMenu
          outputType={OutputType.TEXT}
          payload={{
            title: synthesisResult.synthesis?.title || currentSession?.name || 'Synthesis',
            content: [
              synthesisResult.synthesis?.executive_summary || '',
              ...(synthesisResult.synthesis?.key_insights || []),
              ...(synthesisResult.synthesis?.sections || []).map((s) => `${s.heading}\n${s.content}`),
            ].join('\n\n'),
          }}
          sourceFeature={FeatureKey.SYNTHESIS}
        />
      </Box>
      <Box sx={{ bgcolor: neutral[50], p: 2, borderRadius: 1 }}>
        <Typography variant="h6" gutterBottom>
          {synthesisResult.synthesis?.title}
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          {synthesisResult.synthesis?.executive_summary}
        </Typography>

        {synthesisResult.synthesis?.key_insights && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Key Insights</Typography>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {synthesisResult.synthesis.key_insights.map((insight, idx) => (
                <li key={idx}><Typography variant="body2">{insight}</Typography></li>
              ))}
            </ul>
          </Box>
        )}

        {synthesisResult.synthesis?.sections && (
          <Box>
            {synthesisResult.synthesis.sections.map((section, idx) => (
              <Box key={idx} sx={{ mb: 2 }}>
                <Typography variant="subtitle1">{section.heading}</Typography>
                <Typography variant="body2">{section.content}</Typography>
              </Box>
            ))}
          </Box>
        )}
      </Box>
    </Paper>
  );
}
