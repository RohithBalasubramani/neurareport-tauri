import { useMemo } from 'react'
import Grid from '@mui/material/Grid2'
import { Box, Stack, Tab, Tabs, Typography } from '@mui/material'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import CompanyTemplateCard from './CompanyTemplateCard.jsx'
import StarterGrid from './StarterGrid.jsx'
import RecommendationsGrid from './RecommendationsGrid.jsx'

export default function TemplatePickerTabs({
  activeTab,
  setActiveTab,
  selected,
  outputFormats,
  setOutputFormats,
  tagFilter,
  companyCandidates,
  starterCandidates,
  applyNameFilter,
  applyTagFilter,
  showStarterInAll,
  recommendations,
  deleting,
  exporting,
  onToggle,
  onDelete,
  onExport,
  onEditTemplate,
  onFindInAll,
  toast,
}) {
  const companyMatches = useMemo(
    () => applyNameFilter(applyTagFilter(companyCandidates, tagFilter)),
    [applyNameFilter, applyTagFilter, companyCandidates, tagFilter],
  )
  const starterMatches = useMemo(
    () => applyNameFilter(applyTagFilter(starterCandidates, tagFilter)),
    [applyNameFilter, applyTagFilter, starterCandidates, tagFilter],
  )

  const renderCompanyGrid = (list) => (
    <Grid container spacing={2.5}>
      {list.map((t) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={t.id} sx={{ minWidth: 0 }}>
          <CompanyTemplateCard
            template={t}
            selectedState={selected.includes(t.id)}
            outputFormats={outputFormats}
            setOutputFormats={setOutputFormats}
            deleting={deleting}
            exporting={exporting}
            onToggle={onToggle}
            onDelete={onDelete}
            onExport={onExport}
            onEditTemplate={onEditTemplate}
            toast={toast}
          />
        </Grid>
      ))}
    </Grid>
  )

  const renderAllTab = () => {
    const sections = []
    const hasCompanyTemplates = companyCandidates.length > 0
    const starterSectionList = showStarterInAll ? applyTagFilter(starterCandidates, tagFilter) : starterMatches
    const hasStarterTemplates = showStarterInAll && starterSectionList.length > 0
    if (hasCompanyTemplates) {
      sections.push(
        <Stack key="company" spacing={1.5}>
          <Typography variant="subtitle2">Company templates</Typography>
          {companyMatches.length ? (
            renderCompanyGrid(companyMatches)
          ) : (
            <Typography variant="body2" color="text.secondary">
              No company templates match the current filters.
            </Typography>
          )}
        </Stack>,
      )
    }
    if (hasStarterTemplates) {
      sections.push(
        <Stack key="starter" spacing={1.5}>
          <Typography variant="subtitle2">Starter templates</Typography>
          {starterSectionList.length ? (
            <StarterGrid list={starterSectionList} />
          ) : (
            <Typography variant="body2" color="text.secondary">
              No starter templates match the current filters.
            </Typography>
          )}
        </Stack>,
      )
    }
    if (!sections.length) {
      return (
        <EmptyState
          size="medium"
          title="No templates match the current filters"
          description="Adjust the search text or tags to see more templates."
        />
      )
    }
    return <Stack spacing={3}>{sections}</Stack>
  }

  const renderCompanyTab = () => {
    if (!companyMatches.length) {
      return (
        <EmptyState
          size="medium"
          title="No company templates match"
          description="Try clearing the search text or adjusting the tag filters."
        />
      )
    }
    return renderCompanyGrid(companyMatches)
  }

  const renderStarterTab = () => {
    if (!starterMatches.length) {
      return (
        <EmptyState
          size="medium"
          title="No starter templates available"
          description="Starter templates will appear here when provided by the catalog."
        />
      )
    }
    return <StarterGrid list={starterMatches} />
  }

  const tabContent = () => {
    if (activeTab === 'company') return renderCompanyTab()
    if (activeTab === 'starter') return renderStarterTab()
    if (activeTab === 'recommended') return <RecommendationsGrid recommendations={recommendations} onFindInAll={onFindInAll} />
    return renderAllTab()
  }

  return (
    <>
      <Tabs
        value={activeTab}
        onChange={(event, value) => setActiveTab(value)}
        variant="scrollable"
        allowScrollButtonsMobile
      >
        <Tab label="All" value="all" />
        <Tab label="Company" value="company" />
        <Tab label="Starter" value="starter" />
        <Tab label="Recommended" value="recommended" />
      </Tabs>
      <Box sx={{ mt: 2 }}>{tabContent()}</Box>
    </>
  )
}
