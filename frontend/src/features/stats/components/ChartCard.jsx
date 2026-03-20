import { Box, Stack, Typography, CardContent, useTheme } from '@mui/material'
import { fadeInUp, GlassCard } from '@/styles'

export default function ChartCard({ title, subtitle, children, height = 280, actions }) {
  const theme = useTheme()

  return (
    <GlassCard sx={{ height: '100%', animation: `${fadeInUp} 0.5s ease-out 0.2s both` }}>
      <CardContent sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
          <Box>
            <Typography
              sx={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              {title}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: theme.palette.text.secondary,
                  mt: 0.25,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          {actions}
        </Stack>
        <Box sx={{ flex: 1, minHeight: height }}>
          {children}
        </Box>
      </CardContent>
    </GlassCard>
  )
}
