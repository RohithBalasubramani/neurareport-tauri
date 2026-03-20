/**
 * CommentItem — single comment card with replies and actions.
 */
import { useState } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Avatar,
  Stack,
  Chip,
  Button,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Check as ResolveIcon,
  Reply as ReplyIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { CommentCard, QuotedText, getInitials, formatDate } from './CommentsPanelStyles'
import { CommentReplyInput, CommentReplyList } from './CommentReplies'

export default function CommentItem({ comment, onResolve, onReply, onDelete, onHighlight, isHighlighted }) {
  const theme = useTheme()
  const [expanded, setExpanded] = useState(true)
  const [replyOpen, setReplyOpen] = useState(false)
  const [replyText, setReplyText] = useState('')

  const handleReply = () => {
    if (replyText.trim()) {
      onReply?.(comment.id, replyText.trim())
      setReplyText('')
      setReplyOpen(false)
    }
  }

  const replies = comment.replies || []

  return (
    <CommentCard
      elevation={0}
      isResolved={comment.resolved}
      isHighlighted={isHighlighted}
      onClick={() => onHighlight?.(comment)}
      data-testid={`comment-card-${comment.id}`}
    >
      <Stack direction="row" alignItems="center" spacing={1} mb={1}>
        <Avatar
          sx={{
            width: 28, height: 28, fontSize: '0.75rem',
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
            color: theme.palette.text.secondary,
          }}
        >
          {getInitials(comment.author_name)}
        </Avatar>
        <Box sx={{ flex: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '14px' }}>
            {comment.author_name || 'Anonymous'}
          </Typography>
          <Typography variant="caption" color="text.secondary">{formatDate(comment.created_at)}</Typography>
        </Box>
        {comment.resolved && (
          <Chip label="Resolved" size="small" sx={{
            borderRadius: 1, fontSize: '10px', height: 20,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            color: 'text.secondary',
          }} />
        )}
      </Stack>

      {comment.quoted_text && <QuotedText>"{comment.quoted_text}"</QuotedText>}

      <Typography variant="body2" sx={{ mb: 1.5, fontSize: '14px' }}>{comment.text}</Typography>

      <Stack direction="row" spacing={1} alignItems="center">
        {!comment.resolved && (
          <>
            <Tooltip title="Reply">
              <IconButton size="small" onClick={(e) => { e.stopPropagation(); setReplyOpen(!replyOpen) }}
                data-testid="comment-reply-button" aria-label="Reply">
                <ReplyIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </Tooltip>
            <Tooltip title="Resolve">
              <IconButton size="small" onClick={(e) => { e.stopPropagation(); onResolve?.(comment.id) }}
                data-testid="comment-resolve-button" aria-label="Resolve comment">
                <ResolveIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </IconButton>
            </Tooltip>
          </>
        )}
        <Tooltip title="Delete">
          <IconButton size="small" onClick={(e) => { e.stopPropagation(); onDelete?.(comment.id) }}
            data-testid="comment-delete-button" aria-label="Delete comment">
            <DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          </IconButton>
        </Tooltip>
        {replies.length > 0 && (
          <Box sx={{ flex: 1, textAlign: 'right' }}>
            <Button size="small" endIcon={expanded ? <CollapseIcon /> : <ExpandIcon />}
              onClick={(e) => { e.stopPropagation(); setExpanded(!expanded) }}
              sx={{ fontSize: '12px', textTransform: 'none' }}>
              {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
            </Button>
          </Box>
        )}
      </Stack>

      <CommentReplyInput
        replyOpen={replyOpen} replyText={replyText}
        setReplyText={setReplyText} setReplyOpen={setReplyOpen}
        onSubmit={handleReply}
      />
      <CommentReplyList replies={replies} expanded={expanded} />
    </CommentCard>
  )
}
