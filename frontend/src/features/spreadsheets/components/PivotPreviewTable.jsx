/**
 * Pivot Table Preview
 * Displays a preview of the generated pivot table data.
 */
import {
  Box,
  Typography,
  IconButton,
  Stack,
  Paper,
  alpha,
  useTheme,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Calculate as CalculateIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { AGGREGATIONS } from '../hooks/usePivotTableBuilder'

const PreviewPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(2),
  overflowY: 'auto',
}))

const PreviewTable = styled('table')(({ theme }) => ({
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: '14px',
  '& th, & td': {
    padding: theme.spacing(0.75, 1),
    border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    textAlign: 'left',
  },
  '& th': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    fontWeight: 600,
  },
  '& tbody tr:hover': {
    backgroundColor: alpha(theme.palette.action.hover, 0.5),
  },
}))

export default function PivotPreviewTable({ config, previewData, onClose }) {
  const theme = useTheme()

  return (
    <PreviewPanel>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
          Preview
        </Typography>
        <IconButton size="small" onClick={onClose}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </Stack>

      {config.values.length === 0 ? (
        <Paper
          elevation={0}
          sx={{
            p: 4,
            textAlign: 'center',
            border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
            borderRadius: 1,
          }}
        >
          <CalculateIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="body1" color="text.secondary">
            Drag fields to build your pivot table
          </Typography>
          <Typography variant="body2" color="text.disabled">
            Add at least one field to Values to see results
          </Typography>
        </Paper>
      ) : (
        <Paper
          elevation={0}
          sx={{
            border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
            borderRadius: 1,
            overflow: 'auto',
          }}
        >
          <PreviewTable>
            <thead>
              <tr>
                <th>{config.rows[0]?.customName || config.rows[0]?.name || 'Row Labels'}</th>
                {config.columns.length > 0 ? (
                  <>
                    <th>Value 1</th>
                    <th>Value 2</th>
                  </>
                ) : (
                  config.values.map((v) => (
                    <th key={v.name}>
                      {v.customName || `${AGGREGATIONS.find((a) => a.value === v.aggregation)?.label || 'Sum'} of ${v.name}`}
                    </th>
                  ))
                )}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {previewData.map((row, i) => (
                <tr key={i} style={{ fontWeight: row.rowLabel === 'Grand Total' ? 600 : 400 }}>
                  <td>{row.rowLabel}</td>
                  <td>{row.col1.toLocaleString()}</td>
                  <td>{row.col2.toLocaleString()}</td>
                  <td>{row.total.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </PreviewTable>
        </Paper>
      )}
    </PreviewPanel>
  )
}
