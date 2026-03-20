import {
  Box,
  Typography,
  Button,
  Stack,
  TextField,
  CircularProgress,
  Grid,
  Avatar,
  alpha,
  useTheme,
} from '@mui/material'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import SendIcon from '@mui/icons-material/Send'
import { GlassCard } from '@/styles'
import { neutral } from '@/app/theme'
import QABubble from './QABubble'

export default function QATab({
  question,
  setQuestion,
  isAskingQuestion,
  qaHistory,
  suggestedQuestions,
  onAskQuestion,
}) {
  const theme = useTheme()

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12, lg: 8 }}>
        <GlassCard sx={{ minHeight: 500 }}>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
              <SmartToyIcon />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                Ask AI About Your Document
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Get instant answers with source citations
              </Typography>
            </Box>
          </Stack>

          {/* Chat Area */}
          <Box
            sx={{
              minHeight: 300,
              maxHeight: 400,
              overflowY: 'auto',
              mb: 3,
              p: 2,
              bgcolor: alpha(theme.palette.background.default, 0.5),
              borderRadius: 1,  // Figma spec: 8px
            }}
          >
            {qaHistory.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <Avatar
                  sx={{
                    width: 80,
                    height: 80,
                    mx: 'auto',
                    mb: 2,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                  }}
                >
                  <QuestionAnswerIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
                </Avatar>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Start a conversation
                </Typography>
                <Typography variant="body2" color="text.disabled">
                  Ask questions about the document content
                </Typography>
              </Box>
            ) : (
              qaHistory.map((qa, idx) => <QABubble key={idx} qa={qa} index={idx} />)
            )}
          </Box>

          {/* Input */}
          <Stack direction="row" spacing={2}>
            <TextField
              fullWidth
              placeholder="Ask a question about your document..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && onAskQuestion()}
              disabled={isAskingQuestion}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 1,  // Figma spec: 8px
                  bgcolor: alpha(theme.palette.background.paper, 0.8),
                },
              }}
            />
            <Button
              variant="contained"
              onClick={onAskQuestion}
              disabled={!question.trim() || isAskingQuestion}
              sx={{
                minWidth: 56,
                borderRadius: 1,  // Figma spec: 8px
                background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                '&:hover': {
                  background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                },
              }}
            >
              {isAskingQuestion ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            </Button>
          </Stack>
        </GlassCard>
      </Grid>

      {/* Suggested Questions */}
      <Grid size={{ xs: 12, lg: 4 }}>
        <GlassCard>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Suggested Questions
          </Typography>
          <Stack spacing={1.5}>
            {suggestedQuestions.map((q, idx) => (
              <Button
                key={idx}
                variant="outlined"
                onClick={() => setQuestion(q)}
                sx={{
                  textTransform: 'none',
                  justifyContent: 'flex-start',
                  textAlign: 'left',
                  borderRadius: 1,
                  py: 1.5,
                  px: 2,
                  fontWeight: 500,
                  borderColor: alpha(theme.palette.divider, 0.2),
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                  },
                }}
              >
                {q}
              </Button>
            ))}
          </Stack>
        </GlassCard>
      </Grid>
    </Grid>
  )
}
