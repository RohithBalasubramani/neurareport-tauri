/**
 * Theme create dialog for the Design page.
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
  MenuItem,
} from '@mui/material'
import {
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
} from '@mui/icons-material'

export default function ThemeDialog({
  open,
  onClose,
  themeForm,
  setThemeForm,
  onSave,
}) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>Create Theme</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          fullWidth
          label="Name"
          value={themeForm.name}
          onChange={(e) => setThemeForm({ ...themeForm, name: e.target.value })}
          sx={{ mt: 2, mb: 2 }}
          required
        />
        <TextField
          fullWidth
          label="Description"
          value={themeForm.description}
          onChange={(e) => setThemeForm({ ...themeForm, description: e.target.value })}
          sx={{ mb: 2 }}
          placeholder="Describe this theme..."
        />
        <TextField
          fullWidth
          select
          label="Mode"
          value={themeForm.mode}
          onChange={(e) => setThemeForm({ ...themeForm, mode: e.target.value })}
          sx={{ mb: 2 }}
          SelectProps={{ native: false }}
        >
          <MenuItem value="light">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LightModeIcon fontSize="small" /> Light
            </Box>
          </MenuItem>
          <MenuItem value="dark">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <DarkModeIcon fontSize="small" /> Dark
            </Box>
          </MenuItem>
        </TextField>

        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          Colors
        </Typography>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={4}>
            <TextField
              fullWidth
              type="color"
              label="Primary"
              value={themeForm.primary}
              onChange={(e) => setThemeForm({ ...themeForm, primary: e.target.value })}
              size="small"
            />
          </Grid>
          <Grid item xs={4}>
            <TextField
              fullWidth
              type="color"
              label="Secondary"
              value={themeForm.secondary}
              onChange={(e) => setThemeForm({ ...themeForm, secondary: e.target.value })}
              size="small"
            />
          </Grid>
          <Grid item xs={4}>
            <TextField
              fullWidth
              type="color"
              label="Background"
              value={themeForm.background}
              onChange={(e) => setThemeForm({ ...themeForm, background: e.target.value })}
              size="small"
            />
          </Grid>
        </Grid>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <TextField
              fullWidth
              type="color"
              label="Surface"
              value={themeForm.surface}
              onChange={(e) => setThemeForm({ ...themeForm, surface: e.target.value })}
              size="small"
            />
          </Grid>
          <Grid item xs={6}>
            <TextField
              fullWidth
              type="color"
              label="Text"
              value={themeForm.text}
              onChange={(e) => setThemeForm({ ...themeForm, text: e.target.value })}
              size="small"
            />
          </Grid>
        </Grid>

        {/* Preview */}
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            backgroundColor: themeForm.background,
            border: '1px solid rgba(0,0,0,0.1)',
          }}
        >
          <Typography variant="body2" sx={{ color: themeForm.text, fontWeight: 600, mb: 0.5 }}>
            Theme Preview
          </Typography>
          <Box sx={{ backgroundColor: themeForm.surface, p: 1.5, borderRadius: 1, mb: 1 }}>
            <Typography variant="caption" sx={{ color: themeForm.text }}>
              Surface area with text
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Box sx={{ width: 24, height: 24, borderRadius: '50%', backgroundColor: themeForm.primary }} />
            <Box sx={{ width: 24, height: 24, borderRadius: '50%', backgroundColor: themeForm.secondary }} />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onSave} disabled={!themeForm.name.trim()}>
          Create
        </Button>
      </DialogActions>
    </Dialog>
  )
}
