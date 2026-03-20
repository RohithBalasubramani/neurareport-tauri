import {
  Alert,
  Box,
  Button,
  Chip,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'

import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { toLocalInputValue } from '../../utils/generateFeatureUtils'

export default function RunReportsHeader({
  subline,
  activeDateRange,
  onFind,
  valid,
  findDisabled,
  onGenerate,
  canGenerate,
  generateLabel,
  showGeneratorWarning,
  generatorMissing,
  generatorMessages,
  start,
  end,
  setStart,
  setEnd,
  autoType,
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
              ariaLabel="Run reports guidance"
            />
          </Stack>
          {!!subline && <Typography variant="caption" color="text.secondary">{subline}</Typography>}
          {activeDateRange && (
            <Typography variant="caption" color="text.secondary">
              Range: {activeDateRange.start} → {activeDateRange.end}
              {activeDateRange.time_start && activeDateRange.time_end
                ? ` • data ${activeDateRange.time_start} → ${activeDateRange.time_end}`
                : ''}
            </Typography>
          )}
        </Stack>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1}
          alignItems={{ xs: 'stretch', sm: 'center' }}
          sx={{ width: { xs: '100%', sm: 'auto' } }}
        >
          <Tooltip title="Scan your data to see what can be included in this report">
            <span>
              <Button
                variant="outlined"
                onClick={onFind}
                disabled={!valid || findDisabled}
                sx={{ width: { xs: '100%', sm: 'auto' }, color: 'text.secondary' }}
              >
                Preview Data
              </Button>
            </span>
          </Tooltip>
          <Tooltip title={generateLabel}>
            <span>
              <Button
                variant="contained"
                onClick={onGenerate}
                disabled={!canGenerate}
                aria-label={generateLabel}
                sx={{ width: { xs: '100%', sm: 'auto' } }}
              >
                {generateLabel}
              </Button>
            </span>
          </Tooltip>
        </Stack>

      {showGeneratorWarning && (
        <Alert severity="warning" sx={{ mt: 1 }}>
          {generatorMissing.length
            ? 'Generate SQL & schema assets for all selected templates before continuing.'
            : 'Resolve SQL & schema asset issues before continuing.'}
          {generatorMessages.length ? (
            <Box component="ul" sx={{ pl: 2, mt: 0.5 }}>
              {generatorMessages.map((msg, idx) => (
                <Typography key={`generator-msg-${idx}`} component="li" variant="caption">
                  {msg}
                </Typography>
              ))}
            </Box>
          ) : null}
        </Alert>
      )}
      </Stack>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
        <TextField
          label="Start Date & Time"
          type="datetime-local"
          InputLabelProps={{ shrink: true }}
          value={toLocalInputValue(start)}
          onChange={(e) => setStart(e.target.value)}
          helperText="Timezone: system"
        />
        <TextField
          label="End Date & Time"
          type="datetime-local"
          InputLabelProps={{ shrink: true }}
          value={toLocalInputValue(end)}
          onChange={(e) => setEnd(e.target.value)}
          error={!!(start && end && new Date(end) < new Date(start))}
          helperText={start && end && new Date(end) < new Date(start) ? 'End must be after Start' : ' '}
        />
        <Chip label={`Auto: ${autoType || '-'}`} size="small" variant="outlined" sx={{ alignSelf: { xs: 'flex-start', sm: 'center' } }} />
      </Stack>
    </>
  )
}
