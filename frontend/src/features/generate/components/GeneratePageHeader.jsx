/**
 * Header section for the Generate page.
 */
import { Box, Typography, Stack, Chip, alpha } from '@mui/material'
import { neutral } from '@/app/theme'

export default function GeneratePageHeader({ selected, approved }) {
  return (
    <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
      <Box>
        <Typography variant="h5" fontWeight={600}>
          Generate Reports
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Select templates, configure parameters, and generate reports from your data.
        </Typography>
      </Box>
      <Stack direction="row" spacing={1}>
        {selected.length > 0 && (
          <Chip
            size="small"
            label={`${selected.length} selected`}
            sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
          />
        )}
        <Chip
          size="small"
          label={`${approved.length} available`}
          variant="outlined"
          sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
        />
      </Stack>
    </Stack>
  )
}
