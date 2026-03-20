import {
  Box,
  Typography,
  Stack,
  useTheme,
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import { neutral } from '@/app/theme'
import { StatCardStyled } from './DashboardStyledComponents'

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'inherit', onClick, trend, delay = 0 }) {
  const theme = useTheme()

  return (
    <StatCardStyled color={color} delay={delay} onClick={onClick}>
      <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
        <Box sx={{ flex: 1 }}>
          <Typography
            sx={{
              color: theme.palette.mode === 'dark' ? neutral[500] : neutral[400],
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              fontSize: '12px',
            }}
          >
            {title}
          </Typography>
          <Typography
            sx={{
              fontWeight: 600,
              fontSize: '1.5rem',
              mt: 0.5,
              mb: 0.5,
              color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
            }}
          >
            {value}
          </Typography>
          {subtitle && (
            <Typography sx={{ fontSize: '12px', color: theme.palette.mode === 'dark' ? neutral[500] : neutral[300] }}>
              {subtitle}
            </Typography>
          )}
          {trend !== undefined && (
            <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 0.5 }}>
              {trend >= 0 ? (
                <TrendingUpIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              ) : (
                <TrendingDownIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              )}
              <Typography
                sx={{
                  fontWeight: 600,
                  fontSize: '0.75rem',
                  color: 'text.secondary',
                }}
              >
                {trend >= 0 ? '+' : ''}{trend}%
              </Typography>
            </Stack>
          )}
        </Box>
        <Box
          className="stat-icon"
          sx={{
            width: 48,
            height: 48,
            borderRadius: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : neutral[100],
            color: theme.palette.mode === 'dark' ? neutral[500] : neutral[300],
          }}
        >
          <Icon sx={{ fontSize: 24 }} />
        </Box>
      </Stack>
    </StatCardStyled>
  )
}
