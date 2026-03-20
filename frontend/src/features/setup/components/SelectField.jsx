import {
  Stack, Typography, FormControl, FormHelperText,
  Select,
} from '@mui/material'
import { alpha, styled } from '@mui/material/styles'
import { OutlinedInput } from '@mui/material'
import { CONTROL_HEIGHT, CONTROL_RADIUS } from '../constants/connectDB'
import { SelectFieldRenderValue, SelectFieldMenuItem } from './SelectFieldOption'
import { buildMenuProps } from './selectFieldMenuProps'

const StyledOutlinedInput = styled(OutlinedInput)(({ theme }) => ({
  borderRadius: CONTROL_RADIUS,
  height: CONTROL_HEIGHT,
  paddingRight: theme.spacing(1),
  '& .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '& .MuiOutlinedInput-input': {
    display: 'flex',
    alignItems: 'center',
    height: CONTROL_HEIGHT,
    padding: theme.spacing(1.1, 1.75),
  },
}))

export default function SelectField({
  value,
  options,
  menuProps: menuPropsProp,
  id,
  label,
  labelId,
  onChange,
  onBlur,
  inputRef,
  selectControlSx,
  error,
  helperText,
  widestLabel,
}) {
  const normalizedValue = value ?? ''
  const ghostLabel = widestLabel || options.reduce((longest, opt) => (
    opt.label.length > longest.length ? opt.label : longest
  ), '')

  const menuProps = buildMenuProps(menuPropsProp)

  return (
    <Stack
      direction="row"
      spacing={1}
      alignItems="center"
      sx={{
        width: '100%',
        flexWrap: { xs: 'wrap', sm: 'nowrap' },
        rowGap: { xs: 1, sm: 0 },
        ml: { xs: 0, sm: 3 },
      }}
    >
      <Typography
        id={labelId}
        variant="caption"
        sx={(theme) => ({
          fontWeight: theme.typography.fontWeightBold,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: alpha(theme.palette.text.secondary, 0.85),
          minWidth: 72,
          whiteSpace: 'nowrap',
        })}
      >
        {label}
      </Typography>
      <FormControl
        size="small"
        margin="dense"
        variant="outlined"
        error={error}
        sx={[selectControlSx]}
        aria-labelledby={labelId}
      >
        <Select
          labelId={labelId}
          id={id}
          value={normalizedValue}
          onChange={onChange}
          onBlur={onBlur}
          inputRef={inputRef}
          input={<StyledOutlinedInput sx={{ pl: 0, pr: 3 }} />}
          displayEmpty
          MenuProps={menuProps}
          sx={{
            display: 'block',
            width: '100%',
            '& .MuiSelect-select': {
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              minWidth: 0,
              paddingTop: 0.5,
              paddingBottom: 0.5,
              boxSizing: 'border-box',
            },
            '& .MuiSelect-icon': {
              right: 12,
              color: 'text.secondary',
              opacity: 0.68,
            },
          }}
          renderValue={(selected) => {
            const selectedOption = options.find((opt) => opt.value === selected) || null
            return <SelectFieldRenderValue selectedOption={selectedOption} ghostLabel={ghostLabel} />
          }}
        >
          {options.map((opt) => (
            <SelectFieldMenuItem key={opt.value} opt={opt} />
          ))}
        </Select>
        {helperText ? (
          <FormHelperText sx={{ mt: 0.75, mx: 0.5 }}>{helperText}</FormHelperText>
        ) : null}
      </FormControl>
    </Stack>
  )
}
