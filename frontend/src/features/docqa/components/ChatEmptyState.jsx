/**
 * Empty states for the chat area: no session selected, or session with no messages.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  useTheme,
} from '@mui/material'
import {
  Add as AddIcon,
  CloudUpload as UploadIcon,
  AutoAwesome as AIIcon,
  QuestionAnswer as QAIcon,
  Article as ArticleIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { EmptyState, EmptyIcon, SuggestionCard, NewSessionButton } from './DocQAStyledComponents'

export function NoSessionState({ setCreateDialogOpen }) {
  return (
    <EmptyState>
      <EmptyIcon>
        <QAIcon />
      </EmptyIcon>
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
        Document Intelligence
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 450 }}>
        Create a session, upload your documents, and start asking questions.
        Our AI will analyze and provide accurate answers with citations.
      </Typography>
      <NewSessionButton
        startIcon={<AddIcon />}
        onClick={() => setCreateDialogOpen(true)}
        sx={{ px: 4, py: 1.5 }}
      >
        Create Your First Session
      </NewSessionButton>
    </EmptyState>
  )
}

export function NoMessagesState({
  currentSession,
  connections,
  templates,
  suggestedQuestions,
  setQuestion,
  setAddDocDialogOpen,
  handleOpenReportPicker,
}) {
  const theme = useTheme()
  const hasDocs = currentSession.documents?.length > 0

  return (
    <EmptyState>
      <EmptyIcon>
        <AIIcon />
      </EmptyIcon>
      <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
        {hasDocs
          ? 'Ready to answer your questions'
          : 'Add documents to get started'}
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 400 }}>
        {hasDocs
          ? 'Ask anything about your documents. I\'ll analyze them and provide accurate answers with citations.'
          : 'Upload documents to this session, then ask questions about their content.'}
      </Typography>

      {hasDocs && (
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, maxWidth: 600 }}>
          {suggestedQuestions.map((q, idx) => (
            <SuggestionCard key={idx} onClick={() => setQuestion(q)}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {q}
              </Typography>
            </SuggestionCard>
          ))}
        </Box>
      )}

      {!hasDocs && (
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={() => setAddDocDialogOpen(true)}
            sx={{
              borderRadius: 1,
              textTransform: 'none',
              px: 4,
              py: 1.5,
            }}
          >
            Upload Document
          </Button>
          <Button
            variant="contained"
            startIcon={<ArticleIcon />}
            onClick={handleOpenReportPicker}
            sx={{
              borderRadius: 1,
              textTransform: 'none',
              px: 4,
              py: 1.5,
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
            }}
          >
            Select Existing Report
          </Button>
        </Box>
      )}

      {connections.length > 0 && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {connections.length} database connection{connections.length !== 1 ? 's' : ''} and {templates.length} template{templates.length !== 1 ? 's' : ''} available
          </Typography>
        </Box>
      )}
    </EmptyState>
  )
}
