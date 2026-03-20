/**
 * Compact Feedback Component
 * Inline thumbs-only feedback variant
 */
import {
  IconButton,
  Box,
} from '@mui/material'
import ThumbUpOutlined from '@mui/icons-material/ThumbUpOutlined'
import ThumbUp from '@mui/icons-material/ThumbUp'
import ThumbDownOutlined from '@mui/icons-material/ThumbDownOutlined'
import ThumbDown from '@mui/icons-material/ThumbDown'
import SendIcon from '@mui/icons-material/Send'

export default function CompactFeedback({
  feedbackType,
  onThumb,
  onSubmit,
  submitting,
}) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <IconButton
        size="small"
        onClick={() => onThumb('positive')}
        color={feedbackType === 'positive' ? 'success' : 'default'}
        disabled={submitting}
      >
        {feedbackType === 'positive' ? <ThumbUp fontSize="small" /> : <ThumbUpOutlined fontSize="small" />}
      </IconButton>
      <IconButton
        size="small"
        onClick={() => onThumb('negative')}
        color={feedbackType === 'negative' ? 'error' : 'default'}
        disabled={submitting}
      >
        {feedbackType === 'negative' ? <ThumbDown fontSize="small" /> : <ThumbDownOutlined fontSize="small" />}
      </IconButton>
      {feedbackType && (
        <IconButton size="small" onClick={onSubmit} color="primary" disabled={submitting}>
          <SendIcon fontSize="small" />
        </IconButton>
      )}
    </Box>
  )
}
