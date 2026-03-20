import { Divider, Box, Typography } from '@mui/material'

import Surface from '@/components/layout/Surface.jsx'
import { surfaceStackSx } from '../utils/generateFeatureUtils'
import { useGenerateAndDownload } from '../hooks/useGenerateAndDownload'
import SavedChartsPanel from './run/SavedChartsPanel.jsx'

import RunReportsHeader from './generate-download/RunReportsHeader.jsx'
import KeyTokenValuesSection from './generate-download/KeyTokenValuesSection.jsx'
import FilterGroupSection from './generate-download/FilterGroupSection.jsx'
import DataPreviewSection from './generate-download/DataPreviewSection.jsx'
import ChartSuggestionsSection from './generate-download/ChartSuggestionsSection.jsx'
import ProgressSection from './generate-download/ProgressSection.jsx'
import RecentDownloadsSection from './generate-download/RecentDownloadsSection.jsx'

function GenerateAndDownload({
  selected,
  selectedTemplates,
  autoType,
  start,
  end,
  setStart,
  setEnd,
  onFind,
  findDisabled,
  finding,
  results,
  onToggleBatch,
  onGenerate,
  canGenerate,
  generateLabel,
  generation,
  generatorReady,
  generatorIssues,
  keyValues = {},
  onKeyValueChange = () => {},
  keysReady = true,
  keyOptions = {},
  keyOptionsLoading = {},
  onResampleFilter = () => {},
}) {
  const targetNames = selectedTemplates.map((t) => t.name)
  const subline = targetNames.length
    ? `${targetNames.slice(0, 3).join(', ')}${targetNames.length > 3 ? ', ...' : ''}`
    : ''

  const hook = useGenerateAndDownload({
    selected,
    selectedTemplates,
    start,
    end,
    keyValues,
    keyOptions,
    keyOptionsLoading,
    onResampleFilter,
    results,
    generatorReady,
    generatorIssues,
    keysReady,
  })

  return (
    <>
      <Surface sx={surfaceStackSx}>
        <RunReportsHeader
          subline={subline}
          activeDateRange={hook.activeDateRange}
          onFind={onFind}
          valid={hook.valid}
          findDisabled={findDisabled}
          onGenerate={onGenerate}
          canGenerate={canGenerate}
          generateLabel={generateLabel}
          showGeneratorWarning={hook.showGeneratorWarning}
          generatorMissing={hook.generatorMissing}
          generatorMessages={hook.generatorMessages}
          start={start}
          end={end}
          setStart={setStart}
          setEnd={setEnd}
          autoType={autoType}
        />

        <KeyTokenValuesSection
          selected={selected}
          keysMissing={hook.keysMissing}
          templatesWithKeys={hook.templatesWithKeys}
          keyValues={keyValues}
          keyOptions={keyOptions}
          keyOptionsLoading={keyOptionsLoading}
          onKeyValueChange={onKeyValueChange}
        />

        {hook.activeTemplate && (
          <Box>
            <Divider sx={{ my: 2 }} />
            <FilterGroupSection
              activeTemplate={hook.activeTemplate}
              activeTemplateResult={hook.activeTemplateResult}
              safeResampleConfig={hook.safeResampleConfig}
              handleResampleSelectorChange={hook.handleResampleSelectorChange}
              handleResampleBrushChange={hook.handleResampleBrushChange}
              handleResampleReset={hook.handleResampleReset}
              resampleState={hook.resampleState}
              dimensionOptions={hook.dimensionOptions}
              metricOptions={hook.metricOptions}
              bucketOptions={hook.bucketOptions}
              resampleBucketHelper={hook.resampleBucketHelper}
              selectedMetricLabel={hook.selectedMetricLabel}
              totalBatchCount={hook.totalBatchCount}
              filteredBatchCount={hook.filteredBatchCount}
            />
          </Box>
        )}

        <DataPreviewSection
          finding={finding}
          results={results}
          onToggleBatch={onToggleBatch}
        />

        <ChartSuggestionsSection
          activeTemplate={hook.activeTemplate}
          chartQuestion={hook.chartQuestion}
          setChartQuestion={hook.setChartQuestion}
          chartSuggestMutation={hook.chartSuggestMutation}
          activeBatchData={hook.activeBatchData}
          handleAskCharts={hook.handleAskCharts}
          chartSuggestions={hook.chartSuggestions}
          selectedChartSource={hook.selectedChartSource}
          selectedChartId={hook.selectedChartId}
          handleSelectSuggestion={hook.handleSelectSuggestion}
          selectedChartSpec={hook.selectedChartSpec}
          previewData={hook.previewData}
          usingSampleData={hook.usingSampleData}
          handleSaveCurrentSuggestion={hook.handleSaveCurrentSuggestion}
          selectedSuggestion={hook.selectedSuggestion}
          saveChartLoading={hook.saveChartLoading}
        />

        <Box>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1">Saved charts</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Reuse charts you previously saved for {hook.activeTemplate?.name || hook.activeTemplate?.id || 'this template'}.
          </Typography>
          {!hook.activeTemplate && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Select a template to view saved charts.
            </Typography>
          )}
          {hook.activeTemplate && (
            <SavedChartsPanel
              activeTemplate={hook.activeTemplate}
              savedCharts={hook.savedCharts}
              savedChartsLoading={hook.savedChartsLoading}
              savedChartsError={hook.savedChartsError}
              selectedChartSource={hook.selectedChartSource}
              selectedSavedChartId={hook.selectedSavedChartId}
              onRetry={hook.handleRetrySavedCharts}
              onSelectSavedChart={hook.handleSelectSavedChart}
              onRenameSavedChart={hook.handleRenameSavedChart}
              onDeleteSavedChart={hook.handleDeleteSavedChart}
            />
          )}
        </Box>

        <ProgressSection generation={generation} />
      </Surface>

      <RecentDownloadsSection downloads={hook.downloads} />
    </>
  )
}

export default GenerateAndDownload
