import {
  Box,
  Stack,
  Typography,
  Chip,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import { EDIT_TYPE_CONFIG, formatRelativeTime } from './editHistoryConfig'

export default function HistoryEntry({ entry, isLatest }) {
  const config = EDIT_TYPE_CONFIG[entry.type] || EDIT_TYPE_CONFIG.default
  const Icon = config.icon

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        py: 1,
        px: 1.5,
        borderRadius: 1,
        bgcolor: isLatest ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] : 'transparent',
        '&:hover': {
          bgcolor: 'action.hover',
        },
      }}
    >
      {/* Timeline indicator */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          pt: 0.5,
        }}
      >
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: '50%',
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon
            sx={{
              fontSize: 16,
              color: 'text.secondary',
            }}
          />
        </Box>
        <Box
          sx={{
            width: 2,
            flex: 1,
            mt: 0.5,
            bgcolor: 'divider',
            minHeight: 8,
          }}
        />
      </Box>

      {/* Content */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.25 }}>
          <Chip
            label={config.label}
            size="small"
            variant="outlined"
            sx={{
              height: 20,
              fontSize: '12px',
              borderColor: (theme) => alpha(theme.palette.divider, 0.3),
              color: 'text.secondary',
            }}
          />
          {isLatest && (
            <Chip
              label="Latest"
              size="small"
              sx={{
                height: 20,
                fontSize: '12px',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                color: 'common.white',
              }}
            />
          )}
        </Stack>

        {entry.notes && (
          <Typography
            variant="body2"
            color="text.primary"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: '100%',
            }}
          >
            {entry.notes}
          </Typography>
        )}

        <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
          <AccessTimeIcon sx={{ fontSize: 12, color: 'text.disabled' }} />
          <Typography variant="caption" color="text.disabled">
            {formatRelativeTime(entry.timestamp)}
          </Typography>
        </Stack>
      </Box>
    </Box>
  )
}
