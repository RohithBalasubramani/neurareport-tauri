/**
 * Reusable card wrapper for settings sections
 */
import { Stack, Typography, Box, useTheme, alpha } from '@mui/material'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'

const IconContainer = ({ children, ...props }) => {
  const theme = useTheme()
  return (
    <Box
      sx={{
        width: 32,
        height: 32,
        borderRadius: 8 / 8,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        ...props.sx,
      }}
    >
      {children}
    </Box>
  )
}

export default function SettingCard({ icon: Icon, title, children }) {
  const theme = useTheme()

  return (
    <GlassCard>
      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
        <IconContainer>
          <Icon sx={{ color: 'text.secondary', fontSize: 16 }} />
        </IconContainer>
        <Typography variant="subtitle1" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
          {title}
        </Typography>
      </Stack>
      {children}
    </GlassCard>
  )
}
