import {
  Box,
  Checkbox,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'

import InfoTooltip from '@/components/common/InfoTooltip.jsx'

export default function DataPreviewSection({
  finding,
  results,
  onToggleBatch,
}) {
  if (!finding && !Object.keys(results).length) return null

  return (
    <Box>
      <Divider sx={{ my: 2 }} />
      <Stack direction="row" alignItems="center" spacing={1}>
        <Typography variant="subtitle1">Data Preview</Typography>
        <InfoTooltip
          content="This shows the data sections found in your date range. Each section represents a logical grouping of data (like a time period or category) that will become part of your report."
          ariaLabel="Data preview explanation"
        />
      </Stack>
      {finding ? (
        <Stack spacing={1.25} sx={{ mt: 1.5 }}>
          <LinearProgress aria-label="Scanning your data" />
          <Typography variant="body2" color="text.secondary">
            Scanning your data...
          </Typography>
        </Stack>
      ) : (
        <Stack spacing={1.5} sx={{ mt: 1.5 }}>
          {Object.keys(results).map((tid) => {
            const r = results[tid]
            const filteredCount = r.batches.length
            const originalCount = r.allBatches?.length ?? r.batches_count ?? filteredCount
            const filteredRows = r.batches.reduce((acc, batch) => acc + (batch.rows || 0), 0)
            const summary =
              originalCount === filteredCount
                ? `${filteredCount} ${filteredCount === 1 ? 'section' : 'sections'} \u2022 ${filteredRows.toLocaleString()} records`
                : `${filteredCount} / ${originalCount} sections \u2022 ${filteredRows.toLocaleString()} records`
            return (
              <Box
                key={tid}
                sx={{
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  p: 1.5,
                  bgcolor: 'background.paper',
                }}
              >
                <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={{ xs: 0.5, sm: 1 }}>
                  <Typography variant="subtitle2">{r.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {summary}
                  </Typography>
                </Stack>
                {r.batches.length ? (
                  <Stack spacing={1} sx={{ mt: 1.25 }}>
                    <Typography variant="body2" color="text.secondary">
                      Select which data sections to include in your report:
                    </Typography>
                    {r.batches.map((b, idx) => (
                      <Stack key={b.id || idx} direction="row" spacing={1} alignItems="center">
                        <Checkbox
                          checked={b.selected}
                          onChange={(e) => onToggleBatch(tid, idx, e.target.checked)}
                          inputProps={{ 'aria-label': `Include section ${idx + 1} for ${r.name}` }}
                        />
                        <Typography variant="body2">
                          Section {idx + 1} {'\u2022'} {(b.parent ?? 1)} {(b.parent ?? 1) === 1 ? 'group' : 'groups'} {'\u2022'} {b.rows.toLocaleString()} records
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">No data found for this date range. Try adjusting your dates.</Typography>
                )}
              </Box>
            )
          })}
        </Stack>
      )}
    </Box>
  )
}
