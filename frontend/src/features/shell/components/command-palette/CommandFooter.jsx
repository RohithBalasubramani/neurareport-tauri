import { Box, Typography } from '@mui/material'
import { Kbd } from '@/ui'

export default function CommandFooter() {
  return (
    <Box
      sx={{
        p: 1.5,
        borderTop: 1,
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        bgcolor: 'action.hover',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Kbd>{'\u2191'}</Kbd>
          <Kbd>{'\u2193'}</Kbd>
          <Typography variant="caption" color="text.secondary">
            navigate
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Kbd>{'\u21B5'}</Kbd>
          <Typography variant="caption" color="text.secondary">
            select
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Kbd>esc</Kbd>
          <Typography variant="caption" color="text.secondary">
            close
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}
