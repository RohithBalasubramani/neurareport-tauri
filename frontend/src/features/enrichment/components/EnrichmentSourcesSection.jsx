/**
 * Enrichment sources selection and action buttons.
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Preview as PreviewIcon,
  PlayArrow as RunIcon,
} from '@mui/icons-material';
import { neutral } from '@/app/theme';

export default function EnrichmentSourcesSection({
  allSources,
  customSources,
  selectedSources,
  toggleSource,
  setDeleteSourceConfirm,
  parsedData,
  loading,
  handlePreview,
  handleEnrich,
}) {
  return (
    <Paper sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Enrichment Sources
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {allSources.map((source) => {
          const isCustom = customSources.some((cs) => cs.id === source.id)
          return (
            <Card
              key={source.id}
              variant="outlined"
              sx={{
                cursor: 'pointer',
                borderColor: selectedSources.includes(source.id) ? 'text.secondary' : 'divider',
                bgcolor: selectedSources.includes(source.id) ? 'action.selected' : 'background.paper',
              }}
              onClick={() => toggleSource(source.id)}
            >
              <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="subtitle1">{source.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {source.description}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isCustom ? (
                      <Chip label="Custom" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                    ) : (
                      <Chip label="Built-in" size="small" variant="outlined" />
                    )}
                    {selectedSources.includes(source.id) && (
                      <Chip label="Selected" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                    )}
                    {isCustom && (
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDeleteSourceConfirm({ open: true, sourceId: source.id, sourceName: source.name })
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )
        })}
      </Box>

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={loading ? <CircularProgress size={20} /> : <PreviewIcon />}
          onClick={handlePreview}
          disabled={!parsedData || selectedSources.length === 0 || loading}
        >
          Preview
        </Button>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <RunIcon />}
          onClick={handleEnrich}
          disabled={!parsedData || selectedSources.length === 0 || loading}
        >
          Enrich All
        </Button>
      </Box>
    </Paper>
  );
}
