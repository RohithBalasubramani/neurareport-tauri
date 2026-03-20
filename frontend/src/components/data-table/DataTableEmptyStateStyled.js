/**
 * Styled components for DataTableEmptyState
 */
import {
  Box,
  Typography,
  Button,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { float } from '@/styles'

// =============================================================================
// ANIMATIONS (local — differ from shared versions)
// =============================================================================

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const EmptyContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(8, 4),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  textAlign: 'center',
  backgroundColor: 'transparent',
  position: 'relative',
  overflow: 'hidden',
  animation: `${fadeIn} 0.5s ease-out`,
}))

export const IconContainer = styled(Box)(({ theme }) => ({
  width: 64,
  height: 64,
  borderRadius: 24,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(3),
  position: 'relative',
  animation: `${float} 3s infinite ease-in-out`,
}))

export const StyledIcon = styled(Box)(({ theme }) => ({
  fontSize: 32,
  color: theme.palette.text.secondary,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

export const Title = styled(Typography)(({ theme }) => ({
  fontSize: '1.125rem',
  fontWeight: 600,
  color: theme.palette.text.primary,
  marginBottom: theme.spacing(0.5),
  letterSpacing: '-0.01em',
}))

export const Description = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: theme.palette.text.secondary,
  maxWidth: 360,
  marginBottom: theme.spacing(3),
  lineHeight: 1.6,
}))

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '0.875rem',
  padding: theme.spacing(1.25, 3),
  backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  boxShadow: `0 4px 16px ${alpha(theme.palette.common.black, 0.15)}`,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 24px ${alpha(theme.palette.common.black, 0.2)}`,
  },
  '&:active': {
    transform: 'translateY(0)',
  },
}))

export const SecondaryButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.875rem',
  padding: theme.spacing(1.25, 3),
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.2),
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    color: theme.palette.text.primary,
  },
}))
