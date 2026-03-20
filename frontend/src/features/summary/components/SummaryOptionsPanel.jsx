/**
 * Summary Options — tone, length, and focus area controls.
 */
import React from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Slider,
  alpha,
} from '@mui/material';
import { neutral } from '@/app/theme';

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

export default function SummaryOptionsPanel({
  tone,
  setTone,
  maxSentences,
  setMaxSentences,
  focusAreas,
  customFocus,
  setCustomFocus,
  onAddFocus,
  onRemoveFocus,
  onAddCustomFocus,
}) {
  return (
    <>
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
              onDelete={() => onRemoveFocus(focus)}
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
              onClick={() => onAddFocus(focus)}
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
            onKeyDown={(e) => e.key === 'Enter' && onAddCustomFocus()}
            disabled={focusAreas.length >= 5}
            sx={{ flex: 1 }}
          />
          <Button
            variant="outlined"
            size="small"
            onClick={onAddCustomFocus}
            disabled={!customFocus.trim() || focusAreas.length >= 5}
          >
            Add
          </Button>
        </Box>
      </Box>
    </>
  );
}
