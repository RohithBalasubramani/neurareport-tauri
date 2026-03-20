import {
  Box,
  Stack,
  Typography,
} from '@mui/material'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Brush,
} from 'recharts'

import { secondary } from '@/app/theme'

export default function ResampleChart({
  resampleState,
  selectedMetricLabel,
  handleResampleBrushChange,
  filteredBatchCount,
  totalBatchCount,
  safeResampleConfig,
  resampleBucketHelper,
}) {
  return (
    <>
      <Box sx={{ height: 260, mt: 2 }}>
        {resampleState.series.length ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={resampleState.series}
              margin={{ top: 8, right: 16, bottom: 24, left: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <RechartsTooltip />
              <Bar dataKey="value" fill={secondary.violet[500]} name={selectedMetricLabel} />
              <Brush
                dataKey="label"
                height={24}
                stroke={secondary.violet[500]}
                startIndex={
                  resampleState.displayRange ? resampleState.displayRange[0] : 0
                }
                endIndex={
                  resampleState.displayRange
                    ? resampleState.displayRange[1]
                    : Math.max(resampleState.series.length - 1, 0)
                }
                travellerWidth={8}
                onChange={handleResampleBrushChange}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <Stack
            alignItems="center"
            justifyContent="center"
            sx={{ height: '100%' }}
          >
            <Typography variant="body2" color="text.secondary">
              No buckets available for this selection. Try a different dimension.
            </Typography>
          </Stack>
        )}
      </Box>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        justifyContent="space-between"
        spacing={0.5}
        sx={{ mt: 1 }}
      >
        <Typography variant="caption" color="text.secondary">
          Showing {filteredBatchCount}
          {totalBatchCount && totalBatchCount !== filteredBatchCount
            ? ` / ${totalBatchCount}`
            : ''}{' '}
          {filteredBatchCount === 1 ? 'data section' : 'data sections'}
        </Typography>
        {safeResampleConfig.dimension === 'time' && resampleBucketHelper && (
          <Typography variant="caption" color="text.secondary">
            {resampleBucketHelper}
          </Typography>
        )}
      </Stack>
    </>
  )
}
