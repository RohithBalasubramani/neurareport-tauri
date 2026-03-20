/**
 * Content Skeleton - Pre-built skeleton patterns
 */
import { Box } from '@mui/material'
import Skeleton from './SkeletonLoader'

export default function ContentSkeleton({ type = 'card', count = 1 }) {
  const items = Array.from({ length: count })

  if (type === 'card') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.map((_, i) => (
          <Box key={i} sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>  {/* Figma spec: 8px */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Skeleton variant="circular" width={48} height={48} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width="60%" height={20} />
                <Skeleton variant="text" width="40%" height={16} sx={{ mt: 1 }} />
              </Box>
            </Box>
            <Skeleton variant="text" lines={3} />
          </Box>
        ))}
      </Box>
    )
  }

  if (type === 'list') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {items.map((_, i) => (
          <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 1 }}>
            <Skeleton variant="circular" width={40} height={40} />
            <Box sx={{ flex: 1 }}>
              <Skeleton variant="text" width="70%" />
              <Skeleton variant="text" width="50%" height={14} sx={{ mt: 0.5 }} />
            </Box>
          </Box>
        ))}
      </Box>
    )
  }

  if (type === 'table') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        <Skeleton variant="rectangular" height={48} />
        {items.map((_, i) => (
          <Skeleton key={i} variant="rectangular" height={52} />
        ))}
      </Box>
    )
  }

  if (type === 'chat') {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {items.map((_, i) => (
          <Box
            key={i}
            sx={{
              display: 'flex',
              gap: 2,
              alignSelf: i % 2 === 0 ? 'flex-start' : 'flex-end',
              maxWidth: '70%',
            }}
          >
            {i % 2 === 0 && <Skeleton variant="circular" width={36} height={36} />}
            <Skeleton variant="rounded" width={200 + Math.random() * 100} height={60 + Math.random() * 40} />
            {i % 2 !== 0 && <Skeleton variant="circular" width={36} height={36} />}
          </Box>
        ))}
      </Box>
    )
  }

  return <Skeleton variant="rectangular" />
}
