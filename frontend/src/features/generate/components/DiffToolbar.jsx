import {
  Stack,
  Typography,
  IconButton,
  Chip,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
  alpha,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import UnfoldLessIcon from '@mui/icons-material/UnfoldLess'

export default function DiffToolbar({
  stats,
  diffIndices,
  currentDiffIndex,
  viewMode,
  onNavigateDiff,
  onSetViewMode,
}) {
  return (
    <Stack
      direction="row"
      spacing={2}
      alignItems="center"
      justifyContent="space-between"
      sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}
    >
      <Stack direction="row" spacing={1} alignItems="center">
        <Chip
          size="small"
          icon={<AddIcon />}
          label={`+${stats.added}`}
          variant="outlined"
          sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
        />
        <Chip
          size="small"
          icon={<RemoveIcon />}
          label={`-${stats.removed}`}
          variant="outlined"
          sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
        />
        {stats.modified > 0 && (
          <Chip
            size="small"
            icon={<CompareArrowsIcon />}
            label={`~${stats.modified}`}
            variant="outlined"
            sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
          />
        )}
      </Stack>

      <Stack direction="row" spacing={1} alignItems="center">
        {diffIndices.length > 0 && (
          <>
            <Typography variant="caption" color="text.secondary">
              {currentDiffIndex + 1} / {diffIndices.length}
            </Typography>
            <Tooltip title="Previous change">
              <IconButton size="small" onClick={() => onNavigateDiff(-1)} aria-label="Previous change">
                <KeyboardArrowUpIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Next change">
              <IconButton size="small" onClick={() => onNavigateDiff(1)} aria-label="Next change">
                <KeyboardArrowDownIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </>
        )}

        <ToggleButtonGroup
          size="small"
          value={viewMode}
          exclusive
          onChange={(e, v) => v && onSetViewMode(v)}
        >
          <ToggleButton value="unified">
            <Tooltip title="Unified view">
              <UnfoldLessIcon fontSize="small" />
            </Tooltip>
          </ToggleButton>
          <ToggleButton value="split">
            <Tooltip title="Split view">
              <CompareArrowsIcon fontSize="small" />
            </Tooltip>
          </ToggleButton>
        </ToggleButtonGroup>
      </Stack>
    </Stack>
  )
}
