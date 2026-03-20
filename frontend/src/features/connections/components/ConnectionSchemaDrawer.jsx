/**
 * Premium Connection Schema Drawer
 * Database schema inspector with theme-based styling
 */
import {
  Stack,
  Typography,
  TextField,
  Button,
  Alert,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import { Drawer } from '@/components/drawer'
import { neutral } from '@/app/theme'
import { useSchemaDrawer } from '../hooks/useSchemaDrawer'
import SchemaTableAccordion from './SchemaTableAccordion'

export default function ConnectionSchemaDrawer({ open, onClose, connection }) {
  const theme = useTheme()
  const {
    schema,
    loading,
    error,
    filter,
    setFilter,
    previewState,
    filteredTables,
    handlePreview,
    handleRefreshSchema,
  } = useSchemaDrawer({ open, connection })

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
              borderRadius: 1,
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
              borderRadius: 1,
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
        {loading && <LinearProgress sx={{ borderRadius: 1, bgcolor: (t) => t.palette.mode === 'dark' ? alpha(t.palette.text.primary, 0.1) : neutral[100], '& .MuiLinearProgress-bar': { bgcolor: (t) => t.palette.mode === 'dark' ? neutral[500] : neutral[700] } }} />}
        {error && (
          <Alert
            severity="error"
            sx={{ borderRadius: 1 }}
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
        {filteredTables.map((table) => (
          <SchemaTableAccordion
            key={table.name}
            table={table}
            preview={previewState[table.name] || {}}
            onPreview={handlePreview}
            theme={theme}
          />
        ))}
      </Stack>
    </Drawer>
  )
}
