import { Box, Container, Typography, Tabs, Tab, Paper } from '@mui/material'
import { Outlet, useLocation } from 'react-router-dom'
import { useNavigateInteraction } from '@/components/ux/governance'

const settingsTabs = [
  { label: 'General', path: '/settings/general' },
  { label: 'Database', path: '/settings/database' },
  { label: 'Templates', path: '/settings/templates' },
  { label: 'Notifications', path: '/settings/notifications' },
  { label: 'API', path: '/settings/api' },
]

export default function SettingsLayout({ children }) {
  const navigate = useNavigateInteraction()
  const location = useLocation()

  const currentTab = settingsTabs.findIndex((tab) => location.pathname.startsWith(tab.path))

  return (
    <Box sx={{ py: 3 }}>
      <Container maxWidth="lg">
        <Typography variant="h5" fontWeight={600} sx={{ mb: 3 }}>
          Settings
        </Typography>

        <Paper
          elevation={0}
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,  // Figma spec: 8px
            overflow: 'hidden',
          }}
        >
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={currentTab === -1 ? 0 : currentTab}
              onChange={(_, newValue) =>
                navigate(settingsTabs[newValue].path, {
                  label: `Open ${settingsTabs[newValue].label} settings`,
                  intent: { source: 'settings-layout', tab: settingsTabs[newValue].label },
                })}
              sx={{
                px: 2,
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 500,
                  minHeight: 48,
                },
              }}
            >
              {settingsTabs.map((tab) => (
                <Tab key={tab.path} label={tab.label} />
              ))}
            </Tabs>
          </Box>

          <Box sx={{ p: 3 }}>
            {children || <Outlet />}
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}
