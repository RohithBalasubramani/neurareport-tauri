import { alpha, Alert, Box, Collapse, LinearProgress } from '@mui/material'
import { neutral } from '@/app/theme'
import LoadingState from '@/components/feedback/LoadingState.jsx'
import Surface from '@/components/layout/Surface.jsx'
import { surfaceStackSx } from '../utils/generateFeatureUtils'
import { useTemplatePicker } from '../hooks/useTemplatePicker'
import TemplatePickerToolbar from './template-picker/TemplatePickerToolbar.jsx'
import TemplatePickerTabs from './template-picker/TemplatePickerTabs.jsx'

export function TemplatePicker({ selected, onToggle, outputFormats, setOutputFormats, tagFilter, setTagFilter, onEditTemplate }) {
  const picker = useTemplatePicker({ selected, onToggle, setOutputFormats })

  const showRefreshing = (picker.isFetching && !picker.isLoading) || picker.catalogQuery.isFetching

  return (
    <Surface sx={surfaceStackSx}>
      <TemplatePickerToolbar
        allTags={picker.allTags}
        tagFilter={tagFilter}
        setTagFilter={setTagFilter}
        nameQuery={picker.nameQuery}
        onNameQueryChange={picker.handleNameQueryChange}
        requirement={picker.requirement}
        setRequirement={picker.setRequirement}
        kindHints={picker.kindHints}
        setKindHints={picker.setKindHints}
        kindOptions={picker.kindOptions}
        domainHints={picker.domainHints}
        setDomainHints={picker.setDomainHints}
        domainOptions={picker.domainOptions}
        recommending={picker.recommending}
        queueingRecommendations={picker.queueingRecommendations}
        importing={picker.importing}
        importInputRef={picker.importInputRef}
        onRecommend={picker.handleRecommend}
        onQueueRecommend={picker.handleQueueRecommend}
        onRequirementKeyDown={picker.handleRequirementKeyDown}
        onImport={picker.handleImportTemplate}
      />
      <Collapse in={showRefreshing} unmountOnExit>
        <LinearProgress sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] }, borderRadius: 1 }} aria-label="Refreshing templates" />
      </Collapse>
      {picker.isLoading ? (
        <LoadingState
          label="Loading approved templates..."
          description="Fetching the latest approved templates from the pipeline."
        />
      ) : picker.isError ? (
        <Alert severity="error">
          {String(picker.error?.message || 'Failed to load approved templates.')}
        </Alert>
      ) : (
        <TemplatePickerTabs
          activeTab={picker.activeTab}
          setActiveTab={picker.setActiveTab}
          selected={selected}
          outputFormats={outputFormats}
          setOutputFormats={setOutputFormats}
          tagFilter={tagFilter}
          companyCandidates={picker.companyCandidates}
          starterCandidates={picker.starterCandidates}
          applyNameFilter={picker.applyNameFilter}
          applyTagFilter={picker.applyTagFilter}
          showStarterInAll={picker.showStarterInAll}
          recommendations={picker.recommendations}
          deleting={picker.deleting}
          exporting={picker.exporting}
          onToggle={onToggle}
          onDelete={picker.handleDeleteTemplate}
          onExport={picker.handleExportTemplate}
          onEditTemplate={onEditTemplate}
          onFindInAll={picker.handleFindInAll}
          toast={picker.toast}
        />
      )}
    </Surface>
  )
}

export default TemplatePicker
