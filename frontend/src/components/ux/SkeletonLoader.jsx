/**
 * Skeleton loader for content placeholders
 */
import {
  Box,
  useTheme,
  alpha,
  keyframes,
} from '@mui/material'
import { shimmer } from '@/styles'

// Local pulse animation
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
`

export default function SkeletonLoader({
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
