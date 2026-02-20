/**
 * Progress Overlay Components
 * Visible progress indicators for async operations
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Ongoing state visibility (loading / progress / pending)
 * - Optimize perceived speed
 */
import { useState, useEffect, useMemo } from 'react'
import {
  Box,
  Typography,
  LinearProgress,
  CircularProgress,
  Fade,
  Backdrop,
  Paper,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'
import { shimmer } from '@/styles'

// Local animations — differ from shared versions
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
`

const scaleIn = keyframes`
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
`

/**
 * Full-page progress overlay
 * For operations that block the entire page
 */
export function FullPageProgress({
  open,
  label = 'Loading...',
  progress = null,
  description,
  onCancel,
  cancellable = false,
}) {
  const theme = useTheme()

  return (
    <Backdrop
      open={open}
      sx={{
        zIndex: theme.zIndex.modal + 10,
        bgcolor: alpha(theme.palette.background.default, 0.85),
        backdropFilter: 'blur(8px)',
      }}
    >
      <Fade in={open}>
        <Paper
          elevation={0}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
            p: 4,
            minWidth: 320,
            maxWidth: 400,
            bgcolor: alpha(theme.palette.background.paper, 0.9),
            borderRadius: 1,  // Figma spec: 8px
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          }}
        >
          {progress !== null ? (
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={progress}
                size={80}
                thickness={4}
                sx={{
                  color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                }}
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
                <Typography variant="h6" fontWeight={600}>
                  {Math.round(progress)}%
                </Typography>
              </Box>
            </Box>
          ) : (
            <CircularProgress size={60} thickness={4} />
          )}

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" fontWeight={500}>
              {label}
            </Typography>
            {description && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {description}
              </Typography>
            )}
          </Box>

          {progress !== null && (
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                width: '100%',
                height: 8,
                borderRadius: 4,
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                '& .MuiLinearProgress-bar': {
                  bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                },
              }}
            />
          )}

          {cancellable && onCancel && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                cursor: 'pointer',
                '&:hover': { textDecoration: 'underline' },
              }}
              onClick={onCancel}
            >
              Cancel
            </Typography>
          )}
        </Paper>
      </Fade>
    </Backdrop>
  )
}

/**
 * Inline progress indicator
 * For operations within a component
 */
export function InlineProgress({
  loading,
  label,
  progress = null,
  size = 'medium',
  color = 'primary',
}) {
  const theme = useTheme()

  const sizeConfig = {
    small: { spinner: 16, text: 'caption', spacing: 1 },
    medium: { spinner: 24, text: 'body2', spacing: 1.5 },
    large: { spinner: 32, text: 'body1', spacing: 2 },
  }[size]

  if (!loading) return null

  return (
    <Fade in={loading}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: sizeConfig.spacing,
        }}
      >
        <CircularProgress
          size={sizeConfig.spinner}
          color={color}
          variant={progress !== null ? 'determinate' : 'indeterminate'}
          value={progress}
        />
        {label && (
          <Typography variant={sizeConfig.text} color="text.secondary">
            {label}
          </Typography>
        )}
      </Box>
    </Fade>
  )
}

/**
 * Skeleton loader for content placeholders
 */
export function SkeletonLoader({
  variant = 'text',
  width,
  height,
  lines = 1,
  animation = 'shimmer',
}) {
  const theme = useTheme()

  const animationStyle = animation === 'shimmer'
    ? {
        background: `linear-gradient(90deg,
          ${alpha(theme.palette.text.primary, 0.06)} 25%,
          ${alpha(theme.palette.text.primary, 0.12)} 50%,
          ${alpha(theme.palette.text.primary, 0.06)} 75%)`,
        backgroundSize: '200% 100%',
        animation: `${shimmer} 1.5s infinite`,
      }
    : {
        bgcolor: alpha(theme.palette.text.primary, 0.08),
        animation: `${pulse} 1.5s infinite`,
      }

  if (variant === 'text') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {Array.from({ length: lines }).map((_, i) => (
          <Box
            key={i}
            sx={{
              height: height || 16,
              width: i === lines - 1 && lines > 1 ? '60%' : width || '100%',
              borderRadius: 1,
              ...animationStyle,
            }}
          />
        ))}
      </Box>
    )
  }

  if (variant === 'circular') {
    return (
      <Box
        sx={{
          width: width || 40,
          height: height || 40,
          borderRadius: '50%',
          ...animationStyle,
        }}
      />
    )
  }

  if (variant === 'rectangular') {
    return (
      <Box
        sx={{
          width: width || '100%',
          height: height || 120,
          borderRadius: 1,  // Figma spec: 8px
          ...animationStyle,
        }}
      />
    )
  }

  return null
}

/**
 * Operation completion feedback
 * Shows success/error state after an operation
 */
export function OperationComplete({
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

/**
 * Step progress indicator
 * For multi-step operations
 */
export function StepProgress({
  steps,
  currentStep,
  status = 'in_progress', // 'pending' | 'in_progress' | 'completed' | 'error'
}) {
  const theme = useTheme()

  const getStepStatus = (index) => {
    if (index < currentStep) return 'completed'
    if (index === currentStep) return status
    return 'pending'
  }

  const getStepColor = (stepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
      case 'in_progress':
        return theme.palette.mode === 'dark' ? neutral[300] : neutral[900]
      case 'error':
        return theme.palette.text.secondary
      default:
        return alpha(theme.palette.text.primary, 0.3)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {steps.map((step, index) => {
        const stepStatus = getStepStatus(index)
        const color = getStepColor(stepStatus)

        return (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: stepStatus === 'completed' ? color : 'transparent',
                border: `2px solid ${color}`,
                transition: 'all 0.3s ease',
              }}
            >
              {stepStatus === 'completed' ? (
                <SuccessIcon sx={{ fontSize: 16, color: 'common.white' }} />
              ) : stepStatus === 'in_progress' ? (
                <CircularProgress size={12} sx={{ color }} />
              ) : (
                <Typography variant="caption" fontWeight={600} sx={{ color }}>
                  {index + 1}
                </Typography>
              )}
            </Box>
            <Typography
              variant="body2"
              sx={{
                color: stepStatus === 'pending'
                  ? alpha(theme.palette.text.primary, 0.5)
                  : theme.palette.text.primary,
                fontWeight: stepStatus === 'in_progress' ? 600 : 400,
              }}
            >
              {step}
            </Typography>
          </Box>
        )
      })}
    </Box>
  )
}
