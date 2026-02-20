/**
 * Disabled Tooltip Component
 * Wraps buttons/actions to explain WHY they are disabled
 *
 * UX Laws Addressed:
 * - Make system state always visible
 * - Prevent errors before handling them
 * - Never leave the user guessing
 */
import { forwardRef } from 'react'
import { Tooltip, Box, useTheme, alpha } from '@mui/material'
import { InfoOutlined as InfoIcon } from '@mui/icons-material'
import { neutral } from '@/app/theme'

/**
 * DisabledTooltip - Wrapper that explains why an action is unavailable
 *
 * @param {Object} props
 * @param {boolean} props.disabled - Whether the wrapped element should be disabled
 * @param {string} props.reason - Human-readable reason why it's disabled
 * @param {string} props.hint - Optional hint on how to enable it
 * @param {React.ReactNode} props.children - The element to wrap
 * @param {string} props.placement - Tooltip placement (default: 'top')
 * @param {boolean} props.showIcon - Show info icon when disabled (default: false)
 */
const DisabledTooltip = forwardRef(function DisabledTooltip(
  {
    disabled = false,
    reason,
    hint,
    children,
    placement = 'top',
    showIcon = false,
    ...props
  },
  ref
) {
  const theme = useTheme()

  // If not disabled, just render children
  if (!disabled) {
    return children
  }

  // Build tooltip content
  const tooltipContent = (
    <Box sx={{ maxWidth: 240 }}>
      <Box sx={{ fontWeight: 500, mb: hint ? 0.5 : 0 }}>
        {reason || 'This action is currently unavailable'}
      </Box>
      {hint && (
        <Box sx={{
          fontSize: '14px',
          opacity: 0.85,
          color: alpha(theme.palette.common.white, 0.85),
        }}>
          {hint}
        </Box>
      )}
    </Box>
  )

  return (
    <Tooltip
      ref={ref}
      title={tooltipContent}
      placement={placement}
      arrow
      enterDelay={200}
      leaveDelay={0}
      componentsProps={{
        tooltip: {
          sx: {
            bgcolor: alpha(neutral[900], 0.95),
            backdropFilter: 'blur(8px)',
            borderRadius: '8px',
            px: 1.5,
            py: 1,
            boxShadow: `0 4px 20px ${alpha(theme.palette.common.black, 0.3)}`,
            '& .MuiTooltip-arrow': {
              color: alpha(neutral[900], 0.95),
            },
          },
        },
      }}
      {...props}
    >
      {/* Wrap in span to allow tooltip on disabled elements */}
      <Box
        component="span"
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 0.5,
          cursor: 'not-allowed',
        }}
      >
        {/* Clone children with pointer-events: none so tooltip works */}
        <Box
          component="span"
          sx={{
            display: 'inline-flex',
            pointerEvents: 'none',
          }}
        >
          {children}
        </Box>
        {showIcon && (
          <InfoIcon
            sx={{
              fontSize: 14,
              color: theme.palette.text.disabled,
              ml: 0.25,
            }}
          />
        )}
      </Box>
    </Tooltip>
  )
})

export default DisabledTooltip

/**
 * Common disabled reasons - use these for consistency
 */
export const DisabledReasons = {
  // Input requirements
  FIELD_REQUIRED: 'Please fill in the required field',
  MIN_LENGTH: (min) => `Please enter at least ${min} characters`,
  MAX_LENGTH: (max) => `Maximum ${max} characters allowed`,
  INVALID_FORMAT: 'Please enter a valid format',

  // Selection requirements
  SELECT_ITEM: 'Please select an item first',
  SELECT_CONNECTION: 'Please select a database connection first',
  SELECT_TEMPLATE: 'Please select a template first',
  SELECT_DOCUMENT: 'Please add at least one document',

  // State requirements
  LOADING: 'Please wait for the current operation to complete',
  PROCESSING: 'Processing in progress...',
  SAVING: 'Saving changes...',

  // Permission/access
  NO_PERMISSION: 'You do not have permission for this action',
  FEATURE_UNAVAILABLE: 'This feature is not available',

  // Prerequisite actions
  COMPLETE_PREVIOUS: 'Please complete the previous step first',
  FIX_ERRORS: 'Please fix the errors above first',

  // Connection/network
  OFFLINE: 'No internet connection',
  SERVER_UNAVAILABLE: 'Server is temporarily unavailable',
}

/**
 * Helper to get hint text for common reasons
 */
export const DisabledHints = {
  FIELD_REQUIRED: 'Enter a value to continue',
  SELECT_CONNECTION: 'Use the dropdown above to select',
  LOADING: 'This usually takes a few seconds',
  OFFLINE: 'Check your internet connection',
  FIX_ERRORS: 'Scroll up to see the issues',
}
