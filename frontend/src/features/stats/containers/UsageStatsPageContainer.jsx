/**
 * Premium Usage Statistics Page
 * Beautiful analytics dashboard with charts and theme-based styling
 */
import { useState, useCallback, useEffect, useRef, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Box,
  Typography,
  Stack,
  CardContent,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Grid,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import BarChartIcon from '@mui/icons-material/BarChart'
import PieChartIcon from '@mui/icons-material/PieChart'
import DescriptionIcon from '@mui/icons-material/Description'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import ScheduleIcon from '@mui/icons-material/Schedule'
import WorkIcon from '@mui/icons-material/Work'
import StorageIcon from '@mui/icons-material/Storage'
import DownloadIcon from '@mui/icons-material/Download'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
  LineChart,
  Line,
} from 'recharts'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility, useNavigateInteraction } from '@/components/ux/governance'
import * as api from '@/api/client'
import { neutral, primary, palette } from '@/app/theme'
import { fadeInUp, pulse, GlassCard, StyledFormControl, RefreshButton, ExportButton } from '@/styles'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1400,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

const HeaderContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

const StyledTabs = styled(Tabs)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  '& .MuiTab-root': {
    // Figma spec: Inactive tab - #374151 text, transparent bg
    color: theme.palette.mode === 'dark' ? theme.palette.text.secondary : neutral[700],
    textTransform: 'none',
    minWidth: 100,
    fontWeight: 500,
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    padding: '8px 32px',  // Figma spec
    '&.Mui-selected': {
      // Figma spec: Active tab - #02634E text, #EBFEF6 bg
      color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[900],
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    },
    '&:hover': {
      color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[700],
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
    },
  },
  '& .MuiTabs-indicator': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[900],
    height: 2,
  },
}))

const StatCardContent = styled(CardContent)(({ theme }) => ({
  padding: theme.spacing(2.5),
  '&:last-child': {
    paddingBottom: theme.spacing(2.5),
  },
}))

// =============================================================================
// HELPERS
// =============================================================================

const PERIOD_OPTIONS = [
  { value: 'day', label: 'Last 24 hours' },
  { value: 'week', label: 'Last 7 days' },
  { value: 'month', label: 'Last 30 days' },
]

const getChartColors = (theme) => [
  theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
  theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
  theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  theme.palette.mode === 'dark' ? neutral[300] : neutral[300],
  theme.palette.text.secondary,
]

const getStatusColors = (theme) => ({
  completed: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  failed: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
  pending: theme.palette.mode === 'dark' ? neutral[300] : neutral[500],
  running: theme.palette.mode === 'dark' ? neutral[500] : neutral[500],
  cancelled: theme.palette.text.secondary,
})

// =============================================================================
// STAT CARD COMPONENT
// =============================================================================

function StatCard({ title, value, subtitle, icon: Icon, trend, color, onClick }) {
  const theme = useTheme()
  const trendPositive = trend > 0
  const TrendIcon = trendPositive ? TrendingUpIcon : TrendingDownIcon
  const trendColor = theme.palette.text.secondary
  const accentColor = color || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])

  return (
    <GlassCard
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        animation: `${fadeInUp} 0.5s ease-out`,
        '&:active': onClick ? { transform: 'scale(0.98)' } : {},
      }}
    >
      <StatCardContent>
        <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
          <Box>
            <Typography
              sx={{
                fontSize: '0.75rem',
                fontWeight: 500,
                color: theme.palette.text.secondary,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                mb: 0.5,
              }}
            >
              {title}
            </Typography>
            <Typography
              sx={{
                fontSize: '1.75rem',
                fontWeight: 600,
                color: theme.palette.text.primary,
                lineHeight: 1.2,
              }}
            >
              {value}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: theme.palette.text.secondary,
                  mt: 0.5,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2.5,
              bgcolor: alpha(accentColor, 0.15),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Icon sx={{ fontSize: 20, color: accentColor }} />
          </Box>
        </Stack>
        {trend !== undefined && trend !== null && (
          <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 1.5 }}>
            <TrendIcon sx={{ fontSize: 14, color: trendColor }} />
            <Typography sx={{ fontSize: '0.75rem', color: trendColor, fontWeight: 500 }}>
              {Math.abs(trend)}%
            </Typography>
            <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
              vs previous period
            </Typography>
          </Stack>
        )}
      </StatCardContent>
    </GlassCard>
  )
}

// =============================================================================
// CHART CARD COMPONENT
// =============================================================================

function ChartCard({ title, subtitle, children, height = 280, actions }) {
  const theme = useTheme()

  return (
    <GlassCard sx={{ height: '100%', animation: `${fadeInUp} 0.5s ease-out 0.2s both` }}>
      <CardContent sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
          <Box>
            <Typography
              sx={{
                fontSize: '0.875rem',
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              {title}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: theme.palette.text.secondary,
                  mt: 0.25,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          {actions}
        </Stack>
        <Box sx={{ flex: 1, minHeight: height }}>
          {children}
        </Box>
      </CardContent>
    </GlassCard>
  )
}

// =============================================================================
// CUSTOM TOOLTIP COMPONENT
// =============================================================================

function CustomTooltip({ active, payload, label }) {
  const theme = useTheme()
  if (!active || !payload?.length) return null

  return (
    <Box
      sx={{
        bgcolor: alpha(theme.palette.background.paper, 0.95),
        backdropFilter: 'blur(8px)',
        border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        borderRadius: 1,  // Figma spec: 8px
        p: 1.5,
        boxShadow: `0 4px 12px ${alpha(theme.palette.common.black, 0.15)}`,
      }}
    >
      <Typography sx={{ fontSize: '0.75rem', fontWeight: 600, color: theme.palette.text.primary, mb: 0.5 }}>
        {label}
      </Typography>
      {payload.map((entry, index) => (
        <Stack key={index} direction="row" alignItems="center" spacing={1}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: entry.color,
            }}
          />
          <Typography sx={{ fontSize: '12px', color: theme.palette.text.secondary }}>
            {entry.name}: {entry.value}
          </Typography>
        </Stack>
      ))}
    </Box>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const TAB_MAP = { overview: 0, jobs: 1, templates: 2 }
const TAB_NAMES = ['overview', 'jobs', 'templates']

export default function UsageStatsPage() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const navigate = useNavigateInteraction()
  const [searchParams, setSearchParams] = useSearchParams()
  const didLoadRef = useRef(false)
  const handleNavigate = useCallback(
    (path, label, intent = {}) =>
      navigate(path, { label, intent: { from: 'stats', ...intent } }),
    [navigate]
  )

  // Get tab from URL or default to 0
  const tabParam = searchParams.get('tab') || 'overview'
  const activeTab = TAB_MAP[tabParam] ?? 0

  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(searchParams.get('period') || 'week')

  const [dashboardData, setDashboardData] = useState(null)
  const [usageData, setUsageData] = useState(null)
  const [historyData, setHistoryData] = useState(null)

  // Chart colors based on theme
  const CHART_COLORS = useMemo(() => getChartColors(theme), [theme])
  const STATUS_COLORS = useMemo(() => getStatusColors(theme), [theme])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const [dashboard, usage, history] = await Promise.all([
        api.getDashboardAnalytics(),
        api.getUsageStatistics(period),
        api.getReportHistory({ limit: 100 }),
      ])
      setDashboardData(dashboard)
      setUsageData(usage)
      setHistoryData(history)
    } catch (err) {
      toast.show(err.message || 'Failed to load statistics', 'error')
    } finally {
      setLoading(false)
    }
  }, [period, toast])

  const handleRefresh = useCallback(
    () =>
      execute({
        type: InteractionType.EXECUTE,
        label: 'Refresh usage statistics',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        suppressSuccessToast: true,
        intent: { period },
        action: fetchData,
      }),
    [execute, fetchData, period]
  )

  useEffect(() => {
    if (didLoadRef.current) return
    didLoadRef.current = true
    fetchData()
  }, [fetchData])

  useEffect(() => {
    if (!didLoadRef.current) return
    fetchData()
  }, [period, fetchData])

  const summary = dashboardData?.summary || {}
  const metrics = dashboardData?.metrics || {}
  const jobsTrend = dashboardData?.jobsTrend || []
  const topTemplates = dashboardData?.topTemplates || []

  const statusData = useMemo(() => {
    const byStatus = usageData?.byStatus || {}
    return Object.entries(byStatus).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      color: STATUS_COLORS[name] || theme.palette.text.secondary,
    }))
  }, [usageData, STATUS_COLORS, theme])

  const kindData = useMemo(() => {
    const byKind = usageData?.byKind || {}
    return Object.entries(byKind).map(([name, value]) => ({
      name: name.toUpperCase(),
      value,
      color: name === 'pdf'
        ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900])
        : (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
    }))
  }, [usageData, theme])

  const templateBreakdown = useMemo(() => {
    const breakdown = usageData?.templateBreakdown || []
    if (breakdown.length > 0) return breakdown
    return topTemplates.slice(0, 6).map((t) => ({
      name: t.name || t.id?.slice(0, 12),
      count: t.runCount || 0,
      kind: t.kind || 'pdf',
    }))
  }, [usageData, topTemplates])

  const historyByDay = useMemo(() => {
    const history = historyData?.history || []
    const byDay = {}
    history.forEach((item) => {
      const date = item.createdAt?.split('T')[0]
      if (!date) return
      if (!byDay[date]) {
        byDay[date] = { date, completed: 0, failed: 0, total: 0 }
      }
      byDay[date].total += 1
      if (item.status === 'completed') byDay[date].completed += 1
      else if (item.status === 'failed') byDay[date].failed += 1
    })
    return Object.values(byDay)
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-14)
  }, [historyData])

  const handleExportStats = useCallback(
    () =>
      execute({
        type: InteractionType.DOWNLOAD,
        label: 'Export usage statistics',
        reversibility: Reversibility.FULLY_REVERSIBLE,
        intent: { period },
        action: async () => {
          const exportData = {
            exportedAt: new Date().toISOString(),
            period,
            dashboard: dashboardData,
            usage: usageData,
            historyCount: historyData?.total || 0,
          }
          const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
          const url = URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `neurareport-stats-${period}-${Date.now()}.json`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          URL.revokeObjectURL(url)
        },
      }),
    [execute, period, dashboardData, usageData, historyData]
  )

  if (loading && !dashboardData) {
    return (
      <PageContainer>
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <CircularProgress size={40} />
          <Typography sx={{ mt: 2, color: theme.palette.text.secondary }}>
            Loading statistics...
          </Typography>
        </Box>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      {/* Header */}
      <HeaderContainer direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h5" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
            Usage Statistics
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Detailed analytics and insights for your workspace
          </Typography>
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <StyledFormControl size="small">
            <InputLabel>Time Period</InputLabel>
            <Select
              value={period}
              onChange={(e) => {
                const newPeriod = e.target.value
                setPeriod(newPeriod)
                const newParams = new URLSearchParams(searchParams)
                newParams.set('period', newPeriod)
                setSearchParams(newParams, { replace: true })
              }}
              label="Time Period"
            >
              {PERIOD_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </Select>
          </StyledFormControl>
          <ExportButton
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon sx={{ fontSize: 16 }} />}
            onClick={handleExportStats}
          >
            Export
          </ExportButton>
          <RefreshButton
            onClick={handleRefresh}
            disabled={loading}
            sx={{ color: theme.palette.text.secondary }}
          >
            {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
          </RefreshButton>
        </Stack>
      </HeaderContainer>

      {/* Overview Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Total Jobs"
            value={summary.totalJobs || 0}
            subtitle={`${metrics.jobsThisWeek || 0} this week`}
            icon={WorkIcon}
            color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
            onClick={() => handleNavigate('/jobs', 'Open jobs')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Success Rate"
            value={`${(metrics.successRate || 0).toFixed(1)}%`}
            subtitle={`${summary.completedJobs || 0} completed`}
            icon={CheckCircleIcon}
            color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
            onClick={() => handleNavigate('/history', 'Open history')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Templates"
            value={summary.totalTemplates || 0}
            subtitle={`${summary.approvedTemplates || 0} approved`}
            icon={DescriptionIcon}
            color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
            onClick={() => handleNavigate('/templates', 'Open templates')}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Connections"
            value={summary.totalConnections || 0}
            subtitle={`${summary.activeConnections || 0} active`}
            icon={StorageIcon}
            color={theme.palette.mode === 'dark' ? neutral[300] : neutral[300]}
            onClick={() => handleNavigate('/connections', 'Open connections')}
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <StyledTabs
        value={activeTab}
        onChange={(e, v) => {
          const newParams = new URLSearchParams(searchParams)
          newParams.set('tab', TAB_NAMES[v])
          setSearchParams(newParams, { replace: true })
        }}
      >
        <Tab label="Overview" icon={<BarChartIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
        <Tab label="Jobs" icon={<WorkIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
        <Tab label="Templates" icon={<DescriptionIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
      </StyledTabs>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={2}>
          {/* Jobs Trend Chart */}
          <Grid size={{ xs: 12, lg: 8 }}>
            <ChartCard title="Jobs Trend" subtitle="Daily job completions over the past week">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={jobsTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                  />
                  <YAxis
                    tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="completed" name="Completed" fill={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="failed" name="Failed" fill={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </Grid>

          {/* Status Distribution */}
          <Grid size={{ xs: 12, lg: 4 }}>
            <ChartCard title="Job Status" subtitle="Distribution by status">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value) => (
                      <span style={{ color: theme.palette.text.secondary, fontSize: '0.75rem' }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          </Grid>

          {/* Template Type Distribution */}
          <Grid size={{ xs: 12, md: 6 }}>
            <ChartCard title="Template Types" subtitle="PDF vs Excel usage">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={kindData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={{ stroke: theme.palette.text.secondary }}
                  >
                    {kindData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </ChartCard>
          </Grid>

          {/* Top Templates */}
          <Grid size={{ xs: 12, md: 6 }}>
            <ChartCard title="Top Templates" subtitle="Most used templates">
              {templateBreakdown.length === 0 ? (
                <Box sx={{ py: 6, textAlign: 'center' }}>
                  <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
                    No template usage data
                  </Typography>
                </Box>
              ) : (
                <Stack spacing={1.5}>
                  {templateBreakdown.map((template, index) => (
                    <Box key={index}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.5 }}>
                        <Stack direction="row" alignItems="center" spacing={1}>
                          <Typography sx={{ fontSize: '14px', color: theme.palette.text.primary }}>
                            {template.name}
                          </Typography>
                          <Chip
                            label={template.kind?.toUpperCase()}
                            size="small"
                            sx={{
                              height: 18,
                              fontSize: '10px',
                              bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                              color: 'text.secondary',
                              borderRadius: 1,
                            }}
                          />
                        </Stack>
                        <Typography sx={{ fontSize: '0.75rem', color: theme.palette.text.secondary }}>
                          {template.count} runs
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={
                          templateBreakdown[0]?.count
                            ? (template.count / templateBreakdown[0].count) * 100
                            : 0
                        }
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          bgcolor: alpha(theme.palette.divider, 0.15),
                          '& .MuiLinearProgress-bar': {
                            bgcolor: CHART_COLORS[index % CHART_COLORS.length],
                            borderRadius: 3,
                          },
                        }}
                      />
                    </Box>
                  ))}
                </Stack>
              )}
            </ChartCard>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={2}>
          {/* Jobs Over Time */}
          <Grid size={12}>
            <ChartCard title="Jobs History" subtitle="Job executions over the past 2 weeks" height={320}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={historyByDay}>
                  <defs>
                    <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: theme.palette.text.secondary, fontSize: 10 }}
                    axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                    tickFormatter={(v) => v.slice(5)}
                  />
                  <YAxis
                    tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="completed"
                    name="Completed"
                    stroke={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
                    fill="url(#colorCompleted)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="failed"
                    name="Failed"
                    stroke={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
                    fill="url(#colorFailed)"
                    strokeWidth={2}
                  />
                  <Legend
                    verticalAlign="top"
                    height={36}
                    formatter={(value) => (
                      <span style={{ color: theme.palette.text.secondary, fontSize: '0.75rem' }}>{value}</span>
                    )}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartCard>
          </Grid>

          {/* Job Stats Cards */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Jobs Today"
              value={metrics.jobsToday || 0}
              icon={ScheduleIcon}
              color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
              onClick={() => handleNavigate('/jobs', 'Open jobs')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Jobs This Week"
              value={metrics.jobsThisWeek || 0}
              icon={WorkIcon}
              color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
              onClick={() => handleNavigate('/jobs', 'Open jobs')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Jobs This Month"
              value={metrics.jobsThisMonth || 0}
              icon={BarChartIcon}
              color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
              onClick={() => handleNavigate('/jobs', 'Open jobs')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Failed Jobs"
              value={summary.failedJobs || 0}
              icon={ErrorIcon}
              color={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
              onClick={() =>
                handleNavigate('/history?status=failed', 'Open failed history', { status: 'failed' })
              }
            />
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={2}>
          {/* Template Stats */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Total Templates"
              value={summary.totalTemplates || 0}
              icon={DescriptionIcon}
              color={theme.palette.mode === 'dark' ? neutral[500] : neutral[500]}
              onClick={() => handleNavigate('/templates', 'Open templates')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="PDF Templates"
              value={summary.pdfTemplates || 0}
              icon={DescriptionIcon}
              color={theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}
              onClick={() =>
                handleNavigate('/templates?kind=pdf', 'Open PDF templates', { kind: 'pdf' })
              }
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Excel Templates"
              value={summary.excelTemplates || 0}
              icon={DescriptionIcon}
              color={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}
              onClick={() =>
                handleNavigate('/templates?kind=excel', 'Open Excel templates', { kind: 'excel' })
              }
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Active Schedules"
              value={summary.activeSchedules || 0}
              icon={ScheduleIcon}
              color={theme.palette.mode === 'dark' ? neutral[300] : neutral[500]}
              onClick={() => handleNavigate('/schedules', 'Open schedules')}
            />
          </Grid>

          {/* Template Usage */}
          <Grid size={12}>
            <ChartCard title="Template Usage Breakdown" subtitle="Jobs per template" height={400}>
              {templateBreakdown.length === 0 ? (
                <Box sx={{ py: 8, textAlign: 'center' }}>
                  <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.text.disabled, mb: 2 }} />
                  <Typography sx={{ color: theme.palette.text.secondary, fontSize: '0.875rem' }}>
                    No template usage data available
                  </Typography>
                </Box>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={templateBreakdown} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                    <XAxis
                      type="number"
                      tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                      axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                    />
                    <YAxis
                      type="category"
                      dataKey="name"
                      tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                      axisLine={{ stroke: alpha(theme.palette.divider, 0.3) }}
                      width={120}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" name="Jobs" fill={theme.palette.mode === 'dark' ? neutral[500] : neutral[700]} radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </ChartCard>
          </Grid>
        </Grid>
      )}
    </PageContainer>
  )
}
