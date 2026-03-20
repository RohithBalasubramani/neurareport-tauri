/**
 * Chat messages list with bubbles, citations, follow-ups, and message actions.
 */
import React from 'react'
import {
  Box,
  Typography,
} from '@mui/material'
import {
  Person as UserIcon,
  AutoAwesome as AIIcon,
  FormatQuote as QuoteIcon,
  InsertDriveFile as FileIcon,
  Psychology as ThinkIcon,
} from '@mui/icons-material'
import {
  MessageBubble,
  BubbleContent,
  AvatarStyled,
  CitationBox,
  CitationItem,
  FollowUpChip,
  ThinkingBox,
  TypingIndicator,
} from './DocQAStyledComponents'
import MessageActions from './MessageActions'

export default function ChatMessages({
  messages,
  asking,
  setQuestion,
  handleCopyMessage,
  handleCitationClick,
  handleFeedback,
  handleRegenerate,
}) {
  return (
    <>
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} isUser={msg.role === 'user'} index={idx}>
          <Box
            sx={{
              display: 'flex',
              gap: 1.5,
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              alignItems: 'flex-start',
            }}
          >
            <AvatarStyled isUser={msg.role === 'user'}>
              {msg.role === 'user' ? <UserIcon /> : <AIIcon />}
            </AvatarStyled>

            <Box sx={{ flex: 1 }}>
              <BubbleContent isUser={msg.role === 'user'}>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.6,
                  }}
                >
                  {msg.content}
                </Typography>
              </BubbleContent>

              {/* Citations */}
              {msg.citations?.length > 0 && (
                <CitationBox>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <QuoteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.secondary' }}>
                      Sources ({msg.citations.length})
                    </Typography>
                  </Box>
                  {msg.citations.map((cit, cidx) => (
                    <CitationItem key={cidx} onClick={() => handleCitationClick(cit)}>
                      <FileIcon sx={{ fontSize: 16, color: 'text.secondary', mt: 0.25 }} />
                      <Box>
                        <Typography variant="caption" sx={{ fontWeight: 600, display: 'block' }}>
                          {cit.document_name}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ fontStyle: 'italic' }}
                        >
                          "{cit.quote?.substring(0, 120)}..."
                        </Typography>
                      </Box>
                    </CitationItem>
                  ))}
                </CitationBox>
              )}

              {/* Follow-up questions */}
              {msg.metadata?.follow_up_questions?.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                    Related questions
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {msg.metadata.follow_up_questions.map((fq, fqidx) => (
                      <FollowUpChip
                        key={fqidx}
                        label={fq}
                        size="small"
                        clickable
                        onClick={() => setQuestion(fq)}
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Message actions */}
              {msg.role === 'assistant' && (
                <MessageActions
                  msg={msg}
                  asking={asking}
                  handleCopyMessage={handleCopyMessage}
                  handleFeedback={handleFeedback}
                  handleRegenerate={handleRegenerate}
                />
              )}
            </Box>
          </Box>
        </MessageBubble>
      ))}

      {/* Typing indicator */}
      {asking && (
        <MessageBubble isUser={false} index={messages.length}>
          <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
            <AvatarStyled isUser={false}>
              <AIIcon />
            </AvatarStyled>
            <Box>
              <ThinkingBox>
                <ThinkIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Typography variant="caption" sx={{ fontWeight: 500 }}>
                  Analyzing documents...
                </Typography>
              </ThinkingBox>
              <BubbleContent isUser={false}>
                <TypingIndicator>
                  <span />
                  <span />
                  <span />
                </TypingIndicator>
              </BubbleContent>
            </Box>
          </Box>
        </MessageBubble>
      )}
    </>
  )
}
