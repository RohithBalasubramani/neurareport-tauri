import { useState } from 'react'
import {
  Box,
  Stack,
  Typography,
  Button,
  Paper,
  Chip,
  Collapse,
  alpha,
  Autocomplete,
  TextField,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import { neutral } from '@/app/theme'
import MappingProcessingState from './MappingProcessingState'
import MappingDetailTable, { SPECIAL_VALUES, humanizeToken, humanizeColumn } from './MappingDetailTable'

export default function MappingReviewPanel({
  mappingData, catalog, schemaInfo, onApprove, onSkip, onQueue, approving,
}) {
  const [localMapping, setLocalMapping] = useState(() => ({ ...(mappingData || {}) }))
  const [showDetails, setShowDetails] = useState(false)
  const [editingToken, setEditingToken] = useState(null)

  const catalogOptions = (catalog || []).map((c) => c)

  const handleChange = (token, newValue) => {
    setLocalMapping((prev) => ({ ...prev, [token]: newValue || '' }))
  }

  if (approving) {
    return <MappingProcessingState onQueue={onQueue} />
  }

  const tokens = Object.keys(localMapping)
  const mapped = tokens.filter((t) => !SPECIAL_VALUES.has(localMapping[t]) && localMapping[t])
  const unresolved = tokens.filter((t) => SPECIAL_VALUES.has(localMapping[t]) || !localMapping[t])

  const tables = schemaInfo
    ? [schemaInfo['child table'], schemaInfo['parent table']].filter(Boolean).join(' and ')
    : null

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2, mx: 2, mb: 2, borderRadius: 1,
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.divider, 0.3),
        bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
      }}
    >
      <Stack spacing={1.5}>
        <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
          {tables && <>I found your data in the <strong>{tables}</strong> table{tables.includes(' and ') ? 's' : ''}. </>}
          {mapped.length > 0 && (
            <>I was able to connect <strong>{mapped.length} of {tokens.length}</strong> template fields to your database. </>
          )}
          {unresolved.length > 0 && (
            <>{mapped.length > 0 ? 'However, ' : ''}<strong>{unresolved.length} field{unresolved.length > 1 ? 's' : ''}</strong> still need{unresolved.length === 1 ? 's' : ''} to be configured.</>
          )}
          {unresolved.length === 0 && mapped.length > 0 && <>All fields are mapped and ready to go!</>}
        </Typography>

        {mapped.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 0.5, display: 'block' }}>
              Connected fields:
            </Typography>
            <Stack direction="row" flexWrap="wrap" gap={0.5}>
              {mapped.map((token) => (
                <Chip key={token} label={`${humanizeToken(token)} → ${humanizeColumn(localMapping[token]) || localMapping[token]}`} size="small" variant="outlined" color="success" sx={{ fontSize: '0.7rem' }} />
              ))}
            </Stack>
          </Box>
        )}

        {unresolved.length > 0 && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 0.5, display: 'block' }}>
              Needs your input:
            </Typography>
            <Stack spacing={0.5}>
              {unresolved.map((token) => (
                <Stack key={token} direction="row" alignItems="center" spacing={1}>
                  <Typography variant="body2" sx={{ minWidth: 120 }}>{humanizeToken(token)}</Typography>
                  {editingToken === token ? (
                    <Autocomplete freeSolo size="small" options={catalogOptions} value={localMapping[token] || ''} onChange={(_e, newVal) => { handleChange(token, newVal); setEditingToken(null) }} onBlur={() => setEditingToken(null)} renderInput={(params) => (<TextField {...params} variant="outlined" autoFocus size="small" placeholder="Pick a column..." sx={{ '& .MuiInputBase-root': { fontSize: '0.8rem', py: 0 } }} />)} sx={{ flex: 1, minWidth: 150 }} />
                  ) : (
                    <Chip label="Select column..." size="small" color="warning" variant="outlined" onClick={() => setEditingToken(token)} sx={{ cursor: 'pointer', fontSize: '0.75rem' }} />
                  )}
                </Stack>
              ))}
            </Stack>
          </Box>
        )}

        {mapped.length > 0 && (
          <Button size="small" variant="text" onClick={() => setShowDetails(!showDetails)} endIcon={showDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />} sx={{ alignSelf: 'flex-start', textTransform: 'none', fontSize: '0.75rem' }}>
            {showDetails ? 'Hide all mappings' : 'View all mappings'}
          </Button>
        )}

        <Collapse in={showDetails}>
          <MappingDetailTable tokens={tokens} localMapping={localMapping} catalogOptions={catalogOptions} editingToken={editingToken} onEditToken={setEditingToken} onChangeMapping={handleChange} />
        </Collapse>

        <Typography variant="body2" color="text.secondary" fontSize="0.8rem">
          Looks good? Approve to finalize, or tell me what you'd like to change.
        </Typography>

        <Stack direction="row" spacing={1.5}>
          <Button variant="contained" onClick={() => onApprove(localMapping)} disabled={approving} startIcon={<CheckCircleIcon />} sx={{ textTransform: 'none' }}>
            Looks Good, Approve
          </Button>
          <Button variant="outlined" onClick={() => onApprove(mappingData)} disabled={approving} sx={{ textTransform: 'none' }}>
            You do this
          </Button>
        </Stack>
      </Stack>
    </Paper>
  )
}
