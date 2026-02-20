import { useState, useCallback } from 'react'
import {
  Box,
  Stack,
  Typography,
  TextField,
  Button,
  Paper,
  Chip,
  CircularProgress,
  Collapse,
  IconButton,
  Avatar,
  LinearProgress,
  Alert,
  Tooltip,
  alpha,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import TableChartIcon from '@mui/icons-material/TableChart'
import CheckIcon from '@mui/icons-material/Check'
import ScheduleIcon from '@mui/icons-material/Schedule'
import { recommendTemplates, queueRecommendTemplates } from '@/api/client'
import { useToast } from '@/components/ToastProvider.jsx'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

const KIND_ICONS = {
  pdf: PictureAsPdfIcon,
  excel: TableChartIcon,
}

const KIND_COLORS = {
  pdf: 'error',
  excel: 'success',
}

export default function TemplateRecommender({ onSelectTemplate }) {
  const { execute } = useInteraction()
  const [expanded, setExpanded] = useState(false)
  const [requirement, setRequirement] = useState('')
  const [loading, setLoading] = useState(false)
  const [queueing, setQueueing] = useState(false)
  const [recommendations, setRecommendations] = useState([])
  const [error, setError] = useState(null)
  const toast = useToast()

  const executeUI = useCallback(
    (label, action, intent = {}) =>
      execute({
        type: InteractionType.EXECUTE,
        label,
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        intent: { source: 'template_recommender', ...intent },
        action,
      }),
    [execute]
  )

  const handleSearch = useCallback(() => {
    const trimmed = requirement.trim()
    if (!trimmed) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Recommend templates',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'template_recommender', action: 'recommend_templates', requirement: trimmed },
      action: async () => {
        setLoading(true)
        setError(null)
        setRecommendations([])

        try {
          const results = await recommendTemplates({
            requirement: trimmed,
            limit: 5,
          })
          const normalized = Array.isArray(results) ? results : []
          setRecommendations(normalized)
          if (!normalized.length) {
            setError('No matching templates found. Try a different description.')
          }
          return normalized
        } catch (err) {
          setError(err.message || 'Failed to get recommendations')
          throw err
        } finally {
          setLoading(false)
        }
      },
    })
  }, [execute, requirement])

  const handleQueue = useCallback(() => {
    const trimmed = requirement.trim()
    if (!trimmed) return undefined

    return execute({
      type: InteractionType.GENERATE,
      label: 'Queue template recommendations',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'template_recommender', action: 'queue_recommendations', requirement: trimmed },
      action: async () => {
        setQueueing(true)
        setError(null)
        try {
          const response = await queueRecommendTemplates({
            requirement: trimmed,
            limit: 5,
          })
          if (response?.job_id) {
            toast.show('Recommendation job queued. Track it in Jobs.', 'success')
          } else {
            toast.show('Failed to queue recommendation job.', 'error')
          }
          return response
        } catch (err) {
          toast.show(err.message || 'Failed to queue recommendations', 'error')
          throw err
        } finally {
          setQueueing(false)
        }
      },
    })
  }, [execute, requirement, toast])

  const handleSelect = useCallback(
    (template) =>
      executeUI(
        'Select recommended template',
        () => {
          onSelectTemplate?.(template)
          setExpanded(false)
        },
        { templateId: template?.id }
      ),
    [executeUI, onSelectTemplate]
  )

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSearch()
      }
    },
    [handleSearch]
  )

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

            {/* Loading */}
            {loading && <LinearProgress />}

            {/* Error */}
            {error && (
              <Alert severity="info" onClose={() => executeUI('Dismiss recommendations error', () => setError(null))}>
                {error}
              </Alert>
            )}

            {/* Results */}
            {recommendations.length > 0 && (
              <Stack spacing={1.5}>
                <Typography variant="caption" color="text.secondary">
                  {recommendations.length} template{recommendations.length !== 1 ? 's' : ''} found
                </Typography>
                {recommendations.map((rec, idx) => {
                  const template = rec.template || rec
                  const kind = template.kind || 'pdf'
                  const Icon = KIND_ICONS[kind] || PictureAsPdfIcon
                  const score = typeof rec.score === 'number' ? rec.score : null

                  return (
                    <Paper
                      key={template.id || idx}
                      variant="outlined"
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
                        '&:hover': {
                          borderColor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                          bgcolor: 'action.hover',
                        },
                      }}
                      onClick={() => handleSelect(template)}
                    >
                      <Stack
                        direction="row"
                        alignItems="flex-start"
                        spacing={2}
                      >
                        <Avatar
                          variant="rounded"
                          sx={{
                            width: 40,
                            height: 40,
                            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                          }}
                        >
                          <Icon
                            sx={{
                              color: 'text.secondary',
                            }}
                          />
                        </Avatar>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Stack
                            direction="row"
                            alignItems="center"
                            spacing={1}
                            sx={{ mb: 0.5 }}
                          >
                            <Typography variant="subtitle2" fontWeight={600}>
                              {template.name || template.id}
                            </Typography>
                            <Chip
                              label={kind.toUpperCase()}
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                            />
                            {score !== null && (
                              <Chip
                                label={`${Math.round(score * 100)}% match`}
                                size="small"
                                sx={{ height: 20, fontSize: '10px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                              />
                            )}
                          </Stack>
                          {rec.explanation && (
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {rec.explanation}
                            </Typography>
                          )}
                          {!rec.explanation && template.description && (
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {template.description}
                            </Typography>
                          )}
                        </Box>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<CheckIcon />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleSelect(template)
                      }}
                          sx={{ textTransform: 'none', whiteSpace: 'nowrap' }}
                        >
                          Select
                        </Button>
                      </Stack>
                    </Paper>
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
