import { Box, Typography, MenuItem } from '@mui/material'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'

export function SelectFieldRenderValue({ selectedOption, ghostLabel }) {
  const IconComponent = selectedOption?.icon
  const accentColor = selectedOption?.accent
  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      <Box sx={{ display: 'flex', flexDirection: 'row', gap: 0.6, alignItems: 'center', minWidth: 0, ml: 0.2, justifyContent: 'center' }}>
        {IconComponent ? (
          <Box
            sx={(theme) => ({
              width: 20,
              height: 20,
              borderRadius: 6,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
              backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.12),
              boxShadow: `0 4px 12px ${alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.18)}`,
              flexShrink: 0,
              ml: 0.1,
            })}
          >
            <IconComponent fontSize="small" />
          </Box>
        ) : null}
        <Box sx={{
          flex: 1,
          minWidth: 0,
          overflow: 'hidden',
        }}>
          <Typography
            variant="subtitle2"
            component="span"
            sx={(theme) => ({
              fontWeight: theme.typography.fontWeightBold,
              color: theme.palette.text.primary,
              lineHeight: 1.2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              flexShrink: 0,
              minWidth: 0,
              textAlign: 'center',
            })}
          >
            {selectedOption ? selectedOption.label : 'Choose a database'}
          </Typography>
        </Box>
      </Box>
      <Box
        aria-hidden
        sx={{
          position: 'absolute',
          inset: 0,
          opacity: 0,
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
        }}
      >
        {ghostLabel}
      </Box>
    </Box>
  )
}

export function SelectFieldMenuItem({ opt }) {
  const IconComponent = opt.icon
  const accentColor = opt.accent
  return (
    <MenuItem
      key={opt.value}
      value={opt.value}
      sx={(theme) => ({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 1.1,
        py: 1.15,
        px: 1.75,
        borderRadius: 1,
        transition: 'background-color 140ms cubic-bezier(0.22, 1, 0.36, 1), transform 140ms cubic-bezier(0.22, 1, 0.36, 1)',
        '&:hover': {
          backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.08),
          transform: 'translateX(4px)',
        },
        '&.Mui-selected': {
          backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.12),
          color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
          '&:hover': {
            backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.16),
          },
        },
      })}
    >
      {IconComponent ? (
        <Box
          sx={(theme) => ({
            width: 20,
            height: 20,
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
            backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.1),
            flexShrink: 0,
            ml: 0.15,
          })}
        >
          <IconComponent fontSize="small" />
        </Box>
      ) : null}
      <Typography
        variant="subtitle2"
        component="span"
        sx={(theme) => ({
          fontWeight: theme.typography.fontWeightBold,
          lineHeight: 1.2,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          flexShrink: 0,
          minWidth: 0,
          flex: 1,
          textAlign: 'center',
        })}
      >
        {opt.label}
      </Typography>
    </MenuItem>
  )
}
