import { Typography, Stack, Chip, Button } from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'

const formatFileSize = (bytes) => {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 KB'
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  const digits = value >= 10 || unitIndex === 0 ? 0 : 1
  return `${value.toFixed(digits)} ${units[unitIndex]}`
}

export default function FileInfoBar({ file, format, onClear }) {
  if (!file) return null
  return (
    <Stack
      direction={{ xs: 'column', sm: 'row' }}
      spacing={{ xs: 1.5, sm: 2 }}
      alignItems={{ sm: 'center' }}
      justifyContent="space-between"
      sx={{
        mt: 2,
        px: { xs: 2, sm: 2.5 },
        py: { xs: 1.75, sm: 2 },
        borderRadius: 1,
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.divider, 0.3),
        bgcolor: 'common.white',
        boxShadow: `0 10px 24px ${alpha(neutral[900], 0.06)}`,
      }}
    >
      <Stack spacing={0.5}>
        <Typography variant="subtitle2" sx={{ wordBreak: 'break-word' }}>
          {file.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {(format || 'Unknown format')} - {formatFileSize(file.size)}
        </Typography>
      </Stack>
      <Stack direction="row" spacing={1} alignItems="center" justifyContent="flex-end">
        <Chip
          label={format || 'Unknown'}
          size="small"
          variant={format === 'PDF' || format === 'Excel' ? 'filled' : 'outlined'}
          sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
        />
        <Button variant="text" size="small" onClick={onClear} sx={{ color: 'text.secondary' }}>
          Remove
        </Button>
      </Stack>
    </Stack>
  )
}
