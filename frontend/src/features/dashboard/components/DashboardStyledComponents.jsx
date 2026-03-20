import { Box, alpha, styled } from '@mui/material'
import { neutral } from '@/app/theme'
import { fadeInUp } from '@/styles'

export const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1600,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  position: 'relative',

  // Subtle gradient background
  '&::before': {
    content: '""',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: theme.palette.mode === 'dark'
      ? `radial-gradient(ellipse at top left, ${alpha(theme.palette.text.primary, 0.04)} 0%, transparent 50%),
         radial-gradient(ellipse at bottom right, ${alpha(theme.palette.text.primary, 0.03)} 0%, transparent 50%)`
      : 'none',
    pointerEvents: 'none',
    zIndex: -1,
  },
}))

export const StatCardStyled = styled(Box, {
  shouldForwardProp: (prop) => !['color', 'delay'].includes(prop),
})(({ theme, color = 'inherit', delay = 0 }) => ({
  position: 'relative',
  padding: theme.spacing(2.5),
  minHeight: 110,
  borderRadius: 8,
  backgroundColor: theme.palette.mode === 'dark'
    ? alpha(theme.palette.background.paper, 0.6)
    : theme.palette.common.white,
  backdropFilter: 'none',
  border: 'none',
  boxShadow: theme.palette.mode === 'dark'
    ? 'none'
    : '0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05)',
  cursor: 'pointer',
  overflow: 'hidden',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  animation: `${fadeInUp} 0.5s ease-out ${delay}ms both`,

  '&:hover': {
    boxShadow: theme.palette.mode === 'dark'
      ? '0 4px 12px rgba(0,0,0,0.3)'
      : '0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)',
  },
}))

export const QuickActionCard = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
  padding: theme.spacing(1.5, 2),
  borderRadius: 8,
  backgroundColor: 'transparent',
  border: 'none',
  cursor: 'pointer',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',

  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.04)' : neutral[100],

    '& .action-arrow': {
      transform: 'translateX(4px)',
      opacity: 1,
    },

    '& .action-icon': {
      color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
    },
  },
}))

export const OnboardingStep = styled(Box, {
  shouldForwardProp: (prop) => !['completed', 'disabled'].includes(prop),
})(({ theme, completed, disabled }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius * 1.5,
  backgroundColor: completed
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100])
    : alpha(theme.palette.action.hover, 0.3),
  border: `1px solid ${completed
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200])
    : alpha(theme.palette.divider, 0.1)}`,
  cursor: disabled ? 'not-allowed' : 'pointer',
  opacity: disabled ? 0.5 : 1,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',

  ...(!disabled && !completed && {
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
      borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],
      transform: 'translateX(4px)',
    },
  }),
}))

export const JobListItem = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'status',
})(({ theme, status }) => {
  const statusColors = {
    completed: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    running: theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
    pending: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
    failed: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  }

  return {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
    padding: theme.spacing(1.5, 0),
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.08)}`,
    transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
    cursor: 'pointer',

    '&:last-child': {
      borderBottom: 'none',
    },

    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
      paddingLeft: theme.spacing(1),
      paddingRight: theme.spacing(1),
      marginLeft: theme.spacing(-1),
      marginRight: theme.spacing(-1),
      borderRadius: theme.shape.borderRadius,

      '& .job-arrow': {
        opacity: 1,
        transform: 'translateX(0)',
      },
    },

    '& .status-dot': {
      width: 8,
      height: 8,
      borderRadius: '50%',
      backgroundColor: statusColors[status] || neutral[500],
      boxShadow: `0 0 8px ${alpha(statusColors[status] || neutral[500], 0.3)}`,
    },
  }
})

export const RecommendationCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5),
  borderRadius: theme.shape.borderRadius * 1.5,
  backgroundColor: theme.palette.mode === 'dark'
    ? alpha(theme.palette.background.paper, 0.4)
    : alpha(theme.palette.background.paper, 0.8),
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  cursor: 'pointer',
  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',

  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: theme.palette.mode === 'dark'
      ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.03)} 0%, transparent 50%)`
      : `linear-gradient(135deg, rgba(0,0,0,0.02) 0%, transparent 50%)`,
    opacity: 0,
    transition: 'opacity 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
  },

  '&:hover': {
    transform: 'translateY(-4px) scale(1.02)',
    boxShadow: theme.palette.mode === 'dark'
      ? `0 12px 24px ${alpha(theme.palette.common.black, 0.3)}`
      : '0 12px 24px rgba(0,0,0,0.08)',
    borderColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[200],

    '&::before': {
      opacity: 1,
    },
  },
}))

export const MiniChart = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'flex-end',
  gap: 4,
  height: 50,
  padding: theme.spacing(1, 0),
}))

export const ChartBar = styled(Box, {
  shouldForwardProp: (prop) => !['height', 'color', 'delay'].includes(prop),
})(({ theme, height, color, delay = 0 }) => ({
  flex: 1,
  height: `${height}%`,
  minHeight: 4,
  backgroundColor: color || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
  borderRadius: 1,
  transition: 'height 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
  transitionDelay: `${delay}ms`,
}))
