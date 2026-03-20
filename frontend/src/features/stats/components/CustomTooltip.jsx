import { Box, Stack, Typography, useTheme, alpha } from '@mui/material'

export default function CustomTooltip({ active, payload, label }) {
  const theme = useTheme()
  if (!active || !payload?.length) return null

  return (
    <Box
      sx={{
        bgcolor: alpha(theme.palette.background.paper, 0.95),
        backdropFilter: 'blur(8px)',
        border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        borderRadius: 1,  // Figma spec: 8px
        p: 1.5,
        boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.15)}`,
      }}
    >
      <Typography sx={{ fontSize: '0.75rem', fontWeight: 600, color: theme.palette.text.primary, mb: 0.5 }}>
        {label}
      </Typography>
      {payload.map((entry, index) => (
        <Stack key={index} direction="row" alignItems="center" spacing={1}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: entry.color,
            }}
          />
          <Typography sx={{ fontSize: '12px', color: theme.palette.text.secondary }}>
            {entry.name}: {entry.value}
          </Typography>
        </Stack>
      ))}
    </Box>
  )
}
