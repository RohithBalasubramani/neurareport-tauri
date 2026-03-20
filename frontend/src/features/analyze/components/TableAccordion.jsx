import {
  Box,
  Typography,
  Stack,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  alpha,
} from '@mui/material'
import TableChartIcon from '@mui/icons-material/TableChart'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { neutral } from '@/app/theme'

export default function TableAccordion({ table, theme }) {
  return (
    <Accordion
      sx={{
        mb: 2,
        borderRadius: '12px !important',
        overflow: 'hidden',
        '&:before': { display: 'none' },
        boxShadow: 'none',
        border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        sx={{
          bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.03) : neutral[50],
          '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[100] },
        }}
      >
        <Stack direction="row" alignItems="center" spacing={2}>
          <TableChartIcon sx={{ color: 'text.secondary' }} />
          <Typography fontWeight={600}>{table.title || table.id}</Typography>
          <Chip label={`${table.row_count} rows`} size="small" variant="outlined" sx={{ borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.3) : neutral[200], color: 'text.secondary' }} />
          <Chip label={`${table.column_count} cols`} size="small" variant="outlined" />
        </Stack>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 0 }}>
        <Box sx={{ overflowX: 'auto' }}>
          <Box
            component="table"
            sx={{
              width: '100%',
              borderCollapse: 'collapse',
              '& th': {
                p: 1.5,
                textAlign: 'left',
                fontWeight: 600,
                fontSize: '12px',
                textTransform: 'uppercase',
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                borderBottom: `2px solid ${theme.palette.mode === 'dark' ? neutral[700] : neutral[900]}`,
              },
              '& td': {
                p: 1.5,
                fontSize: '0.875rem',
                borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
              },
              '& tr:hover td': {
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
              },
            }}
          >
            <thead>
              <tr>
                {table.headers.map((header, i) => (
                  <th key={i}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.slice(0, 10).map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Box>
          {table.rows.length > 10 && (
            <Box sx={{ p: 2, textAlign: 'center', bgcolor: alpha(neutral[500], 0.05) }}>
              <Typography variant="caption" color="text.secondary">
                Showing 10 of {table.rows.length} rows
              </Typography>
            </Box>
          )}
        </Box>
      </AccordionDetails>
    </Accordion>
  )
}
