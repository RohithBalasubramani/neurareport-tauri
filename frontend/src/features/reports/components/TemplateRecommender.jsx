import { Box, Stack, Typography, TextField, Button, Paper, Chip, CircularProgress,
  Collapse, IconButton, Avatar, LinearProgress, Alert, Tooltip } from '@mui/material'
import { neutral } from '@/app/theme'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { useTemplateRecommender } from '../hooks/useTemplateRecommender'
import RecommendationCard from './RecommendationCard'

export default function TemplateRecommender({ onSelectTemplate }) {
  const {
    expanded,
    setExpanded,
    requirement,
    setRequirement,
    loading,
    queueing,
    recommendations,
    error,
    setError,
    executeUI,
    handleSearch,
    handleQueue,
    handleSelect,
    handleKeyDown,
  } = useTemplateRecommender({ onSelectTemplate })

  return (
    <Paper
      sx={{
        border: 1,
        borderColor: 'divider',
        borderStyle: expanded ? 'solid' : 'dashed',
        transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          px: 2,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          bgcolor: expanded ? 'action.selected' : 'transparent',
          '&:hover': {
            bgcolor: 'action.hover',
          },
        }}
      onClick={() => executeUI('Toggle template recommender', () => setExpanded((prev) => !prev))}
      >
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Avatar
            sx={{
              width: 32,
              height: 32,
              bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.08)' : neutral[100],
            }}
          >
            <AutoAwesomeIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
          </Avatar>
          <Box>
            <Typography variant="subtitle2" fontWeight={600}>
              AI Template Picker
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Describe what you need and let AI find the best template
            </Typography>
          </Box>
        </Stack>
        <Tooltip title={expanded ? 'Collapse' : 'Expand'}>
          <IconButton size="small" aria-label={expanded ? 'Collapse' : 'Expand'}>
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* Expanded Content */}
      <Collapse in={expanded}>
        <Box sx={{ px: 2, pb: 2 }}>
          <Stack spacing={2}>
            {/* Search Input */}
            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                size="small"
                placeholder="e.g., monthly sales report with charts, inventory tracking spreadsheet..."
                value={requirement}
                onChange={(e) => setRequirement(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'background.paper',
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSearch}
                disabled={loading || queueing || !requirement.trim()}
                startIcon={
                  loading ? (
                    <CircularProgress size={16} color="inherit" />
                  ) : (
                    <AutoAwesomeIcon />
                  )
                }
                sx={{ minWidth: 120, textTransform: 'none' }}
              >
                {loading ? 'Searching...' : 'Find'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleQueue}
                disabled={loading || queueing || !requirement.trim()}
                startIcon={
                  queueing ? (
                    <CircularProgress size={16} color="inherit" />
                  ) : (
                    <ScheduleIcon />
                  )
                }
                sx={{ minWidth: 120, textTransform: 'none' }}
              >
                {queueing ? 'Queueing...' : 'Queue'}
              </Button>
            </Stack>

            {loading && <LinearProgress />}

            {error && (
              <Alert severity="info" onClose={() => executeUI('Dismiss recommendations error', () => setError(null))}>
                {error}
              </Alert>
            )}

            {recommendations.length > 0 && (
              <Stack spacing={1.5}>
                <Typography variant="caption" color="text.secondary">
                  {recommendations.length} template{recommendations.length !== 1 ? 's' : ''} found
                </Typography>
                {recommendations.map((rec, idx) => {
                  const template = rec.template || rec
                  return (
                    <RecommendationCard
                      key={template.id || idx}
                      rec={rec}
                      onSelect={handleSelect}
                    />
                  )
                })}
              </Stack>
            )}

            {/* Quick Examples */}
            {!loading && recommendations.length === 0 && (
              <Box>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Try these examples:
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {[
                    'monthly financial report',
                    'inventory tracking',
                    'sales summary with charts',
                    'equipment status report',
                  ].map((example) => (
                    <Chip
                      key={example}
                      label={example}
                      size="small"
                      variant="outlined"
                      onClick={() => executeUI('Set example requirement', () => setRequirement(example), { example })}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Stack>
              </Box>
            )}
          </Stack>
        </Box>
      </Collapse>
    </Paper>
  )
}
