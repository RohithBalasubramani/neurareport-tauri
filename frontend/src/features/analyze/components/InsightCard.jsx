import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Avatar,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import SecurityIcon from '@mui/icons-material/Security'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck'
import { neutral } from '@/app/theme'

export default function InsightCard({ insight, type = 'insight', index = 0 }) {
  const theme = useTheme()

  const config = {
    insight: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      icon: <LightbulbIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    risk: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      icon: <SecurityIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    opportunity: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
      icon: <RocketLaunchIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    action: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
      icon: <PlaylistAddCheckIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
  }

  const { gradient, borderColor, icon, iconBg } = config[type] || config.insight

  const priorityColors = {
    critical: { bg: theme.palette.mode === 'dark' ? neutral[700] : neutral[900], text: 'common.white' },
    high: { bg: theme.palette.mode === 'dark' ? neutral[500] : neutral[700], text: 'common.white' },
    medium: { bg: theme.palette.mode === 'dark' ? neutral[500] : neutral[500], text: 'common.white' },
    low: { bg: theme.palette.mode === 'dark' ? neutral[300] : neutral[500], text: theme.palette.mode === 'dark' ? neutral[900] : 'common.white' },
  }

  const priorityConfig = priorityColors[insight.priority?.toLowerCase()] || priorityColors.medium

  return (
    <Fade in timeout={400 + index * 100}>
      <Card
        sx={{
          mb: 2,
          background: gradient,
          borderLeft: `4px solid ${borderColor}`,
          borderRadius: 1,  // Figma spec: 8px
          overflow: 'hidden',
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'translateX(8px)',
            boxShadow: `0 8px 24px ${alpha(borderColor, 0.2)}`,
          },
        }}
      >
        <CardContent sx={{ py: 2.5, px: 3 }}>
          <Stack direction="row" spacing={2}>
            <Avatar
              sx={{
                bgcolor: iconBg,
                color: borderColor,
                width: 48,
                height: 48,
              }}
            >
              {icon}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                <Typography variant="subtitle1" fontWeight={600}>
                  {insight.title}
                </Typography>
                {insight.priority && (
                  <Chip
                    label={insight.priority}
                    size="small"
                    sx={{
                      height: 22,
                      fontSize: 10,
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      bgcolor: priorityConfig.bg,
                      color: priorityConfig.text,
                    }}
                  />
                )}
                {insight.confidence && (
                  <Chip
                    label={`${Math.round(insight.confidence * 100)}% confident`}
                    size="small"
                    variant="outlined"
                    sx={{ height: 22, fontSize: 10 }}
                  />
                )}
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                {insight.description}
              </Typography>
              {insight.suggested_actions?.length > 0 && (
                <Box sx={{ mt: 2, p: 2, bgcolor: alpha(borderColor, 0.08), borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight={600} color={borderColor}>
                    SUGGESTED ACTIONS
                  </Typography>
                  <Stack spacing={0.5} sx={{ mt: 1 }}>
                    {insight.suggested_actions.map((action, i) => (
                      <Stack key={i} direction="row" alignItems="center" spacing={1}>
                        <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: borderColor }} />
                        <Typography variant="body2">{action}</Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Box>
              )}
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Fade>
  )
}
