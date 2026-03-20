import {
  Box, Typography, Stack, Button, Chip, alpha,
} from '@mui/material'
import CheckRoundedIcon from '@mui/icons-material/CheckRounded'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import SearchIcon from '@mui/icons-material/Search'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import Surface from '@/components/layout/Surface.jsx'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import ReportGlossaryNotice from '@/components/ux/ReportGlossaryNotice.jsx'
import { neutral } from '@/app/theme'

export default function TemplatesPaneHeader({
  selected,
  dateRangeValid,
  hasResults,
  batchCount,
  finding,
  onFind,
  onGenerate,
  canGenerate,
  generateLabel,
}) {
  return (
    <>
      <Surface sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }} justifyContent="space-between">
          <Stack direction="row" alignItems="center" spacing={1}>
            <Typography variant="h6" fontWeight={600}>Run Reports</Typography>
            <InfoTooltip content={TOOLTIP_COPY.runReports} ariaLabel="Run report guidance" />
          </Stack>

          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              size="small"
              icon={<CheckRoundedIcon />}
              label={`${selected.length} design${selected.length !== 1 ? 's' : ''}`}
              variant={selected.length > 0 ? 'filled' : 'outlined'}
              sx={{ bgcolor: selected.length > 0 ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] : undefined, color: 'text.secondary' }}
            />
            <Chip
              size="small"
              icon={<CalendarMonthIcon />}
              label={dateRangeValid ? 'Date set' : 'No date'}
              variant={dateRangeValid ? 'filled' : 'outlined'}
              sx={{ bgcolor: dateRangeValid ? (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] : undefined, color: 'text.secondary' }}
            />
            {hasResults && (
              <Chip
                size="small"
                icon={<SearchIcon />}
                label={`${batchCount} batch${batchCount !== 1 ? 'es' : ''}`}
                variant="filled"
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            )}
          </Stack>

          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<SearchIcon />}
              onClick={onFind}
              disabled={finding || !selected.length || !dateRangeValid}
            >
              {finding ? 'Finding...' : 'Find Reports'}
            </Button>
            <Button
              variant="contained"
              size="small"
              startIcon={<PlayArrowIcon />}
              onClick={onGenerate}
              disabled={!canGenerate}
            >
              {generateLabel}
            </Button>
          </Stack>
        </Stack>
      </Surface>

      <Box sx={{ mt: 2 }}>
        <ReportGlossaryNotice dense showChips={false} />
      </Box>
    </>
  )
}
