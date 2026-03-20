import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
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
  Tabs,
  Tab,
  Alert,
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
import { neutral } from '@/app/theme'
import { TabPanel, ExtractedTableView, MetricsSection } from './AnalysisSubComponents'
import { exportCSV, exportJSON } from './analysisExportUtils'

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
          <Button startIcon={<DownloadIcon />} size="small" onClick={() => exportCSV(raw_data, document_name)} disabled={!raw_data?.length}>
            Export CSV
          </Button>
          <Button startIcon={<DownloadIcon />} size="small" onClick={() => exportJSON(raw_data, document_name)} disabled={!raw_data?.length}>
            Export JSON
          </Button>
        </Stack>
      </Stack>

      {summary && <Alert severity="info" sx={{ mb: 2 }}>{summary}</Alert>}
      {warnings.length > 0 && <Alert severity="warning" sx={{ mb: 2 }}>{warnings.join('; ')}</Alert>}

      <MetricsSection data_points={data_points} />

      <Paper variant="outlined" sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
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
                <ZoomableChart data={raw_data} spec={currentChartSpec} height={400} showBrush={raw_data.length > 15} />
              )}
            </Box>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>No chart suggestions available</Typography>
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
                      <Typography fontWeight={500}>{table.title || table.id || `Table ${idx + 1}`}</Typography>
                      <Chip label={`${table.rows?.length || 0} rows`} size="small" variant="outlined" />
                      <Chip label={`${table.headers?.length || 0} cols`} size="small" variant="outlined" />
                      {table.source_page && <Chip label={`Page ${table.source_page}`} size="small" />}
                      {table.source_sheet && <Chip label={table.source_sheet} size="small" />}
                    </Stack>
                  </AccordionSummary>
                  <AccordionDetails sx={{ p: 0 }}>
                    <ExtractedTableView table={table} />
                  </AccordionDetails>
                </Accordion>
              ))}
            </Stack>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>No tables extracted</Typography>
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
                          color={field.type === 'numeric' ? 'success' : field.type === 'datetime' ? 'info' : 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{field.sample_values?.slice(0, 3).join(', ') || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography color="text.secondary" textAlign="center" py={4}>No field information available</Typography>
          )}
        </TabPanel>
      </Paper>
    </Box>
  )
}
