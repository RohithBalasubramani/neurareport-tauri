/**
 * Key-value row for settings display
 */
import { Box, Typography, useTheme } from '@mui/material'

export default function ConfigRow({ label, value, mono = false }) {
  const theme = useTheme()

  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 0.75 }}>
      <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
        {label}
      </Typography>
      <Typography
        variant="body2"
        sx={{
          color: theme.palette.text.primary,
          ...(mono && { fontFamily: 'monospace', fontSize: '14px' }),
        }}
      >
        {value}
      </Typography>
    </Box>
  )
}
