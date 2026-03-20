import {
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  Switch,
  FormControlLabel,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { status } from '@/app/theme'

export default function FormPreviewDialog({ open, onClose, formTitle, fields }) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>{formTitle}</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2}>
          {fields.map((field) => (
            <Box key={field.id}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                {field.label}
                {field.required && <span style={{ color: status.destructive }}> *</span>}
              </Typography>
              {field.description && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  {field.description}
                </Typography>
              )}
              {field.type === 'textarea' ? (
                <TextField fullWidth multiline rows={3} size="small" placeholder={field.placeholder} />
              ) : field.type === 'select' ? (
                <FormControl fullWidth size="small">
                  <Select defaultValue="">
                    <MenuItem value="">Select...</MenuItem>
                    {(field.options || []).map((opt, i) => (
                      <MenuItem key={i} value={opt}>{opt}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              ) : field.type === 'checkbox' ? (
                <FormControlLabel control={<Switch />} label={field.options?.[0] || 'Enable'} />
              ) : (
                <TextField fullWidth size="small" type={field.type} placeholder={field.placeholder} />
              )}
            </Box>
          ))}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button variant="contained">Submit</Button>
      </DialogActions>
    </Dialog>
  )
}
