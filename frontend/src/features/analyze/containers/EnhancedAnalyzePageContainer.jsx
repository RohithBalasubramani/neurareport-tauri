import { useCallback, useState, useRef, useMemo } from 'react'
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Stack,
  TextField,
  CircularProgress,
  Chip,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Avatar,
  Fade,
  Zoom,
  Grow,
  Skeleton,
  alpha,
  useTheme,
} from '@mui/material'
import { float, GlassCard } from '@/styles'
import RefreshIcon from '@mui/icons-material/Refresh'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import InsightsOutlinedIcon from '@mui/icons-material/InsightsOutlined'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer'
import BarChartIcon from '@mui/icons-material/BarChart'
import TableChartIcon from '@mui/icons-material/TableChart'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import DownloadIcon from '@mui/icons-material/Download'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import SendIcon from '@mui/icons-material/Send'
import AssessmentIcon from '@mui/icons-material/Assessment'
import SecurityIcon from '@mui/icons-material/Security'
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck'
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt'
import SentimentVeryDissatisfiedIcon from '@mui/icons-material/SentimentVeryDissatisfied'
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral'
import DescriptionIcon from '@mui/icons-material/Description'
import DataObjectIcon from '@mui/icons-material/DataObject'
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong'
import GavelIcon from '@mui/icons-material/Gavel'
import SpeedIcon from '@mui/icons-material/Speed'
import BoltIcon from '@mui/icons-material/Bolt'
import AutoGraphIcon from '@mui/icons-material/AutoGraph'
import PsychologyIcon from '@mui/icons-material/Psychology'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import ArticleIcon from '@mui/icons-material/Article'

import ZoomableChart from '../components/ZoomableChart'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import TemplateSelector from '@/components/common/TemplateSelector'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import AiUsageNotice from '@/components/ai/AiUsageNotice'
import {
  uploadAndAnalyzeEnhanced,
  askQuestion,
  generateCharts,
  exportAnalysis,
} from '../services/enhancedAnalyzeApi'
import { normalizeChartSpec } from '../services/analyzeApi'
import { neutral, palette } from '@/app/theme'

// Animated stat card
function StatCard({ icon, label, value, delay = 0 }) {
  const theme = useTheme()
  return (
    <Grow in timeout={500 + delay * 100}>
      <Card
        sx={{
          minWidth: 140,
          background: theme.palette.mode === 'dark'
            ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.03)} 100%)`
            : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
          borderRadius: 1,  // Figma spec: 8px
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'scale(1.05)',
            boxShadow: theme.palette.mode === 'dark' ? `0 8px 24px ${alpha(theme.palette.common.black, 0.3)}` : '0 8px 24px rgba(0,0,0,0.08)',
          },
        }}
      >
        <CardContent sx={{ py: 2, px: 2.5, '&:last-child': { pb: 2 } }}>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Avatar
              sx={{
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                color: 'text.secondary',
                width: 40,
                height: 40,
              }}
            >
              {icon}
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight={600} color="text.primary">
                {value}
              </Typography>
              <Typography variant="caption" color="text.secondary" fontWeight={500}>
                {label}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Grow>
  )
}

// Enhanced metric card
function MetricCard({ metric, index }) {
  const theme = useTheme()
  const isPositive = metric.change > 0
  const isNegative = metric.change < 0

  return (
    <Zoom in timeout={300 + index * 50}>
      <Card
        sx={{
          minWidth: 220,
          background: `linear-gradient(145deg, ${theme.palette.background.paper} 0%, ${alpha(theme.palette.text.primary, 0.02)} 100%)`,
          border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          borderRadius: 1,  // Figma spec: 8px
          overflow: 'hidden',
          position: 'relative',
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'translateY(-6px)',
            boxShadow: theme.palette.mode === 'dark' ? `0 12px 32px ${alpha(theme.palette.common.black, 0.3)}` : '0 12px 32px rgba(0,0,0,0.08)',
            '& .metric-icon': {
              transform: 'scale(1.2) rotate(10deg)',
            },
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
          },
        }}
      >
        <CardContent sx={{ py: 2.5, px: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={600}
                sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}
              >
                {metric.name}
              </Typography>
              <Typography
                variant="h4"
                fontWeight={600}
                sx={{
                  mt: 0.5,
                  color: theme.palette.text.primary,
                }}
              >
                {metric.raw_value}
              </Typography>
              {metric.change !== undefined && metric.change !== null && (
                <Chip
                  size="small"
                  icon={isPositive ? <TrendingUpIcon sx={{ fontSize: 14 }} /> : isNegative ? <TrendingUpIcon sx={{ fontSize: 14, transform: 'rotate(180deg)' }} /> : null}
                  label={`${isPositive ? '+' : ''}${metric.change}%`}
                  sx={{
                    mt: 1,
                    height: 24,
                    fontWeight: 600,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                    color: 'text.secondary',
                    '& .MuiChip-icon': {
                      color: 'inherit',
                    },
                  }}
                />
              )}
            </Box>
            <Box
              className="metric-icon"
              sx={{
                transition: 'transform 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
                color: alpha(theme.palette.text.primary, 0.15),
              }}
            >
              <AutoGraphIcon sx={{ fontSize: 48 }} />
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Zoom>
  )
}

// Enhanced insight card
function InsightCard({ insight, type = 'insight', index = 0 }) {
  const theme = useTheme()

  const config = {
    insight: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      icon: <LightbulbIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    risk: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
      icon: <SecurityIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    opportunity: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
      icon: <RocketLaunchIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
    action: {
      gradient: theme.palette.mode === 'dark'
        ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.08)} 0%, ${alpha(theme.palette.text.primary, 0.04)} 100%)`
        : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 100%)`,
      borderColor: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
      icon: <PlaylistAddCheckIcon />,
      iconBg: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
    },
  }

  const { gradient, borderColor, icon, iconBg } = config[type] || config.insight

  const priorityColors = {
    critical: { bg: theme.palette.mode === 'dark' ? neutral[700] : neutral[900], text: 'common.white' },
    high: { bg: theme.palette.mode === 'dark' ? neutral[500] : neutral[700], text: 'common.white' },
    medium: { bg: theme.palette.mode === 'dark' ? neutral[500] : neutral[500], text: 'common.white' },
    low: { bg: theme.palette.mode === 'dark' ? neutral[300] : neutral[500], text: theme.palette.mode === 'dark' ? neutral[900] : 'common.white' },
  }

  const priorityConfig = priorityColors[insight.priority?.toLowerCase()] || priorityColors.medium

  return (
    <Fade in timeout={400 + index * 100}>
      <Card
        sx={{
          mb: 2,
          background: gradient,
          borderLeft: `4px solid ${borderColor}`,
          borderRadius: 1,  // Figma spec: 8px
          overflow: 'hidden',
          transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
          '&:hover': {
            transform: 'translateX(8px)',
            boxShadow: `0 8px 24px ${alpha(borderColor, 0.2)}`,
          },
        }}
      >
        <CardContent sx={{ py: 2.5, px: 3 }}>
          <Stack direction="row" spacing={2}>
            <Avatar
              sx={{
                bgcolor: iconBg,
                color: borderColor,
                width: 48,
                height: 48,
              }}
            >
              {icon}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                <Typography variant="subtitle1" fontWeight={600}>
                  {insight.title}
                </Typography>
                {insight.priority && (
                  <Chip
                    label={insight.priority}
                    size="small"
                    sx={{
                      height: 22,
                      fontSize: 10,
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      bgcolor: priorityConfig.bg,
                      color: priorityConfig.text,
                    }}
                  />
                )}
                {insight.confidence && (
                  <Chip
                    label={`${Math.round(insight.confidence * 100)}% confident`}
                    size="small"
                    variant="outlined"
                    sx={{ height: 22, fontSize: 10 }}
                  />
                )}
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                {insight.description}
              </Typography>
              {insight.suggested_actions?.length > 0 && (
                <Box sx={{ mt: 2, p: 2, bgcolor: alpha(borderColor, 0.08), borderRadius: 1 }}>
                  <Typography variant="caption" fontWeight={600} color={borderColor}>
                    SUGGESTED ACTIONS
                  </Typography>
                  <Stack spacing={0.5} sx={{ mt: 1 }}>
                    {insight.suggested_actions.map((action, i) => (
                      <Stack key={i} direction="row" alignItems="center" spacing={1}>
                        <Box sx={{ width: 6, height: 6, borderRadius: '50%', bgcolor: borderColor }} />
                        <Typography variant="body2">{action}</Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Box>
              )}
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Fade>
  )
}

// Sentiment display component
function SentimentDisplay({ sentiment }) {
  const theme = useTheme()
  if (!sentiment) return null

  const getSentimentConfig = (level) => {
    const neutralColor = theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
    const neutralGradient = theme.palette.mode === 'dark'
      ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.12)} 0%, ${alpha(theme.palette.text.primary, 0.06)} 100%)`
      : `linear-gradient(135deg, ${neutral[200]} 0%, ${neutral[100]} 100%)`
    if (level?.includes('positive')) {
      return {
        icon: <SentimentSatisfiedAltIcon sx={{ fontSize: 32 }} />,
        color: neutralColor,
        label: 'Positive',
        gradient: neutralGradient,
      }
    }
    if (level?.includes('negative')) {
      return {
        icon: <SentimentVeryDissatisfiedIcon sx={{ fontSize: 32 }} />,
        color: neutralColor,
        label: 'Negative',
        gradient: neutralGradient,
      }
    }
    return {
      icon: <SentimentNeutralIcon sx={{ fontSize: 32 }} />,
      color: neutralColor,
      label: 'Neutral',
      gradient: neutralGradient,
    }
  }

  const config = getSentimentConfig(sentiment.overall_sentiment)
  const score = Math.round((sentiment.overall_score + 1) * 50) // Convert -1 to 1 → 0 to 100

  return (
    <GlassCard hover={false} sx={{ p: 2.5 }}>
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              background: config.gradient,
              color: config.color,
            }}
          >
            {config.icon}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="overline" color="text.secondary" fontWeight={600}>
              Document Sentiment
            </Typography>
            <Typography variant="h5" fontWeight={600} color={config.color}>
              {config.label}
            </Typography>
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Box sx={{ position: 'relative', display: 'inline-flex' }}>
              <CircularProgress
                variant="determinate"
                value={score}
                size={60}
                thickness={6}
                sx={{ color: config.color }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="body2" fontWeight={600} color={config.color}>
                  {score}%
                </Typography>
              </Box>
            </Box>
          </Box>
        </Stack>
        <Stack direction="row" spacing={2}>
          <Chip
            size="small"
            label={`Tone: ${sentiment.emotional_tone || 'Neutral'}`}
            sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}
          />
          <Chip
            size="small"
            label={`Urgency: ${sentiment.urgency_level || 'Normal'}`}
            sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}
          />
        </Stack>
      </Stack>
    </GlassCard>
  )
}

// Data quality gauge
function DataQualityGauge({ quality }) {
  const theme = useTheme()
  if (!quality) return null

  const score = Math.round((quality.quality_score || 0) * 100)
  const getColor = (s) => {
    if (s >= 80) return theme.palette.mode === 'dark' ? neutral[500] : neutral[700]
    if (s >= 60) return theme.palette.mode === 'dark' ? neutral[500] : neutral[500]
    return theme.palette.mode === 'dark' ? neutral[300] : neutral[500]
  }
  const color = getColor(score)

  return (
    <GlassCard hover={false} sx={{ p: 2.5 }}>
      <Stack spacing={2}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <Box sx={{ position: 'relative', display: 'inline-flex' }}>
            <CircularProgress
              variant="determinate"
              value={100}
              size={80}
              thickness={6}
              sx={{ color: alpha(color, 0.2) }}
            />
            <CircularProgress
              variant="determinate"
              value={score}
              size={80}
              thickness={6}
              sx={{
                color: color,
                position: 'absolute',
                left: 0,
                '& .MuiCircularProgress-circle': {
                  strokeLinecap: 'round',
                },
              }}
            />
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h5" fontWeight={600} color={color}>
                {score}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Score
              </Typography>
            </Box>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="overline" color="text.secondary" fontWeight={600}>
              Data Quality
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Attention'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {quality.total_rows} rows, {quality.total_columns} columns
            </Typography>
          </Box>
        </Stack>
        {quality.recommendations?.length > 0 && (
          <Box sx={{ p: 1.5, bgcolor: alpha(color, 0.1), borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {quality.recommendations[0]}
            </Typography>
          </Box>
        )}
      </Stack>
    </GlassCard>
  )
}

// Tab panel
function TabPanel({ children, value, index, ...other }) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Fade in timeout={300}><Box sx={{ py: 3 }}>{children}</Box></Fade>}
    </div>
  )
}

// Q&A Message bubble
function QABubble({ qa, index }) {
  const theme = useTheme()
  return (
    <Fade in timeout={300 + index * 100}>
      <Box sx={{ mb: 3 }}>
        {/* Question */}
        <Stack direction="row" justifyContent="flex-end" sx={{ mb: 1.5 }}>
          <Paper
            sx={{
              maxWidth: '80%',
              p: 2,
              px: 3,
              borderRadius: '20px 20px 4px 20px',
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              color: 'common.white',
              boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.2)}`,
            }}
          >
            <Typography variant="body1" fontWeight={500}>
              {qa.question}
            </Typography>
          </Paper>
        </Stack>

        {/* Answer */}
        <Stack direction="row" sx={{ mb: 1 }}>
          <Avatar
            sx={{
              width: 36,
              height: 36,
              mr: 1.5,
              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
              color: 'text.secondary',
            }}
          >
            <SmartToyIcon sx={{ fontSize: 20 }} />
          </Avatar>
          <Paper
            sx={{
              maxWidth: '80%',
              p: 2,
              px: 3,
              borderRadius: '4px 20px 20px 20px',
              bgcolor: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)',
              border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
              {qa.answer}
            </Typography>
            {qa.sources?.length > 0 && (
              <Box sx={{ mt: 2, pt: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  Sources:
                </Typography>
                {qa.sources.slice(0, 2).map((source, i) => (
                  <Typography key={i} variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
                    "{source.content_preview?.slice(0, 100)}..."
                  </Typography>
                ))}
              </Box>
            )}
          </Paper>
        </Stack>
      </Box>
    </Fade>
  )
}

// Main component
export default function EnhancedAnalyzePageContainer() {
  const theme = useTheme()
  const [activeTab, setActiveTab] = useState(0)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [progressStage, setProgressStage] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [error, setError] = useState(null)
  const [suggestedQuestions, setSuggestedQuestions] = useState([])

  // Q&A state
  const [question, setQuestion] = useState('')
  const [isAskingQuestion, setIsAskingQuestion] = useState(false)
  const [qaHistory, setQaHistory] = useState([])

  // Chart generation state
  const [chartQuery, setChartQuery] = useState('')
  const [isGeneratingCharts, setIsGeneratingCharts] = useState(false)
  const [generatedCharts, setGeneratedCharts] = useState([])

  // Data source selectors
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [selectedTemplateId, setSelectedTemplateId] = useState('')

  // Export state
  const [exportMenuAnchor, setExportMenuAnchor] = useState(null)
  const [isExporting, setIsExporting] = useState(false)

  // Preferences
  const [preferences] = useState({
    analysis_depth: 'standard',
    focus_areas: [],
    output_format: 'executive',
    industry: null,
    enable_predictions: true,
    auto_chart_generation: true,
    max_charts: 10,
  })

  const abortControllerRef = useRef(null)
  const fileInputRef = useRef(null)
  const toast = useToast()
  const { execute } = useInteraction()

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setAnalysisResult(null)
    }
  }, [])

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      setAnalysisResult(null)
    }
  }, [])

  const handleAnalyze = useCallback(() => {
    if (!selectedFile) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Analyze document',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      suppressSuccessToast: true,
      intent: { fileName: selectedFile?.name },
      action: async () => {
        abortControllerRef.current = new AbortController()

        setIsAnalyzing(true)
        setAnalysisProgress(0)
        setProgressStage('Initializing AI analysis...')
        setError(null)

        try {
          const result = await uploadAndAnalyzeEnhanced({
            file: selectedFile,
            preferences,
            connectionId: selectedConnectionId || undefined,
            templateId: selectedTemplateId || undefined,
            signal: abortControllerRef.current?.signal,
            onProgress: (event) => {
              if (event.event === 'stage') {
                setAnalysisProgress(event.progress || 0)
                setProgressStage(event.detail || event.stage || 'Processing...')
              }
            },
          })

          if (result.event === 'result') {
            setAnalysisResult(result)
            setSuggestedQuestions(result.suggested_questions || [])
            setGeneratedCharts(
              (result.chart_suggestions || [])
                .map((c, idx) => ({ ...c, ...normalizeChartSpec(c, idx) }))
                .filter(Boolean)
            )
            setActiveTab(0)
            toast.show('Analysis complete!', 'success')
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            toast.show('Analysis cancelled', 'info')
          } else {
            setError(err.message || 'Analysis failed')
          }
        } finally {
          setIsAnalyzing(false)
          setAnalysisProgress(100)
          abortControllerRef.current = null
        }
      },
    })
  }, [execute, selectedFile, preferences, toast])

  const handleCancelAnalysis = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Cancel analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'enhanced-analyze' },
      action: () => {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort()
          setIsAnalyzing(false)
          setAnalysisProgress(0)
          setProgressStage('')
        }
      },
    })
  }, [execute])

  const handleAskQuestion = useCallback(() => {
    if (!analysisResult?.analysis_id || !question.trim()) return undefined

    return execute({
      type: InteractionType.ANALYZE,
      label: 'Ask analysis question',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId: analysisResult.analysis_id },
      action: async () => {
        setIsAskingQuestion(true)
        try {
          const response = await askQuestion(analysisResult.analysis_id, {
            question: question.trim(),
            includeSources: true,
          })

          setQaHistory((prev) => [
            ...prev,
            {
              question: question.trim(),
              answer: response.answer,
              sources: response.sources,
              timestamp: new Date(),
            },
          ])
          setQuestion('')

          if (response.suggested_followups?.length) {
            setSuggestedQuestions(response.suggested_followups)
          }
        } catch (err) {
          toast.show(err.message || 'Failed to get answer', 'error')
        } finally {
          setIsAskingQuestion(false)
        }
      },
    })
  }, [analysisResult?.analysis_id, execute, question, toast])

  const handleGenerateCharts = useCallback(() => {
    if (!analysisResult?.analysis_id || !chartQuery.trim()) return undefined

    return execute({
      type: InteractionType.GENERATE,
      label: 'Generate charts',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId: analysisResult.analysis_id },
      action: async () => {
        setIsGeneratingCharts(true)
        try {
          const response = await generateCharts(analysisResult.analysis_id, {
            query: chartQuery.trim(),
            includeTrends: true,
            includeForecasts: false,
          })

          if (response.charts?.length) {
            const normalized = response.charts
              .map((c, i) => ({ ...c, ...normalizeChartSpec(c, i) }))
              .filter(Boolean)
            setGeneratedCharts((prev) => [...normalized, ...prev])
            setChartQuery('')
            toast.show(`Generated ${response.charts.length} chart(s)`, 'success')
          } else {
            toast.show(response.message || 'No charts could be generated for this query. Try a different request or re-analyze the document.', 'warning')
          }
        } catch (err) {
          toast.show(err.message || 'Failed to generate charts', 'error')
        } finally {
          setIsGeneratingCharts(false)
        }
      },
    })
  }, [analysisResult?.analysis_id, chartQuery, execute, toast])

  const handleExport = useCallback((format) => {
    if (!analysisResult?.analysis_id) return undefined

    return execute({
      type: InteractionType.DOWNLOAD,
      label: `Export analysis (${format.toUpperCase()})`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { analysisId: analysisResult.analysis_id, format },
      action: async () => {
        setExportMenuAnchor(null)
        setIsExporting(true)

        try {
          const blob = await exportAnalysis(analysisResult.analysis_id, { format })
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `analysis_${analysisResult.analysis_id}.${format}`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          URL.revokeObjectURL(url)
          toast.show(`Exported as ${format.toUpperCase()}`, 'success')
        } catch (err) {
          toast.show(err.message || 'Export failed', 'error')
        } finally {
          setIsExporting(false)
        }
      },
    })
  }, [analysisResult?.analysis_id, execute, toast])

  const handleReset = useCallback(() => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Reset analysis',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'enhanced-analyze' },
      action: () => {
        setSelectedFile(null)
        setAnalysisResult(null)
        setError(null)
        setSuggestedQuestions([])
        setQaHistory([])
        setGeneratedCharts([])
        setActiveTab(0)
      },
    })
  }, [execute])

  // Stats
  const stats = useMemo(() => {
    if (!analysisResult) return null
    return {
      tables: analysisResult.total_tables || analysisResult.tables?.length || 0,
      metrics: analysisResult.total_metrics || analysisResult.metrics?.length || 0,
      entities: analysisResult.total_entities || analysisResult.entities?.length || 0,
      insights: analysisResult.insights?.length || 0,
      risks: analysisResult.risks?.length || 0,
      opportunities: analysisResult.opportunities?.length || 0,
      charts: generatedCharts.length,
    }
  }, [analysisResult, generatedCharts.length])

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: theme.palette.mode === 'dark'
          ? `linear-gradient(180deg, ${alpha(theme.palette.text.primary, 0.02)} 0%, ${theme.palette.background.default} 50%)`
          : `linear-gradient(180deg, ${neutral[50]} 0%, ${theme.palette.background.default} 50%)`,
      }}
    >
      {/* Hero Header */}
      <Box
        sx={{
          pt: 4,
          pb: analysisResult ? 2 : 4,
          px: 4,
          background: theme.palette.mode === 'dark'
            ? `linear-gradient(135deg, ${alpha(theme.palette.text.primary, 0.06)} 0%, ${alpha(theme.palette.text.primary, 0.03)} 50%, transparent 100%)`
            : `linear-gradient(135deg, ${neutral[100]} 0%, ${neutral[50]} 50%, transparent 100%)`,
          borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        }}
      >
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Stack direction="row" alignItems="center" spacing={2}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                boxShadow: `0 8px 24px ${alpha(theme.palette.common.black, 0.2)}`,
              }}
            >
              <PsychologyIcon sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography
                variant="h5"
                fontWeight={600}
                color="text.primary"
              >
                AI Document Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary" fontWeight={500}>
                Intelligent extraction, analysis, visualization & insights powered by AI
              </Typography>
            </Box>
          </Stack>
          <Stack direction="row" spacing={1.5}>
            {analysisResult && (
              <>
                <Button
                  variant="outlined"
                  startIcon={isExporting ? <CircularProgress size={16} color="inherit" /> : <DownloadIcon />}
                  onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                  disabled={isExporting}
                  sx={{
                    borderRadius: 1,
                    textTransform: 'none',
                    fontWeight: 600,
                    borderWidth: 2,
                    '&:hover': { borderWidth: 2 },
                  }}
                >
                  Export
                </Button>
                <Menu
                  anchorEl={exportMenuAnchor}
                  open={Boolean(exportMenuAnchor)}
                  onClose={() => setExportMenuAnchor(null)}
                  PaperProps={{
                    sx: { borderRadius: 1, minWidth: 140 },
                  }}
                >
                  {['json', 'excel', 'pdf', 'csv', 'markdown', 'html'].map((fmt) => (
                    <MenuItem key={fmt} onClick={() => handleExport(fmt)}>
                      {fmt.toUpperCase()}
                    </MenuItem>
                  ))}
                </Menu>
                <Button
                  variant="contained"
                  startIcon={<RefreshIcon />}
                  onClick={handleReset}
                  sx={{
                    borderRadius: 1,
                    textTransform: 'none',
                    fontWeight: 600,
                    background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                    boxShadow: `0 4px 14px ${alpha(theme.palette.common.black, 0.2)}`,
                    '&:hover': {
                      background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                    },
                  }}
                >
                  New Analysis
                </Button>
              </>
            )}
          </Stack>
        </Stack>

        <Box sx={{ mt: 3 }}>
          <AiUsageNotice
            title="AI analysis"
            description="Uses the document you upload. Results are generated by AI; review before sharing."
            chips={[
              { label: 'Source: Uploaded document', color: 'default', variant: 'outlined' },
              { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
              { label: 'Reversible: No source changes', color: 'success', variant: 'outlined' },
            ]}
            dense
          />
        </Box>

        {/* Stats Bar */}
        {stats && (
          <Stack direction="row" spacing={2} sx={{ mt: 3, flexWrap: 'wrap' }} useFlexGap>
            <StatCard icon={<TableChartIcon />} label="Tables" value={stats.tables} delay={0} />
            <StatCard icon={<AssessmentIcon />} label="Metrics" value={stats.metrics} delay={1} />
            <StatCard icon={<DataObjectIcon />} label="Entities" value={stats.entities} delay={2} />
            <StatCard icon={<LightbulbIcon />} label="Insights" value={stats.insights} delay={3} />
            <StatCard icon={<WarningAmberIcon />} label="Risks" value={stats.risks} delay={4} />
            <StatCard icon={<TrendingUpIcon />} label="Opportunities" value={stats.opportunities} delay={5} />
            <StatCard icon={<BarChartIcon />} label="Charts" value={stats.charts} delay={6} />
          </Stack>
        )}
      </Box>

      {/* Main Content */}
      <Box sx={{ px: 4, py: 3, maxWidth: 1400, mx: 'auto', width: '100%' }}>
        {/* Upload Section */}
        {!analysisResult && (
          <Fade in>
            <Box>
              {/* Data Source Selectors */}
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
                <ConnectionSelector
                  value={selectedConnectionId}
                  onChange={setSelectedConnectionId}
                  label="Analyze from Connection (Optional)"
                  size="small"
                  showStatus
                />
                <TemplateSelector
                  value={selectedTemplateId}
                  onChange={setSelectedTemplateId}
                  label="Report Template (Optional)"
                  size="small"
                />
              </Stack>

              {/* Dropzone */}
              <GlassCard
                gradient
                hover={false}
                sx={{
                  p: 6,
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: `2px dashed ${isDragOver ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.3)}`,
                  bgcolor: isDragOver ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : undefined,
                  transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  hidden
                  accept=".pdf,.xlsx,.xls,.csv,.doc,.docx,.png,.jpg,.jpeg"
                  onChange={handleFileSelect}
                />

                {!selectedFile && !isAnalyzing && (
                  <Box>
                    <Avatar
                      sx={{
                        width: 100,
                        height: 100,
                        mx: 'auto',
                        mb: 3,
                        background: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                        animation: `${float} 3s ease-in-out infinite`,
                      }}
                    >
                      <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
                    </Avatar>
                    <Typography variant="h5" fontWeight={600} gutterBottom>
                      Drop your document here
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                      or click to browse files
                    </Typography>
                    <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
                      {['PDF', 'Excel', 'CSV', 'Word', 'Images'].map((type) => (
                        <Chip
                          key={type}
                          label={type}
                          size="small"
                          sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100] }}
                        />
                      ))}
                    </Stack>
                  </Box>
                )}

                {selectedFile && !isAnalyzing && (
                  <Box>
                    <Avatar
                      sx={{
                        width: 80,
                        height: 80,
                        mx: 'auto',
                        mb: 3,
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                      }}
                    >
                      <CheckCircleIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
                    </Avatar>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      {selectedFile.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleAnalyze()
                      }}
                      startIcon={<BoltIcon />}
                      sx={{
                        px: 6,
                        py: 2,
                        borderRadius: 1,  // Figma spec: 8px
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        textTransform: 'none',
                        bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.2)}`,
                        transition: 'all 0.3s cubic-bezier(0.22, 1, 0.36, 1)',
                        '&:hover': {
                          transform: 'scale(1.05)',
                          bgcolor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                          boxShadow: `0 12px 40px ${alpha(theme.palette.common.black, 0.25)}`,
                        },
                      }}
                    >
                      Analyze with AI
                    </Button>
                  </Box>
                )}

                {isAnalyzing && (
                  <Box>
                    <Box
                      sx={{
                        width: 120,
                        height: 120,
                        mx: 'auto',
                        mb: 3,
                        position: 'relative',
                      }}
                    >
                      <CircularProgress
                        variant="determinate"
                        value={100}
                        size={120}
                        thickness={4}
                        sx={{ color: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] }}
                      />
                      <CircularProgress
                        variant="determinate"
                        value={analysisProgress}
                        size={120}
                        thickness={4}
                        sx={{
                          position: 'absolute',
                          left: 0,
                          color: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                          '& .MuiCircularProgress-circle': { strokeLinecap: 'round' },
                        }}
                      />
                      <Box
                        sx={{
                          position: 'absolute',
                          inset: 0,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Typography variant="h4" fontWeight={600} color="text.primary">
                          {analysisProgress}%
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      {progressStage}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={analysisProgress}
                      sx={{
                        maxWidth: 400,
                        mx: 'auto',
                        mt: 2,
                        height: 8,
                        borderRadius: 4,
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        },
                      }}
                    />
                    <Button
                      variant="outlined"
                      startIcon={<CancelIcon />}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleCancelAnalysis()
                      }}
                      sx={{ mt: 3, borderRadius: 1, textTransform: 'none' }}
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </GlassCard>

              {error && (
                <Paper
                  sx={{
                    mt: 2,
                    p: 2,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.error.main, 0.1) : alpha(theme.palette.error.main, 0.05),
                    border: `1px solid ${alpha(theme.palette.error.main, 0.3)}`,
                    borderRadius: 1,
                  }}
                >
                  <Typography color="error.main" sx={{ fontWeight: 500 }}>{error}</Typography>
                </Paper>
              )}
            </Box>
          </Fade>
        )}

        {/* Results Section */}
        {analysisResult && (
          <Fade in>
            <Box>
              {/* Warnings from partial failures */}
              {analysisResult.warnings?.length > 0 && (
                <Paper
                  sx={{
                    mb: 2,
                    p: 2,
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.warning.main, 0.1) : alpha(theme.palette.warning.main, 0.05),
                    border: `1px solid ${alpha(theme.palette.warning.main, 0.3)}`,
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2" color="warning.main" sx={{ fontWeight: 500 }}>
                    Analysis completed with warnings:
                  </Typography>
                  {analysisResult.warnings.map((w, i) => (
                    <Typography key={i} variant="body2" color="text.secondary" sx={{ ml: 2, mt: 0.5 }}>
                      {w}
                    </Typography>
                  ))}
                </Paper>
              )}

              {/* Tabs */}
              <GlassCard hover={false} sx={{ p: 0, mb: 3 }}>
                <Tabs
                  value={activeTab}
                  onChange={(e, v) => setActiveTab(v)}
                  variant="scrollable"
                  scrollButtons="auto"
                  sx={{
                    '& .MuiTab-root': {
                      textTransform: 'none',
                      fontWeight: 600,
                      fontSize: '16px',
                      minHeight: 64,
                      transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                      '&:hover': {
                        bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                      },
                      '&.Mui-selected': {
                        color: 'text.primary',
                      },
                    },
                    '& .MuiTabs-indicator': {
                      height: 3,
                      borderRadius: '3px 3px 0 0',
                      background: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
                    },
                  }}
                >
                  <Tab icon={<InsightsOutlinedIcon />} iconPosition="start" label="Overview" />
                  <Tab icon={<QuestionAnswerIcon />} iconPosition="start" label="Q&A" />
                  <Tab icon={<BarChartIcon />} iconPosition="start" label="Charts" />
                  <Tab icon={<TableChartIcon />} iconPosition="start" label="Data" />
                  <Tab icon={<LightbulbIcon />} iconPosition="start" label="Insights" />
                </Tabs>
              </GlassCard>

              {/* Overview Tab */}
              <TabPanel value={activeTab} index={0}>
                <Grid container spacing={3}>
                  {/* Executive Summary */}
                  <Grid size={{ xs: 12, lg: 8 }}>
                    <GlassCard sx={{ height: '100%' }}>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <ArticleIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Executive Summary
                        </Typography>
                      </Stack>
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8, color: 'text.secondary' }}
                      >
                        {analysisResult.summaries?.executive?.content ||
                          analysisResult.summaries?.comprehensive?.content ||
                          'Summary not available'}
                      </Typography>

                      {analysisResult.summaries?.executive?.bullet_points?.length > 0 && (
                        <Box
                          sx={{
                            mt: 3,
                            p: 2.5,
                            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                            borderRadius: 1,  // Figma spec: 8px
                            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          }}
                        >
                          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                            Key Points
                          </Typography>
                          <Stack spacing={1}>
                            {analysisResult.summaries.executive.bullet_points.map((point, i) => (
                              <Stack key={i} direction="row" alignItems="flex-start" spacing={1.5}>
                                <Box
                                  sx={{
                                    width: 24,
                                    height: 24,
                                    borderRadius: '50%',
                                    bgcolor: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                                    color: 'common.white',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: 12,
                                    fontWeight: 600,
                                    flexShrink: 0,
                                    mt: 0.25,
                                  }}
                                >
                                  {i + 1}
                                </Box>
                                <Typography variant="body2">{point}</Typography>
                              </Stack>
                            ))}
                          </Stack>
                        </Box>
                      )}
                    </GlassCard>
                  </Grid>

                  {/* Sidebar */}
                  <Grid size={{ xs: 12, lg: 4 }}>
                    <Stack spacing={3}>
                      <SentimentDisplay sentiment={analysisResult.sentiment} />
                      <DataQualityGauge quality={analysisResult.data_quality} />
                    </Stack>
                  </Grid>

                  {/* Key Metrics */}
                  <Grid size={12}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <SpeedIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Key Metrics
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                        {analysisResult.metrics?.slice(0, 8).map((metric, i) => (
                          <MetricCard key={metric.id} metric={metric} index={i} />
                        ))}
                      </Stack>
                    </GlassCard>
                  </Grid>

                  {/* Top Insights Preview */}
                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <LightbulbIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Top Insights
                        </Typography>
                      </Stack>
                      {analysisResult.insights?.slice(0, 3).map((insight, i) => (
                        <InsightCard key={insight.id} insight={insight} type="insight" index={i} />
                      ))}
                    </GlassCard>
                  </Grid>

                  {/* Risks & Opportunities Preview */}
                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <SecurityIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Risks & Opportunities
                        </Typography>
                      </Stack>
                      {analysisResult.risks?.slice(0, 2).map((risk, i) => (
                        <InsightCard key={risk.id} insight={risk} type="risk" index={i} />
                      ))}
                      {analysisResult.opportunities?.slice(0, 2).map((opp, i) => (
                        <InsightCard key={opp.id} insight={opp} type="opportunity" index={i + 2} />
                      ))}
                    </GlassCard>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Q&A Tab */}
              <TabPanel value={activeTab} index={1}>
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, lg: 8 }}>
                    <GlassCard sx={{ minHeight: 500 }}>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <SmartToyIcon />
                        </Avatar>
                        <Box>
                          <Typography variant="h6" fontWeight={600}>
                            Ask AI About Your Document
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Get instant answers with source citations
                          </Typography>
                        </Box>
                      </Stack>

                      {/* Chat Area */}
                      <Box
                        sx={{
                          minHeight: 300,
                          maxHeight: 400,
                          overflowY: 'auto',
                          mb: 3,
                          p: 2,
                          bgcolor: alpha(theme.palette.background.default, 0.5),
                          borderRadius: 1,  // Figma spec: 8px
                        }}
                      >
                        {qaHistory.length === 0 ? (
                          <Box sx={{ textAlign: 'center', py: 6 }}>
                            <Avatar
                              sx={{
                                width: 80,
                                height: 80,
                                mx: 'auto',
                                mb: 2,
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                              }}
                            >
                              <QuestionAnswerIcon sx={{ fontSize: 40, color: 'text.secondary' }} />
                            </Avatar>
                            <Typography variant="h6" color="text.secondary" gutterBottom>
                              Start a conversation
                            </Typography>
                            <Typography variant="body2" color="text.disabled">
                              Ask questions about the document content
                            </Typography>
                          </Box>
                        ) : (
                          qaHistory.map((qa, idx) => <QABubble key={idx} qa={qa} index={idx} />)
                        )}
                      </Box>

                      {/* Input */}
                      <Stack direction="row" spacing={2}>
                        <TextField
                          fullWidth
                          placeholder="Ask a question about your document..."
                          value={question}
                          onChange={(e) => setQuestion(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleAskQuestion()}
                          disabled={isAskingQuestion}
                          sx={{
                            '& .MuiOutlinedInput-root': {
                              borderRadius: 1,  // Figma spec: 8px
                              bgcolor: alpha(theme.palette.background.paper, 0.8),
                            },
                          }}
                        />
                        <Button
                          variant="contained"
                          onClick={handleAskQuestion}
                          disabled={!question.trim() || isAskingQuestion}
                          sx={{
                            minWidth: 56,
                            borderRadius: 1,  // Figma spec: 8px
                            background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                            '&:hover': {
                              background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                            },
                          }}
                        >
                          {isAskingQuestion ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                        </Button>
                      </Stack>
                    </GlassCard>
                  </Grid>

                  {/* Suggested Questions */}
                  <Grid size={{ xs: 12, lg: 4 }}>
                    <GlassCard>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Suggested Questions
                      </Typography>
                      <Stack spacing={1.5}>
                        {suggestedQuestions.map((q, idx) => (
                          <Button
                            key={idx}
                            variant="outlined"
                            onClick={() => setQuestion(q)}
                            sx={{
                              textTransform: 'none',
                              justifyContent: 'flex-start',
                              textAlign: 'left',
                              borderRadius: 1,
                              py: 1.5,
                              px: 2,
                              fontWeight: 500,
                              borderColor: alpha(theme.palette.divider, 0.2),
                              '&:hover': {
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                                borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                              },
                            }}
                          >
                            {q}
                          </Button>
                        ))}
                      </Stack>
                    </GlassCard>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Charts Tab */}
              <TabPanel value={activeTab} index={2}>
                <GlassCard sx={{ mb: 3 }}>
                  <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                    <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                      <AutoAwesomeIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        Generate Charts with Natural Language
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Describe the visualization you want and AI will create it
                      </Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={2}>
                    <TextField
                      fullWidth
                      placeholder='e.g., "Show revenue by quarter as a line chart" or "Compare categories in a pie chart"'
                      value={chartQuery}
                      onChange={(e) => setChartQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleGenerateCharts()}
                      disabled={isGeneratingCharts}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 1,  // Figma spec: 8px
                        },
                      }}
                    />
                    <Button
                      variant="contained"
                      onClick={handleGenerateCharts}
                      disabled={!chartQuery.trim() || isGeneratingCharts}
                      startIcon={isGeneratingCharts ? <CircularProgress size={16} color="inherit" /> : <BarChartIcon />}
                      sx={{
                        minWidth: 160,
                        borderRadius: 1,  // Figma spec: 8px
                        textTransform: 'none',
                        fontWeight: 600,
                        background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
                        '&:hover': {
                          background: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                        },
                      }}
                    >
                      Generate
                    </Button>
                  </Stack>
                </GlassCard>

                <Grid container spacing={3}>
                  {generatedCharts.map((chart, idx) => (
                    <Grid size={{ xs: 12, md: 6 }} key={chart.id || idx}>
                      <Zoom in timeout={300 + idx * 100}>
                        <Box>
                          <GlassCard>
                            <Typography variant="h6" fontWeight={600} gutterBottom>
                              {chart.title}
                            </Typography>
                            {chart.description && (
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                {chart.description}
                              </Typography>
                            )}
                            <Box sx={{ height: 320 }}>
                              <ZoomableChart spec={chart} data={chart.data} height={300} />
                            </Box>
                            {chart.ai_insights?.length > 0 && (
                              <Box
                                sx={{
                                  mt: 2,
                                  p: 2,
                                  bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                                  borderRadius: 1,
                                  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                                }}
                              >
                                <Typography variant="caption" fontWeight={600} color="text.secondary">
                                  AI INSIGHTS
                                </Typography>
                                {chart.ai_insights.map((insight, i) => (
                                  <Typography key={i} variant="body2" sx={{ mt: 0.5 }}>
                                    • {insight}
                                  </Typography>
                                ))}
                              </Box>
                            )}
                          </GlassCard>
                        </Box>
                      </Zoom>
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>

              {/* Data Tab */}
              <TabPanel value={activeTab} index={3}>
                <Grid container spacing={3}>
                  {/* Tables */}
                  <Grid size={12}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <TableChartIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Extracted Tables ({analysisResult.tables?.length || 0})
                        </Typography>
                      </Stack>
                      {analysisResult.tables?.map((table) => (
                        <Accordion
                          key={table.id}
                          sx={{
                            mb: 2,
                            borderRadius: '12px !important',
                            overflow: 'hidden',
                            '&:before': { display: 'none' },
                            boxShadow: 'none',
                            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                          }}
                        >
                          <AccordionSummary
                            expandIcon={<ExpandMoreIcon />}
                            sx={{
                              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50],
                              '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[100] },
                            }}
                          >
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <TableChartIcon sx={{ color: 'text.secondary' }} />
                              <Typography fontWeight={600}>{table.title || table.id}</Typography>
                              <Chip label={`${table.row_count} rows`} size="small" variant="outlined" sx={{ borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[200], color: 'text.secondary' }} />
                              <Chip label={`${table.column_count} cols`} size="small" variant="outlined" />
                            </Stack>
                          </AccordionSummary>
                          <AccordionDetails sx={{ p: 0 }}>
                            <Box sx={{ overflowX: 'auto' }}>
                              <Box
                                component="table"
                                sx={{
                                  width: '100%',
                                  borderCollapse: 'collapse',
                                  '& th': {
                                    p: 1.5,
                                    textAlign: 'left',
                                    fontWeight: 600,
                                    fontSize: '12px',
                                    textTransform: 'uppercase',
                                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                                    borderBottom: `2px solid ${theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}`,
                                  },
                                  '& td': {
                                    p: 1.5,
                                    fontSize: '0.875rem',
                                    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                                  },
                                  '& tr:hover td': {
                                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
                                  },
                                }}
                              >
                                <thead>
                                  <tr>
                                    {table.headers.map((header, i) => (
                                      <th key={i}>{header}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {table.rows.slice(0, 10).map((row, i) => (
                                    <tr key={i}>
                                      {row.map((cell, j) => (
                                        <td key={j}>{cell}</td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </Box>
                              {table.rows.length > 10 && (
                                <Box sx={{ p: 2, textAlign: 'center', bgcolor: alpha(neutral[500], 0.05) }}>
                                  <Typography variant="caption" color="text.secondary">
                                    Showing 10 of {table.rows.length} rows
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          </AccordionDetails>
                        </Accordion>
                      ))}
                    </GlassCard>
                  </Grid>

                  {/* Entities */}
                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <DataObjectIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Entities ({analysisResult.entities?.length || 0})
                        </Typography>
                      </Stack>
                      <Stack spacing={1.5}>
                        {analysisResult.entities?.slice(0, 20).map((entity) => (
                          <Stack
                            key={entity.id}
                            direction="row"
                            alignItems="center"
                            spacing={1.5}
                            sx={{
                              p: 1.5,
                              borderRadius: 1,
                              bgcolor: alpha(theme.palette.background.default, 0.5),
                              transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                              '&:hover': {
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                              },
                            }}
                          >
                            <Chip
                              label={entity.type}
                              size="small"
                              sx={{
                                minWidth: 80,
                                fontWeight: 600,
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
                                color: 'text.secondary',
                              }}
                            />
                            <Typography variant="body2" fontWeight={500}>
                              {entity.value}
                            </Typography>
                            {entity.normalized_value && entity.normalized_value !== entity.value && (
                              <Typography variant="caption" color="text.secondary">
                                → {entity.normalized_value}
                              </Typography>
                            )}
                          </Stack>
                        ))}
                      </Stack>
                    </GlassCard>
                  </Grid>

                  {/* Invoices & Contracts */}
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Stack spacing={3}>
                      {analysisResult.invoices?.length > 0 && (
                        <GlassCard>
                          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                              <ReceiptLongIcon />
                            </Avatar>
                            <Typography variant="h6" fontWeight={600}>
                              Invoices Detected
                            </Typography>
                          </Stack>
                          {analysisResult.invoices.map((invoice) => (
                            <Box
                              key={invoice.id}
                              sx={{
                                p: 2,
                                mb: 2,
                                borderRadius: 1,
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                                border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                              }}
                            >
                              <Typography variant="subtitle2" fontWeight={600}>
                                {invoice.vendor_name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Invoice #{invoice.invoice_number} • {invoice.invoice_date}
                              </Typography>
                              <Typography variant="h5" fontWeight={600} color="text.primary" sx={{ mt: 1 }}>
                                {invoice.currency} {invoice.grand_total}
                              </Typography>
                            </Box>
                          ))}
                        </GlassCard>
                      )}

                      {analysisResult.contracts?.length > 0 && (
                        <GlassCard>
                          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                            <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                              <GavelIcon />
                            </Avatar>
                            <Typography variant="h6" fontWeight={600}>
                              Contracts Detected
                            </Typography>
                          </Stack>
                          {analysisResult.contracts.map((contract) => (
                            <Box
                              key={contract.id}
                              sx={{
                                p: 2,
                                borderRadius: 1,
                                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                                border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
                              }}
                            >
                              <Typography variant="subtitle2" fontWeight={600}>
                                {contract.contract_type}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {contract.effective_date} → {contract.expiration_date}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Parties: {contract.parties?.map((p) => p.name).join(', ')}
                              </Typography>
                            </Box>
                          ))}
                        </GlassCard>
                      )}
                    </Stack>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Insights Tab */}
              <TabPanel value={activeTab} index={4}>
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <LightbulbIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Key Insights ({analysisResult.insights?.length || 0})
                        </Typography>
                      </Stack>
                      {analysisResult.insights?.map((insight, i) => (
                        <InsightCard key={insight.id} insight={insight} type="insight" index={i} />
                      ))}
                    </GlassCard>
                  </Grid>

                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <SecurityIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Risks ({analysisResult.risks?.length || 0})
                        </Typography>
                      </Stack>
                      {analysisResult.risks?.map((risk, i) => (
                        <InsightCard key={risk.id} insight={risk} type="risk" index={i} />
                      ))}
                    </GlassCard>
                  </Grid>

                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <RocketLaunchIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Opportunities ({analysisResult.opportunities?.length || 0})
                        </Typography>
                      </Stack>
                      {analysisResult.opportunities?.map((opp, i) => (
                        <InsightCard key={opp.id} insight={opp} type="opportunity" index={i} />
                      ))}
                    </GlassCard>
                  </Grid>

                  <Grid size={{ xs: 12, md: 6 }}>
                    <GlassCard>
                      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 3 }}>
                        <Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], color: 'text.secondary' }}>
                          <PlaylistAddCheckIcon />
                        </Avatar>
                        <Typography variant="h6" fontWeight={600}>
                          Action Items ({analysisResult.action_items?.length || 0})
                        </Typography>
                      </Stack>
                      {analysisResult.action_items?.map((action, i) => (
                        <InsightCard key={action.id} insight={action} type="action" index={i} />
                      ))}
                    </GlassCard>
                  </Grid>
                </Grid>
              </TabPanel>
            </Box>
          </Fade>
        )}

        {/* Footer */}
        <Box sx={{ textAlign: 'center', py: 4, mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Supported formats: PDF, Excel (XLSX, XLS), CSV, Word, Images
          </Typography>
          <Typography variant="caption" color="text.disabled" sx={{ mt: 0.5, display: 'block' }}>
            AI-powered analysis with intelligent extraction, multi-mode summaries, Q&A, and visualization
          </Typography>
        </Box>
      </Box>
    </Box>
  )
}
