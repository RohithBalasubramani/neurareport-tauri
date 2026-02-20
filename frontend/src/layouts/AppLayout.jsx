import { Box } from '@mui/material'
import { Outlet } from 'react-router-dom'
import { ToastProvider } from '../components/ToastProvider'

export default function AppLayout({ children }) {
  return (
    <ToastProvider>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        {children || <Outlet />}
      </Box>
    </ToastProvider>
  )
}
