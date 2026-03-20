import { useState, useEffect } from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  Paper,
  CircularProgress,
  alpha,
} from '@mui/material'
import LinearProgress from '@mui/material/LinearProgress'
import QueueIcon from '@mui/icons-material/Queue'

const PROGRESS_STEPS = [
  'Preparing mapping...',
  'Building contract...',
  'Generating report assets...',
  'Finalizing template...',
]

export default function MappingProcessingState({ onQueue }) {
  const [progressStep, setProgressStep] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setProgressStep((prev) => (prev + 1) % PROGRESS_STEPS.length)
    }, 3000)
    return () => clearInterval(timer)
  }, [])

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2.5,
        mx: 2,
        mb: 2,
        borderRadius: 1,
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.primary.main, 0.3),
        bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.primary.main, 0.08) : alpha(theme.palette.primary.main, 0.04),
      }}
    >
      <Stack spacing={2} alignItems="center">
        <Stack direction="row" spacing={1.5} alignItems="center">
          <CircularProgress size={22} thickness={5} />
          <Typography variant="subtitle2" fontWeight={600}>
            Setting up your template...
          </Typography>
        </Stack>

        <Box sx={{ width: '100%' }}>
          <LinearProgress
            variant="indeterminate"
            sx={{
              height: 6,
              borderRadius: 3,
              bgcolor: (theme) => alpha(theme.palette.primary.main, 0.12),
              '& .MuiLinearProgress-bar': { borderRadius: 3 },
            }}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ minHeight: 20, transition: 'opacity 0.3s' }}>
          {PROGRESS_STEPS[progressStep]}
        </Typography>

        {onQueue && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<QueueIcon />}
            onClick={onQueue}
            sx={{ textTransform: 'none', mt: 0.5 }}
          >
            Queue & Continue — I'll finish this in the background
          </Button>
        )}
      </Stack>
    </Paper>
  )
}
