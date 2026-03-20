import { Box, Card, alpha, styled } from '@mui/material'

export const PaletteContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
}))

export const CategoryHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  cursor: 'pointer',
  padding: theme.spacing(0.5, 0),
  '&:hover': {
    opacity: 0.8,
  },
}))

export const WidgetCard = styled(Card)(({ theme }) => ({
  cursor: 'grab',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  position: 'relative',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 4px 12px ${theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : alpha(theme.palette.text.primary, 0.08)}`,
    borderColor: theme.palette.divider,
  },
  '&:active': {
    cursor: 'grabbing',
    transform: 'scale(0.98)',
  },
}))

export const WidgetGrid = styled(Box)(({ theme }) => ({
  display: 'grid',
  gridTemplateColumns: 'repeat(2, 1fr)',
  gap: theme.spacing(1),
}))

export const VariantBadge = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 2,
  right: 2,
  width: 14,
  height: 14,
  borderRadius: '50%',
  backgroundColor: alpha(theme.palette.primary.main, 0.15),
  color: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '10px',
  fontWeight: 600,
}))
