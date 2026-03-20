import {
  Typography, Stack, Button, Chip, Tooltip, IconButton,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'
import ListAltIcon from '@mui/icons-material/ListAlt'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import SearchIcon from '@mui/icons-material/Search'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'

export default function RunReportsHeader({
  valid,
  findDisabled,
  finding,
  onFind,
  onGenerate,
  canGenerate,
  generateLabel,
  generateTooltip,
  start,
  end,
  setStart,
  setEnd,
  autoType,
  resultCount,
  onOpenDiscovery,
  hasDiscoveryTargets,
  discoveryCountLabel,
  targetNames,
  safeResampleConfig,
  resampleState,
  discoveryDimensions,
  discoveryMetrics,
}) {
  return (
    <>
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
    </>
  )
}
