/**
 * Styled components for the Activity page
 */
import {
  Box,
  Stack,
  IconButton,
  alpha,
  styled,
} from '@mui/material'
import { neutral } from '@/app/theme'
import { fadeInUp } from '@/styles'

export const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1000,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

export const HeaderContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

export const FilterContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out 0.1s both`,
}))

export const ActivityListContainer = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  backdropFilter: 'blur(20px)',
  borderRadius: 8,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  padding: theme.spacing(2),
  boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  animation: `${fadeInUp} 0.5s ease-out 0.2s both`,
}))

export const DeleteButton = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    color: theme.palette.text.primary,
  },
}))

export const EmptyStateContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(6),
  textAlign: 'center',
  animation: `${fadeInUp} 0.5s ease-out`,
}))
