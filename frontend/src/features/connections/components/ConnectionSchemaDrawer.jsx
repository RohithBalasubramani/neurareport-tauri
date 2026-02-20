/**
 * Premium Connection Schema Drawer
 * Database schema inspector with theme-based styling
 */
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Box,
  Stack,
  Typography,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Alert,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import RefreshIcon from '@mui/icons-material/Refresh'
import VisibilityIcon from '@mui/icons-material/Visibility'
import { Drawer } from '@/components/Drawer'
import * as api from '@/api/client'
import { neutral, palette } from '@/app/theme'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

const formatRowCount = (value) => {
  if (value == null) return 'n/a'
  return value.toLocaleString()
}

export default function ConnectionSchemaDrawer({ open, onClose, connection }) {
  const theme = useTheme()
  const { execute } = useInteraction()
  const [schema, setSchema] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')
  const [previewState, setPreviewState] = useState({})

  const fetchSchema = useCallback(async () => {
    if (!connection?.id) return
    setLoading(true)
    setError(null)
    try {
      const result = await api.getConnectionSchema(connection.id, {
        includeRowCounts: true,
        includeForeignKeys: true,
      })
      setSchema(result)
    } catch (err) {
      setError(err.message || 'Failed to load schema')
    } finally {
      setLoading(false)
    }
  }, [connection?.id])

  useEffect(() => {
    if (open) {
      fetchSchema()
    }
  }, [open, fetchSchema])

  const filteredTables = useMemo(() => {
    const tables = schema?.tables || []
    const query = filter.trim().toLowerCase()
    if (!query) return tables
    return tables.filter((table) => table.name.toLowerCase().includes(query))
  }, [schema, filter])

  const handlePreview = useCallback((tableName) => {
    if (!connection?.id || !tableName) return undefined
    return execute({
      type: InteractionType.EXECUTE,
      label: `Preview ${tableName}`,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { connectionId: connection.id, table: tableName },
      action: async () => {
        setPreviewState((prev) => ({
          ...prev,
          [tableName]: { ...(prev[tableName] || {}), loading: true, error: null },
        }))
        try {
          const result = await api.getConnectionTablePreview(connection.id, {
            table: tableName,
            limit: 6,
          })
          setPreviewState((prev) => ({
            ...prev,
            [tableName]: {
              loading: false,
              error: null,
              columns: result.columns || [],
              rows: result.rows || [],
            },
          }))
        } catch (err) {
          setPreviewState((prev) => ({
            ...prev,
            [tableName]: { ...(prev[tableName] || {}), loading: false, error: err.message || 'Preview failed' },
          }))
        }
      },
    })
  }, [connection?.id, execute])

  const handleRefreshSchema = useCallback(() => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Refresh schema',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { connectionId: connection?.id },
      action: fetchSchema,
    })
  }, [connection?.id, execute, fetchSchema])

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="Connection Schema"
      subtitle={connection?.name || connection?.summary || 'Database overview'}
      width={680}
      actions={(
        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button
            variant="outlined"
            onClick={handleRefreshSchema}
            startIcon={<RefreshIcon />}
            sx={{
              borderRadius: 1,  // Figma spec: 8px
              textTransform: 'none',
              borderColor: alpha(theme.palette.divider, 0.2),
              color: theme.palette.text.secondary,
              '&:hover': {
                borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
              },
            }}
          >
            Refresh
          </Button>
        </Stack>
      )}
    >
      <Stack spacing={2}>
        <TextField
          label="Filter tables"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          size="small"
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 1,  // Figma spec: 8px
              bgcolor: alpha(theme.palette.background.paper, 0.5),
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.15),
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: alpha(theme.palette.divider, 0.3),
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
              },
            },
          }}
        />
        {loading && <LinearProgress sx={{ borderRadius: 1, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }} />}
        {error && (
          <Alert
            severity="error"
            sx={{ borderRadius: 1 }}  // Figma spec: 8px
            action={
              <Button color="inherit" size="small" onClick={handleRefreshSchema}>
                Retry
              </Button>
            }
          >
            {error === 'Failed to load schema'
              ? 'Unable to connect to database. Please verify the connection is active and try again.'
              : error}
          </Alert>
        )}
        {!loading && !error && (
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            {schema?.table_count || 0} tables found
          </Typography>
        )}
        {filteredTables.map((table) => {
          const preview = previewState[table.name] || {}
          return (
            <Accordion
              key={table.name}
              disableGutters
              sx={{
                bgcolor: alpha(theme.palette.background.paper, 0.5),
                border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
                borderRadius: '8px !important',  // Figma spec: 8px
                '&:before': { display: 'none' },
                '&.Mui-expanded': {
                  margin: 0,
                },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: theme.palette.text.secondary }} />}
                sx={{
                  borderRadius: 1,  // Figma spec: 8px
                  '&:hover': {
                    bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                  },
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                    {table.name}
                  </Typography>
                  <Chip
                    size="small"
                    label={`${formatRowCount(table.row_count)} rows`}
                    sx={{
                      bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                      color: theme.palette.text.secondary,
                      fontSize: '12px',
                      height: 22,
                      borderRadius: 1,  // Figma spec: 8px
                    }}
                  />
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={1.5}>
                  <Box>
                    <Typography
                      variant="subtitle2"
                      sx={{ mb: 1, color: theme.palette.text.primary }}
                    >
                      Columns
                    </Typography>
                    <Table
                      size="small"
                      sx={{
                        '& .MuiTableCell-head': {
                          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                          fontWeight: 600,
                          fontSize: '0.75rem',
                          color: theme.palette.text.secondary,
                        },
                        '& .MuiTableCell-body': {
                          fontSize: '14px',
                          color: theme.palette.text.primary,
                        },
                      }}
                    >
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>PK</TableCell>
                          <TableCell>Required</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {(table.columns || []).map((column) => (
                          <TableRow key={column.name}>
                            <TableCell>{column.name}</TableCell>
                            <TableCell>{column.type || '-'}</TableCell>
                            <TableCell>{column.pk ? 'Yes' : '-'}</TableCell>
                            <TableCell>{column.notnull ? 'Yes' : '-'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </Box>

                  <Box>
                    <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                      <Typography
                        variant="subtitle2"
                        sx={{ color: theme.palette.text.primary }}
                      >
                        Preview
                      </Typography>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<VisibilityIcon />}
                        onClick={() => handlePreview(table.name)}
                        sx={{
                          borderRadius: 1,  // Figma spec: 8px
                          textTransform: 'none',
                          fontSize: '0.75rem',
                          borderColor: alpha(theme.palette.divider, 0.2),
                          '&:hover': {
                            borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
                            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                          },
                        }}
                      >
                        Load preview
                      </Button>
                    </Stack>
                    {preview.loading && <LinearProgress sx={{ mt: 1, borderRadius: 1, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }} />}
                    {preview.error && (
                      <Alert severity="error" sx={{ mt: 1, borderRadius: 1 }}>  {/* Figma spec: 8px */}
                        {preview.error}
                      </Alert>
                    )}
                    {preview.rows && preview.rows.length > 0 && (
                      <Table
                        size="small"
                        sx={{
                          mt: 1,
                          '& .MuiTableCell-head': {
                            bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            color: theme.palette.text.secondary,
                          },
                          '& .MuiTableCell-body': {
                            fontSize: '0.75rem',
                            color: theme.palette.text.primary,
                          },
                        }}
                      >
                        <TableHead>
                          <TableRow>
                            {(preview.columns || []).map((col) => (
                              <TableCell key={col}>{col}</TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {preview.rows.map((row, idx) => (
                            <TableRow key={`${table.name}-row-${idx}`}>
                              {(preview.columns || []).map((col) => (
                                <TableCell key={`${table.name}-${idx}-${col}`}>
                                  {row[col] == null ? '-' : String(row[col])}
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                    {!preview.loading && preview.rows && preview.rows.length === 0 && (
                      <Typography
                        variant="body2"
                        sx={{ mt: 1, color: theme.palette.text.secondary }}
                      >
                        No rows returned.
                      </Typography>
                    )}
                  </Box>
                </Stack>
              </AccordionDetails>
            </Accordion>
          )
        })}
      </Stack>
    </Drawer>
  )
}
