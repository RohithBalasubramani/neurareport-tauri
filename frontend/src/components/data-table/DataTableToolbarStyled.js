/**
 * Styled components for DataTableToolbar
 */
import {
  Box,
  TextField,
  Button,
  Stack,
  Typography,
  Chip,
  Menu,
  MenuItem,
  IconButton,
  Badge,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import { neutral } from '@/app/theme'

// =============================================================================
// ANIMATIONS
// =============================================================================

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const ToolbarContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2.5, 3),
  backgroundColor: alpha(theme.palette.background.paper, 0.4),
  backdropFilter: 'blur(10px)',
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
}))

export const HeaderRow = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}))

export const TitleSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(0.25),
}))

export const Title = styled(Typography)(({ theme }) => ({
  fontSize: '1.125rem',
  fontWeight: 600,
  color: theme.palette.text.primary,
  letterSpacing: '-0.01em',
}))

export const Subtitle = styled(Typography)(({ theme }) => ({
  fontSize: '14px',
  color: theme.palette.text.secondary,
}))

export const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
  padding: theme.spacing(0.75, 2),
  transition: 'all 0.2s ease',
  '&.MuiButton-outlined': {
    borderColor: alpha(theme.palette.divider, 0.2),
    '&:hover': {
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    },
  },
  '&.MuiButton-contained': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.15)}`,
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      boxShadow: `0 6px 20px ${alpha(theme.palette.common.black, 0.2)}`,
      transform: 'translateY(-1px)',
    },
  },
}))

export const SelectionBar = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  padding: theme.spacing(1.5, 2),
  background: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  borderRadius: 8,  // Figma spec: 8px
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  animation: `${slideIn} 0.3s ease-out`,
}))

export const SelectionText = styled(Typography)(({ theme }) => ({
  fontSize: '14px',
  fontWeight: 500,
  color: theme.palette.text.primary,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}))

export const SelectionBadge = styled(Box)(({ theme }) => ({
  width: 24,
  height: 24,
  borderRadius: 8,
  backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  color: theme.palette.common.white,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.75rem',
  fontWeight: 600,
}))

export const SelectionAction = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontSize: '0.75rem',
  fontWeight: 500,
  padding: theme.spacing(0.5, 1.5),
  minWidth: 'auto',
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.text.primary, 0.1),
  '&:hover': {
    borderColor: alpha(theme.palette.text.primary, 0.2),
    backgroundColor: alpha(theme.palette.text.primary, 0.04),
  },
}))

export const DeleteAction = styled(SelectionAction)(({ theme }) => ({
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.3),
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const SearchField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,  // Figma spec: 8px
    backgroundColor: alpha(theme.palette.background.paper, 0.6),
    transition: 'all 0.2s ease',
    '& fieldset': {
      borderColor: alpha(theme.palette.divider, 0.1),
      transition: 'all 0.2s ease',
    },
    '&:hover fieldset': {
      borderColor: alpha(theme.palette.divider, 0.3),
    },
    '&.Mui-focused': {
      backgroundColor: theme.palette.background.paper,
      boxShadow: `0 0 0 3px ${alpha(theme.palette.divider, 0.1)}`,
      '& fieldset': {
        borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      },
    },
  },
  '& .MuiInputBase-input': {
    fontSize: '0.875rem',
    padding: theme.spacing(1, 1.5),
    '&::placeholder': {
      color: theme.palette.text.disabled,
      opacity: 1,
    },
  },
}))

export const FilterButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '14px',
  padding: theme.spacing(0.75, 1.5),
  color: theme.palette.text.secondary,
  borderColor: alpha(theme.palette.divider, 0.2),
  '&:hover': {
    borderColor: alpha(theme.palette.divider, 0.3),
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  },
  '&.active': {
    color: theme.palette.text.primary,
    borderColor: alpha(theme.palette.divider, 0.5),
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const FilterChip = styled(Chip)(({ theme }) => ({
  borderRadius: 8,
  height: 28,
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  color: theme.palette.text.secondary,
  fontWeight: 500,
  fontSize: '0.75rem',
  animation: `${slideIn} 0.2s ease-out`,
  '& .MuiChip-deleteIcon': {
    color: theme.palette.text.disabled,
    fontSize: 16,
    '&:hover': {
      color: theme.palette.text.secondary,
    },
  },
}))

export const IconButtonStyled = styled(IconButton)(({ theme }) => ({
  borderRadius: 8,  // Figma spec: 8px
  color: theme.palette.text.secondary,
  transition: 'all 0.2s ease',
  '&:hover': {
    color: theme.palette.text.primary,
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
}))

export const StyledMenu = styled(Menu)(({ theme }) => ({
  '& .MuiPaper-root': {
    backgroundColor: alpha(theme.palette.background.paper, 0.95),
    backdropFilter: 'blur(20px)',
    borderRadius: 8,  // Figma spec: 8px
    border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.12)}`,
    minWidth: 200,
    marginTop: theme.spacing(0.5),
  },
}))

export const MenuSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 0),
}))

export const MenuLabel = styled(Typography)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: theme.palette.text.disabled,
}))

export const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  fontSize: '14px',
  padding: theme.spacing(1, 2),
  borderRadius: 6,
  margin: theme.spacing(0, 1),
  transition: 'all 0.15s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    color: theme.palette.text.primary,
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.16) : neutral[200],
    },
  },
}))

export const FilterBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
    color: theme.palette.common.white,
    fontSize: '10px',
    fontWeight: 600,
    minWidth: 16,
    height: 16,
    borderRadius: 6,
    padding: '0 4px',
  },
}))
