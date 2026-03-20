import {
  Box,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  ContentCopy as CopyIcon,
  ThumbUp as ThumbUpIcon,
  ThumbDown as ThumbDownIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { ActionButton } from './DocQAStyledComponents'

export default function MessageActions({ msg, asking, handleCopyMessage, handleFeedback, handleRegenerate }) {
  const theme = useTheme()

  return (
    <Box sx={{ display: 'flex', gap: 0.5, mt: 1.5 }}>
      <Tooltip title="Copy">
        <ActionButton size="small" onClick={() => handleCopyMessage(msg.content)}>
          <CopyIcon sx={{ fontSize: 16 }} />
        </ActionButton>
      </Tooltip>
      <Tooltip title={msg.feedback?.feedback_type === 'helpful' ? 'Marked as helpful' : 'Helpful'}>
        <ActionButton
          size="small"
          onClick={() => handleFeedback(msg.id, 'helpful')}
          sx={{
            color: msg.feedback?.feedback_type === 'helpful'
              ? 'text.primary'
              : undefined,
            bgcolor: msg.feedback?.feedback_type === 'helpful'
              ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100])
              : undefined,
          }}
        >
          <ThumbUpIcon sx={{ fontSize: 16 }} />
        </ActionButton>
      </Tooltip>
      <Tooltip title={msg.feedback?.feedback_type === 'not_helpful' ? 'Marked as not helpful' : 'Not helpful'}>
        <ActionButton
          size="small"
          onClick={() => handleFeedback(msg.id, 'not_helpful')}
          sx={{
            color: msg.feedback?.feedback_type === 'not_helpful'
              ? 'text.primary'
              : undefined,
            bgcolor: msg.feedback?.feedback_type === 'not_helpful'
              ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100])
              : undefined,
          }}
        >
          <ThumbDownIcon sx={{ fontSize: 16 }} />
        </ActionButton>
      </Tooltip>
      <Tooltip title="Regenerate response">
        <ActionButton
          size="small"
          onClick={() => handleRegenerate(msg.id)}
          disabled={asking}
        >
          <RefreshIcon sx={{ fontSize: 16 }} />
        </ActionButton>
      </Tooltip>
    </Box>
  )
}
