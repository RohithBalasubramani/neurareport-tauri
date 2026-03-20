/**
 * Premium Sidebar Navigation
 * Sophisticated sidebar with glassmorphism, smooth animations, and modern interactions
 */
import { useTheme } from '@mui/material'
import { Box, Drawer, alpha } from '@mui/material'
import { useSidebarNavigation, useSidebarSections, useSidebarControls, useSidebarActiveState } from './hooks/useSidebar'
import { SidebarContainer } from './components/SidebarStyles'
import NAV_ITEMS from './components/SidebarNavItems'
import SidebarHeader from './components/SidebarHeader'
import SidebarSection from './components/SidebarSection'
import SidebarFooter from './components/SidebarFooter'

export default function Sidebar({ width, collapsed, mobileOpen, onClose, onToggle }) {
  const theme = useTheme()
  const { handleNavigate, executeUI } = useSidebarNavigation(onClose)
  const { expandedSections, handleToggleSection } = useSidebarSections(executeUI)
  const { handleToggleSidebar, handleCloseSidebar } = useSidebarControls(executeUI, collapsed, onToggle, onClose)
  const { isActive, activeJobs } = useSidebarActiveState()

  const sidebarContent = (
    <SidebarContainer>
      <SidebarHeader
        collapsed={collapsed}
        handleNavigate={handleNavigate}
        handleToggleSidebar={handleToggleSidebar}
      />

      {/* Navigation */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 1,
          '&::-webkit-scrollbar': { width: 4 },
          '&::-webkit-scrollbar-track': { backgroundColor: 'transparent' },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: alpha(theme.palette.text.primary, 0.1),
            borderRadius: 1,  // Figma spec: 8px
          },
        }}
      >
        {NAV_ITEMS.map((section, sectionIndex) => (
          <SidebarSection
            key={section.section}
            section={section}
            collapsed={collapsed}
            isExpanded={expandedSections[section.section] !== false}
            isLast={sectionIndex === NAV_ITEMS.length - 1}
            activeJobs={activeJobs}
            isActive={isActive}
            handleNavigate={handleNavigate}
            handleToggleSection={handleToggleSection}
          />
        ))}
      </Box>

      <SidebarFooter collapsed={collapsed} />
    </SidebarContainer>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width,
          flexShrink: 0,
          transition: (theme) => theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: 200,
          }),
          '& .MuiDrawer-paper': {
            width,
            boxSizing: 'border-box',
            borderRight: 'none',
            bgcolor: 'transparent',
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: 200,
            }),
          },
        }}
        open
      >
        {sidebarContent}
      </Drawer>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleCloseSidebar}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: 280,
            boxSizing: 'border-box',
            bgcolor: 'transparent',
          },
        }}
      >
        {sidebarContent}
      </Drawer>
    </>
  )
}
