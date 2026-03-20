/**
 * CommentReplies — reply list and reply input for a comment.
 */
import {
  Box,
  Typography,
  Avatar,
  Stack,
  Collapse,
  alpha,
  useTheme,
} from '@mui/material'
import { neutral } from '@/app/theme'
import {
  ReplyCard,
  ActionButton,
  CompactTextField,
  getInitials,
  formatDate,
} from './CommentsPanelStyles'

export function CommentReplyInput({ replyOpen, replyText, setReplyText, setReplyOpen, onSubmit }) {
  return (
    <Collapse in={replyOpen}>
      <Box sx={{ mt: 2 }}>
        <CompactTextField
          fullWidth
          size="small"
          multiline
          minRows={2}
          placeholder="Write a reply..."
          value={replyText}
          onChange={(e) => setReplyText(e.target.value)}
          onClick={(e) => e.stopPropagation()}
        />
        <Stack direction="row" spacing={1} mt={1} justifyContent="flex-end">
          <ActionButton
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              setReplyOpen(false)
              setReplyText('')
            }}
          >
            Cancel
          </ActionButton>
          <ActionButton
            size="small"
            variant="contained"
            disabled={!replyText.trim()}
            onClick={(e) => {
              e.stopPropagation()
              onSubmit()
            }}
          >
            Reply
          </ActionButton>
        </Stack>
      </Box>
    </Collapse>
  )
}

export function CommentReplyList({ replies, expanded }) {
  const theme = useTheme()

  return (
    <Collapse in={expanded && replies.length > 0}>
      {replies.map((reply) => (
        <ReplyCard key={reply.id}>
          <Stack direction="row" alignItems="center" spacing={1} mb={0.5}>
            <Avatar
              sx={{
                width: 22,
                height: 22,
                fontSize: '10px',
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[200],
                color: theme.palette.text.secondary,
              }}
            >
              {getInitials(reply.author_name)}
            </Avatar>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              {reply.author_name || 'Anonymous'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatDate(reply.created_at)}
            </Typography>
          </Stack>
          <Typography variant="body2" sx={{ fontSize: '14px', pl: 3.75 }}>
            {reply.text}
          </Typography>
        </ReplyCard>
      ))}
    </Collapse>
  )
}
