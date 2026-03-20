/**
 * Loading skeleton for document grid.
 */
import React from 'react'
import { Box, Grid, Card, useTheme, alpha } from '@mui/material'

export default function LoadingSkeleton() {
  const theme = useTheme()

  return (
    <Grid container spacing={2}>
      {Array.from({ length: 6 }).map((_, i) => (
        <Grid item xs={12} sm={6} md={4} key={i}>
          <Card variant="outlined" sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
              <Box sx={{ width: '70%', height: 20, bgcolor: alpha(theme.palette.text.primary, 0.08), borderRadius: 1 }} />
              <Box sx={{ width: 24, height: 24, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: '50%' }} />
            </Box>
            <Box sx={{ width: '50%', height: 14, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1, mb: 1.5 }} />
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Box sx={{ width: 48, height: 20, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1 }} />
              <Box sx={{ width: 56, height: 20, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1 }} />
            </Box>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}
