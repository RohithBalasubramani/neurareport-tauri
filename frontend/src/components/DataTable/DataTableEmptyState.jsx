/**
 * Premium Data Table Empty State
 * Beautiful empty state with animations and call-to-action
 */
import {
  Box,
  Typography,
  Button,
  useTheme,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { Inbox as InboxIcon, Add as AddIcon } from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'
import { float, shimmer } from '@/styles'

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

const pulse = keyframes`
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const EmptyContainer = styled(Box)(({ theme }) => ({
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

const IconContainer = styled(Box)(({ theme }) => ({
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

const StyledIcon = styled(Box)(({ theme }) => ({
  fontSize: 32,
  color: theme.palette.text.secondary,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const Title = styled(Typography)(({ theme }) => ({
  fontSize: '1.125rem',
  fontWeight: 600,
  color: theme.palette.text.primary,
  marginBottom: theme.spacing(0.5),
  letterSpacing: '-0.01em',
}))

const Description = styled(Typography)(({ theme }) => ({
  fontSize: '0.875rem',
  color: theme.palette.text.secondary,
  maxWidth: 360,
  marginBottom: theme.spacing(3),
  lineHeight: 1.6,
}))

const ActionButton = styled(Button)(({ theme }) => ({
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

const SecondaryButton = styled(Button)(({ theme }) => ({
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

const DecorativeDots = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  marginTop: theme.spacing(4),
  '& span': {
    width: 6,
    height: 6,
    borderRadius: '50%',
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    '&:nth-of-type(2)': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

const IllustrationLines = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: 40,
  left: '50%',
  transform: 'translateX(-50%)',
  display: 'flex',
  flexDirection: 'column',
  gap: 6,
  opacity: 0.3,
  '& span': {
    height: 4,
    borderRadius: 1,  // Figma spec: 8px
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    '&:nth-of-type(1)': { width: 120 },
    '&:nth-of-type(2)': { width: 80, marginLeft: 20 },
    '&:nth-of-type(3)': { width: 100, marginLeft: 10 },
  },
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DataTableEmptyState({
  icon: Icon = InboxIcon,
  title = 'No data',
  description,
  action,
  actionLabel,
  onAction,
  secondaryAction,
  secondaryActionLabel,
  onSecondaryAction,
}) {
  const theme = useTheme()

  return (
    <EmptyContainer>
      <IconContainer>
        <StyledIcon as={Icon} />
      </IconContainer>

      <Title>{title}</Title>

      {description && <Description>{description}</Description>}

      <Box sx={{ display: 'flex', gap: 1.5 }}>
        {(action || onAction) && (
          <ActionButton
            onClick={onAction}
            startIcon={action?.icon || <AddIcon />}
          >
            {actionLabel || action?.label || 'Get Started'}
          </ActionButton>
        )}

        {(secondaryAction || onSecondaryAction) && (
          <SecondaryButton
            variant="outlined"
            onClick={onSecondaryAction}
            startIcon={secondaryAction?.icon}
          >
            {secondaryActionLabel || secondaryAction?.label || 'Learn More'}
          </SecondaryButton>
        )}
      </Box>

    </EmptyContainer>
  )
}
