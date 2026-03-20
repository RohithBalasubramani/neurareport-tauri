import Grid from '@mui/material/Grid2'
import {
  Autocomplete,
  Button,
  Chip,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import InfoTooltip from '@/components/common/InfoTooltip.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'

export default function SetupTemplateToolbar({
  selected,
  filtered,
  allTags,
  tagFilter,
  setTagFilter,
  nameQuery,
  setNameQuery,
  importing,
  fileInputRef,
  onImportClick,
  onImportInputChange,
}) {
  return (
    <>
      <Stack spacing={1.5}>
        <Stack direction="row" alignItems="center" spacing={0.75}>
          <Typography variant="h6">Select Templates</Typography>
          <InfoTooltip content={TOOLTIP_COPY.templatePicker} ariaLabel="How to select templates" />
        </Stack>
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={1}
          alignItems={{ xs: 'flex-start', md: 'center' }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            Export from any template card to download the entire uploads folder. Import the ZIP here to restore it on this device.
          </Typography>
          <Stack direction="row" spacing={1}>
            <Chip size="small" variant="outlined" label={`${selected.length} selected`} />
            <Chip size="small" variant="outlined" label={`${filtered.length} showing`} />
          </Stack>
        </Stack>
      </Stack>
      <Grid container spacing={1.5} alignItems="center" sx={{ pb: 1 }}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Autocomplete
            multiple
            options={allTags}
            value={tagFilter}
            onChange={(e, v) => setTagFilter(v)}
            freeSolo
            renderInput={(params) => <TextField {...params} label="Filter by tags" />}
          />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <TextField
            label="Search by name"
            value={nameQuery}
            onChange={(e) => setNameQuery(e.target.value)}
            fullWidth
          />
        </Grid>
        <Grid
          size={{ xs: 12, md: 4 }}
          sx={{ display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            style={{ display: 'none' }}
            onChange={onImportInputChange}
          />
          <Tooltip title="Import an exported template bundle">
            <span>
              <Button
                variant="contained"
                startIcon={<UploadFileIcon />}
                onClick={onImportClick}
                disabled={importing}
              >
                {importing ? 'Importing...' : 'Import Template'}
              </Button>
            </span>
          </Tooltip>
        </Grid>
      </Grid>
    </>
  )
}
