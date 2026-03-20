import {
  Autocomplete,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import FileUploadOutlinedIcon from '@mui/icons-material/FileUploadOutlined'
import ScheduleIcon from '@mui/icons-material/Schedule'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'

export default function TemplatePickerToolbar({
  allTags,
  tagFilter,
  setTagFilter,
  nameQuery,
  onNameQueryChange,
  requirement,
  setRequirement,
  kindHints,
  setKindHints,
  kindOptions,
  domainHints,
  setDomainHints,
  domainOptions,
  recommending,
  queueingRecommendations,
  importing,
  importInputRef,
  onRecommend,
  onQueueRecommend,
  onRequirementKeyDown,
  onImport,
}) {
  return (
    <Stack spacing={1.5}>
      <Stack direction="row" alignItems="center" spacing={0.75} justifyContent="space-between" flexWrap="wrap">
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Template Picker</Typography>
          <InfoTooltip
            content={TOOLTIP_COPY.templatePicker}
            ariaLabel="Template picker guidance"
          />
        </Stack>
        <Stack direction="row" spacing={1}>
          <input
            type="file"
            accept=".zip"
            ref={importInputRef}
            onChange={onImport}
            style={{ display: 'none' }}
            aria-label="Import template zip file"
          />
          <Button
            size="small"
            variant="outlined"
            startIcon={
              importing ? (
                <CircularProgress size={16} color="inherit" />
              ) : (
                <FileUploadOutlinedIcon fontSize="small" />
              )
            }
            onClick={() => importInputRef.current?.click()}
            disabled={importing}
          >
            {importing ? 'Importing...' : 'Import Template'}
          </Button>
        </Stack>
      </Stack>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems={{ xs: 'stretch', md: 'center' }}>
        <Autocomplete
          multiple
          options={allTags}
          value={tagFilter}
          onChange={(e, v) => setTagFilter(v)}
          freeSolo
          renderInput={(params) => <TextField {...params} label="Filter by tags" />}
          sx={{ maxWidth: 440 }}
        />
        <TextField
          label="Search by name"
          size="small"
          value={nameQuery}
          onChange={(e) => onNameQueryChange(e.target.value)}
          sx={{ maxWidth: 320 }}
        />
      </Stack>
      <Stack
        direction={{ xs: 'column', md: 'row' }}
        spacing={1}
        alignItems={{ xs: 'stretch', md: 'center' }}
      >
        <TextField
          label="Describe what you need"
          size="small"
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          onKeyDown={onRequirementKeyDown}
          fullWidth
          id="template-recommendation-requirement"
          InputLabelProps={{ shrink: true }}
          inputProps={{ 'aria-label': 'Describe what you need' }}
        />
        <Autocomplete
          multiple
          options={kindOptions}
          value={kindHints}
          onChange={(_e, v) => setKindHints(v)}
          size="small"
          renderInput={(params) => <TextField {...params} label="Kinds (pdf/excel)" />}
          sx={{ minWidth: 200 }}
        />
        <Autocomplete
          multiple
          options={domainOptions}
          value={domainHints}
          onChange={(_e, v) => setDomainHints(v)}
          size="small"
          renderInput={(params) => <TextField {...params} label="Domains" />}
          sx={{ minWidth: 220 }}
        />
        <Button
          variant="contained"
          onClick={onRecommend}
          disabled={recommending || queueingRecommendations}
          sx={{ whiteSpace: 'nowrap' }}
        >
          {recommending ? 'Finding...' : 'Get recommendations'}
        </Button>
        <Button
          variant="outlined"
          onClick={onQueueRecommend}
          disabled={recommending || queueingRecommendations}
          startIcon={
            queueingRecommendations ? (
              <CircularProgress size={16} color="inherit" />
            ) : (
              <ScheduleIcon fontSize="small" />
            )
          }
          sx={{ whiteSpace: 'nowrap' }}
        >
          {queueingRecommendations ? 'Queueing...' : 'Queue'}
        </Button>
      </Stack>
    </Stack>
  )
}
