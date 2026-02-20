/**
 * Button Component - Desktop UI Overhaul
 * Height: 40px, Border-radius: 8px, Font: Inter Medium 14px (Label Medium)
 * Primary: #3B82F6 bg, #2563EB hover, Disabled: Neutral 200 bg / Neutral 400 text
 */
import { forwardRef } from 'react'
import { Button as MuiButton, CircularProgress } from '@mui/material'

// FIGMA Button Constants
const FIGMA_BUTTON = {
  height: 40,           // 40px from Figma
  heightSmall: 32,      // Compact size
  heightLarge: 44,      // Large size
  borderRadius: 8,      // 8px from Figma
  fontSize: 14,         // 14px from Figma
  fontWeight: 500,      // Medium from Figma
}

const Button = forwardRef(function Button(
  {
    children,
    variant = 'contained',
    size = 'medium',
    loading = false,
    disabled = false,
    startIcon,
    endIcon,
    fullWidth = false,
    color = 'primary',
    ...props
  },
  ref
) {
  const getHeight = () => {
    switch (size) {
      case 'small': return FIGMA_BUTTON.heightSmall
      case 'large': return FIGMA_BUTTON.heightLarge
      default: return FIGMA_BUTTON.height
    }
  }

  return (
    <MuiButton
      ref={ref}
      variant={variant}
      size={size}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={16} color="inherit" /> : startIcon}
      endIcon={endIcon}
      fullWidth={fullWidth}
      color={color}
      sx={{
        // FIGMA Button Specs
        textTransform: 'none',
        fontWeight: FIGMA_BUTTON.fontWeight,
        fontSize: `${FIGMA_BUTTON.fontSize}px`,
        lineHeight: '16px',
        borderRadius: `${FIGMA_BUTTON.borderRadius}px`,
        minHeight: getHeight(),
        px: size === 'small' ? 1.5 : 2,
        py: size === 'small' ? 0.75 : 1,
        // No box-shadow on buttons (clean Figma style)
        boxShadow: 'none',
        '&:hover': {
          boxShadow: 'none',
        },
        '&.Mui-disabled': {
          bgcolor: variant === 'contained' ? 'action.disabledBackground' : 'transparent',
        },
        ...props.sx,
      }}
      {...props}
    >
      {children}
    </MuiButton>
  )
})

export default Button
