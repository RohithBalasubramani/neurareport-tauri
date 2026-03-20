import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Avatar,
  Grow,
  alpha,
  useTheme,
} from '@mui/material'
import { neutral } from '@/app/theme'

export default function StatCard({ icon, label, value, delay = 0 }) {
  const theme = useTheme()
  return (
    <Grow in timeout={500 + delay * 100}>
      <Card
        sx={{
          minWidth: 140,
          background: theme.palette.mode === 'dark'
            ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.03)} 100%)`
            : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          borderRadius: 1,  // Figma spec: 8px
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'scale(1.05)',
            boxShadow: theme.palette.mode === 'dark' ? `0 8px 24px ${alpha(theme.palette.common.black, 0.3)}` : '0 8px 24px rgba(0,0,0,0.08)',
          },
        }}
      >
        <CardContent sx={{ py: 2, px: 2.5, '&:last-child': { pb: 2 } }}>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Avatar
              sx={{
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                color: 'text.secondary',
                width: 40,
                height: 40,
              }}
            >
              {icon}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight={600} color="text.primary">
                {value}
              </Typography>
              <Typography variant="caption" color="text.secondary" fontWeight={500}>
                {label}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Grow>
  )
}
