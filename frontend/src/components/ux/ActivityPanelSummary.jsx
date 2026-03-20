/**
 * Activity Panel Summary Bar
 * Shows completed/failed counts and clear button
 */
import {
  Box,
  Typography,
  Button,
  useTheme,
  alpha,
} from '@mui/material'
import { ClearAll as ClearIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'

export default function ActivityPanelSummary({ completedCount, failedCount, onClearCompleted }) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        p: 2,
        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50],
        borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
      }}
    >
      <Box sx={{ flex: 1, display: 'flex', gap: 2 }}>
        <Typography variant="body2">
          <Box component="span" fontWeight={600}>{completedCount}</Box> completed
        </Typography>
        {failedCount > 0 && (
          <Typography variant="body2" color="text.secondary">
            <Box component="span" fontWeight={600}>{failedCount}</Box> failed
          </Typography>
        )}
      </Box>
      {completedCount > 0 && (
        <Button
          size="small"
          startIcon={<ClearIcon />}
          onClick={onClearCompleted}
          sx={{ textTransform: 'none' }}
        >
          Clear completed
        </Button>
      )}
    </Box>
  )
}
