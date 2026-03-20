import {
  Box,
  Stack,
  Typography,
  Chip,
  Checkbox,
  Divider,
  Alert,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'

const formatCount = (value) => {
  const num = Number(value || 0)
  if (!Number.isFinite(num)) return '0'
  return num.toLocaleString()
}

const rowsForEntry = (entry) => {
  if (typeof entry?.rows_total === 'number') return entry.rows_total
  if (!Array.isArray(entry?.batches)) return 0
  return entry.batches.reduce((sum, batch) => sum + (batch?.rows || 0), 0)
}

const batchesForEntry = (entry) => {
  if (typeof entry?.batches_count === 'number') return entry.batches_count
  if (!Array.isArray(entry?.batches)) return 0
  return entry.batches.length
}

export { formatCount, rowsForEntry, batchesForEntry }

export default function DiscoveryBatchList({ entries, updateBatch }) {
  return (
    <Stack spacing={2}>
      {entries.map(([tplId, entry], index) => {
        const batchCount = batchesForEntry(entry)
        const rowTotal = rowsForEntry(entry)
        const templateTitle = entry?.name || tplId
        const batches = Array.isArray(entry?.batches) ? entry.batches : []
        return (
          <Box
            key={tplId}
            sx={{
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 1,
              p: { xs: 1.5, sm: 2 },
              bgcolor: 'background.paper',
            }}
          >
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={1}
              justifyContent="space-between"
              alignItems={{ xs: 'flex-start', sm: 'center' }}
            >
              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {templateTitle}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {`${formatCount(batchCount)} ${batchCount === 1 ? 'batch' : 'batches'} • ${formatCount(rowTotal)} rows`}
                </Typography>
              </Box>
              <Chip
                label={`Template ${index + 1}`}
                size="small"
                variant="outlined"
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            </Stack>
            <Divider sx={{ my: 1.5 }} />
            {batches.length ? (
              <Stack spacing={1}>
                {batches.map((batch, batchIdx) => (
                  <Stack
                    key={batch?.id || `${tplId}-${batchIdx}`}
                    direction={{ xs: 'column', sm: 'row' }}
                    spacing={1}
                    alignItems={{ xs: 'flex-start', sm: 'center' }}
                  >
                    <Checkbox
                      checked={!!batch?.selected}
                      onChange={(event) =>
                        updateBatch(tplId, batchIdx, event.target.checked)
                      }
                      sx={{ p: 0.5 }}
                    />
                    <Typography variant="body2" sx={{ flex: 1, overflowWrap: 'anywhere' }}>
                      {`Batch ${batchIdx + 1} • ${(batch?.parent ?? 1)} ${(batch?.parent ?? 1) === 1 ? 'parent' : 'parents'} • ${formatCount(batch?.rows || 0)} rows`}
                    </Typography>
                  </Stack>
                ))}
              </Stack>
            ) : (
              <Alert severity="info">No data found for this range.</Alert>
            )}
          </Box>
        )
      })}
    </Stack>
  )
}
