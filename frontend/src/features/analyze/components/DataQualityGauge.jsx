import {
  Box,
  Typography,
  Stack,
  CircularProgress,
  alpha,
  useTheme,
} from '@mui/material'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'

export default function DataQualityGauge({ quality }) {
  const theme = useTheme()
  if (!quality) return null

  const score = Math.round((quality.quality_score || 0) * 100)
  const getColor = (s) => {
    if (s >= 80) return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
    if (s >= 60) return theme.palette.mode === 'dark' ? neutral[500] : neutral[500]
    return theme.palette.mode === 'dark' ? neutral[300] : neutral[500]
  }
  const color = getColor(score)

  return (
    <GlassCard hover={false} sx={{ p: 2.5 }}>
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              variant="determinate"
              value={100}
              size={80}
              thickness={6}
              sx={{ color: alpha(color, 0.2) }}
            />
            <CircularProgress
              variant="determinate"
              value={score}
              size={80}
              thickness={6}
              sx={{
                color: color,
                position: 'absolute',
                left: 0,
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                },
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h5" fontWeight={600} color={color}>
                {score}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Score
              </Typography>
            </Box>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="overline" color="text.secondary" fontWeight={600}>
              Data Quality
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Attention'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {quality.total_rows} rows, {quality.total_columns} columns
            </Typography>
          </Box>
        </Stack>
        {quality.recommendations?.length > 0 && (
          <Box sx={{ p: 1.5, bgcolor: alpha(color, 0.1), borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {quality.recommendations[0]}
            </Typography>
          </Box>
        )}
      </Stack>
    </GlassCard>
  )
}
