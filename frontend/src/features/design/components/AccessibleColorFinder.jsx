/**
 * Accessible Color Finder section of the Color Tools tab.
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Paper,
  Grid,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import { Accessibility as A11yIcon } from '@mui/icons-material'
import { ActionButton } from './DesignStyledComponents'

export default function AccessibleColorFinder({
  loading,
  a11yBg,
  setA11yBg,
  a11ySuggestions,
  handleSuggestA11y,
  handleCopyColor,
}) {
  const theme = useTheme()

  return (
    <>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3 }}>
          <TextField
            fullWidth
            type="color"
            label="Background Color"
            value={a11yBg}
            onChange={(e) => setA11yBg(e.target.value)}
            sx={{ mb: 1 }}
          />
          <Typography variant="caption" sx={{ fontFamily: 'monospace', display: 'block', mb: 2 }}>
            {a11yBg}
          </Typography>
          <ActionButton
            variant="contained"
            fullWidth
            onClick={handleSuggestA11y}
            disabled={loading}
            data-testid="suggest-a11y-button"
            startIcon={<A11yIcon />}
          >
            Find Accessible Text Colors
          </ActionButton>
        </Paper>
      </Grid>
      <Grid item xs={12} md={8}>
        {a11ySuggestions ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2 }}>
              Text colors that pass WCAG AA on{' '}
              <Box
                component="span"
                sx={{
                  display: 'inline-block',
                  width: 14,
                  height: 14,
                  borderRadius: '50%',
                  backgroundColor: a11ySuggestions.background_color,
                  border: '1px solid rgba(0,0,0,0.2)',
                  verticalAlign: 'middle',
                  mr: 0.5,
                }}
              />
              <code>{a11ySuggestions.background_color}</code>
            </Typography>
            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
              {a11ySuggestions.colors?.map((s, i) => (
                <Tooltip
                  key={i}
                  title={`${s.label} — ${s.contrast_ratio}:1`}
                  arrow
                >
                  <Box
                    sx={{ textAlign: 'center', cursor: 'pointer' }}
                    onClick={() => handleCopyColor(s.hex)}
                  >
                    <Box
                      sx={{
                        width: 56,
                        height: 56,
                        borderRadius: 2,
                        backgroundColor: a11ySuggestions.background_color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '1px solid rgba(0,0,0,0.1)',
                        mb: 0.5,
                      }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 700, color: s.hex }}
                      >
                        Aa
                      </Typography>
                    </Box>
                    <Typography
                      variant="caption"
                      display="block"
                      sx={{ fontFamily: 'monospace' }}
                    >
                      {s.hex}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {s.contrast_ratio}:1
                    </Typography>
                  </Box>
                </Tooltip>
              ))}
              {a11ySuggestions.colors?.length === 0 && (
                <Typography variant="body2" color="text.secondary">
                  No strongly accessible text colors found for this background.
                </Typography>
              )}
            </Box>
          </Paper>
        ) : (
          <Paper
            sx={{
              height: 160,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
              backgroundColor: 'transparent',
            }}
            elevation={0}
          >
            <Typography color="text.secondary">
              Pick a background color to find accessible text colors
            </Typography>
          </Paper>
        )}
      </Grid>
    </>
  )
}
