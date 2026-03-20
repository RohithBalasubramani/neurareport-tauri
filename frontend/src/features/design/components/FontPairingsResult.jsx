/**
 * Font pairing suggestions result display.
 */
import React from 'react'
import { Box, Typography, Paper, useTheme, alpha } from '@mui/material'
import { FontSample } from './DesignStyledComponents'

export default function FontPairingsResult({ selectedFont, fontPairings }) {
  const theme = useTheme()

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
        Pairing suggestions for{' '}
        <FontSample component="span" fontFamily={selectedFont}>
          {selectedFont}
        </FontSample>
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Recommended body fonts to pair with your heading font
      </Typography>

      {fontPairings.pairings?.map((p, i) => (
        <Box key={i} sx={{ mb: 3 }}>
          <Box
            sx={{
              border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
              borderRadius: 2,
              p: 2.5,
              mb: 1,
            }}
          >
            <FontSample
              variant="h5"
              fontFamily={selectedFont}
              sx={{ fontWeight: 700, mb: 1 }}
            >
              Heading in {selectedFont}
            </FontSample>
            <FontSample
              variant="body1"
              fontFamily={p.font}
              sx={{ color: 'text.secondary' }}
            >
              Body text in {p.font}. The quick brown fox jumps over the lazy dog.
              Design is not just what it looks like — design is how it works.
            </FontSample>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {p.font}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {p.category} &middot; {p.reason}
              </Typography>
            </Box>
          </Box>
        </Box>
      ))}
    </Paper>
  )
}
