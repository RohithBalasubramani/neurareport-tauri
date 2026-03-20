/**
 * Color Tools tab content for the Design page.
 */
import React from 'react'
import { Typography, Grid, Divider } from '@mui/material'
import PaletteGenerator from './PaletteGenerator'
import ContrastChecker from './ContrastChecker'
import AccessibleColorFinder from './AccessibleColorFinder'

export default function ColorToolsTab({
  loading,
  baseColor,
  setBaseColor,
  colorScheme,
  setColorScheme,
  generatedPalette,
  contrastFg,
  setContrastFg,
  contrastBg,
  setContrastBg,
  contrastResult,
  a11yBg,
  setA11yBg,
  a11ySuggestions,
  handleGeneratePalette,
  handleCheckContrast,
  handleSuggestA11y,
  handleCopyColor,
}) {
  return (
    <Grid container spacing={3}>
      <PaletteGenerator
        loading={loading}
        baseColor={baseColor}
        setBaseColor={setBaseColor}
        colorScheme={colorScheme}
        setColorScheme={setColorScheme}
        generatedPalette={generatedPalette}
        handleGeneratePalette={handleGeneratePalette}
        handleCopyColor={handleCopyColor}
      />

      <Grid item xs={12}>
        <Divider sx={{ my: 1 }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mt: 2, mb: 2 }}>
          WCAG Contrast Checker
        </Typography>
      </Grid>
      <ContrastChecker
        loading={loading}
        contrastFg={contrastFg}
        setContrastFg={setContrastFg}
        contrastBg={contrastBg}
        setContrastBg={setContrastBg}
        contrastResult={contrastResult}
        handleCheckContrast={handleCheckContrast}
      />

      <Grid item xs={12}>
        <Divider sx={{ my: 1 }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mt: 2, mb: 2 }}>
          Accessible Color Finder
        </Typography>
      </Grid>
      <AccessibleColorFinder
        loading={loading}
        a11yBg={a11yBg}
        setA11yBg={setA11yBg}
        a11ySuggestions={a11ySuggestions}
        handleSuggestA11y={handleSuggestA11y}
        handleCopyColor={handleCopyColor}
      />
    </Grid>
  )
}
