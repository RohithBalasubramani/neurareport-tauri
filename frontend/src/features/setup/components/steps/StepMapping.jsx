import { useState, useCallback, useEffect } from 'react'
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { useAppStore } from '@/stores'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import * as api from '@/api/client'
import { neutral, palette } from '@/app/theme'

export default function StepMapping({ wizardState, updateWizardState, onComplete, setLoading }) {
  const toast = useToast()
  const { execute } = useInteraction()

  const templateId = useAppStore((s) => s.templateId) || wizardState.templateId
  const activeConnection = useAppStore((s) => s.activeConnection)
  const setLastApprovedTemplate = useAppStore((s) => s.setLastApprovedTemplate)

  const [loading, setLocalLoading] = useState(false)
  const [mapping, setMapping] = useState(wizardState.mapping || {})
  const [keys, setKeys] = useState(wizardState.keys || [])
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [approving, setApproving] = useState(false)
  const [approved, setApproved] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    const fetchMapping = async () => {
      if (!templateId) return

      setLocalLoading(true)
      try {
        const connectionId = wizardState.connectionId || activeConnection?.id
        await execute({
          type: InteractionType.ANALYZE,
          label: 'Load mapping preview',
          reversibility: Reversibility.SYSTEM_MANAGED,
          suppressSuccessToast: true,
          suppressErrorToast: true,
          blocksNavigation: false,
          intent: {
            connectionId,
            templateId,
            templateKind: wizardState.templateKind || 'pdf',
            action: 'mapping_preview',
          },
          action: async () => {
            try {
              const result = await api.mappingPreview(templateId, connectionId, {
                kind: wizardState.templateKind || 'pdf',
              })

              if (!cancelled) {
                if (result.mapping) {
                  setMapping(result.mapping)
                  updateWizardState({ mapping: result.mapping })
                }
                if (result.keys) {
                  setKeys(result.keys)
                  updateWizardState({ keys: result.keys })
                }
              }
              return result
            } catch (err) {
              if (!cancelled) {
                setError(err.message || 'Failed to load mapping')
              }
              throw err
            }
          },
        })
      } finally {
        if (!cancelled) {
          setLocalLoading(false)
        }
      }
    }

    if (!wizardState.mapping) {
      fetchMapping()
    }

    return () => { cancelled = true }
  }, [templateId, wizardState.connectionId, wizardState.templateKind, wizardState.mapping, activeConnection?.id, updateWizardState, execute])

  const handleMappingChange = useCallback((token, field, value) => {
    setMapping((prev) => ({
      ...prev,
      [token]: {
        ...prev[token],
        [field]: value,
      },
    }))
  }, [])

  const handleApprove = useCallback(async () => {
    setApproving(true)
    setError(null)

    try {
      const connectionId = wizardState.connectionId || activeConnection?.id

      await execute({
        type: InteractionType.UPDATE,
        label: 'Approve template mapping',
        reversibility: Reversibility.SYSTEM_MANAGED,
        suppressSuccessToast: true,
        suppressErrorToast: true,
        blocksNavigation: true,
        intent: {
          connectionId,
          templateId,
          templateKind: wizardState.templateKind || 'pdf',
          action: 'mapping_approve',
        },
        action: async () => {
          try {
            const result = await api.mappingApprove(templateId, mapping, {
              connectionId,
              keys,
              kind: wizardState.templateKind || 'pdf',
              onProgress: () => {
                // Handle progress events
              },
            })

            if (result.ok) {
              setApproved(true)
              setLastApprovedTemplate({
                id: templateId,
                name: wizardState.templateName,
                kind: wizardState.templateKind,
              })
              toast.show('Template approved and ready to use!', 'success')
            }
            return result
          } catch (err) {
            setError(err.message || 'Failed to approve mapping')
            toast.show(err.message || 'Failed to approve mapping', 'error')
            throw err
          }
        },
      })
    } finally {
      setApproving(false)
    }
  }, [templateId, mapping, keys, wizardState, activeConnection?.id, setLastApprovedTemplate, toast, execute])

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
        <Alert
          severity="success"
          icon={<CheckCircleIcon />}
          sx={{ mb: 3 }}
        >
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
                      <Chip
                        label={token}
                        size="small"
                        variant="outlined"
                        sx={{ fontFamily: 'monospace' }}
                      />
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
                      {config?.column || config?.expression ? (
                        <Chip label="Mapped" size="small" variant="outlined" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                      ) : (
                        <Chip label="Unmapped" size="small" variant="outlined" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>

          {/* Advanced Settings */}
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

          {/* Approve Button */}
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
