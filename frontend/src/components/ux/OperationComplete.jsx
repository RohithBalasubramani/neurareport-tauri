/**
 * Operation completion feedback
 * Shows success/error state after an operation
 */
import { useEffect } from 'react'
import {
  Box,
  Typography,
  Fade,
  useTheme,
  keyframes,
} from '@mui/material'
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'

const scaleIn = keyframes`
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
`

export default function OperationComplete({
  show,
  success = true,
  message,
  onDismiss,
  autoDismiss = true,
  dismissDelay = 2000,
}) {
  const theme = useTheme()

  useEffect(() => {
    if (show && autoDismiss && onDismiss) {
      const timer = setTimeout(onDismiss, dismissDelay)
      return () => clearTimeout(timer)
    }
  }, [show, autoDismiss, onDismiss, dismissDelay])

  if (!show) return null

  const config = success
    ? {
        icon: SuccessIcon,
        color: theme.palette.text.secondary,
        defaultMessage: 'Done!',
      }
    : {
        icon: ErrorIcon,
        color: theme.palette.text.secondary,
        defaultMessage: 'Something went wrong',
      }

  const Icon = config.icon

  return (
    <Fade in={show}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          animation: `${scaleIn} 0.3s ease-out`,
        }}
      >
        <Icon sx={{ color: config.color }} />
        <Typography variant="body2" fontWeight={500} color={config.color}>
          {message || config.defaultMessage}
        </Typography>
      </Box>
    </Fade>
  )
}
