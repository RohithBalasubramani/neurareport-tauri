/**
 * Sidebar container styled components and constants
 */
import {
  Box,
  IconButton,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import {
  neutral,
  primary,
  secondary,
  palette,
  figmaSpacing,
  fontFamilyUI,
} from '@/app/theme'

// =============================================================================
// FIGMA DESIGN CONSTANTS (EXACT from Figma specs)
// =============================================================================
export const FIGMA_SIDEBAR = {
  width: figmaSpacing.sidebarWidth,  // 250px
  background: neutral[50],         // #F9F9F8
  padding: { horizontal: 16, vertical: 20 },
  borderRadius: 8,
  itemHeight: 40,
  itemGap: 12,
  iconSize: 20,
}

// =============================================================================
// ANIMATIONS (local — differ from shared versions)
// =============================================================================

export const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`

export const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`

export const glow = keyframes`
  0%, 100% { box-shadow: 0 0 10px ${alpha(secondary.violet[500], 0.3)}; }
  50% { box-shadow: 0 0 20px ${alpha(secondary.violet[500], 0.5)}; }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const SidebarContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  width: FIGMA_SIDEBAR.width,  // 250px from Figma
  // Sidebar background from Figma - Grey/200
  backgroundColor: theme.palette.mode === 'dark' ? palette.scale[1000] : neutral[50],
  borderRight: 'none',  // No border per Figma design
  borderRadius: FIGMA_SIDEBAR.borderRadius,  // 8px from Figma
  padding: `${FIGMA_SIDEBAR.padding.vertical}px ${FIGMA_SIDEBAR.padding.horizontal}px`,
  position: 'relative',
}))

export const LogoContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'collapsed',
})(({ theme, collapsed }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: collapsed ? 'center' : 'space-between',
  padding: theme.spacing(2.5, 2),
  minHeight: 64,
  borderBottom: 'none',
}))

export const LogoBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: 32,
  height: 32,
  borderRadius: 6,
  overflow: 'hidden',
  '& img': {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  },
}))

export const NewReportButton = styled(Box)(({ theme }) => ({
  border: 'none',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1, 1.5),
  borderRadius: 0,
  height: 40,
  backgroundColor: 'transparent',
  color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  cursor: 'pointer',
  transition: 'background-color 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  width: '100%',
  textAlign: 'left',
  font: 'inherit',

  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.common.white, 0.04)
      : neutral[100],  // Grey/300
  },

  '&:focus-visible': {
    outline: `2px solid ${alpha(theme.palette.text.primary, 0.35)}`,
    outlineOffset: 2,
  },
}))

export const CollapseButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  right: -14,
  top: 72,
  width: 28,
  height: 28,
  backgroundColor: theme.palette.mode === 'dark' ? neutral[900] : theme.palette.common.white,
  border: `1px solid ${theme.palette.mode === 'dark' ? neutral[700] : neutral[200]}`,
  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  transition: 'all 0.2s ease',
  zIndex: 1,
  color: theme.palette.mode === 'dark' ? neutral[400] : neutral[600],
  opacity: 1,

  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[700] : neutral[100],
    color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
    transform: 'scale(1.1)',
  },

  '& svg': {
    fontSize: 16,
  },
}))
