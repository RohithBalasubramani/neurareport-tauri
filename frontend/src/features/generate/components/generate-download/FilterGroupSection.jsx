import {
  Box,
  Button,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material'

import {
  RESAMPLE_AGGREGATION_OPTIONS,
} from '../../utils/generateFeatureUtils'
import ResampleChart from './ResampleChart.jsx'

export default function FilterGroupSection({
  activeTemplate,
  activeTemplateResult,
  safeResampleConfig,
  handleResampleSelectorChange,
  handleResampleBrushChange,
  handleResampleReset,
  resampleState,
  dimensionOptions,
  metricOptions,
  bucketOptions,
  resampleBucketHelper,
  selectedMetricLabel,
  totalBatchCount,
  filteredBatchCount,
}) {
  if (!activeTemplate) return null

  const hasBatchMetrics =
    Array.isArray(activeTemplateResult?.batchMetrics) &&
    activeTemplateResult.batchMetrics.length > 0

  return (
    <Box>
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        spacing={{ xs: 0.5, md: 1 }}
        alignItems={{ xs: 'flex-start', md: 'center' }}
        justifyContent="space-between"
      >
        <Stack spacing={0.5}>
          <Typography variant="subtitle1">Filter & Group Data</Typography>
          <Typography variant="body2" color="text.secondary">
            Narrow down your data before generating reports. Use the chart below to select specific time periods or groups.
          </Typography>
        </Stack>
        <Button
          size="small"
          variant="text"
          onClick={handleResampleReset}
          disabled={!resampleState.filterActive}
        >
          Reset filter
        </Button>
      </Stack>
      {hasBatchMetrics ? (
        <>
          <Stack
            direction={{ xs: 'column', lg: 'row' }}
            spacing={1.25}
            sx={{ mt: 1.5 }}
          >
            <TextField
              select size="small" label="Dimension"
              value={safeResampleConfig.dimension}
              onChange={handleResampleSelectorChange('dimension')}
              sx={{ minWidth: { xs: '100%', lg: 180 } }}
            >
              {dimensionOptions.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              select size="small" label="Metric"
              value={safeResampleConfig.metric}
              onChange={handleResampleSelectorChange('metric')}
              sx={{ minWidth: { xs: '100%', lg: 180 } }}
            >
              {metricOptions.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              select size="small" label="Aggregation"
              value={safeResampleConfig.aggregation}
              onChange={handleResampleSelectorChange('aggregation')}
              sx={{ minWidth: { xs: '100%', lg: 180 } }}
            >
              {RESAMPLE_AGGREGATION_OPTIONS.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              select size="small" label="Time bucket"
              value={safeResampleConfig.bucket}
              onChange={handleResampleSelectorChange('bucket')}
              disabled={!bucketOptions.length || safeResampleConfig.dimensionKind === 'categorical'}
              helperText={
                safeResampleConfig.dimensionKind === 'temporal'
                  ? resampleBucketHelper
                  : safeResampleConfig.dimensionKind === 'numeric'
                    ? 'Applies to numeric bucketing'
                    : 'Not applicable to this dimension'
              }
              sx={{ minWidth: { xs: '100%', lg: 180 } }}
            >
              {bucketOptions.map((o) => (
                <MenuItem key={o.value} value={o.value}>{o.label}</MenuItem>
              ))}
            </TextField>
          </Stack>
          <ResampleChart
            resampleState={resampleState}
            selectedMetricLabel={selectedMetricLabel}
            handleResampleBrushChange={handleResampleBrushChange}
            filteredBatchCount={filteredBatchCount}
            totalBatchCount={totalBatchCount}
            safeResampleConfig={safeResampleConfig}
            resampleBucketHelper={resampleBucketHelper}
          />
        </>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
          Run discovery for this template to populate resampling metrics.
        </Typography>
      )}
    </Box>
  )
}
