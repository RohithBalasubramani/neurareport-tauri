import {
  Button,
  Chip,
  CircularProgress,
  MenuItem,
  Select,
  Stack,
  Typography,
} from '@mui/material'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'

export default function CompanyCardFooter({ t, type, fmt, selectedState, deleting, exporting, setOutputFormats, handleCardToggle, onDelete, onExport, onEditTemplate, lastEditChipLabel, lastEditChipColor, lastEditChipVariant, lastEditInfo }) {
  return (
    <Stack spacing={1} alignItems="flex-start">
      <Typography variant="subtitle1" sx={{ fontWeight: 600, lineHeight: 1.2 }} noWrap>
        {t.name}
      </Typography>
      <Stack
        direction="row"
        spacing={1}
        alignItems="center"
        sx={{ flexWrap: 'wrap', rowGap: 1 }}
      >
        <Chip size="small" label={type} variant="outlined" />
        <Select
          size="small"
          value={fmt}
          onChange={(e) => setOutputFormats((m) => ({ ...m, [t.id]: e.target.value }))}
          onClick={(event) => event.stopPropagation()}
          onMouseDown={(event) => event.stopPropagation()}
          sx={{ bgcolor: 'background.paper', minWidth: 132 }}
          aria-label="Output format"
        >
          <MenuItem value="auto">Auto ({type})</MenuItem>
          <MenuItem value="pdf">PDF</MenuItem>
          <MenuItem value="docx">Word (DOCX)</MenuItem>
          <MenuItem value="xlsx">Excel (XLSX)</MenuItem>
        </Select>
        <Button
          size="small"
          variant={selectedState ? 'contained' : 'outlined'}
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleCardToggle() }}
          onMouseDown={(e) => e.stopPropagation()}
        >
          {selectedState ? 'Selected' : 'Select'}
        </Button>
        <Button
          size="small"
          variant="outlined"
          sx={{ color: 'text.secondary' }}
          startIcon={deleting === t.id ? <CircularProgress size={16} color="inherit" /> : <DeleteOutlineIcon fontSize="small" />}
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(t) }}
          onMouseDown={(e) => e.stopPropagation()}
          disabled={deleting === t.id}
          aria-label={`Delete ${t.name || 'template'}`}
        >
          Delete
        </Button>
        {typeof onEditTemplate === 'function' && (
          <Button
            size="small"
            variant="outlined"
            startIcon={<EditOutlinedIcon fontSize="small" />}
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); onEditTemplate(t) }}
            onMouseDown={(e) => e.stopPropagation()}
            aria-label={`Edit ${t.name || t.id}`}
          >
            Edit
          </Button>
        )}
        <Button
          size="small"
          variant="outlined"
          startIcon={exporting === t.id ? <CircularProgress size={16} color="inherit" /> : <DownloadOutlinedIcon fontSize="small" />}
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onExport(t) }}
          onMouseDown={(e) => e.stopPropagation()}
          disabled={exporting === t.id}
          aria-label={`Export ${t.name || 'template'}`}
        >
          Export
        </Button>
        <Chip
          size="small"
          label={lastEditChipLabel}
          color={lastEditInfo ? lastEditChipColor : 'default'}
          variant={lastEditInfo ? lastEditChipVariant : 'outlined'}
          sx={{ mt: 0.5 }}
        />
      </Stack>
    </Stack>
  )
}
