/**
 * Step 1: Analyzing progress display
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  LinearProgress,
} from '@mui/material'
import CancelIcon from '@mui/icons-material/Cancel'

export default function AnalyzingStep({
  analysisProgress,
  progressStage,
  onCancelAnalysis,
}) {
  return (
    <Box sx={{ textAlign: 'center', py: 6 }}>
      <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
        <CircularProgress
          size={80} thickness={4}
          variant={analysisProgress > 0 ? 'determinate' : 'indeterminate'}
          value={analysisProgress}
          sx={{ color: 'text.secondary' }}
        />
        <Box sx={{ position: 'absolute', top: 0, left: 0, bottom: 0, right: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="caption" fontWeight={600} color="text.secondary">
            {analysisProgress}%
          </Typography>
        </Box>
      </Box>
      <Typography variant="h6" fontWeight={600} gutterBottom>
        {progressStage || 'Analyzing document...'}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        AI is extracting tables, metrics, and generating chart suggestions
      </Typography>
      <LinearProgress
        variant="determinate" value={analysisProgress}
        sx={{
          height: 6, borderRadius: 1, maxWidth: 400, mx: 'auto', mb: 3,
          bgcolor: 'action.hover',
          '& .MuiLinearProgress-bar': { borderRadius: 1 },
        }}
      />
      <Button variant="outlined" color="inherit" startIcon={<CancelIcon />} onClick={onCancelAnalysis} sx={{ textTransform: 'none', fontWeight: 500 }}>
        Cancel Analysis
      </Button>
    </Box>
  )
}
