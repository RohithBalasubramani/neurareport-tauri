/**
 * Live mini preview for a brand kit card.
 */
import React from 'react'
import { Box, Typography, alpha } from '@mui/material'

export default function BrandKitPreview({ kit }) {
  return (
    <Box
      sx={{
        mt: 1,
        p: 1.5,
        borderRadius: 1,
        border: '1px solid rgba(0,0,0,0.08)',
        backgroundColor: kit.background_color || '#ffffff',
        overflow: 'hidden',
      }}
    >
      <Typography
        variant="caption"
        sx={{
          fontFamily: `"${kit.typography?.heading_font || kit.typography?.font_family || 'Inter'}", sans-serif`,
          fontWeight: 700,
          color: kit.text_color || '#333',
          display: 'block',
          fontSize: 11,
          mb: 0.5,
        }}
      >
        Report Title Preview
      </Typography>
      <Box
        sx={{
          display: 'flex',
          gap: 0,
          borderRadius: 0.5,
          overflow: 'hidden',
          mb: 0.5,
        }}
      >
        <Box sx={{ flex: 1, height: 16, backgroundColor: kit.primary_color, display: 'flex', alignItems: 'center', px: 0.5 }}>
          <Typography sx={{ fontSize: 7, color: '#fff', fontWeight: 600 }}>Header</Typography>
        </Box>
        <Box sx={{ flex: 1, height: 16, backgroundColor: kit.secondary_color, display: 'flex', alignItems: 'center', px: 0.5 }}>
          <Typography sx={{ fontSize: 7, color: '#fff', fontWeight: 600 }}>Column</Typography>
        </Box>
        <Box sx={{ flex: 1, height: 16, backgroundColor: kit.accent_color, display: 'flex', alignItems: 'center', px: 0.5 }}>
          <Typography sx={{ fontSize: 7, color: '#fff', fontWeight: 600 }}>Accent</Typography>
        </Box>
      </Box>
      <Typography
        variant="caption"
        sx={{
          fontFamily: `"${kit.typography?.body_font || kit.typography?.font_family || 'Inter'}", sans-serif`,
          color: alpha(kit.text_color || '#333', 0.7),
          fontSize: 9,
          lineHeight: 1.3,
        }}
      >
        Body text sample in {kit.typography?.font_family || 'Inter'}
      </Typography>
    </Box>
  )
}
