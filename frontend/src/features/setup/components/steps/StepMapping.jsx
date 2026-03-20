import {
  Box,
  Typography,
  Stack,
  Alert,
  Paper,
  LinearProgress,
  Chip,
  Button,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { neutral } from '@/app/theme'
import { useStepMapping } from '../../hooks/useStepMapping'

export default function StepMapping({ wizardState, updateWizardState, onComplete, setLoading }) {
  const {
    loading,
    mapping,
    keys,
    setKeys,
    showAdvanced,
    setShowAdvanced,
    approving,
    approved,
    error,
    setError,
    handleMappingChange,
    handleApprove,
  } = useStepMapping({ wizardState, updateWizardState })

  const mappingEntries = Object.entries(mapping)

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        Configure Field Mapping
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Map template placeholders to your database columns for automatic data insertion.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {approved && (
        <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 3 }}>
          Template mapping approved! You can now generate reports.
        </Alert>
      )}

      {loading ? (
        <Box sx={{ py: 4 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2, textAlign: 'center' }}>
            Loading mapping configuration...
          </Typography>
          <LinearProgress />
        </Box>
      ) : mappingEntries.length === 0 ? (
        <Alert severity="info">
          No mappings found. The template may not have any placeholder tokens.
        </Alert>
      ) : (
        <>
          <Paper variant="outlined" sx={{ overflow: 'hidden' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: 'action.hover' }}>
                  <TableCell sx={{ fontWeight: 600 }}>Template Field</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Database Column</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {mappingEntries.map(([token, config]) => (
                  <TableRow key={token}>
                    <TableCell>
                      <Chip label={token} size="small" variant="outlined" sx={{ fontFamily: 'monospace' }} />
                    </TableCell>
                    <TableCell>
                      <TextField
                        size="small"
                        value={config?.column || config?.expression || ''}
                        onChange={(e) => handleMappingChange(token, 'column', e.target.value)}
                        placeholder="Enter column name"
                        fullWidth
                        disabled={approved}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={config?.column || config?.expression ? 'Mapped' : 'Unmapped'}
                        size="small"
                        variant="outlined"
                        sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>

          <Box sx={{ mt: 3 }}>
            <Button
              variant="text"
              size="small"
              onClick={() => setShowAdvanced((prev) => !prev)}
              endIcon={showAdvanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ textTransform: 'none', fontWeight: 500 }}
            >
              Advanced Settings
            </Button>

            <Collapse in={showAdvanced}>
              <Paper sx={{ mt: 2, p: 2, bgcolor: 'action.hover' }}>
                <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
                  Key Fields
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Select fields that will be used as filter keys when generating reports.
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                  {mappingEntries.map(([token]) => (
                    <Chip
                      key={token}
                      label={token}
                      size="small"
                      variant={keys.includes(token) ? 'filled' : 'outlined'}
                      sx={keys.includes(token) ? { bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' } : {}}
                      onClick={() => {
                        if (keys.includes(token)) {
                          setKeys((prev) => prev.filter((k) => k !== token))
                        } else {
                          setKeys((prev) => [...prev, token])
                        }
                      }}
                      disabled={approved}
                    />
                  ))}
                </Stack>
              </Paper>
            </Collapse>
          </Box>

          {!approved && (
            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleApprove}
                disabled={approving}
                startIcon={<AutoFixHighIcon />}
              >
                {approving ? 'Approving...' : 'Approve Mapping'}
              </Button>
            </Box>
          )}
        </>
      )}
    </Box>
  )
}
