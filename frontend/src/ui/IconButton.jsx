import { forwardRef } from 'react'
import { IconButton as MuiIconButton, Tooltip, alpha } from '@mui/material'
import { neutral, palette } from '@/app/theme'

const IconButton = forwardRef(function IconButton(
  {
    children,
    tooltip,
    size = 'medium',
    color = 'default',
    disabled = false,
    'aria-label': ariaLabel,
    ...props
  },
  ref
) {
  const button = (
    <MuiIconButton
      ref={ref}
      size={size}
      color={color}
      disabled={disabled}
      aria-label={ariaLabel || tooltip}
      sx={{
        borderRadius: 1,  // Figma spec: 8px
        transition: 'all 150ms ease',
        '&:hover': {
          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        },
        ...props.sx,
      }}
      {...props}
    >
      {children}
    </MuiIconButton>
  )

  if (tooltip && !disabled) {
    return (
      <Tooltip title={tooltip} arrow>
        {button}
      </Tooltip>
    )
  }

  return button
})

export default IconButton
