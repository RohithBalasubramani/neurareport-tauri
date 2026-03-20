/**
 * Premium Usage Statistics Page
 * Beautiful analytics dashboard with charts and theme-based styling
 */
import {
  Box,
  Typography,
  Stack,
  CircularProgress,
  Tabs,
  Tab,
  alpha,
  styled,
} from '@mui/material'
import BarChartIcon from '@mui/icons-material/BarChart'
import DescriptionIcon from '@mui/icons-material/Description'
import WorkIcon from '@mui/icons-material/Work'
import { fadeInUp } from '@/styles'
import { neutral } from '@/app/theme'

import { useUsageStats } from '../hooks/useUsageStats'
import StatsHeader from '../components/StatsHeader'
import OverviewTab from '../components/OverviewTab'
import JobsTab from '../components/JobsTab'
import TemplatesTab from '../components/TemplatesTab'

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
    color: theme.palette.mode === 'dark' ? theme.palette.text.secondary : neutral[700],
    textTransform: 'none',
    minWidth: 100,
    fontWeight: 500,
    transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
    padding: '8px 32px',
    '&.Mui-selected': {
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

export default function UsageStatsPage() {
  const stats = useUsageStats()
  const {
    theme, loading, period, activeTab,
    summary, metrics, jobsTrend,
    statusData, kindData, templateBreakdown,
    historyByDay, CHART_COLORS,
    handleNavigate, handleRefresh, handleExportStats,
    handleTabChange, handlePeriodChange, dashboardData,
  } = stats

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
      <StatsHeader
        theme={theme}
        period={period}
        loading={loading}
        summary={summary}
        metrics={metrics}
        handleNavigate={handleNavigate}
        handleRefresh={handleRefresh}
        handleExportStats={handleExportStats}
        handlePeriodChange={handlePeriodChange}
        HeaderContainer={HeaderContainer}
      />

      <StyledTabs value={activeTab} onChange={handleTabChange}>
        <Tab label="Overview" icon={<BarChartIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
        <Tab label="Jobs" icon={<WorkIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
        <Tab label="Templates" icon={<DescriptionIcon sx={{ fontSize: 18 }} />} iconPosition="start" />
      </StyledTabs>

      {activeTab === 0 && (
        <OverviewTab
          jobsTrend={jobsTrend}
          statusData={statusData}
          kindData={kindData}
          templateBreakdown={templateBreakdown}
          CHART_COLORS={CHART_COLORS}
        />
      )}

      {activeTab === 1 && (
        <JobsTab
          historyByDay={historyByDay}
          metrics={metrics}
          summary={summary}
          handleNavigate={handleNavigate}
        />
      )}

      {activeTab === 2 && (
        <TemplatesTab
          summary={summary}
          templateBreakdown={templateBreakdown}
          handleNavigate={handleNavigate}
        />
      )}
    </PageContainer>
  )
}
