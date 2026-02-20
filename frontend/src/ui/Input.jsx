/**
 * Input Component - Design System v4
 * Height: 40px, Border-radius: 8px
 * Background: Neutral 100, Border: Neutral 300, Focus: Primary 500
 * Placeholder: Neutral 500
 */
import { forwardRef } from 'react'
import { TextField, InputAdornment, alpha } from '@mui/material'
import { neutral, primary, palette } from '@/app/theme'

// FIGMA Input Constants (from searchInput specs)
const FIGMA_INPUT = {
  height: 40,             // 40px from Figma
  borderRadius: 8,        // 8px from Figma
  fontSize: 14,           // 14px from Figma
  iconSize: 20,           // 20px from Figma
  paddingHorizontal: 12,  // 12px from Figma
  paddingVertical: 8,     // 8px from Figma
}

const Input = forwardRef(function Input(
  {
    label,
    placeholder,
    value,
    onChange,
    onKeyDown,
    startIcon,
    endIcon,
    error,
    helperText,
    multiline = false,
    rows,
    maxRows,
    fullWidth = true,
    size = 'medium',
    disabled = false,
    autoFocus = false,
    type = 'text',
    ...props
  },
  ref
) {
  return (
    <TextField
      ref={ref}
      label={label}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      error={!!error}
      helperText={error || helperText}
      multiline={multiline}
      rows={rows}
      maxRows={maxRows}
      fullWidth={fullWidth}
      size={size}
      disabled={disabled}
      autoFocus={autoFocus}
      type={type}
      InputProps={{
        startAdornment: startIcon ? (
          <InputAdornment position="start" sx={{ '& svg': { fontSize: FIGMA_INPUT.iconSize } }}>
            {startIcon}
          </InputAdornment>
        ) : undefined,
        endAdornment: endIcon ? (
          <InputAdornment position="end" sx={{ '& svg': { fontSize: FIGMA_INPUT.iconSize } }}>
            {endIcon}
          </InputAdornment>
        ) : undefined,
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: `${FIGMA_INPUT.borderRadius}px`,
          minHeight: FIGMA_INPUT.height,
          fontSize: `${FIGMA_INPUT.fontSize}px`,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.6) : neutral[100],
          transition: 'all 150ms ease',
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[300],
          },
          '&:hover': {
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.7) : neutral[100],
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.2) : neutral[400],
            },
          },
          '&.Mui-focused': {
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.background.paper, 0.8) : neutral[100],
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: (theme) => theme.palette.mode === 'dark' ? theme.palette.text.secondary : primary[500],
              borderWidth: 1,
            },
          },
          '& input::placeholder': {
            color: neutral[500],
            opacity: 1,
          },
        },
        ...props.sx,
      }}
      {...props}
    />
  )
})

export default Input
