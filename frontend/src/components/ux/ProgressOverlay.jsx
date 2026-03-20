/**
 * Progress Overlay Components
 * Visible progress indicators for async operations
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Ongoing state visibility (loading / progress / pending)
 * - Optimize perceived speed
 */
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
} from '@mui/material'
import { neutral } from '@/app/theme'

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

// Re-export sub-components for backward compatibility
export { default as SkeletonLoader } from './SkeletonLoader'
export { default as OperationComplete } from './OperationComplete'
export { default as StepProgress } from './StepProgress'
