import { useMemo } from 'react'
import {
  Box, Typography, Stack, Button, TextField, Chip, Divider, LinearProgress,
  Tooltip, Alert, Autocomplete, IconButton,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral, palette } from '@/app/theme'
import ListAltIcon from '@mui/icons-material/ListAlt'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import SearchIcon from '@mui/icons-material/Search'
import DownloadIcon from '@mui/icons-material/Download'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'
import ReplayIcon from '@mui/icons-material/Replay'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { withBase } from '@/api/client'
import { useAppStore } from '@/stores'
import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { ALL_OPTION, buildDownloadUrl, formatCount, formatTokenLabel, surfaceStackSx } from '../utils/templatesPaneUtils'
import {
  DEFAULT_RESAMPLE_CONFIG,
  RESAMPLE_AGGREGATION_OPTIONS,
  RESAMPLE_BUCKET_OPTIONS,
  RESAMPLE_NUMERIC_BUCKET_OPTIONS,
  RESAMPLE_DIMENSION_OPTIONS,
  RESAMPLE_METRIC_OPTIONS,
  buildResampleComputation,
  collectIdsFromSeries,
  clampBrushRange,
} from '@/features/generate/utils/resample'

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
  const valid = selectedTemplates.length > 0 && !!start && !!end && end.valueOf() >= start.valueOf()
  const { downloads } = useAppStore()
  const targetNames = Object.values(results).map((r) => r.name)
  const firstResult = Object.values(results || {})[0] || null
  const numericBins = firstResult?.numericBins || {}
  const hasDiscoveryTargets = targetNames.length > 0
  const discoveryCountLabel = hasDiscoveryTargets
    ? `${targetNames.length} ${targetNames.length === 1 ? 'template' : 'templates'}`
    : ''
  const resampleConfig = firstResult?.resample?.config || DEFAULT_RESAMPLE_CONFIG
  const dimensionOptions = useMemo(() => {
    if (firstResult?.discoverySchema?.dimensions) {
      return firstResult.discoverySchema.dimensions.map((dim) => ({
        value: dim.name,
        label: dim.name,
        kind: dim.kind || dim.type || 'categorical',
        bucketable: Boolean(dim.bucketable),
      }))
    }
    return RESAMPLE_DIMENSION_OPTIONS
  }, [firstResult])
  const metricOptions = useMemo(() => {
    if (firstResult?.discoverySchema?.metrics) {
      return firstResult.discoverySchema.metrics.map((m) => ({ value: m.name, label: m.name }))
    }
    return RESAMPLE_METRIC_OPTIONS
  }, [firstResult])
  const safeResampleConfig = useMemo(() => {
    const next = { ...DEFAULT_RESAMPLE_CONFIG, ...resampleConfig }
    const activeDim = dimensionOptions.find((opt) => opt.value === next.dimension) || dimensionOptions[0]
    if (activeDim) {
      const kindText = (activeDim.kind || activeDim.type || '').toLowerCase()
      next.dimensionKind = kindText.includes('time')
        ? 'temporal'
        : kindText.includes('num')
          ? 'numeric'
          : 'categorical'
      next.dimension = activeDim.value
    }
    if (!metricOptions.some((opt) => opt.value === next.metric)) {
      next.metric = metricOptions[0]?.value || DEFAULT_RESAMPLE_CONFIG.metric
    }
    return next
  }, [dimensionOptions, metricOptions, resampleConfig])

  const resampleState = useMemo(
    () => buildResampleComputation(firstResult?.batchMetrics, safeResampleConfig, numericBins, firstResult?.categoryGroups),
    [firstResult, safeResampleConfig, numericBins],
  )
  const templatesWithKeys = useMemo(
    () =>
      selectedTemplates
        .map((tpl) => {
          const mappingTokens = Array.isArray(tpl?.mappingKeys)
            ? tpl.mappingKeys.map((token) => (typeof token === 'string' ? token.trim() : '')).filter(Boolean)
            : []
          const templateOptions = keyOptions[tpl.id] || {}
          const sourceTokens = mappingTokens.length ? mappingTokens : Object.keys(templateOptions)
          if (!sourceTokens.length) return null
          const tokens = sourceTokens.map((token) => ({
            name: token,
            required: mappingTokens.includes(token),
            options: templateOptions[token] || [],
          }))
          return { tpl, tokens }
        })
        .filter(Boolean),
    [selectedTemplates, keyOptions],
  )
  const resultCount = useMemo(() => Object.keys(results).length, [results])
  const keyPanelVisible = templatesWithKeys.length > 0 && resultCount > 0
  const discoverySummary = useMemo(() => {
    const entries = Object.values(results || {})
    if (!entries.length) return null
    return entries.reduce(
      (acc, entry) => {
        const batches = typeof entry.batches_count === 'number'
          ? entry.batches_count
          : Array.isArray(entry.batches)
            ? entry.batches.length
            : 0
        const rows = typeof entry.rows_total === 'number'
          ? entry.rows_total
          : Array.isArray(entry.batches)
            ? entry.batches.reduce((sum, batch) => sum + (batch.rows || 0), 0)
            : 0
        const selectedBatches = Array.isArray(entry.batches)
          ? entry.batches.filter((batch) => batch.selected).length
          : 0
        return {
          templates: acc.templates + 1,
          batches: acc.batches + batches,
          rows: acc.rows + rows,
          selected: acc.selected + selectedBatches,
        }
      },
      { templates: 0, batches: 0, rows: 0, selected: 0 },
    )
  }, [results])

  const discoveryDimensions = useMemo(() => {
    if (firstResult?.discoverySchema && Array.isArray(firstResult.discoverySchema.dimensions)) {
      return firstResult.discoverySchema.dimensions
    }
    return []
  }, [firstResult])
  const discoveryMetrics = useMemo(() => {
    if (firstResult?.discoverySchema && Array.isArray(firstResult.discoverySchema.metrics)) {
      return firstResult.discoverySchema.metrics
    }
    return []
  }, [firstResult])
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
      <Surface sx={surfaceStackSx}>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        justifyContent="space-between"
        spacing={{ xs: 1, sm: 2 }}
      >
        <Stack spacing={0.5}>
          <Stack direction="row" alignItems="center" spacing={0.75}>
            <Typography variant="h6">Run Reports</Typography>
            <InfoTooltip
              content={TOOLTIP_COPY.runReports}
              ariaLabel="How to run reports"
            />
          </Stack>
          {resampleState?.series?.length ? (
            <Typography variant="caption" color="text.secondary">
              Filter batches by {safeResampleConfig.dimension} ({safeResampleConfig.dimensionKind}) using buckets.
            </Typography>
          ) : null}
          {!!discoveryDimensions.length && (
            <Typography variant="caption" color="text.secondary">
              Available dimensions: {discoveryDimensions.map((d) => d.name).join(', ')}
            </Typography>
          )}
            {!!discoveryMetrics.length && (
              <Typography variant="caption" color="text.secondary">
                Available metrics: {discoveryMetrics.map((m) => m.name).join(', ')}
              </Typography>
            )}
            {hasDiscoveryTargets && (
              <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mt: 0.5 }}>
                <Chip size="small" variant="outlined" label={discoveryCountLabel} />
                <Tooltip title={targetNames.join(', ')}>
                  <IconButton
                    size="small"
                    aria-label="View discovery targets"
                    sx={{ color: 'text.secondary' }}
                  >
                    <ListAltIcon fontSize="inherit" />
                  </IconButton>
                </Tooltip>
              </Stack>
            )}
          </Stack>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1}
            alignItems={{ xs: 'stretch', sm: 'center' }}
            sx={{ width: { xs: '100%', sm: 'auto' }, flexWrap: 'wrap' }}
          >
            <Button
              variant="outlined"
              startIcon={<SearchIcon />}
              onClick={onFind}
              disabled={!valid || findDisabled}
              aria-label="Discover matching reports"
              sx={{ width: { xs: '100%', sm: 'auto' }, color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3) }}
            >
              Find Reports
            </Button>
            <Tooltip title={generateTooltip || generateLabel}>
              <span>
                <Button
                  variant="contained"
                  disableElevation
                  startIcon={<RocketLaunchIcon />}
                  onClick={onGenerate}
                  disabled={!canGenerate}
                  aria-label={generateTooltip || generateLabel}
                  sx={{ width: { xs: '100%', sm: 'auto' }, bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
                >
                  {generateLabel}
                </Button>
              </span>
            </Tooltip>
          </Stack>
        </Stack>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <DateTimePicker
              label="Start Date & Time"
              value={start}
              onChange={(v) => setStart(v)}
              slotProps={{
                textField: {
                  size: 'small',
                  FormHelperTextProps: { sx: { color: 'text.primary' } },
                },
              }}
            />
            <DateTimePicker
              label="End Date & Time"
              slotProps={{
                textField: {
                  size: 'small',
                  error: !!(start && end && end.isBefore(start)),
                  helperText: start && end && end.isBefore(start) ? 'End must be after Start' : ' ',
                  FormHelperTextProps: { sx: { color: 'text.primary' } },
                },
              }}
              value={end}
              onChange={(v) => setEnd(v)}
            />
            <Chip
              label={`Auto: ${autoType || '-'}`}
              size="small"
              variant="outlined"
              sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }}
            />
          </Stack>
        </LocalizationProvider>

        <Tooltip
          title={
            resultCount > 0
              ? 'Open the full discovery list panel'
              : 'Run Find Reports to populate discovery lists'
          }
        >
          <span>
            <Button
              variant="outlined"
              size="small"
              startIcon={<ListAltIcon />}
              endIcon={<OpenInNewIcon />}
              onClick={onOpenDiscovery}
              disabled={resultCount === 0 && !finding}
              sx={{ alignSelf: { xs: 'stretch', sm: 'flex-start' } }}
            >
              Discovery Lists
            </Button>
          </span>
        </Tooltip>
        {finding ? (
          <Stack spacing={1.25} sx={{ mt: 1.5 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary">
              Searching data...
            </Typography>
          </Stack>
        ) : discoverySummary ? (
          <Alert severity="success" sx={{ mt: 1.5 }}>
            {`${formatCount(discoverySummary.templates)} ${discoverySummary.templates === 1 ? 'template' : 'templates'} \u2022 ${formatCount(discoverySummary.batches)} ${discoverySummary.batches === 1 ? 'batch' : 'batches'} \u2022 ${formatCount(discoverySummary.rows)} rows`}
            <Typography component="span" variant="body2" sx={{ display: 'block', mt: 0.5 }}>
              {discoverySummary.selected > 0
                ? `${formatCount(discoverySummary.selected)} batch${discoverySummary.selected === 1 ? '' : 'es'} selected for run`
                : 'No batches selected yet. Update selections in the discovery panel.'}
            </Typography>
          </Alert>
        ) : (
          <Alert severity="info" sx={{ mt: 1.5 }}>
            No discovery results yet. Run Find Reports after setting your date range.
          </Alert>
        )}

        {templatesWithKeys.length > 0 && resultCount > 0 && (
          <Stack spacing={1.5} sx={{ mt: 2 }}>
            <Typography variant="subtitle2">Key Token Values</Typography>
            {!keysReady && (
              <Alert severity="warning">Fill in all key token values to enable discovery and runs.</Alert>
            )}
            {templatesWithKeys.map(({ tpl, tokens }) => (
              <Box
                key={tpl.id}
                sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1.5, bgcolor: 'background.paper' }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600 }}>{tpl.name || tpl.id}</Typography>
                <Stack spacing={1} sx={{ mt: 1 }}>
                  {tokens.map(({ name, required, options = [] }) => {
                    const rawOptions = Array.isArray(options) && options.length ? options : (keyOptions?.[tpl.id]?.[name] || [])
                    const normalizedOptions = Array.from(
                      new Set(
                        rawOptions
                          .map((option) => (option == null ? '' : String(option).trim()))
                          .filter(Boolean),
                      ),
                    )
                    const dropdownOptions = [ALL_OPTION, ...normalizedOptions]
                    const loading = Boolean(keyOptionsLoading?.[tpl.id])
                    const storedValue = Array.isArray(keyValues?.[tpl.id]?.[name]) ? keyValues[tpl.id][name] : []
                    const value = storedValue.includes(ALL_OPTION)
                      ? [ALL_OPTION]
                      : storedValue
                    return (
                      <Autocomplete
                        key={`${tpl.id}-${name}`}
                        multiple
                        disableCloseOnSelect
                        options={dropdownOptions}
                        value={value}
                        loading={loading}
                        onChange={(_event, newValue) => {
                          let next = Array.isArray(newValue) ? newValue.filter(Boolean) : []
                          if (next.includes(ALL_OPTION)) {
                            next = [ALL_OPTION, ...normalizedOptions]
                          } else {
                            next = Array.from(new Set(next))
                          }
                          onKeyValueChange(tpl.id, name, next)
                        }}
                        getOptionLabel={(option) => (option === ALL_OPTION ? 'All' : option)}
                        renderTags={(tagValue, getTagProps) =>
                          tagValue.map((option, index) => (
                            <Chip
                              {...getTagProps({ index })}
                              key={`${tpl.id}-${name}-tag-${option}-${index}`}
                              size="small"
                              label={option === ALL_OPTION ? 'All' : option}
                            />
                          ))
                        }
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label={`${formatTokenLabel(name)}${required ? ' *' : ''}`}
                            required={required}
                            placeholder={loading ? 'Loading...' : dropdownOptions.length ? 'Select values' : 'No options'}
                          />
                        )}
                      />
                    )
                  })}
                </Stack>
              </Box>
            ))}
          </Stack>
        )}

        <Box>
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
      <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1">Progress</Typography>
          <Stack spacing={1.5} sx={{ mt: 1.5 }}>
            {generation.items.map((item) => (
              <Box
                key={item.id}
                sx={{
                  p: 1.5,
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  bgcolor: 'background.paper',
                }}
              >
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  justifyContent="space-between"
                  alignItems={{ xs: 'flex-start', sm: 'center' }}
                  spacing={{ xs: 0.5, sm: 1 }}
                >
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {item.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {item.status}
                  </Typography>
                </Stack>
                <LinearProgress variant="determinate" value={item.progress} sx={{ mt: 1 }} />
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<OpenInNewIcon />}
                    disabled={!item.htmlUrl}
                    component="a"
                    href={item.htmlUrl || '#'}
                    target="_blank"
                    rel="noopener"
                  >
                    Open
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    disableElevation
                    startIcon={<DownloadIcon />}
                    disabled={!item.pdfUrl}
                    component="a"
                    href={item.pdfUrl ? buildDownloadUrl(item.pdfUrl) : '#'}
                    target="_blank"
                    rel="noopener"
                    sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
                  >
                    Download
                  </Button>
                  {item.docxUrl && (
                    <Button
                      size="small"
                      variant="contained"
                      disableElevation
                      startIcon={<DownloadIcon />}
                      component="a"
                      href={buildDownloadUrl(item.docxUrl)}
                      target="_blank"
                      rel="noopener"
                      sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[500] } }}
                    >
                      Download DOCX
                    </Button>
                  )}
                  {item.xlsxUrl && (
                    <Button
                      size="small"
                      variant="contained"
                      disableElevation
                      startIcon={<DownloadIcon />}
                      component="a"
                      href={buildDownloadUrl(item.xlsxUrl)}
                      target="_blank"
                      rel="noopener"
                      sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[500], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[300] : neutral[500] } }}
                    >
                      Download XLSX
                    </Button>
                  )}
                  <Button size="small" variant="text" startIcon={<FolderOpenIcon />} disabled>
                    Show in folder
                  </Button>
                  {item.status === 'failed' && (
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<ReplayIcon />}
                      onClick={() => onRetryGeneration(item)}
                      sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3) }}
                    >
                      Retry
                    </Button>
                  )}
                </Stack>
              </Box>
            ))}
            {!generation.items.length && <Typography variant="body2" color="text.secondary">No runs yet</Typography>}
          </Stack>
        </Box>
      </Surface>


      <Surface sx={surfaceStackSx}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Recently Downloaded</Typography>
          <InfoTooltip
            content={TOOLTIP_COPY.recentDownloads}
            ariaLabel="How to use recent downloads"
          />
        </Stack>
        <Stack spacing={1.5}>
          {downloads.map((d, i) => {
            const metaLine = [d.template, d.format ? d.format.toUpperCase() : null, d.size || 'Size unknown']
              .filter(Boolean)
              .join(' \u2022 ')
            const formatChips = [
              d.pdfUrl && { label: 'PDF', color: 'primary' },
              d.docxUrl && { label: 'DOCX', color: 'secondary' },
              d.xlsxUrl && { label: 'XLSX', color: 'info' },
            ].filter(Boolean)
            const actionButtons = [
              {
                key: 'open',
                label: 'Open preview',
                variant: 'outlined',
                color: 'inherit',
                disabled: !d.htmlUrl,
                href: d.htmlUrl ? withBase(d.htmlUrl) : null,
              },
              {
                key: 'pdf',
                label: 'Download PDF',
                variant: 'contained',
                color: 'primary',
                disabled: !d.pdfUrl,
                href: d.pdfUrl ? buildDownloadUrl(withBase(d.pdfUrl)) : null,
              },
              d.docxUrl && {
                key: 'docx',
                label: 'Download DOCX',
                variant: 'outlined',
                color: 'primary',
                href: buildDownloadUrl(withBase(d.docxUrl)),
              },
              d.xlsxUrl && {
                key: 'xlsx',
                label: 'Download XLSX',
                variant: 'outlined',
                color: 'info',
                href: buildDownloadUrl(withBase(d.xlsxUrl)),
              },
            ].filter(Boolean)
            return (
              <Box
                key={`${d.filename}-${i}`}
                sx={{
                  p: { xs: 1.5, md: 2 },
                  borderRadius: 1,  // Figma spec: 8px
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: 'background.paper',
                  boxShadow: `0 6px 20px ${alpha(neutral[900], 0.06)}`,
                  transition: 'border-color 200ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 200ms cubic-bezier(0.22, 1, 0.36, 1), transform 160ms cubic-bezier(0.22, 1, 0.36, 1)',
                  '&:hover': {
                    borderColor: 'primary.light',
                    boxShadow: `0 10px 30px ${alpha(secondary.violet[500], 0.14)}`,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <Stack spacing={1.5}>
                  <Stack
                    direction={{ xs: 'column', md: 'row' }}
                    spacing={1}
                    justifyContent="space-between"
                    alignItems={{ md: 'center' }}
                  >
                    <Box sx={{ minWidth: 0 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap title={d.filename}>
                        {d.filename}
                      </Typography>
                      {metaLine && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ mt: 0.5 }}
                          noWrap
                          title={metaLine}
                        >
                          {metaLine}
                        </Typography>
                      )}
                    </Box>
                    {!!formatChips.length && (
                      <Stack direction="row" spacing={0.75} flexWrap="wrap" justifyContent={{ xs: 'flex-start', md: 'flex-end' }}>
                        {formatChips.map(({ label, color: colorKey }) => (
                          <Chip
                            key={label}
                            size="small"
                            label={label}
                            sx={(theme) => ({
                              borderRadius: 1,
                              fontWeight: 600,
                              bgcolor: alpha(theme.palette[colorKey].main, 0.12),
                              color: theme.palette[colorKey].dark,
                              border: '1px solid',
                              borderColor: alpha(theme.palette[colorKey].main, 0.3),
                            })}
                          />
                        ))}
                      </Stack>
                    )}
                  </Stack>

                  <Divider />

                  <Stack
                    direction={{ xs: 'column', lg: 'row' }}
                    spacing={1.25}
                    alignItems={{ lg: 'flex-start' }}
                  >
                    <Stack
                      direction="row"
                      spacing={1}
                      flexWrap="wrap"
                      sx={{ flexGrow: 1, columnGap: 1, rowGap: 1 }}
                    >
                      {actionButtons.map((action) => {
                        const linkProps = action.href
                          ? { component: 'a', href: action.href, target: '_blank', rel: 'noopener' }
                          : {}
                        return (
                          <Button
                            key={action.key}
                            size="small"
                            variant={action.variant}
                            color={action.color}
                            disabled={action.disabled}
                            sx={{
                              textTransform: 'none',
                              minWidth: { xs: '100%', sm: 0 },
                              flex: { xs: '1 1 100%', sm: '0 0 auto' },
                              px: 2.5,
                            }}
                            {...linkProps}
                          >
                            {action.label}
                          </Button>
                        )
                      })}
                    </Stack>
                    <Box sx={{ width: { xs: '100%', lg: 'auto' } }}>
                      <Button
                        size="small"
                        variant="contained"
                        disableElevation
                        startIcon={<ReplayIcon />}
                        onClick={d.onRerun}
                        sx={{ width: { xs: '100%', lg: 'auto' }, textTransform: 'none', px: 2.5, bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
                      >
                        Re-run
                      </Button>
                    </Box>
                  </Stack>
                </Stack>
              </Box>
            )
          })}
          {!downloads.length && <Typography variant="body2" color="text.secondary">No recent downloads yet.</Typography>}
        </Stack>
      </Surface>
    </>
  )
}

export default GenerateAndDownload
