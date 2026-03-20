/**
 * WCAG Contrast Checker section of the Color Tools tab.
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Paper,
  Grid,
  Chip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Check as CheckIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { ActionButton, ContrastBar } from './DesignStyledComponents'

export default function ContrastChecker({
  loading,
  contrastFg,
  setContrastFg,
  contrastBg,
  setContrastBg,
  contrastResult,
  handleCheckContrast,
}) {
  const theme = useTheme()

  return (
    <>
      <Grid item xs={12} md={5}>
        <Paper sx={{ p: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                type="color"
                label="Foreground"
                value={contrastFg}
                onChange={(e) => setContrastFg(e.target.value)}
              />
              <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                {contrastFg}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                type="color"
                label="Background"
                value={contrastBg}
                onChange={(e) => setContrastBg(e.target.value)}
              />
              <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                {contrastBg}
              </Typography>
            </Grid>
          </Grid>
          <ActionButton
            variant="contained"
            fullWidth
            sx={{ mt: 2 }}
            onClick={handleCheckContrast}
            disabled={loading}
            data-testid="check-contrast-button"
          >
            Check Contrast
          </ActionButton>
        </Paper>
      </Grid>
      <Grid item xs={12} md={7}>
        {contrastResult ? (
          <Paper sx={{ p: 3 }}>
            <Box
              sx={{
                backgroundColor: contrastResult.color2,
                color: contrastResult.color1,
                p: 3,
                borderRadius: 2,
                mb: 2,
                textAlign: 'center',
              }}
            >
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                Sample Text
              </Typography>
              <Typography variant="body2">
                The quick brown fox jumps over the lazy dog
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
              <Typography variant="h4" sx={{ fontWeight: 700, fontFamily: 'monospace' }}>
                {contrastResult.contrast_ratio}:1
              </Typography>
              <ContrastBar ratio={contrastResult.contrast_ratio} />
            </Box>

            <Grid container spacing={1}>
              {[
                { label: 'AA Normal (4.5:1)', pass: contrastResult.wcag_aa_normal },
                { label: 'AA Large (3:1)', pass: contrastResult.wcag_aa_large },
                { label: 'AAA Normal (7:1)', pass: contrastResult.wcag_aaa_normal },
                { label: 'AAA Large (4.5:1)', pass: contrastResult.wcag_aaa_large },
              ].map(({ label, pass }) => (
                <Grid item xs={6} key={label}>
                  <Chip
                    label={label}
                    size="small"
                    icon={pass ? <CheckIcon /> : <CloseIcon />}
                    color={pass ? 'success' : 'default'}
                    variant={pass ? 'filled' : 'outlined'}
                    sx={{ width: '100%', justifyContent: 'flex-start' }}
                  />
                </Grid>
              ))}
            </Grid>
          </Paper>
        ) : (
          <Paper
            sx={{
              height: 200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
              backgroundColor: 'transparent',
            }}
            elevation={0}
          >
            <Typography color="text.secondary">
              Pick two colors and check their WCAG contrast ratio
            </Typography>
          </Paper>
        )}
      </Grid>
    </>
  )
}
