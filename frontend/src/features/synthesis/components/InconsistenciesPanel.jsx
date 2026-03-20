/**
 * Inconsistencies display panel for SynthesisPage
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import { neutral } from '@/app/theme';
import {
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';

export default function InconsistenciesPanel({ inconsistencies }) {
  if (!inconsistencies.length) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <WarningIcon sx={{ color: 'text.secondary' }} /> Inconsistencies Found ({inconsistencies.length})
      </Typography>
      {inconsistencies.map((item, idx) => (
        <Accordion key={idx} variant="outlined">
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                size="small"
                label={item.severity}
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
              <Typography>{item.field_or_topic}</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {item.description}
            </Typography>
            {item.suggested_resolution && (
              <Alert severity="info" sx={{ mt: 1 }}>
                <strong>Suggestion:</strong> {item.suggested_resolution}
              </Alert>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Paper>
  );
}
