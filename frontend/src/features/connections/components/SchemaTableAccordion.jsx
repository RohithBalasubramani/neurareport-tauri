import { Box, Stack, Typography, Accordion, AccordionSummary, AccordionDetails,
  Chip, Button, Table, TableHead, TableRow, TableCell, TableBody,
  Alert, LinearProgress, alpha } from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import VisibilityIcon from '@mui/icons-material/Visibility'
import { neutral } from '@/app/theme'

const formatRowCount = (value) => {
  if (value == null) return 'n/a'
  return value.toLocaleString()
}

export default function SchemaTableAccordion({ table, preview, onPreview, theme }) {
  return (
    <Accordion
      disableGutters
      sx={{
        bgcolor: alpha(theme.palette.background.paper, 0.5),
        border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
        borderRadius: '8px !important',
        '&:before': { display: 'none' },
        '&.Mui-expanded': {
          margin: 0,
        },
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon sx={{ color: theme.palette.text.secondary }} />}
        sx={{
          borderRadius: 1,
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
              borderRadius: 1,
            }}
          />
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Stack spacing={1.5}>
          <ColumnsTable table={table} theme={theme} />
          <PreviewSection table={table} preview={preview} onPreview={onPreview} theme={theme} />
        </Stack>
      </AccordionDetails>
    </Accordion>
  )
}

function ColumnsTable({ table, theme }) {
  return (
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
  )
}

function PreviewSection({ table, preview, onPreview, theme }) {
  return (
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
          onClick={() => onPreview(table.name)}
          sx={{
            borderRadius: 1,
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
        <Alert severity="error" sx={{ mt: 1, borderRadius: 1 }}>
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
  )
}
