import {
  Box,
  Typography,
  Stack,
  Chip,
  CircularProgress,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt'
import SentimentVeryDissatisfiedIcon from '@mui/icons-material/SentimentVeryDissatisfied'
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'

export default function SentimentDisplay({ sentiment }) {
  const theme = useTheme()
  if (!sentiment) return null

  const getSentimentConfig = (level) => {
    const neutralColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
    const neutralGradient = theme.palette.mode === 'dark'
      ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.12)} 0%, ${alpha(theme.palette.text.primary, 0.06)} 100%)`
      : `linear-gradient(135deg, ${neutral[200]} 0%, ${neutral[100]} 100%)`
    if (level?.includes('positive')) {
      return {
        icon: <SentimentSatisfiedAltIcon sx={{ fontSize: 32 }} />,
        color: neutralColor,
        label: 'Positive',
        gradient: neutralGradient,
      }
    }
    if (level?.includes('negative')) {
      return {
        icon: <SentimentVeryDissatisfiedIcon sx={{ fontSize: 32 }} />,
        color: neutralColor,
        label: 'Negative',
        gradient: neutralGradient,
      }
    }
    return {
      icon: <SentimentNeutralIcon sx={{ fontSize: 32 }} />,
      color: neutralColor,
      label: 'Neutral',
      gradient: neutralGradient,
    }
  }

  const config = getSentimentConfig(sentiment.overall_sentiment)
  const score = Math.round((sentiment.overall_score + 1) * 50) // Convert -1 to 1 → 0 to 100

  return (
    <GlassCard hover={false} sx={{ p: 2.5 }}>
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              background: config.gradient,
              color: config.color,
            }}
          >
            {config.icon}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="overline" color="text.secondary" fontWeight={600}>
              Document Sentiment
            </Typography>
            <Typography variant="h5" fontWeight={600} color={config.color}>
              {config.label}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={score}
                size={60}
                thickness={6}
                sx={{ color: config.color }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="body2" fontWeight={600} color={config.color}>
                  {score}%
                </Typography>
              </Box>
            </Box>
          </Box>
        </Stack>
        <Stack direction="row" spacing={2}>
          <Chip
            size="small"
            label={`Tone: ${sentiment.emotional_tone || 'Neutral'}`}
            sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}
          />
          <Chip
            size="small"
            label={`Urgency: ${sentiment.urgency_level || 'Normal'}`}
            sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}
          />
        </Stack>
      </Stack>
    </GlassCard>
  )
}
