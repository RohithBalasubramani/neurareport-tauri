import { Button, alpha, styled } from '@mui/material'
import { neutral } from '@/app/theme'

export const OAuthButtonStyled = styled(Button, {
  shouldForwardProp: (prop) => !['connected', 'providerColor'].includes(prop),
})(({ theme, connected, providerColor }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  padding: theme.spacing(1.5, 3),
  backgroundColor: connected
    ? alpha(theme.palette.text.secondary, 0.05)
    : alpha(providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.1),
  color: connected
    ? theme.palette.text.secondary
    : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
  border: `1px solid ${alpha(connected ? theme.palette.text.secondary : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.3)}`,
  '&:hover': {
    backgroundColor: alpha(connected ? theme.palette.text.secondary : providerColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.15),
  },
  '&:disabled': {
    opacity: 0.6,
  },
}))
