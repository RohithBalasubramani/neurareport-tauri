import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'

const baseMenuProps = {
  autoWidth: false,
  PaperProps: {
    elevation: 0,
    style: {
      borderRadius: '8px',
      borderTopLeftRadius: '12px',
      borderTopRightRadius: '12px',
      borderBottomRightRadius: '12px',
      borderBottomLeftRadius: '12px',
    },
    sx: {
      mt: 1.25,
      maxHeight: 320,
      minWidth: 360,
      borderRadius: '8px !important',
      borderTopLeftRadius: '12px !important',
      borderTopRightRadius: '12px !important',
      borderBottomRightRadius: '12px !important',
      borderBottomLeftRadius: '12px !important',
      border: `1px solid ${alpha(neutral[400], 0.28)}`,
      backgroundColor: 'rgba(255,255,255,0.98)',
      backdropFilter: 'blur(10px)',
      boxShadow: `0 22px 52px ${alpha(neutral[900], 0.22)}`,
      overflow: 'hidden',
      '&.MuiPaper-rounded': {
        borderRadius: '8px !important',
        borderTopLeftRadius: '12px !important',
        borderTopRightRadius: '12px !important',
        borderBottomRightRadius: '12px !important',
        borderBottomLeftRadius: '12px !important',
      },
    },
  },
  MenuListProps: {
    sx: { py: 1.1, px: 0.5 },
  },
}

export function buildMenuProps(menuPropsProp) {
  const menuProps = {
    ...baseMenuProps,
    ...menuPropsProp,
  }
  if (menuPropsProp?.PaperProps) {
    menuProps.PaperProps = {
      ...baseMenuProps.PaperProps,
      ...menuPropsProp.PaperProps,
      sx: {
        ...baseMenuProps.PaperProps.sx,
        ...(menuPropsProp.PaperProps?.sx || {}),
      },
    }
  }
  if (menuPropsProp?.MenuListProps) {
    menuProps.MenuListProps = {
      ...baseMenuProps.MenuListProps,
      ...menuPropsProp.MenuListProps,
      sx: {
        ...(baseMenuProps.MenuListProps?.sx || {}),
        ...(menuPropsProp.MenuListProps?.sx || {}),
      },
    }
  }
  return menuProps
}
