import { Box, Stack, Typography, CardContent, useTheme, alpha } from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import { fadeInUp, GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import { styled } from '@mui/material'

const StatCardContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing(2.5),
  '&:last-child': {
    paddingBottom: theme.spacing(2.5),
  },
}))

export default function StatCard({ title, value, subtitle, icon: Icon, trend, color, onClick }) {
  const theme = useTheme()
  const trendPositive = trend > 0
  const TrendIcon = trendPositive ? TrendingUpIcon : TrendingDownIcon
  const trendColor = theme.palette.text.secondary
  const accentColor = color || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])

  return (
    <GlassCard
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        animation: `${fadeInUp} 0.5s ease-out`,
        '&:active': onClick ? { transform: 'scale(0.98)' } : {},
      }}
    >
      <StatCardContent>
        <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
          <Box>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 500,
                color: theme.palette.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                mb: 0.5,
              }}
            >
              {title}
            </Typography>
            <Typography
              sx={{
                fontSize: '1.75rem',
                fontWeight: 600,
                color: theme.palette.text.primary,
                lineHeight: 1.2,
              }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: theme.palette.text.secondary,
                  mt: 0.5,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2.5,
              bgcolor: alpha(accentColor, 0.15),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ fontSize: 20, color: accentColor }} />
          </Box>
        </Stack>
        {trend !== undefined && trend !== null && (
          <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 1.5 }}>
            <TrendIcon sx={{ fontSize: 14, color: trendColor }} />
            <Typography sx={{ fontSize: '0.75rem', color: trendColor, fontWeight: 500 }}>
              {Math.abs(trend)}%
            </Typography>
            <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
              vs previous period
            </Typography>
          </Stack>
        )}
      </StatCardContent>
    </GlassCard>
  )
}
