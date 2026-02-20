import { Box, Stack, Typography, Button, Alert, AlertTitle, Collapse, alpha } from '@mui/material'
import RestoreIcon from '@mui/icons-material/Restore'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import AccessTimeIcon from '@mui/icons-material/AccessTime'

function formatTimeAgo(timestamp) {
  if (!timestamp) return 'Unknown time'

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`

  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function DraftRecoveryBanner({
  show,
  draftData,
  onRestore,
  onDiscard,
  restoring = false,
}) {
  if (!show || !draftData) return null

  return (
    <Collapse in={show}>
      <Alert
        severity="info"
        icon={<RestoreIcon />}
        sx={{
          mb: 2,
          borderRadius: 1,  // Figma spec: 8px
          '& .MuiAlert-message': { width: '100%' },
        }}
        action={
          <Stack direction="row" spacing={1}>
            <Button
              size="small"
              variant="contained"
              startIcon={<RestoreIcon />}
              onClick={onRestore}
              disabled={restoring}
            >
              {restoring ? 'Restoring...' : 'Restore'}
            </Button>
            <Button
              size="small"
              variant="outlined"
              color="inherit"
              startIcon={<DeleteOutlineIcon />}
              onClick={onDiscard}
              disabled={restoring}
            >
              Discard
            </Button>
          </Stack>
        }
      >
        <AlertTitle sx={{ fontWeight: 600 }}>Unsaved Draft Found</AlertTitle>
        <Stack direction="row" spacing={2} alignItems="center">
          <Typography variant="body2">
            You have unsaved changes from a previous session.
          </Typography>
          <Stack direction="row" spacing={0.5} alignItems="center">
            <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              {formatTimeAgo(draftData.savedAt)}
            </Typography>
          </Stack>
        </Stack>
      </Alert>
    </Collapse>
  )
}

export function AutoSaveIndicator({ lastSaved, dirty }) {
  if (!lastSaved && !dirty) return null

  return (
    <Stack
      direction="row"
      spacing={0.5}
      alignItems="center"
      sx={{
        py: 0.5,
        px: 1,
        borderRadius: 1,
        bgcolor: (theme) =>
          dirty
            ? alpha(theme.palette.text.primary, 0.05)
            : alpha(theme.palette.text.primary, 0.05),
      }}
    >
      <Box
        sx={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          bgcolor: 'text.secondary',
        }}
      />
      <Typography variant="caption" color="text.secondary">
        {dirty
          ? 'Unsaved changes'
          : lastSaved
          ? `Draft saved ${formatTimeAgo(lastSaved)}`
          : 'All changes saved'}
      </Typography>
    </Stack>
  )
}
