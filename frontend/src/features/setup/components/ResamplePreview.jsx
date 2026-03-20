import {
  Box, Typography, Stack, TextField, MenuItem, Divider,
} from '@mui/material'
import {
  RESAMPLE_AGGREGATION_OPTIONS,
  RESAMPLE_BUCKET_OPTIONS,
  RESAMPLE_NUMERIC_BUCKET_OPTIONS,
} from '@/features/generate/utils/resample'

export default function ResamplePreview({
  safeResampleConfig,
  resampleState,
  dimensionOptions,
  metricOptions,
}) {
  const bucketOptions =
    safeResampleConfig.dimensionKind === 'numeric' ? RESAMPLE_NUMERIC_BUCKET_OPTIONS : RESAMPLE_BUCKET_OPTIONS
  const resampleBucketHelper =
    (safeResampleConfig.dimensionKind === 'temporal' || safeResampleConfig.dimension === 'time') &&
    safeResampleConfig.bucket === 'auto'
      ? `Auto bucket: ${resampleState.resolvedBucket}`
      : safeResampleConfig.dimensionKind === 'numeric'
        ? 'Buckets group numeric values into ranges'
        : ''

  return (
    <>
      <Divider sx={{ my: 2 }} />
      {resampleState?.series ? (
        <Stack spacing={1.25}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25}>
            <TextField
              select
              size="small"
              label="Dimension"
              value={safeResampleConfig.dimension}
              SelectProps={{ native: false }}
              sx={{ minWidth: { xs: '100%', sm: 200 } }}
              disabled
              helperText="Configurable on Generate page"
            >
              {dimensionOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              size="small"
              label="Metric"
              value={safeResampleConfig.metric}
              disabled
              sx={{ minWidth: { xs: '100%', sm: 200 } }}
              helperText="Configurable on Generate page"
            >
              {metricOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              size="small"
              label="Aggregation"
              value={safeResampleConfig.aggregation}
              disabled
              sx={{ minWidth: { xs: '100%', sm: 180 } }}
            >
              {RESAMPLE_AGGREGATION_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              size="small"
              label="Bucket"
              value={safeResampleConfig.bucket}
              disabled
              helperText={resampleBucketHelper || ' '}
              sx={{ minWidth: { xs: '100%', sm: 200 } }}
            >
              {bucketOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
          <Box
            sx={{
              height: 200,
              border: '1px dashed',
              borderColor: 'divider',
              borderRadius: 1,
              bgcolor: 'background.default',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'text.secondary',
              textAlign: 'center',
            }}
          >
            Resampling available on Generate page. Buckets computed: {resampleState.series.length}
          </Box>
        </Stack>
      ) : null}
    </>
  )
}
