/**
 * Palette Generator section of the Color Tools tab.
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  Paper,
  Grid,
  MenuItem,
  InputAdornment,
  useTheme,
  alpha,
} from '@mui/material'
import { ColorSwatch, ActionButton, COLOR_SCHEMES } from './DesignStyledComponents'

export default function PaletteGenerator({
  loading,
  baseColor,
  setBaseColor,
  colorScheme,
  setColorScheme,
  generatedPalette,
  handleGeneratePalette,
  handleCopyColor,
}) {
  const theme = useTheme()

  return (
    <>
      <Grid item xs={12}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
          Palette Generator
        </Typography>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3 }}>
          <TextField
            fullWidth
            label="Base Color"
            type="color"
            value={baseColor}
            onChange={(e) => setBaseColor(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                    {baseColor}
                  </Typography>
                </InputAdornment>
              ),
            }}
          />
          <TextField
            fullWidth
            select
            label="Harmony"
            value={colorScheme}
            onChange={(e) => setColorScheme(e.target.value)}
            sx={{ mb: 2 }}
            SelectProps={{ native: false }}
          >
            {COLOR_SCHEMES.map((s) => (
              <MenuItem key={s.value} value={s.value}>
                <Box>
                  <Typography variant="body2">{s.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {s.desc}
                  </Typography>
                </Box>
              </MenuItem>
            ))}
          </TextField>
          <ActionButton
            variant="contained"
            fullWidth
            onClick={handleGeneratePalette}
            disabled={loading}
            data-testid="generate-palette-button"
          >
            Generate Palette
          </ActionButton>
        </Paper>
      </Grid>
      <Grid item xs={12} md={8}>
        {generatedPalette ? (
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2 }}>
              {colorScheme.charAt(0).toUpperCase() + colorScheme.slice(1)} palette from{' '}
              <code>{generatedPalette.base_color}</code>
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {generatedPalette.colors?.map((color, index) => {
                const hex = typeof color === 'string' ? color : color.hex
                const name = typeof color === 'string' ? `Color ${index + 1}` : color.name
                return (
                  <Box key={index} sx={{ textAlign: 'center' }}>
                    <ColorSwatch
                      color={hex}
                      size={60}
                      onClick={() => handleCopyColor(hex)}
                      data-testid={`generated-color-${index}`}
                    />
                    <Typography variant="caption" display="block" sx={{ fontFamily: 'monospace', mt: 0.5 }}>
                      {hex}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {name}
                    </Typography>
                  </Box>
                )
              })}
            </Box>
          </Paper>
        ) : (
          <Paper
            sx={{
              height: 200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px dashed ${alpha(theme.palette.divider, 0.3)}`,
              backgroundColor: 'transparent',
            }}
            elevation={0}
          >
            <Typography color="text.secondary">
              Choose a base color and harmony type, then generate
            </Typography>
          </Paper>
        )}
      </Grid>
    </>
  )
}
