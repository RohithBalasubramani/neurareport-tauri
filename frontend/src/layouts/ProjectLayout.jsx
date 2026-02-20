/**
 * Premium Project Layout
 * Sophisticated shell with glassmorphism effects and smooth transitions
 */

import { useState, useCallback } from 'react'
import {
  Box,
  useMediaQuery,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import { Outlet } from 'react-router-dom'
import Sidebar from '../navigation/Sidebar'
import TopNav from '../navigation/TopNav'
import OfflineBanner from '../components/OfflineBanner'
import { useAppStore } from '../stores'
import { fadeIn } from '@/styles'

// =============================================================================
// CONSTANTS
// =============================================================================

// FIGMA SPEC: Sidebar width = 250px
const SIDEBAR_WIDTH = 250
const SIDEBAR_COLLAPSED_WIDTH = 64

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const LayoutRoot = styled(Box)(({ theme }) => ({
  display: 'flex',
  minHeight: '100vh',
  // Clean, flat background - NO gradients
  backgroundColor: theme.palette.background.default,
  position: 'relative',
}))

const MainContent = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'isMobile',
})(({ theme, isMobile }) => ({
  flexGrow: 1,
  minWidth: 0, // allow flex children to shrink instead of forcing horizontal overflow
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
  // The permanent MUI Drawer already reserves layout space; avoid double-offsetting.
  marginLeft: 0,
  position: 'relative',
  zIndex: 1,
}))

const PageContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'auto',
  backgroundColor: 'transparent',
  // Warm chart-paper grid overlay (webshell desktop UI pattern)
  backgroundImage: theme.palette.mode === 'dark'
    ? 'none'
    : `repeating-linear-gradient(to right, rgba(59, 130, 246, 0.02) 0, rgba(59, 130, 246, 0.02) 1px, transparent 1px, transparent 60px), repeating-linear-gradient(to bottom, rgba(59, 130, 246, 0.02) 0, rgba(59, 130, 246, 0.02) 1px, transparent 1px, transparent 60px)`,
  animation: `${fadeIn} 0.3s cubic-bezier(0.22, 1, 0.36, 1)`,

  // Custom scrollbar styling
  '&::-webkit-scrollbar': {
    width: 8,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    borderRadius: 4,
    '&:hover': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ProjectLayout({ children }) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const activeConnection = useAppStore((s) => s.activeConnection)

  const handleToggleSidebar = useCallback(() => {
    if (isMobile) {
      setMobileOpen((prev) => !prev)
    } else {
      setSidebarCollapsed((prev) => !prev)
    }
  }, [isMobile])

  const handleCloseMobile = useCallback(() => {
    setMobileOpen(false)
  }, [])

  const sidebarWidth = sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH

  return (
    <LayoutRoot>
      {/* Sidebar */}
      <Sidebar
        width={sidebarWidth}
        collapsed={sidebarCollapsed}
        mobileOpen={mobileOpen}
        onClose={handleCloseMobile}
        onToggle={handleToggleSidebar}
      />

      {/* Main Content */}
      <MainContent isMobile={isMobile}>
        {/* Offline Banner */}
        <OfflineBanner />

        {/* Top Navigation */}
        <TopNav
          onMenuClick={handleToggleSidebar}
          showMenuButton={isMobile}
          connection={activeConnection}
        />

        {/* Page Content */}
        <PageContent>
          {children || <Outlet />}
        </PageContent>
      </MainContent>
    </LayoutRoot>
  )
}

export { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH }
