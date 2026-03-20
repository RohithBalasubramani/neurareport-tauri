/**
 * Step 2: Results display with chart question input
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Stack,
  Divider,
  TextField,
  CircularProgress,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import AnalysisResults from './AnalysisResults'
import Surface from '@/components/layout/Surface'

export default function AnalysisResultsStep({
  analysisResult,
  chartQuestion,
  setChartQuestion,
  isLoadingCharts,
  onAskCharts,
}) {
  return (
    <Box>
      <AnalysisResults result={analysisResult} />
      <Divider sx={{ my: 3 }} />

      <Surface variant="outlined" sx={{ p: 2.5, bgcolor: 'action.hover', border: '1px dashed', borderColor: 'divider' }}>
        <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
          <AutoAwesomeIcon color="inherit" fontSize="small" sx={{ color: 'text.secondary' }} />
          <Typography variant="subtitle1" fontWeight={600}>
            Ask for more insights
          </Typography>
        </Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField
            fullWidth
            placeholder="e.g., Show me revenue trends over time, Compare categories by month..."
            value={chartQuestion}
            onChange={(e) => setChartQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && onAskCharts()}
            disabled={isLoadingCharts}
            size="small"
            sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'background.paper' } }}
          />
          <Button
            variant="contained" onClick={onAskCharts}
            disabled={!chartQuestion.trim() || isLoadingCharts}
            startIcon={isLoadingCharts ? <CircularProgress size={16} color="inherit" /> : <AutoAwesomeIcon />}
            sx={{ minWidth: 160, textTransform: 'none', fontWeight: 600, whiteSpace: 'nowrap' }}
          >
            {isLoadingCharts ? 'Generating...' : 'Generate Charts'}
          </Button>
        </Stack>
      </Surface>
    </Box>
  )
}
