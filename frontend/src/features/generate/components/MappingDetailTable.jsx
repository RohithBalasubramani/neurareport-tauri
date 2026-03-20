import {
  Box,
  Chip,
  Typography,
  Autocomplete,
  TextField,
  Table,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from '@mui/material'

const SPECIAL_VALUES = new Set(['UNRESOLVED', 'INPUT_SAMPLE', 'LATER_SELECTED'])

function humanizeToken(token) {
  return token.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function humanizeColumn(col) {
  if (!col || SPECIAL_VALUES.has(col)) return null
  const parts = col.split('.')
  if (parts.length === 2) {
    const table = parts[0].replace(/_/g, ' ')
    const column = parts[1].replace(/_/g, ' ')
    return `${column} from ${table}`
  }
  return col.replace(/_/g, ' ')
}

export { SPECIAL_VALUES, humanizeToken, humanizeColumn }

export default function MappingDetailTable({
  tokens,
  localMapping,
  catalogOptions,
  editingToken,
  onEditToken,
  onChangeMapping,
}) {
  return (
    <Box sx={{ maxHeight: 250, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 0.5 }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 600, bgcolor: 'background.paper', width: '40%', py: 0.5 }}>Field</TableCell>
            <TableCell sx={{ fontWeight: 600, bgcolor: 'background.paper', py: 0.5 }}>Source</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {tokens.map((token) => {
            const value = localMapping[token]
            const isSpecial = SPECIAL_VALUES.has(value) || !value
            return (
              <TableRow key={token} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
                <TableCell sx={{ py: 0.5 }}>
                  <Typography variant="body2" fontSize="0.8rem">{humanizeToken(token)}</Typography>
                </TableCell>
                <TableCell sx={{ py: 0.5 }}>
                  {editingToken === token ? (
                    <Autocomplete
                      freeSolo
                      size="small"
                      options={catalogOptions}
                      value={value || ''}
                      onChange={(_e, newVal) => { onChangeMapping(token, newVal); onEditToken(null) }}
                      onBlur={() => onEditToken(null)}
                      renderInput={(params) => (
                        <TextField {...params} variant="outlined" autoFocus size="small"
                          sx={{ '& .MuiInputBase-root': { fontSize: '0.8rem', py: 0 } }}
                        />
                      )}
                      sx={{ minWidth: 150 }}
                    />
                  ) : (
                    <Chip
                      label={isSpecial ? 'Not set' : (humanizeColumn(value) || value)}
                      size="small"
                      color={isSpecial ? 'warning' : 'default'}
                      variant="outlined"
                      onClick={() => onEditToken(token)}
                      sx={{ cursor: 'pointer', fontSize: '0.7rem' }}
                    />
                  )}
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </Box>
  )
}
