/**
 * Shared styled components and constants for the Design feature.
 */
import { Box, Card, Paper, Typography, Button, styled, alpha } from '@mui/material'
import { neutral } from '@/app/theme'

export const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

export const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

export const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

export const BrandKitCard = styled(Card)(({ theme, isDefault }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  border: isDefault
    ? `2px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}`
    : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 24px ${alpha(theme.palette.text.primary, 0.15)}`,
  },
}))

export const ColorSwatch = styled(Box)(({ color: bgColor, size = 40 }) => ({
  width: size,
  height: size,
  borderRadius: 8,
  backgroundColor: bgColor,
  border: '2px solid rgba(0,0,0,0.1)',
  cursor: 'pointer',
  transition: 'transform 0.2s',
  flexShrink: 0,
  '&:hover': {
    transform: 'scale(1.1)',
  },
}))

export const ThemeCard = styled(Paper)(({ theme, isActive }) => ({
  padding: theme.spacing(2),
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  border: isActive
    ? `2px solid ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}`
    : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    backgroundColor:
      theme.palette.mode === 'dark'
        ? alpha(theme.palette.text.primary, 0.05)
        : neutral[50],
  },
}))

export const ActionButton = styled(Button)(() => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

export const ContrastBar = styled(Box)(({ ratio }) => {
  const pct = Math.min((ratio / 21) * 100, 100)
  const hue = ratio >= 7 ? 120 : ratio >= 4.5 ? 60 : 0
  return {
    height: 8,
    borderRadius: 4,
    background: `linear-gradient(90deg, hsl(${hue},70%,50%) ${pct}%, transparent ${pct}%)`,
    backgroundColor: 'rgba(0,0,0,0.08)',
    width: '100%',
  }
})

export const FontSample = styled(Typography)(({ fontFamily }) => ({
  fontFamily: `"${fontFamily}", sans-serif`,
  lineHeight: 1.4,
}))

// =============================================================================
// CONSTANTS
// =============================================================================

export const COLOR_SCHEMES = [
  { name: 'Complementary', value: 'complementary', desc: 'Opposite on the color wheel' },
  { name: 'Analogous', value: 'analogous', desc: 'Adjacent colors' },
  { name: 'Triadic', value: 'triadic', desc: 'Three equally spaced' },
  { name: 'Split-Comp.', value: 'split-complementary', desc: 'Complementary with neighbors' },
  { name: 'Tetradic', value: 'tetradic', desc: 'Four colors in rectangle' },
]

export const EMPTY_KIT_FORM = {
  name: '',
  description: '',
  primary_color: '#1976d2',
  secondary_color: '#dc004e',
  accent_color: '#ff9800',
  text_color: '#333333',
  background_color: '#ffffff',
  font_family: 'Inter',
  heading_font: '',
  body_font: '',
}

export const EMPTY_THEME_FORM = {
  name: '',
  description: '',
  mode: 'light',
  primary: '#1976d2',
  secondary: '#dc004e',
  background: '#ffffff',
  surface: '#f5f5f5',
  text: '#333333',
}
