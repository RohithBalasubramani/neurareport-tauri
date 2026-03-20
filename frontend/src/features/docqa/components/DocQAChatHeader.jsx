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
import AiUsageNotice from '@/components/ai/AiUsageNotice'
import { ChatHeader } from './DocQAStyledComponents'

export default function DocQAChatHeader({ currentSession, messages, connections, docCount, setClearChatConfirm }) {
  const theme = useTheme()

  return (
    <>
      <ChatHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: 1,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : 'neutral.100',
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
              {messages.length} messages •{' '}
              {connections.length} connections available
            </Typography>
          </Box>
        </Box>
        {messages.length > 0 && (
          <Button
            size="small"
            startIcon={<ClearIcon />}
            onClick={() => setClearChatConfirm({
              open: true,
              sessionId: currentSession.id,
              sessionName: currentSession.name,
              messageCount: messages.length,
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

      <Box sx={{ px: 3, pt: 2 }}>
        <AiUsageNotice
          title="AI answers"
          description="Responses are generated from documents in this session. Review citations before sharing."
          chips={[
            { label: `Source: ${docCount} document${docCount === 1 ? '' : 's'}`, color: 'info', variant: 'outlined' },
            { label: 'Confidence: Verify citations', color: 'warning', variant: 'outlined' },
            { label: 'Reversible: No source changes', color: 'success', variant: 'outlined' },
          ]}
          dense
        />
      </Box>
    </>
  )
}
