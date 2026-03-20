/**
 * Advanced options section of the Brand Kit dialog (text/bg colors, typography).
 */
import React from 'react'
import { Typography, TextField, Grid, MenuItem } from '@mui/material'

export default function BrandKitDialogAdvanced({ kitForm, setKitForm, fonts }) {
  return (
    <>
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            type="color"
            label="Text Color"
            value={kitForm.text_color}
            onChange={(e) => setKitForm({ ...kitForm, text_color: e.target.value })}
            size="small"
          />
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            type="color"
            label="Background"
            value={kitForm.background_color}
            onChange={(e) => setKitForm({ ...kitForm, background_color: e.target.value })}
            size="small"
          />
        </Grid>
      </Grid>

      <Typography variant="subtitle2" sx={{ mb: 1 }}>
        Typography
      </Typography>
      <TextField
        fullWidth
        select
        label="Primary Font"
        value={kitForm.font_family}
        onChange={(e) => setKitForm({ ...kitForm, font_family: e.target.value })}
        sx={{ mb: 2 }}
        size="small"
        SelectProps={{ native: false }}
      >
        {fonts.map((f) => (
          <MenuItem key={f.name} value={f.name}>
            {f.name}
            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
              ({f.category})
            </Typography>
          </MenuItem>
        ))}
        {fonts.length === 0 && (
          <MenuItem value={kitForm.font_family}>{kitForm.font_family}</MenuItem>
        )}
      </TextField>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <TextField
            fullWidth
            select
            label="Heading Font"
            value={kitForm.heading_font}
            onChange={(e) => setKitForm({ ...kitForm, heading_font: e.target.value })}
            size="small"
            SelectProps={{ native: false }}
          >
            <MenuItem value="">
              <em>Same as primary</em>
            </MenuItem>
            {fonts.map((f) => (
              <MenuItem key={f.name} value={f.name}>
                {f.name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={6}>
          <TextField
            fullWidth
            select
            label="Body Font"
            value={kitForm.body_font}
            onChange={(e) => setKitForm({ ...kitForm, body_font: e.target.value })}
            size="small"
            SelectProps={{ native: false }}
          >
            <MenuItem value="">
              <em>Same as primary</em>
            </MenuItem>
            {fonts.map((f) => (
              <MenuItem key={f.name} value={f.name}>
                {f.name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>
    </>
  )
}
