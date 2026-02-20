/**
 * Comments Panel
 * Sidebar for document comments with threading, replies, and resolution.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  TextField,
  Button,
  Avatar,
  Stack,
  Chip,
  Collapse,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Comment as CommentIcon,
  Send as SendIcon,
  Check as ResolveIcon,
  Reply as ReplyIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 320,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const CommentComposer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.default, 0.5),
}))

const CommentCard = styled(Paper, {
  shouldForwardProp: (prop) => !['isResolved', 'isHighlighted'].includes(prop),
})(({ theme, isResolved, isHighlighted }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  border: `1px solid ${
    isHighlighted
      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
      : isResolved
      ? alpha(theme.palette.divider, 0.3)
      : alpha(theme.palette.divider, 0.1)
  }`,
  backgroundColor: isResolved
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50])
    : isHighlighted
    ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50])
    : 'transparent',
  opacity: isResolved ? 0.7 : 1,
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
}))

const ReplyCard = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1.5),
  paddingTop: theme.spacing(1.5),
  paddingLeft: theme.spacing(2),
  borderLeft: `2px solid ${alpha(theme.palette.divider, 0.3)}`,
}))

const QuotedText = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  marginBottom: theme.spacing(1),
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  borderLeft: `3px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[300]}`,
  borderRadius: '0 4px 4px 0',
  fontSize: '0.75rem',
  fontStyle: 'italic',
  color: theme.palette.text.secondary,
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.75rem',
}))

const CompactTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 8,
    fontSize: '0.875rem',
  },
}))

// =============================================================================
// HELPERS
// =============================================================================

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

// =============================================================================
// COMMENT ITEM COMPONENT
// =============================================================================

function CommentItem({
  comment,
  onResolve,
  onReply,
  onDelete,
  onHighlight,
  isHighlighted,
}) {
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
      {/* Comment Header */}
      <Stack direction="row" alignItems="center" spacing={1} mb={1}>
        <Avatar
          sx={{
            width: 28,
            height: 28,
            fontSize: '0.75rem',
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
          <Typography variant="caption" color="text.secondary">
            {formatDate(comment.created_at)}
          </Typography>
        </Box>
        {comment.resolved && (
          <Chip
            label="Resolved"
            size="small"
            sx={{
              borderRadius: 1,
              fontSize: '10px',
              height: 20,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              color: 'text.secondary',
            }}
          />
        )}
      </Stack>

      {/* Quoted Text */}
      {comment.quoted_text && (
        <QuotedText>"{comment.quoted_text}"</QuotedText>
      )}

      {/* Comment Text */}
      <Typography variant="body2" sx={{ mb: 1.5, fontSize: '14px' }}>
        {comment.text}
      </Typography>

      {/* Actions */}
      <Stack direction="row" spacing={1} alignItems="center">
        {!comment.resolved && (
          <>
            <Tooltip title="Reply">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  setReplyOpen(!replyOpen)
                }}
                data-testid="comment-reply-button"
                aria-label="Reply"
              >
                <ReplyIcon sx={{ fontSize: 16 }} />
              </IconButton>
            </Tooltip>
            <Tooltip title="Resolve">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  onResolve?.(comment.id)
                }}
                data-testid="comment-resolve-button"
                aria-label="Resolve comment"
              >
                <ResolveIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              </IconButton>
            </Tooltip>
          </>
        )}
        <Tooltip title="Delete">
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation()
              onDelete?.(comment.id)
            }}
            data-testid="comment-delete-button"
            aria-label="Delete comment"
          >
            <DeleteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          </IconButton>
        </Tooltip>

        {replies.length > 0 && (
          <Box sx={{ flex: 1, textAlign: 'right' }}>
            <Button
              size="small"
              endIcon={expanded ? <CollapseIcon /> : <ExpandIcon />}
              onClick={(e) => {
                e.stopPropagation()
                setExpanded(!expanded)
              }}
              sx={{ fontSize: '12px', textTransform: 'none' }}
            >
              {replies.length} {replies.length === 1 ? 'reply' : 'replies'}
            </Button>
          </Box>
        )}
      </Stack>

      {/* Reply Input */}
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
                handleReply()
              }}
            >
              Reply
            </ActionButton>
          </Stack>
        </Box>
      </Collapse>

      {/* Replies */}
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
    </CommentCard>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function CommentsPanel({
  comments = [],
  loading = false,
  highlightedCommentId = null,
  selectedText = '',
  onAddComment,
  onResolveComment,
  onReplyComment,
  onDeleteComment,
  onHighlightComment,
  onClose,
}) {
  const theme = useTheme()
  const [newCommentText, setNewCommentText] = useState('')
  const [filter, setFilter] = useState('all') // 'all', 'open', 'resolved'

  const handleAddComment = useCallback(() => {
    if (newCommentText.trim()) {
      onAddComment?.({
        text: newCommentText.trim(),
        quoted_text: selectedText || undefined,
      })
      setNewCommentText('')
    }
  }, [newCommentText, selectedText, onAddComment])

  const filteredComments = comments.filter((c) => {
    if (filter === 'open') return !c.resolved
    if (filter === 'resolved') return c.resolved
    return true
  })

  const openCount = comments.filter((c) => !c.resolved).length
  const resolvedCount = comments.filter((c) => c.resolved).length

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <CommentIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Comments
          </Typography>
          <Chip
            label={comments.length}
            size="small"
            sx={{ borderRadius: 1, fontSize: '12px', height: 20 }}
          />
        </Stack>
        <IconButton size="small" onClick={onClose} data-testid="comments-panel-close" aria-label="Close comments">
          <CloseIcon fontSize="small" />
        </IconButton>
      </PanelHeader>

      {/* Filter Tabs */}
      <Box sx={{ px: 2, py: 1, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Stack direction="row" spacing={1}>
          <Chip
            label={`All (${comments.length})`}
            size="small"
            onClick={() => setFilter('all')}
            variant={filter === 'all' ? 'filled' : 'outlined'}
            data-testid="comments-filter-all"
            sx={{
              borderRadius: 1,
              fontSize: '12px',
              bgcolor: filter === 'all' ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : 'transparent',
              color: filter === 'all' ? 'common.white' : 'text.secondary',
              borderColor: filter === 'all' ? 'transparent' : alpha(theme.palette.divider, 0.3),
            }}
          />
          <Chip
            label={`Open (${openCount})`}
            size="small"
            onClick={() => setFilter('open')}
            variant={filter === 'open' ? 'filled' : 'outlined'}
            data-testid="comments-filter-open"
            sx={{
              borderRadius: 1,
              fontSize: '12px',
              bgcolor: filter === 'open' ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : 'transparent',
              color: filter === 'open' ? 'common.white' : 'text.secondary',
              borderColor: filter === 'open' ? 'transparent' : alpha(theme.palette.divider, 0.3),
            }}
          />
          <Chip
            label={`Resolved (${resolvedCount})`}
            size="small"
            onClick={() => setFilter('resolved')}
            variant={filter === 'resolved' ? 'filled' : 'outlined'}
            data-testid="comments-filter-resolved"
            sx={{
              borderRadius: 1,
              fontSize: '12px',
              bgcolor: filter === 'resolved' ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : 'transparent',
              color: filter === 'resolved' ? 'common.white' : 'text.secondary',
              borderColor: filter === 'resolved' ? 'transparent' : alpha(theme.palette.divider, 0.3),
            }}
          />
        </Stack>
      </Box>

      <PanelContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : filteredComments.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CommentIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {filter === 'all'
                ? 'No comments yet'
                : filter === 'open'
                ? 'No open comments'
                : 'No resolved comments'}
            </Typography>
            {filter === 'all' && (
              <Typography variant="caption" color="text.disabled">
                Select text and add a comment
              </Typography>
            )}
          </Box>
        ) : (
          filteredComments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              isHighlighted={highlightedCommentId === comment.id}
              onResolve={onResolveComment}
              onReply={onReplyComment}
              onDelete={onDeleteComment}
              onHighlight={onHighlightComment}
            />
          ))
        )}
      </PanelContent>

      {/* Comment Composer */}
      <CommentComposer>
        {selectedText && (
          <QuotedText sx={{ mb: 1.5 }}>
            Selected: "{selectedText.slice(0, 100)}
            {selectedText.length > 100 ? '...' : ''}"
          </QuotedText>
        )}
        <CompactTextField
          fullWidth
          size="small"
          multiline
          minRows={2}
          placeholder={selectedText ? 'Add a comment about this selection...' : 'Add a comment...'}
          value={newCommentText}
          onChange={(e) => setNewCommentText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
              handleAddComment()
            }
          }}
        />
        <Stack direction="row" justifyContent="space-between" alignItems="center" mt={1}>
          <Typography variant="caption" color="text.secondary">
            Ctrl+Enter to submit
          </Typography>
          <ActionButton
            variant="contained"
            size="small"
            endIcon={<SendIcon sx={{ fontSize: 14 }} />}
            disabled={!newCommentText.trim()}
            onClick={handleAddComment}
            data-testid="comment-submit-button"
          >
            Comment
          </ActionButton>
        </Stack>
      </CommentComposer>
    </PanelContainer>
  )
}
