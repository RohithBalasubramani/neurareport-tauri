/**
 * Comments Panel
 * Sidebar for document comments with threading, replies, and resolution.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Stack,
  Chip,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Close as CloseIcon,
  Comment as CommentIcon,
  Send as SendIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import {
  PanelContainer,
  PanelHeader,
  PanelContent,
  CommentComposer,
  QuotedText,
  ActionButton,
  CompactTextField,
} from './CommentsPanelStyles'
import CommentItem from './CommentItem'

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

  const filterOptions = [
    { key: 'all', label: `All (${comments.length})`, testId: 'comments-filter-all' },
    { key: 'open', label: `Open (${openCount})`, testId: 'comments-filter-open' },
    { key: 'resolved', label: `Resolved (${resolvedCount})`, testId: 'comments-filter-resolved' },
  ]

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
          {filterOptions.map(({ key, label, testId }) => (
            <Chip
              key={key}
              label={label}
              size="small"
              onClick={() => setFilter(key)}
              variant={filter === key ? 'filled' : 'outlined'}
              data-testid={testId}
              sx={{
                borderRadius: 1,
                fontSize: '12px',
                bgcolor: filter === key ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : 'transparent',
                color: filter === key ? 'common.white' : 'text.secondary',
                borderColor: filter === key ? 'transparent' : alpha(theme.palette.divider, 0.3),
              }}
            />
          ))}
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
