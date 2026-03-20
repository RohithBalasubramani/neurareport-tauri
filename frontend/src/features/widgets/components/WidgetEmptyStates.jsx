import {
  Box,
  Typography,
  Chip,
  CircularProgress,
  Button,
} from '@mui/material'
import {
  LinkOff as NoConnectionIcon,
  Cable as ConnectionsIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import PageHeader from '@/components/layout/PageHeader'

export function NoConnectionState() {
  const navigate = useNavigate()
  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader
        title="Widget Intelligence"
        description="Dynamic data-driven widget recommendations"
      />
      <Box
        sx={{
          py: 10,
          textAlign: 'center',
          border: 1,
          borderColor: 'divider',
          borderRadius: 2,
          borderStyle: 'dashed',
        }}
      >
        <NoConnectionIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No database connected
        </Typography>
        <Typography variant="body2" color="text.disabled" sx={{ mb: 2 }}>
          Connect a database from the Connections page to see intelligent widget
          recommendations tailored to your data.
        </Typography>
        <Button
          variant="contained"
          startIcon={<ConnectionsIcon />}
          onClick={() => navigate('/connections')}
          sx={{ textTransform: 'none' }}
        >
          Go to Connections
        </Button>
      </Box>
    </Box>
  )
}

export function LoadingState({ connectionName }) {
  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader title="Widget Intelligence" description={`Analyzing ${connectionName}...`} />
      <Box
        sx={{ py: 8, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}
      >
        <CircularProgress />
        <Typography variant="body2" color="text.secondary">
          Analyzing database schema and recommending widgets...
        </Typography>
      </Box>
    </Box>
  )
}

export function ErrorState({ connectionName, error, onRetry }) {
  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <PageHeader title="Widget Intelligence" description={connectionName} />
      <Box sx={{ py: 8, textAlign: 'center' }}>
        <Typography variant="h6" color="error" gutterBottom>
          Recommendation failed
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {error}
        </Typography>
        <Chip label="Retry" onClick={onRetry} color="primary" clickable />
      </Box>
    </Box>
  )
}
