import { useState } from 'react'
import {
  Box, Typography, CircularProgress, Accordion, AccordionSummary,
  AccordionDetails, Chip, Table, TableHead, TableRow, TableCell, TableBody,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import DescriptionIcon from '@mui/icons-material/Description'
import { GlassCard } from '@/styles/components'

const typeColors = {
  float: 'primary',
  int: 'secondary',
  bool: 'success',
  string: 'warning',
}

export default function SchemaExplorer({ schemas = [], loading }) {
  const [expanded, setExpanded] = useState(null)

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (schemas.length === 0) {
    return (
      <GlassCard sx={{ textAlign: 'center', py: 6 }}>
        <DescriptionIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">No schemas found</Typography>
        <Typography variant="body2" color="text.secondary">
          This Logger database has no registered device schemas.
        </Typography>
      </GlassCard>
    )
  }

  return (
    <Box>
      {schemas.map((schema) => (
        <Accordion
          key={schema.id}
          expanded={expanded === schema.id}
          onChange={() => setExpanded(expanded === schema.id ? null : schema.id)}
          sx={{ mb: 1, borderRadius: '8px !important', '&:before': { display: 'none' } }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              <Typography variant="subtitle1" fontWeight={600}>
                {schema.name}
              </Typography>
              <Chip label={`${(schema.fields || []).length} fields`} size="small" variant="outlined" />
              {schema.description && (
                <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto', mr: 2 }}>
                  {schema.description}
                </Typography>
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {(schema.fields || []).length > 0 ? (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 600 }}>Field Key</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Unit</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Scale</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {schema.fields.map((field, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">{field.key}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={field.field_type}
                          size="small"
                          color={typeColors[field.field_type] || 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{field.unit || '—'}</TableCell>
                      <TableCell>{field.scale != null ? field.scale : '—'}</TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {field.description || '—'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Typography variant="body2" color="text.secondary">No fields defined</Typography>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  )
}
