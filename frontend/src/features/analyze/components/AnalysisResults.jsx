import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
  Card,
  CardContent,
  Tabs,
  Tab,
  Alert,
  Divider,
  Button,
  alpha,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import TableChartIcon from '@mui/icons-material/TableChart'
import InsightsIcon from '@mui/icons-material/Insights'
import TimelineIcon from '@mui/icons-material/Timeline'
import BarChartIcon from '@mui/icons-material/BarChart'
import DownloadIcon from '@mui/icons-material/Download'

import ZoomableChart from './ZoomableChart'
import { neutral, palette } from '@/app/theme'

function TabPanel({ children, value, index, ...other }) {
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

function MetricCard({ metric }) {
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

function ExtractedTableView({ table, maxRows = 50 }) {
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

export default function AnalysisResults({ result }) {
  const [tabValue, setTabValue] = useState(0)
  const [selectedChart, setSelectedChart] = useState(0)

  const {
    document_name,
    document_type,
    processing_time_ms,
    summary,
    tables = [],
    data_points = [],
    chart_suggestions = [],
    raw_data = [],
    field_catalog = [],
    warnings = [],
  } = result || {}

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue)
  }

  const handleExportCSV = () => {
    if (!raw_data || raw_data.length === 0) return

    const headers = Object.keys(raw_data[0])
    const csvRows = [
      headers.join(','),
      ...raw_data.map((row) =>
        headers.map((h) => {
          const val = row[h]
          if (val === null || val === undefined) return ''
          const str = String(val)
          return str.includes(',') || str.includes('"') ? `"${str.replace(/"/g, '""')}"` : str
        }).join(',')
      ),
    ]
    const csvContent = csvRows.join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${document_name || 'analysis'}_data.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleExportJSON = () => {
    if (!raw_data || raw_data.length === 0) return

    const jsonContent = JSON.stringify(raw_data, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${document_name || 'analysis'}_data.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const currentChartSpec = chart_suggestions[selectedChart] || null

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="h6">{document_name || 'Analysis Results'}</Typography>
          <Chip label={document_type?.toUpperCase()} size="small" variant="outlined" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
          {processing_time_ms && (
            <Chip label={`${(processing_time_ms / 1000).toFixed(1)}s`} size="small" variant="outlined" />
          )}
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button
            startIcon={<DownloadIcon />}
            size="small"
            onClick={handleExportCSV}
            disabled={!raw_data?.length}
          >
            Export CSV
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            size="small"
            onClick={handleExportJSON}
            disabled={!raw_data?.length}
          >
            Export JSON
          </Button>
        </Stack>
      </Stack>

      {summary && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {summary}
        </Alert>
      )}

      {warnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {warnings.join('; ')}
        </Alert>
      )}

      {data_points.length > 0 && (
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
      )}

      <Paper variant="outlined" sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab icon={<BarChartIcon />} label={`Charts (${chart_suggestions.length})`} iconPosition="start" />
          <Tab icon={<TableChartIcon />} label={`Tables (${tables.length})`} iconPosition="start" />
          <Tab icon={<InsightsIcon />} label={`Fields (${field_catalog.length})`} iconPosition="start" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {chart_suggestions.length > 0 ? (
            <Box>
              <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
                {chart_suggestions.map((chart, idx) => (
                  <Chip
                    key={idx}
                    label={chart.title || `Chart ${idx + 1}`}
                    onClick={() => setSelectedChart(idx)}
                    color={selectedChart === idx ? 'primary' : 'default'}
                    variant={selectedChart === idx ? 'filled' : 'outlined'}
                    icon={chart.type === 'line' ? <TimelineIcon /> : <BarChartIcon />}
                  />
                ))}
              </Stack>

              {currentChartSpec && (
                <ZoomableChart
                  data={raw_data}
                  spec={currentChartSpec}
                  height={400}
                  showBrush={raw_data.length > 15}
                />
              )}
            </Box>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>
              No chart suggestions available
            </Typography>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {tables.length > 0 ? (
            <Stack spacing={2}>
              {tables.map((table, idx) => (
                <Accordion key={idx} defaultExpanded={idx === 0}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <TableChartIcon fontSize="small" color="action" />
                      <Typography fontWeight={500}>
                        {table.title || table.id || `Table ${idx + 1}`}
                      </Typography>
                      <Chip
                        label={`${table.rows?.length || 0} rows`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`${table.headers?.length || 0} cols`}
                        size="small"
                        variant="outlined"
                      />
                      {table.source_page && (
                        <Chip label={`Page ${table.source_page}`} size="small" />
                      )}
                      {table.source_sheet && (
                        <Chip label={table.source_sheet} size="small" />
                      )}
                    </Stack>
                  </AccordionSummary>
                  <AccordionDetails sx={{ p: 0 }}>
                    <ExtractedTableView table={table} />
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>
              No tables extracted
            </Typography>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {field_catalog.length > 0 ? (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Field Name</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Sample Values</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {field_catalog.map((field, idx) => (
                    <TableRow key={idx} hover>
                      <TableCell>{field.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={field.type}
                          size="small"
                          color={
                            field.type === 'numeric'
                              ? 'success'
                              : field.type === 'datetime'
                                ? 'info'
                                : 'default'
                          }
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        {field.sample_values?.slice(0, 3).join(', ') || '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>
              No field information available
            </Typography>
          )}
        </TabPanel>
      </Paper>
    </Box>
  )
}
