/**
 * Dashboard Page - Premium Analytics Dashboard
 * Sophisticated UI with modern design patterns and micro-interactions
 */

import { Box } from '@mui/material'
import SuccessCelebration from '@/components/SuccessCelebration'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice'

import {
  useDashboardNavigation,
  useDashboardData,
  useRecommendations,
  useOnboarding,
  useCommandPalette,
} from '../hooks/useDashboardData'

import { PageContainer } from '../components/DashboardStyledComponents'
import DashboardHeader from '../components/DashboardHeader'
import OnboardingSection from '../components/OnboardingSection'
import StatsGrid from '../components/StatsGrid'
import QuickActionsPanel from '../components/QuickActionsPanel'
import RecentJobsPanel from '../components/RecentJobsPanel'
import RightSidebar from '../components/RightSidebar'
import RecommendationsSection from '../components/RecommendationsSection'
import ActiveConnectionBanner from '../components/ActiveConnectionBanner'

export default function DashboardPage() {
  const { execute, handleNavigate } = useDashboardNavigation()
  const {
    templates,
    savedConnections,
    activeConnection,
    jobs,
    analytics,
    favorites,
    loading,
    refreshing,
    handleRefresh,
  } = useDashboardData()

  const {
    recommendations,
    recLoading,
    recFromAI,
    handleRefreshRecommendations,
  } = useRecommendations(templates)

  const { handleOpenCommandPalette } = useCommandPalette()

  const summary = analytics?.summary || {}
  const metrics = analytics?.metrics || {}
  const topTemplates = analytics?.topTemplates || []
  const jobsTrend = analytics?.jobsTrend || []

  const {
    needsOnboarding,
    celebrating,
    onCelebrationComplete,
    handleDismissOnboarding,
  } = useOnboarding(savedConnections, templates, metrics, execute)

  const maxTrend = Math.max(...jobsTrend.map(d => d.total || 0), 1)

  return (
    <PageContainer>
      <SuccessCelebration trigger={celebrating} onComplete={onCelebrationComplete} />

      <DashboardHeader
        refreshing={refreshing}
        handleRefresh={handleRefresh}
        handleNavigate={handleNavigate}
        handleOpenCommandPalette={handleOpenCommandPalette}
      />

      <ReportGlossaryNotice dense showChips={false} sx={{ mb: 3 }} />

      <OnboardingSection
        needsOnboarding={needsOnboarding}
        savedConnections={savedConnections}
        templates={templates}
        metrics={metrics}
        handleNavigate={handleNavigate}
        handleDismissOnboarding={handleDismissOnboarding}
      />

      <StatsGrid
        summary={summary}
        metrics={metrics}
        savedConnections={savedConnections}
        templates={templates}
        handleNavigate={handleNavigate}
      />

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '320px 1fr 300px' },
          gap: 3,
        }}
      >
        <QuickActionsPanel
          handleNavigate={handleNavigate}
          jobsTrend={jobsTrend}
          maxTrend={maxTrend}
        />
        <RecentJobsPanel
          jobs={jobs}
          loading={loading}
          handleNavigate={handleNavigate}
        />
        <RightSidebar
          topTemplates={topTemplates}
          favorites={favorites}
          handleNavigate={handleNavigate}
        />
      </Box>

      <RecommendationsSection
        recommendations={recommendations}
        recLoading={recLoading}
        recFromAI={recFromAI}
        templates={templates}
        handleRefreshRecommendations={handleRefreshRecommendations}
        handleNavigate={handleNavigate}
      />

      <ActiveConnectionBanner activeConnection={activeConnection} />
    </PageContainer>
  )
}
