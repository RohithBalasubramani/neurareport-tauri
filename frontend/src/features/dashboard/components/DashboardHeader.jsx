import {
  Box,
  Typography,
  Stack,
  Button,
  IconButton,
  Tooltip,
  alpha,
  useTheme,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import RefreshIcon from '@mui/icons-material/Refresh'
import KeyboardCommandKeyIcon from '@mui/icons-material/KeyboardCommandKey'
import {
  neutral,
  fontFamilyHeading,
} from '@/app/theme'
import { fadeInUp, spin } from '@/styles'

export default function DashboardHeader({ refreshing, handleRefresh, handleNavigate, handleOpenCommandPalette }) {
  const theme = useTheme()

  return (
    <Stack
      direction={{ xs: 'column', md: 'row' }}
      alignItems={{ xs: 'stretch', md: 'center' }}
      justifyContent="space-between"
      spacing={3}
      sx={{ mb: 4 }}
    >
      <Box sx={{ animation: `${fadeInUp} 0.4s ease-out` }}>
        <Typography
          sx={{
            fontFamily: fontFamilyHeading,
            fontWeight: 500,
            fontSize: '24px',
            lineHeight: 'normal',
            letterSpacing: 0,
            mb: 0.5,
            color: theme.palette.mode === 'dark' ? neutral[100] : neutral[900],
          }}
        >
          Welcome back
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Generate intelligent reports from your data with AI-powered insights
        </Typography>
      </Box>

      <Stack
        direction="row"
        spacing={1.5}
        sx={{ animation: `${fadeInUp} 0.5s ease-out 100ms both` }}
      >
        <Tooltip title="Press \u2318K for quick actions">
          <IconButton
            onClick={handleOpenCommandPalette}
            aria-label="Open command palette"
            sx={{
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              bgcolor: alpha(theme.palette.background.paper, 0.5),
              backdropFilter: 'blur(8px)',
            }}
          >
            <KeyboardCommandKeyIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Tooltip>

        <IconButton
          onClick={handleRefresh}
          disabled={refreshing}
          sx={{
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            bgcolor: alpha(theme.palette.background.paper, 0.5),
            backdropFilter: 'blur(8px)',
          }}
        >
          <RefreshIcon
            sx={{
              fontSize: 20,
              animation: refreshing ? `${spin} 1s linear infinite` : 'none',
            }}
          />
        </IconButton>

        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleNavigate('/setup/wizard', 'Open setup wizard')}
          sx={{
            px: 3,
            py: 1,
            borderRadius: '8px',
            fontWeight: 500,
            fontSize: '0.875rem',
            boxShadow: 'none',
            '&:hover': {
              boxShadow: 'none',
            },
          }}
        >
          New Report
        </Button>
      </Stack>
    </Stack>
  )
}
