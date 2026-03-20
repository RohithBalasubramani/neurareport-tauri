/**
 * Sidebar footer with user avatar
 */
import {
  Box,
  Typography,
  Avatar,
  useTheme,
} from '@mui/material'
import { neutral } from '@/app/theme'

export default function SidebarFooter({ collapsed }) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        p: 2,
        borderTop: 'none',
      }}
    >
      {!collapsed ? (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1.5,
            p: 1,
            borderRadius: 1,
            bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : neutral[200],
          }}
        >
          <Avatar
            sx={{
              width: 32,
              height: 32,
              bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[500],
              fontSize: '0.75rem',
              fontWeight: 600,
            }}
          >
            U
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              sx={{
                fontSize: '12px',
                fontWeight: 500,
                color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
              }}
              noWrap
            >
              NeuraReport
            </Typography>
            <Typography
              sx={{
                fontSize: '10px',
                color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                display: 'block'
              }}
            >
              v1.0
            </Typography>
          </Box>
        </Box>
      ) : (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[500],
            fontSize: '0.75rem',
            fontWeight: 600,
            mx: 'auto',
          }}
        >
          U
        </Avatar>
      )}
    </Box>
  )
}
