/**
 * Chat input area with send button and disabled tooltip.
 */
import React from 'react'
import {
  Box,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Send as SendIcon,
  AttachFile as AttachIcon,
} from '@mui/icons-material'
import DisabledTooltip from '@/components/ux/DisabledTooltip'
import {
  InputArea,
  InputContainer,
  StyledTextField,
  SendButton,
  MIN_QUESTION_LENGTH,
  MAX_QUESTION_LENGTH,
} from './DocQAStyledComponents'

export default function ChatInput({
  currentSession,
  question,
  setQuestion,
  asking,
  error,
  reset,
  inputRef,
  handleKeyDown,
  handleAskQuestion,
  setAddDocDialogOpen,
}) {
  const hasDocuments = currentSession?.documents?.length > 0
  const isDisabled =
    !question.trim()
    || question.trim().length < MIN_QUESTION_LENGTH
    || question.trim().length > MAX_QUESTION_LENGTH
    || asking
    || !hasDocuments

  const disabledReason = asking
    ? 'Please wait for the current question to complete'
    : !hasDocuments
      ? 'Add at least one document first'
      : !question.trim()
        ? 'Enter a question to ask'
        : question.trim().length < MIN_QUESTION_LENGTH
          ? `Question must be at least ${MIN_QUESTION_LENGTH} characters`
          : question.trim().length > MAX_QUESTION_LENGTH
            ? `Question exceeds ${MAX_QUESTION_LENGTH} character limit`
            : undefined

  const disabledHint = !hasDocuments
    ? 'Click the attach button or drag a file'
    : !question.trim()
      ? 'Type your question in the field above'
      : undefined

  return (
    <InputArea>
      {error && (
        <Alert
          severity="error"
          onClose={() => reset()}
          sx={{ mb: 2, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}
      <InputContainer>
        <Tooltip title="Attach file">
          <IconButton
            size="small"
            onClick={() => setAddDocDialogOpen(true)}
            sx={{ color: 'text.secondary' }}
          >
            <AttachIcon />
          </IconButton>
        </Tooltip>
        <StyledTextField
          ref={inputRef}
          fullWidth
          placeholder={
            hasDocuments
              ? 'Ask a question about your documents...'
              : 'Add documents to start asking questions...'
          }
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={asking || !hasDocuments}
          multiline
          maxRows={4}
          inputProps={{ maxLength: MAX_QUESTION_LENGTH }}
        />
        <DisabledTooltip
          disabled={isDisabled}
          reason={disabledReason}
          hint={disabledHint}
        >
          <SendButton
            onClick={handleAskQuestion}
            disabled={isDisabled}
          >
            {asking ? (
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  border: '2px solid',
                  borderColor: 'rgba(255,255,255,0.3)',
                  borderTopColor: 'common.white',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                }}
              />
            ) : (
              <SendIcon />
            )}
          </SendButton>
        </DisabledTooltip>
      </InputContainer>
    </InputArea>
  )
}
