import { useMemo } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Typography,
  Button,
  Alert,
  Chip,
  Checkbox,
  Divider,
  LinearProgress,
  IconButton,
  Box,
  alpha,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import { neutral, palette } from '@/app/theme'
import { useAppStore } from '@/stores'

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

export default function DiscoveryListsPanel({ open, onClose }) {
  const results = useAppStore((state) => state.discoveryResults)
  const finding = useAppStore((state) => state.discoveryFinding)
  const updateBatch = useAppStore((state) => state.updateDiscoveryBatchSelection)
  const discoveryMeta = useAppStore((state) => state.discoveryMeta)

  const entries = useMemo(() => Object.entries(results || {}), [results])
  const aggregate = useMemo(() => {
    if (!entries.length) return null
    return entries.reduce(
      (acc, [, entry]) => {
        const batches = batchesForEntry(entry)
        const rows = rowsForEntry(entry)
        const selected = Array.isArray(entry?.batches)
          ? entry.batches.filter((batch) => batch?.selected).length
          : 0
        return {
          templates: acc.templates + 1,
          batches: acc.batches + batches,
          rows: acc.rows + rows,
          selected: acc.selected + selected,
        }
      },
      { templates: 0, batches: 0, rows: 0, selected: 0 },
    )
  }, [entries])
  const hasData = entries.length > 0
  const connectionLabel = discoveryMeta?.connectionName || discoveryMeta?.connectionId || null

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="md"
      PaperProps={{
        sx: {
          borderRadius: 1,  // Figma spec: 8px
          width: '100%',
          maxWidth: 1040,
        },
      }}
    >
      <DialogTitle sx={{ pb: 0 }}>
        <Stack direction="row" alignItems="flex-start" justifyContent="space-between" spacing={2}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Discovery Lists</Typography>
            <Typography variant="body2" color="text.secondary">
              Review every batch found during discovery without stretching the Run Reports pane.
            </Typography>
          </Stack>
          <IconButton edge="end" onClick={onClose} aria-label="Close discovery lists">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>
      <DialogContent dividers sx={{ pt: 2.5, display: 'grid', gap: 2.5 }}>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          {connectionLabel ? (
            <Chip label={`Connection: ${connectionLabel}`} size="small" variant="outlined" />
          ) : null}
          {discoveryMeta?.startDisplay && discoveryMeta?.endDisplay ? (
            <Chip
              label={`${discoveryMeta.startDisplay} → ${discoveryMeta.endDisplay}`}
              size="small"
              variant="outlined"
            />
          ) : null}
          {discoveryMeta?.autoType ? (
            <Chip label={`Auto: ${discoveryMeta.autoType}`} size="small" variant="outlined" />
          ) : null}
        </Stack>

        {aggregate ? (
          <Alert severity="success">
            {`${formatCount(aggregate.templates)} ${aggregate.templates === 1 ? 'template' : 'templates'} • ${formatCount(aggregate.batches)} ${aggregate.batches === 1 ? 'batch' : 'batches'} • ${formatCount(aggregate.rows)} rows`}
            <Typography component="span" variant="body2" sx={{ display: 'block', mt: 0.5 }}>
              {aggregate.selected > 0
                ? `${formatCount(aggregate.selected)} batch${aggregate.selected === 1 ? '' : 'es'} selected`
                : 'No batches selected yet.'}
            </Typography>
          </Alert>
        ) : (
          <Alert severity="info">
            Run Find Reports in the main pane to populate discovery data, then reopen this panel.
          </Alert>
        )}

        {finding ? (
          <Stack spacing={1.25}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary">
              Fetching discovery data…
            </Typography>
          </Stack>
        ) : hasData ? (
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
                    borderRadius: 1,  // Figma spec: 8px
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
        ) : null}
      </DialogContent>
      <DialogActions sx={{ px: 3, py: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
          {discoveryMeta?.fetchedAt
            ? `Last updated ${new Date(discoveryMeta.fetchedAt).toLocaleString()}`
            : null}
        </Typography>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  )
}
