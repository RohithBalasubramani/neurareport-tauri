/**
 * Search results main panel with empty state
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Chip,
  styled,
  alpha,
} from '@mui/material'
import {
  Search as SearchIcon,
  BookmarkBorder as SaveIcon,
  Description as DocIcon,
} from '@mui/icons-material'
import { sanitizeHighlight } from '@/utils/sanitize'
import { neutral } from '@/app/theme'

const MainPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

const ResultCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

export default function SearchResultsPanel({
  results,
  totalResults,
  searching,
  onSaveClick,
  onExampleClick,
}) {
  if (results.length > 0) {
    return (
      <MainPanel>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="subtitle1">
            {totalResults} results found
          </Typography>
          <ActionButton size="small" startIcon={<SaveIcon />} onClick={onSaveClick}>
            Save Search
          </ActionButton>
        </Box>

        {results.map((result, index) => (
          <ResultCard key={result.id || index} variant="outlined">
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <DocIcon color="inherit" />
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {result.title || result.filename || 'Untitled'}
                </Typography>
                {result.highlight && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 0.5 }}
                    dangerouslySetInnerHTML={{ __html: sanitizeHighlight(result.highlight) }}
                  />
                )}
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  {result.score && (
                    <Chip size="small" label={`Score: ${(result.score * 100).toFixed(0)}%`} />
                  )}
                  {result.type && (
                    <Chip size="small" label={result.type.toUpperCase()} variant="outlined" />
                  )}
                </Box>
              </Box>
            </Box>
          </ResultCard>
        ))}
      </MainPanel>
    )
  }

  if (!searching) {
    return (
      <MainPanel>
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            maxWidth: 500,
            mx: 'auto',
          }}
        >
          <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            Search Your Documents
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Find what you need across all your documents using different search modes.
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, width: '100%', maxWidth: 300 }}>
            <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'left', mb: 0.5 }}>
              Try these example searches:
            </Typography>
            {[
              { query: 'quarterly revenue', type: 'fulltext', label: 'Full Text' },
              { query: 'documents about marketing strategy', type: 'semantic', label: 'Semantic' },
              { query: '(budget AND 2024) OR forecast', type: 'boolean', label: 'Boolean' },
            ].map((example) => (
              <Button
                key={example.query}
                variant="outlined"
                size="small"
                onClick={() => onExampleClick(example)}
                sx={{ justifyContent: 'flex-start', textTransform: 'none', textAlign: 'left' }}
              >
                <Chip size="small" label={example.label} sx={{ mr: 1, pointerEvents: 'none' }} />
                <Typography variant="body2" noWrap>{example.query}</Typography>
              </Button>
            ))}
          </Box>
        </Box>
      </MainPanel>
    )
  }

  return <MainPanel />
}
