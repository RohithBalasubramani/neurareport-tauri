/**
 * Chat header bar showing session info and clear button.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  useTheme,
  alpha,
} from '@mui/material'
import {
  QuestionAnswer as QAIcon,
  Clear as ClearIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { ChatHeader } from './DocQAStyledComponents'

export default function ChatHeaderBar({
  currentSession,
  messagesCount,
  connectionsCount,
  setClearChatConfirm,
}) {
  const theme = useTheme()

  return (
    <ChatHeader>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1,
            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <QAIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            {currentSession.name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {currentSession.documents?.length || 0} documents •{' '}
            {messagesCount} messages •{' '}
            {connectionsCount} connections available
          </Typography>
        </Box>
      </Box>
      {messagesCount > 0 && (
        <Button
          size="small"
          startIcon={<ClearIcon />}
          onClick={() => setClearChatConfirm({
            open: true,
            sessionId: currentSession.id,
            sessionName: currentSession.name,
            messageCount: messagesCount,
          })}
          sx={{
            borderRadius: 1,
            textTransform: 'none',
            color: 'text.secondary',
          }}
        >
          Clear Chat
        </Button>
      )}
    </ChatHeader>
  )
}
