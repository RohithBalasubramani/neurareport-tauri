/**
 * Typography tab content for the Design page.
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
import { TextFields as FontIcon } from '@mui/icons-material'
import { FontSample } from './DesignStyledComponents'
import FontPairingsResult from './FontPairingsResult'

export default function TypographyTab({
  selectedFont,
  fontPairings,
  fontFilter,
  setFontFilter,
  filteredFonts,
  handleGetPairings,
}) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={5}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
            Font Library
          </Typography>
          <TextField
            fullWidth
            size="small"
            placeholder="Search fonts..."
            value={fontFilter}
            onChange={(e) => setFontFilter(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Box sx={{ maxHeight: 480, overflow: 'auto' }}>
            {filteredFonts.map((f) => (
              <Box
                key={f.name}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  py: 1,
                  px: 1.5,
                  borderRadius: 1,
                  cursor: 'pointer',
                  backgroundColor:
                    selectedFont === f.name
                      ? alpha(theme.palette.primary.main, 0.08)
                      : 'transparent',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.04),
                  },
                }}
                onClick={() => handleGetPairings(f.name)}
              >
                <Box>
                  <FontSample variant="body1" fontFamily={f.name} sx={{ fontWeight: 600 }}>
                    {f.name}
                  </FontSample>
                  <Typography variant="caption" color="text.secondary">
                    {f.category} &middot; {f.weights?.length || 0} weights
                  </Typography>
                </Box>
                <Chip label={f.category} size="small" variant="outlined" />
              </Box>
            ))}
            {filteredFonts.length === 0 && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                No fonts match your search
              </Typography>
            )}
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={7}>
        {selectedFont && fontPairings ? (
          <FontPairingsResult selectedFont={selectedFont} fontPairings={fontPairings} />
        ) : (
          <Paper
            sx={{
              height: 300,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
              backgroundColor: 'transparent',
            }}
            elevation={0}
          >
            <FontIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography color="text.secondary">
              Select a font to see pairing suggestions
            </Typography>
          </Paper>
        )}

        {/* Type scale preview */}
        {selectedFont && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Type Scale Preview
            </Typography>
            {[
              { label: 'Display', variant: 'h3', weight: 800 },
              { label: 'Heading 1', variant: 'h4', weight: 700 },
              { label: 'Heading 2', variant: 'h5', weight: 600 },
              { label: 'Heading 3', variant: 'h6', weight: 600 },
              { label: 'Body', variant: 'body1', weight: 400 },
              { label: 'Caption', variant: 'caption', weight: 400 },
            ].map(({ label, variant, weight }) => (
              <Box key={label} sx={{ display: 'flex', alignItems: 'baseline', gap: 2, mb: 1 }}>
                <Typography variant="caption" color="text.secondary" sx={{ width: 80, flexShrink: 0 }}>
                  {label}
                </Typography>
                <FontSample variant={variant} fontFamily={selectedFont} sx={{ fontWeight: weight }}>
                  Almost before we knew it, we had left the ground.
                </FontSample>
              </Box>
            ))}
          </Paper>
        )}
      </Grid>
    </Grid>
  )
}
