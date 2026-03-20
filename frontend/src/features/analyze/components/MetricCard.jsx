import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Zoom,
  alpha,
  useTheme,
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import AutoGraphIcon from '@mui/icons-material/AutoGraph'
import { neutral } from '@/app/theme'

export default function MetricCard({ metric, index }) {
  const theme = useTheme()
  const isPositive = metric.change > 0
  const isNegative = metric.change < 0

  return (
    <Zoom in timeout={300 + index * 50}>
      <Card
        sx={{
          minWidth: 220,
          background: `linear-gradient(145deg, ${theme.palette.background.paper} 0%, ${alpha(theme.palette.text.primary, 0.02)} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          borderRadius: 1,  // Figma spec: 8px
          overflow: 'hidden',
          position: 'relative',
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'translateY(-6px)',
            boxShadow: theme.palette.mode === 'dark' ? `0 12px 32px ${alpha(theme.palette.common.black, 0.3)}` : '0 12px 32px rgba(0,0,0,0.08)',
            '& .metric-icon': {
              transform: 'scale(1.2) rotate(10deg)',
            },
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          },
        }}
      >
        <CardContent sx={{ py: 2.5, px: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={600}
                sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}
              >
                {metric.name}
              </Typography>
              <Typography
                variant="h4"
                fontWeight={600}
                sx={{
                  mt: 0.5,
                  color: theme.palette.text.primary,
                }}
              >
                {metric.raw_value}
              </Typography>
              {metric.change !== undefined && metric.change !== null && (
                <Chip
                  size="small"
                  icon={isPositive ? <TrendingUpIcon sx={{ fontSize: 14 }} /> : isNegative ? <TrendingUpIcon sx={{ fontSize: 14, transform: 'rotate(180deg)' }} /> : null}
                  label={`${isPositive ? '+' : ''}${metric.change}%`}
                  sx={{
                    mt: 1,
                    height: 24,
                    fontWeight: 600,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                    color: 'text.secondary',
                    '& .MuiChip-icon': {
                      color: 'inherit',
                    },
                  }}
                />
              )}
            </Box>
            <Box
              className="metric-icon"
              sx={{
                transition: 'transform 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
                color: alpha(theme.palette.text.primary, 0.15),
              }}
            >
              <AutoGraphIcon sx={{ fontSize: 48 }} />
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Zoom>
  )
}
