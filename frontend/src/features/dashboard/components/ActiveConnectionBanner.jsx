import {
  Box,
  Typography,
  Stack,
  Chip,
  Avatar,
  Fade,
  alpha,
  useTheme,
} from '@mui/material'
import StorageIcon from '@mui/icons-material/Storage'
import { neutral } from '@/app/theme'
import { pulse, GlassCard } from '@/styles'

export default function ActiveConnectionBanner({ activeConnection }) {
  const theme = useTheme()

  if (!activeConnection) return null

  return (
    <Fade in>
      <GlassCard sx={{ mt: 3, animationDelay: '450ms' }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            }}
          >
            <StorageIcon sx={{ color: 'text.secondary' }} />
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" fontWeight={600}>
              Connected to {activeConnection.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {activeConnection.db_type}
              {activeConnection.summary && ` \u2022 ${activeConnection.summary}`}
            </Typography>
          </Box>
          <Chip
            label="Active"
            size="small"
            sx={{
              fontWeight: 600,
              animation: `${pulse} 2s ease-in-out infinite`,
              bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
              color: 'text.secondary',
            }}
          />
        </Stack>
      </GlassCard>
    </Fade>
  )
}
