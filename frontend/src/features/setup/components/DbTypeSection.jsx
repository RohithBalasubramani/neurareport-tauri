import {
  Box, Typography, FormControl, FormHelperText,
  ToggleButton, ToggleButtonGroup,
} from '@mui/material'
import { alpha } from '@mui/material/styles'
import { Controller } from 'react-hook-form'
import { neutral } from '@/app/theme'
import { DB_TYPE_OPTIONS } from '../constants/connectDB'

const dbTypeToggleGroupSx = (theme) => ({
  marginTop: theme.spacing(1),
  display: 'grid',
  width: '100%',
  gap: theme.spacing(1),
  gridTemplateColumns: 'repeat(auto-fit, minmax(175px, 1fr))',
  [theme.breakpoints.down('sm')]: {
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
  },
  '& .MuiToggleButtonGroup-grouped': {
    margin: 0,
    border: 'none',
  },
})

const buildDbTypeButtonSx = (accent) => (theme) => {
  const accentColor = accent || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
  return {
    justifyContent: 'center',
    alignItems: 'center',
    textTransform: 'none',
    borderRadius: 8,
    border: `1px solid ${alpha(theme.palette.divider, 0.75)}`,
    padding: theme.spacing(1.1, 1.5),
    minHeight: 68,
    display: 'flex',
    flexDirection: 'row',
    gap: theme.spacing(1.1),
    minWidth: 0,
    backgroundColor: alpha(theme.palette.background.paper, 0.96),
    color: theme.palette.text.primary,
    transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1), background-color 160ms cubic-bezier(0.22, 1, 0.36, 1), transform 160ms cubic-bezier(0.22, 1, 0.36, 1)',
    '& .db-type-icon': {
      width: 24,
      height: 24,
      borderRadius: 7,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: accentColor,
      backgroundColor: alpha(accentColor, 0.14),
      boxShadow: `0 4px 14px ${alpha(accentColor, 0.24)}`,
      flexShrink: 0,
    },
    '& .db-type-meta': {
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing(0.25),
      alignItems: 'center',
      textAlign: 'center',
      minWidth: 0,
    },
    '&:hover': {
      borderColor: accentColor,
      backgroundColor: alpha(accentColor, 0.08),
    },
    '&:focus-visible': {
      outline: `2px solid ${alpha(accentColor, 0.5)}`,
      outlineOffset: 2,
    },
    '&.Mui-selected': {
      borderColor: accentColor,
      backgroundColor: alpha(accentColor, 0.14),
      boxShadow: `0 18px 36px ${alpha(accentColor, 0.28)}`,
      transform: 'translateY(-1px)',
    },
    '&.Mui-selected .db-type-icon': {
      backgroundColor: alpha(accentColor, 0.22),
    },
  }
}

export default function DbTypeSection({ control, errors }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography
        variant="overline"
        id="dbtype-label"
        sx={(theme) => ({
          display: 'block',
          fontWeight: theme.typography.fontWeightBold,
          letterSpacing: '0.12em',
          color: alpha(theme.palette.text.secondary, 0.75),
        })}
      >
        Database Type
      </Typography>
      <Controller
        name="db_type"
        control={control}
        render={({ field }) => (
          <FormControl component="fieldset" error={!!errors.db_type} fullWidth>
            <ToggleButtonGroup
              exclusive
              color="standard"
              value={field.value ?? 'sqlite'}
              onChange={(_, value) => {
                if (!value) return
                field.onChange(value)
              }}
              onBlur={field.onBlur}
              ref={field.ref}
              sx={dbTypeToggleGroupSx}
              aria-labelledby="dbtype-label"
            >
              {DB_TYPE_OPTIONS.map((option) => {
                const IconComponent = option.icon
                return (
                  <ToggleButton
                    key={option.value}
                    value={option.value}
                    disableRipple
                    sx={buildDbTypeButtonSx(option.accent)}
                    aria-label={option.label}
                  >
                    {IconComponent ? (
                      <Box className="db-type-icon">
                        <IconComponent fontSize="small" />
                      </Box>
                    ) : null}
                    <Box className="db-type-meta">
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }} noWrap>
                        {option.label}
                      </Typography>
                    </Box>
                  </ToggleButton>
                )
              })}
            </ToggleButtonGroup>
            <FormHelperText sx={{ mt: 1, textAlign: 'center' }}>
              {errors.db_type?.message || 'Choose the database engine you are connecting to'}
            </FormHelperText>
          </FormControl>
        )}
      />
    </Box>
  )
}
