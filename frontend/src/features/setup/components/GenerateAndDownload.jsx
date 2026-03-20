import { Box, Divider } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import { surfaceStackSx } from '../utils/templatesPaneUtils'
import { useGenerateAndDownload } from '../hooks/useGenerateAndDownload'
import RunReportsHeader from './RunReportsHeader'
import DiscoveryStatus from './DiscoveryStatus'
import KeyTokenPanel from './KeyTokenPanel'
import ResamplePreview from './ResamplePreview'
import ProgressList from './ProgressList'
import RecentDownloadsSection from './RecentDownloadsSection'

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
  onGenerate,
  canGenerate,
  generateLabel,
  generateTooltip = '',
  generation,
  onRetryGeneration = () => {},
  keyValues = {},
  onKeyValueChange = () => {},
  keysReady = true,
  keyOptions = {},
  keyOptionsLoading = {},
  onOpenDiscovery = () => {},
  discoverySchema = null,
}) {
  const {
    valid,
    downloads,
    targetNames,
    hasDiscoveryTargets,
    discoveryCountLabel,
    dimensionOptions,
    metricOptions,
    safeResampleConfig,
    resampleState,
    templatesWithKeys,
    resultCount,
    keyPanelVisible,
    discoverySummary,
    discoveryDimensions,
    discoveryMetrics,
  } = useGenerateAndDownload({ selectedTemplates, start, end, results, keyOptions })

  return (
    <>
      <Surface sx={surfaceStackSx}>
        <RunReportsHeader
          valid={valid}
          findDisabled={findDisabled}
          finding={finding}
          onFind={onFind}
          onGenerate={onGenerate}
          canGenerate={canGenerate}
          generateLabel={generateLabel}
          generateTooltip={generateTooltip}
          start={start}
          end={end}
          setStart={setStart}
          setEnd={setEnd}
          autoType={autoType}
          resultCount={resultCount}
          onOpenDiscovery={onOpenDiscovery}
          hasDiscoveryTargets={hasDiscoveryTargets}
          discoveryCountLabel={discoveryCountLabel}
          targetNames={targetNames}
          safeResampleConfig={safeResampleConfig}
          resampleState={resampleState}
          discoveryDimensions={discoveryDimensions}
          discoveryMetrics={discoveryMetrics}
        />

        <DiscoveryStatus finding={finding} discoverySummary={discoverySummary} />

        {keyPanelVisible && (
          <KeyTokenPanel
            templatesWithKeys={templatesWithKeys}
            keysReady={keysReady}
            keyValues={keyValues}
            keyOptions={keyOptions}
            keyOptionsLoading={keyOptionsLoading}
            onKeyValueChange={onKeyValueChange}
          />
        )}

        <Box>
          <ResamplePreview
            safeResampleConfig={safeResampleConfig}
            resampleState={resampleState}
            dimensionOptions={dimensionOptions}
            metricOptions={metricOptions}
          />
          <Divider sx={{ my: 2 }} />
          <ProgressList generation={generation} onRetryGeneration={onRetryGeneration} />
        </Box>
      </Surface>

      <RecentDownloadsSection downloads={downloads} />
    </>
  )
}

export default GenerateAndDownload
