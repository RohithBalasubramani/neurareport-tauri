/**
 * Sidebar navigation item styled components
 */
import {
  Box,
  alpha,
  styled,
} from '@mui/material'
import {
  neutral,
  fontFamilyUI,
} from '@/app/theme'
import { FIGMA_SIDEBAR } from './SidebarStyles'

export const SectionHeader = styled(Box, {
  shouldForwardProp: (prop) => !['collapsed', 'collapsible'].includes(prop),
})(({ theme, collapsed, collapsible }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 2, 0.75),
  cursor: collapsible ? 'pointer' : 'default',

  ...(collapsible && {
    '&:hover': {
      '& .expand-icon': {
        color: theme.palette.text.secondary,
      },
    },
  }),
}))

// FIGMA NAV ITEM BUTTON (EXACT from Figma sidebar navigation specs)
// Height: 40px, Gap: 8px (icon to text), Border-radius: 8px
// Active: #E9E8E6 background, Text: Inter Medium 16px
export const NavItemButton = styled(Box, {
  shouldForwardProp: (prop) => !['active', 'collapsed', 'highlight'].includes(prop),
})(({ theme, active, collapsed, highlight }) => ({
  border: 'none',
  backgroundColor: 'transparent',
  display: 'flex',
  alignItems: 'center',
  gap: 8,  // 8px gap from Figma
  padding: '10px 12px',
  margin: 0,
  borderRadius: 8,  // 8px from Figma
  cursor: 'pointer',
  position: 'relative',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  justifyContent: collapsed ? 'center' : 'flex-start',
  height: FIGMA_SIDEBAR.itemHeight,  // 40px from Figma
  fontFamily: fontFamilyUI,  // Inter from Figma
  width: '100%',
  textAlign: 'left',
  font: 'inherit',

  // Active state from Figma - Grey/400 background
  ...(active && {
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.common.white, 0.08)
      : neutral[200],  // #E9E8E6 from Figma
    color: theme.palette.mode === 'dark'
      ? neutral[100]
      : neutral[900],  // #21201C from Figma
  }),

  // Inactive state - Grey/1100 text
  ...(!active && {
    color: theme.palette.mode === 'dark'
      ? neutral[500]  // #8D8D86
      : neutral[700],  // #63635E from Figma

    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark'
        ? alpha(theme.palette.common.white, 0.04)
        : neutral[100],  // #F1F0EF on hover
      color: theme.palette.mode === 'dark'
        ? neutral[100]
        : neutral[900],  // #21201C on hover
    },
  }),

  // Highlight items - same as regular, no special treatment
  ...(highlight && !active && {
    backgroundColor: 'transparent',

    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark'
        ? alpha(theme.palette.common.white, 0.04)
        : neutral[100],
    },
  }),

  '&:focus-visible': {
    outline: `2px solid ${alpha(theme.palette.text.primary, 0.35)}`,
    outlineOffset: 2,
  },
}))

// FIGMA NAV ICON (EXACT from Figma: 20x20px)
export const NavIcon = styled(Box, {
  shouldForwardProp: (prop) => !['active', 'highlight'].includes(prop),
})(({ theme, active, highlight }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  width: FIGMA_SIDEBAR.iconSize,  // 20px from Figma
  height: FIGMA_SIDEBAR.iconSize,  // 20px from Figma
  flexShrink: 0,
  transition: 'transform 0.2s ease',

  '& svg': {
    fontSize: FIGMA_SIDEBAR.iconSize,  // 20px from Figma
    // Icon color from Figma - Grey/900 for inactive, Grey/1100 for active
    color: active
      ? (theme.palette.mode === 'dark' ? neutral[100] : neutral[700])
      : (theme.palette.mode === 'dark' ? neutral[500] : neutral[500]),
  },
}))
