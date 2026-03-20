/**
 * Sidebar header (logo + collapse button + new report button)
 */
import {
  Box,
  Typography,
  Tooltip,
  useTheme,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import { neutral, fontFamilyDisplay } from '@/app/theme'
import {
  LogoContainer,
  LogoBox,
  NewReportButton,
  CollapseButton,
} from './SidebarStyles'

export default function SidebarHeader({ collapsed, handleNavigate, handleToggleSidebar }) {
  const theme = useTheme()

  return (
    <>
      {/* Logo/Header */}
      <LogoContainer collapsed={collapsed}>
        {!collapsed && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              cursor: 'pointer',
            }}
            onClick={() => handleNavigate('/')}
          >
            <LogoBox>
              <img src={`${import.meta.env.BASE_URL}logo.png`} alt="NeuraReport" />
            </LogoBox>
            <Typography
              sx={{
                // Display font for logo text (Space Grotesk)
                fontFamily: fontFamilyDisplay,
                fontSize: '20px',
                fontWeight: 500,
                lineHeight: 'normal',
                letterSpacing: 0,
                color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
              }}
            >
              NeuraReport
            </Typography>
          </Box>
        )}

        {collapsed && (
          <LogoBox onClick={() => handleNavigate('/')} sx={{ cursor: 'pointer' }}>
            <img src={`${import.meta.env.BASE_URL}logo.png`} alt="NeuraReport" />
          </LogoBox>
        )}

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }} />
      </LogoContainer>

      {/* Collapse Button */}
      <CollapseButton
        size="small"
        onClick={handleToggleSidebar}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        data-testid="sidebar-collapse-button"
      >
        {collapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
      </CollapseButton>

      {/* New Report Button */}
      <Box sx={{ p: 1.5, pt: 2 }}>
        <Tooltip title={collapsed ? 'New Report' : ''} placement="right" arrow>
          <NewReportButton
            component="button"
            type="button"
            onClick={() => handleNavigate('/setup/wizard')}
            sx={{ justifyContent: collapsed ? 'center' : 'flex-start' }}
          >
            <AddIcon sx={{ fontSize: 18 }} />
            {!collapsed && (
              <Typography variant="body2" fontWeight={500}>
                New Report
              </Typography>
            )}
          </NewReportButton>
        </Tooltip>
      </Box>
    </>
  )
}
