import {
  Box, Stack, Button, Typography, Chip, IconButton,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import SpeedIcon from '@mui/icons-material/Speed'
import EditIcon from '@mui/icons-material/Edit'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight'
import CloseIcon from '@mui/icons-material/Close'
import HeartbeatBadge from '@/components/HeartbeatBadge.jsx'
import { neutral, fontFamilyMono } from '@/app/theme'

export function PanelHeader({
  detailConnection, detailStatus, detailLatency,
  detailNote, setDetailId, activeConnectionId,
}) {
  return (
    <Box
      sx={{
        px: 2,
        py: 1.25,
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      <Button
        size="small"
        onClick={() => setDetailId(null)}
        sx={{
          display: { xs: 'inline-flex', md: 'none' },
          textTransform: 'none',
          px: 0,
          minWidth: 0,
          color: 'text.secondary',
        }}
        startIcon={<KeyboardArrowRightIcon sx={{ transform: 'rotate(180deg)' }} />}
      >
        Back
      </Button>
      <Typography
        variant="subtitle1"
        noWrap
        title={detailConnection.name}
        sx={{ flexGrow: 1, minWidth: 0 }}
      >
        {detailConnection.name}
      </Typography>
      <Stack direction="row" spacing={1} alignItems="center" sx={{ flexShrink: 0 }}>
        {activeConnectionId === detailConnection.backend_connection_id ||
        activeConnectionId === detailConnection.id ? (
          <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
        ) : null}
        <HeartbeatBadge
          withText
          size="small"
          status={detailStatus}
          latencyMs={detailLatency != null ? detailLatency : undefined}
          tooltip={detailNote}
        />
      </Stack>
      <IconButton
        aria-label="Close details"
        onClick={() => setDetailId(null)}
        sx={{ color: 'text.secondary' }}
      >
        <CloseIcon />
      </IconButton>
    </Box>
  )
}

export function PanelBody({ detailConnection, detailLatency, detailNote }) {
  return (
    <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
      <Stack spacing={1.5}>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
            DB TYPE
          </Typography>
          <Typography variant="body2">
            {detailConnection.db_type || '--'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
            HOST / PATH
          </Typography>
          <Typography
            variant="body2"
            sx={{
              fontFamily: fontFamilyMono,
              wordBreak: 'break-all',
            }}
          >
            {detailConnection.host || detailConnection.db_url || '--'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
            LATENCY
          </Typography>
          <Typography variant="body2">
            {detailLatency != null ? `${Math.round(detailLatency)}ms` : '--'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
            LAST CONNECTED
          </Typography>
          <Typography variant="body2">
            {detailConnection.lastConnected
              ? new Date(detailConnection.lastConnected).toLocaleString()
              : 'Never connected'}
          </Typography>
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
            NOTES
          </Typography>
          <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
            {detailNote || '--'}
          </Typography>
        </Box>
      </Stack>
    </Box>
  )
}

export function PanelActions({
  detailConnection, requestSelect, handleRowTest,
  beginEditConnection, setConfirmDelete,
}) {
  return (
    <Box
      sx={{
        px: 2,
        py: 1.25,
        borderTop: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        gap: 1,
        flexWrap: { xs: 'wrap', sm: 'nowrap' },
        justifyContent: 'flex-start',
      }}
    >
      <Button
        variant="contained"
        size="small"
        startIcon={<CheckCircleOutlineIcon />}
        onClick={() => requestSelect(detailConnection)}
      >
        Select Connection
      </Button>
      <Button
        variant="outlined"
        size="small"
        startIcon={<SpeedIcon />}
        onClick={() => handleRowTest(detailConnection)}
      >
        Test Connection
      </Button>
      <Button
        variant="text"
        size="small"
        startIcon={<EditIcon />}
        onClick={() => beginEditConnection(detailConnection)}
      >
        Edit Settings
      </Button>
      <Button
        variant="text"
        size="small"
        startIcon={<DeleteOutlineIcon />}
        onClick={() => setConfirmDelete(detailConnection.id)}
        sx={{ color: 'text.secondary' }}
      >
        Delete
      </Button>
    </Box>
  )
}
