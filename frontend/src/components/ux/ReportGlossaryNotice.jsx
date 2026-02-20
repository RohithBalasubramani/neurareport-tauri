import { Alert, Chip, Stack, Typography } from '@mui/material'
import DescriptionIcon from '@mui/icons-material/Description'
import ArticleIcon from '@mui/icons-material/Article'
import WorkOutlineIcon from '@mui/icons-material/WorkOutline'

export default function ReportGlossaryNotice({
  dense = false,
  showChips = true,
  sx,
}) {
  return (
    <Alert severity="info" sx={{ borderRadius: 1, ...sx }}>  {/* Figma spec: 8px */}
      <Stack spacing={dense ? 0.5 : 0.75}>
        <Typography variant={dense ? 'subtitle2' : 'subtitle1'} fontWeight={600}>
          Report designs vs reports
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Report designs are the blueprints. Reports are the generated outputs. Runs happen in the
          background; track progress in Jobs and download finished files in History.
        </Typography>
        {showChips && (
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              size="small"
              variant="outlined"
              icon={<DescriptionIcon fontSize="small" />}
              label="Designs = blueprint"
            />
            <Chip
              size="small"
              variant="outlined"
              icon={<WorkOutlineIcon fontSize="small" />}
              label="Jobs = progress"
            />
            <Chip
              size="small"
              variant="outlined"
              icon={<ArticleIcon fontSize="small" />}
              label="History = downloads"
            />
          </Stack>
        )}
      </Stack>
    </Alert>
  )
}
