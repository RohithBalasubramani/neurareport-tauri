/**
 * Brand Kit create/edit dialog for the Design page.
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Collapse,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material'
import { ColorSwatch } from './DesignStyledComponents'
import BrandKitDialogAdvanced from './BrandKitDialogAdvanced'

export default function BrandKitDialog({
  open,
  onClose,
  mode,
  kitForm,
  setKitForm,
  kitFormExpanded,
  setKitFormExpanded,
  onSave,
  fonts,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {mode === 'edit' ? 'Edit Brand Kit' : 'Create Brand Kit'}
      </DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Name"
          value={kitForm.name}
          onChange={(e) => setKitForm({ ...kitForm, name: e.target.value })}
          sx={{ mt: 2, mb: 2 }}
          required
        />
        <TextField
          fullWidth
          label="Description"
          value={kitForm.description}
          onChange={(e) => setKitForm({ ...kitForm, description: e.target.value })}
          sx={{ mb: 2 }}
          multiline
          rows={2}
          placeholder="What is this brand kit for?"
        />
        <Typography variant="subtitle2" sx={{ mb: 1 }}>Colors</Typography>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={4}>
            <TextField fullWidth type="color" label="Primary" value={kitForm.primary_color}
              onChange={(e) => setKitForm({ ...kitForm, primary_color: e.target.value })} size="small" />
          </Grid>
          <Grid item xs={4}>
            <TextField fullWidth type="color" label="Secondary" value={kitForm.secondary_color}
              onChange={(e) => setKitForm({ ...kitForm, secondary_color: e.target.value })} size="small" />
          </Grid>
          <Grid item xs={4}>
            <TextField fullWidth type="color" label="Accent" value={kitForm.accent_color}
              onChange={(e) => setKitForm({ ...kitForm, accent_color: e.target.value })} size="small" />
          </Grid>
        </Grid>

        <Box
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer', mb: 1 }}
          onClick={() => setKitFormExpanded(!kitFormExpanded)}
        >
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            Advanced options
          </Typography>
          {kitFormExpanded ? <ExpandLessIcon fontSize="small" sx={{ ml: 0.5 }} /> : <ExpandMoreIcon fontSize="small" sx={{ ml: 0.5 }} />}
        </Box>

        <Collapse in={kitFormExpanded}>
          <BrandKitDialogAdvanced kitForm={kitForm} setKitForm={setKitForm} fonts={fonts} />
        </Collapse>

        <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
          {[kitForm.primary_color, kitForm.secondary_color, kitForm.accent_color, kitForm.text_color, kitForm.background_color]
            .filter(Boolean)
            .map((c, i) => <ColorSwatch key={i} color={c} size={32} />)}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onSave} disabled={!kitForm.name.trim()}>
          {mode === 'edit' ? 'Save' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
