import { Box } from '@mui/material'
import { alpha } from '@mui/material/styles'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import { neutral } from '@/app/theme'

export default function StepIndicator(props) {
  const { active, completed, icon } = props
  return (
    <Box
      sx={{
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 600,
        fontSize: 14,
        border: '2px solid',
        borderColor: (theme) => completed ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : active ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'divider',
        bgcolor: (theme) => completed ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : active ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : 'background.paper',
        color: completed || active ? 'common.white' : 'text.secondary',
        boxShadow: (theme) => active ? `0 6px 16px ${alpha(theme.palette.common.black, 0.15)}` : 'none',
        transition: 'all 160ms cubic-bezier(0.22, 1, 0.36, 1)',
      }}
    >
      {completed ? <CheckRoundedIcon fontSize="small" /> : icon}
    </Box>
  )
}
