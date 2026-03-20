/**
 * FAQ view - generated questions and answers.
 */
import React from 'react'
import { Box, Typography, Paper, Chip } from '@mui/material'
import { QuestionAnswer as FaqIcon } from '@mui/icons-material'
import { ActionButton } from './KnowledgeStyles'

export default function FaqView({ faq, loading, documents, onGenerateFaq }) {
  if (faq.length === 0) {
    return (
      <Box
        sx={{
          height: '50vh', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}
      >
        <FaqIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No FAQ generated yet
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
          Generate FAQ from your documents to surface the most important questions and answers.
        </Typography>
        <ActionButton
          variant="contained" size="large" startIcon={<FaqIcon />}
          onClick={onGenerateFaq} disabled={loading || !documents.length}
        >
          Generate FAQ
        </ActionButton>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Frequently Asked Questions</Typography>
          <Typography variant="body2" color="text.secondary">
            {faq.length} question{faq.length !== 1 ? 's' : ''} generated from your documents
          </Typography>
        </Box>
        <ActionButton startIcon={<FaqIcon />} onClick={onGenerateFaq} disabled={loading}>
          Regenerate
        </ActionButton>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {faq.map((item, idx) => (
          <Paper key={idx} variant="outlined" sx={{ p: 2.5, borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
              <FaqIcon sx={{ color: 'text.secondary', fontSize: 20, mt: 0.25, flexShrink: 0 }} />
              <Box sx={{ flex: 1 }}>
                <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                  {item.question}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                  {item.answer}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1.5 }}>
                  {item.category && (
                    <Chip size="small" label={item.category} variant="outlined" />
                  )}
                  {item.confidence != null && (
                    <Chip
                      size="small"
                      label={`${Math.round(item.confidence * 100)}% confidence`}
                      variant="outlined"
                      color={item.confidence >= 0.8 ? 'success' : item.confidence >= 0.5 ? 'warning' : 'default'}
                    />
                  )}
                </Box>
              </Box>
            </Box>
          </Paper>
        ))}
      </Box>
    </Box>
  )
}
