/**
 * Enhanced Loading State Component
 * Provides consistent loading feedback across the application
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Ongoing state visibility (loading / progress / pending)
 * - Optimize perceived speed
 */
import {
  LinearProgress,
  Stack,
  Typography,
  Box,
  CircularProgress,
  Fade,
} from '@mui/material'

/**
 * Primary Loading State Component
 */
export default function LoadingState({
  label = 'Loading\u2026',
  description,
  progress = null,
  inline = false,
  dense = false,
  color = 'primary',
  variant = 'linear', // 'linear' | 'circular' | 'skeleton'
  size = 'medium', // 'small' | 'medium' | 'large'
  centered = false,
  sx = [],
  ...props
}) {
  const sxArray = Array.isArray(sx) ? sx : [sx]
  const spacing = inline || dense ? 0.75 : 1.5
  const width = inline ? 'auto' : '100%'

  // Size configurations
  const sizeConfig = {
    small: { circular: 20, text: 'caption' },
    medium: { circular: 32, text: 'body2' },
    large: { circular: 48, text: 'body1' },
  }[size]

  // Circular variant
  if (variant === 'circular') {
    return (
      <Fade in>
        <Stack
          direction={inline ? 'row' : 'column'}
          spacing={spacing}
          alignItems="center"
          justifyContent={centered ? 'center' : 'flex-start'}
          role="status"
          aria-live="polite"
          sx={[{ width: centered ? '100%' : width }, ...sxArray]}
          {...props}
        >
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              size={sizeConfig.circular}
              color={color}
              variant={progress != null ? 'determinate' : 'indeterminate'}
              value={progress ?? undefined}
            />
            {progress != null && (
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="caption" fontWeight={600}>
                  {Math.round(progress)}%
                </Typography>
              </Box>
            )}
          </Box>
          {label && (
            <Typography variant={sizeConfig.text} color="text.secondary">
              {label}
            </Typography>
          )}
        </Stack>
      </Fade>
    )
  }

  // Default linear variant
  return (
    <Fade in>
      <Stack
        direction="column"
        spacing={spacing}
        role="status"
        aria-live="polite"
        sx={[
          {
            width,
            maxWidth: inline ? '100%' : 440,
          },
          ...sxArray,
        ]}
        {...props}
      >
        <Typography variant={sizeConfig.text} color="text.secondary">
          {label}
        </Typography>
        <LinearProgress
          variant={progress == null ? 'indeterminate' : 'determinate'}
          value={progress ?? undefined}
          color={color}
          aria-label={label}
          sx={{ borderRadius: 1, height: size === 'small' ? 3 : size === 'large' ? 6 : 4 }}  // Figma spec: 8px
        />
        {description && (
          <Typography variant="caption" color="text.secondary">
            {description}
          </Typography>
        )}
      </Stack>
    </Fade>
  )
}

/**
 * Inline Loading Indicator
 * For use within buttons or inline content
 */
export function InlineLoading({ size = 16, color = 'inherit', sx = [] }) {
  const sxArray = Array.isArray(sx) ? sx : [sx]
  return (
    <CircularProgress
      size={size}
      color={color}
      sx={[{ ml: 1 }, ...sxArray]}
    />
  )
}

// Re-export for backward compatibility
export { default as Skeleton } from './SkeletonLoader'
export { default as ContentSkeleton } from './ContentSkeleton'
