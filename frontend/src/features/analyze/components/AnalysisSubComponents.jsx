import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'

export function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  )
}

export function MetricCard({ metric }) {
  const formatValue = (value, unit) => {
    if (value === null || value === undefined) return 'N/A'
    if (typeof value === 'number') {
      const formatted = value.toLocaleString(undefined, {
        maximumFractionDigits: 2,
      })
      return unit ? `${formatted} ${unit}` : formatted
    }
    return String(value)
  }

  return (
    <Card variant="outlined">
      <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          {metric.key}
        </Typography>
        <Typography variant="h6" fontWeight={600}>
          {formatValue(metric.value, metric.unit)}
        </Typography>
        {metric.context && (
          <Typography variant="caption" color="text.secondary">
            {metric.context}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}

export function ExtractedTableView({ table, maxRows = 50 }) {
  const displayRows = table.rows?.slice(0, maxRows) || []
  const hasMore = (table.rows?.length || 0) > maxRows

  return (
    <TableContainer sx={{ maxHeight: 400 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            {table.headers?.map((header, idx) => (
              <TableCell key={idx} sx={{ fontWeight: 600, bgcolor: 'background.paper' }}>
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <span>{header}</span>
                  {table.data_types?.[idx] && (
                    <Chip
                      label={table.data_types[idx]}
                      size="small"
                      variant="outlined"
                      sx={{ fontSize: '10px', height: 18 }}
                    />
                  )}
                </Stack>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {displayRows.map((row, rowIdx) => (
            <TableRow key={rowIdx} hover>
              {row.map((cell, cellIdx) => (
                <TableCell key={cellIdx} sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {cell || '-'}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {hasMore && (
        <Typography variant="caption" color="text.secondary" sx={{ p: 1, display: 'block' }}>
          Showing {maxRows} of {table.rows.length} rows
        </Typography>
      )}
    </TableContainer>
  )
}

export function MetricsSection({ data_points }) {
  if (!data_points?.length) return null

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Key Metrics
      </Typography>
      <Grid container spacing={2}>
        {data_points.slice(0, 8).map((metric, idx) => (
          <Grid size={{ xs: 6, sm: 4, md: 3 }} key={idx}>
            <MetricCard metric={metric} />
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
