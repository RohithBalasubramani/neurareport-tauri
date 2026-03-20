import { CONTROL_HEIGHT, CONTROL_RADIUS } from '../constants/connectDB'

export const gridItemSx = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'stretch',
  flex: 1,
  minWidth: 0,
  maxWidth: '100%',
}

export const sharedFieldSx = {
  '& .MuiOutlinedInput-root': {
    borderRadius: CONTROL_RADIUS,
    minHeight: CONTROL_HEIGHT,
    alignItems: 'center',
    width: '100%',
    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
  },
  '& .MuiOutlinedInput-notchedOutline': {
    borderRadius: CONTROL_RADIUS,
    borderColor: 'divider',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    borderColor: 'divider',
  },
  '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
    borderColor: 'text.secondary',
    borderWidth: 2,
  },
  '& .MuiOutlinedInput-input': { py: 1.25 },
  '& .MuiInputLabel-root': (theme) => ({
    ...theme.typography.overline,
    color: theme.palette.text.secondary,
    letterSpacing: '0.14em',
  }),
}

export const fieldSx = { width: '100%', flexGrow: 1, ...sharedFieldSx }
