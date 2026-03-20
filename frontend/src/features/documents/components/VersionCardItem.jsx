import {
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Stack,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Restore as RestoreIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { VersionCard, formatDate } from './trackChangesStyles'

export default function VersionCardItem({
  version,
  index,
  isSelected,
  compareMode,
  onVersionClick,
  onRestore,
}) {
  const theme = useTheme()

  return (
    <VersionCard
      elevation={0}
      isSelected={isSelected}
      onClick={() => onVersionClick(version)}
      data-testid={`version-card-${version.id}`}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Chip
            label={`v${version.version}`}
            size="small"
            sx={{
              borderRadius: 1,
              fontWeight: 600,
              fontSize: '12px',
              bgcolor: index === 0 ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]),
              color: index === 0 ? 'common.white' : 'text.secondary',
            }}
          />
          {index === 0 && (
            <Chip label="Current" size="small" variant="outlined" sx={{ borderRadius: 1, fontSize: '10px' }} />
          )}
        </Stack>
        {!compareMode && index !== 0 && (
          <Tooltip title="Restore this version">
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                onRestore(version)
              }}
              data-testid={`version-restore-${version.id}`}
              aria-label={`Restore version ${version.version}`}
              sx={{ color: 'text.secondary' }}
            >
              <RestoreIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Stack>

      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
        {formatDate(version.created_at)}
      </Typography>

      {version.author_name && (
        <Stack direction="row" alignItems="center" spacing={0.5}>
          <PersonIcon sx={{ fontSize: 14, color: 'text.disabled' }} />
          <Typography variant="caption" color="text.disabled">
            {version.author_name}
          </Typography>
        </Stack>
      )}

      {version.changes_summary && (
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 1,
            color: 'text.secondary',
            fontStyle: 'italic',
          }}
        >
          {version.changes_summary}
        </Typography>
      )}
    </VersionCard>
  )
}
