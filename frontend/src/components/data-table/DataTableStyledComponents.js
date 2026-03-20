/**
 * Styled components, constants, and helpers for DataTable
 */
import {
  Box,
  Table,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Checkbox,
  Skeleton,
  TableSortLabel,
  alpha,
  styled,
  keyframes,
} from '@mui/material'
import {
  neutral,
  figmaComponents,
  fontFamilyBody,
} from '@/app/theme'
import { shimmer } from '@/styles'

// =============================================================================
// FIGMA DATA TABLE CONSTANTS (EXACT from Figma specs)
// =============================================================================
export const FIGMA_TABLE = {
  headerHeight: figmaComponents.dataTable.headerHeight,  // 60px
  rowHeight: figmaComponents.dataTable.rowHeight,        // 60px
  cellPadding: figmaComponents.dataTable.cellPadding,    // 16px
}

// =============================================================================
// ANIMATIONS (local — differ from shared versions)
// =============================================================================

export const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`

// =============================================================================
// HELPERS
// =============================================================================

function descendingComparator(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) return -1
  if (b[orderBy] > a[orderBy]) return 1
  return 0
}

export function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy)
}

export const STORAGE_PREFIX = 'neurareport_table_'

export function loadPersistedState(key) {
  if (!key) return null
  try {
    const stored = localStorage.getItem(`${STORAGE_PREFIX}${key}`)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

export function savePersistedState(key, state) {
  if (!key) return
  try {
    localStorage.setItem(`${STORAGE_PREFIX}${key}`, JSON.stringify(state))
  } catch {
    // Ignore storage errors
  }
}

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

export const TableWrapper = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  borderRadius: 8,  // Figma spec: 8px
  border: `1px solid ${alpha(theme.palette.divider, 0.25)}`,
  overflow: 'hidden',
  // In flex layouts, allow the table wrapper to shrink so wide tables don't force horizontal page scroll.
  minWidth: 0,
  maxWidth: '100%',
  boxShadow: `0 4px 24px ${alpha(theme.palette.common.black, 0.06)}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  },
}))

export const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  overflowX: 'auto',
  '&::-webkit-scrollbar': {
    width: 8,
    height: 8,
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: 'transparent',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.text.primary, 0.1),
    borderRadius: 4,
    '&:hover': {
      backgroundColor: alpha(theme.palette.text.primary, 0.2),
    },
  },
}))

// FIGMA STYLED TABLE HEAD (EXACT from Figma: 60px height, 16px padding)
export const StyledTableHead = styled(TableHead)(({ theme }) => ({
  '& .MuiTableCell-head': {
    backgroundColor: theme.palette.mode === 'dark'
      ? alpha(theme.palette.background.paper, 0.5)
      : neutral[50],  // #F9F9F8 from Figma
    fontFamily: fontFamilyBody,  // Lato from Figma
    fontWeight: 500,
    fontSize: '14px',
    textTransform: 'none',  // No uppercase per Figma
    letterSpacing: 'normal',
    color: theme.palette.mode === 'dark' ? theme.palette.text.secondary : neutral[700],  // #63635E
    borderBottom: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.divider, 0.08) : neutral[200]}`,
    height: FIGMA_TABLE.headerHeight,  // 60px from Figma
    padding: `0 ${FIGMA_TABLE.cellPadding}px`,  // 16px from Figma
    transition: 'background-color 0.2s ease',
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[100],
    },
  },
}))

// FIGMA STYLED TABLE ROW (EXACT from Figma: 60px height)
export const StyledTableRow = styled(TableRow, {
  shouldForwardProp: (prop) => !['rowIndex', 'isClickable'].includes(prop),
})(({ theme, rowIndex, isClickable }) => ({
  height: FIGMA_TABLE.rowHeight,  // 60px from Figma
  animation: `${fadeInUp} 0.4s ease-out`,
  animationDelay: `${rowIndex * 0.03}s`,
  animationFillMode: 'both',
  transition: 'all 0.2s ease',
  cursor: isClickable ? 'pointer' : 'default',
  '& .MuiTableCell-body': {
    fontFamily: fontFamilyBody,  // Lato from Figma
    borderBottom: `1px solid ${theme.palette.mode === 'dark' ? alpha(theme.palette.divider, 0.05) : neutral[200]}`,
    padding: `0 ${FIGMA_TABLE.cellPadding}px`,  // 16px from Figma
    height: FIGMA_TABLE.rowHeight,  // 60px from Figma
    fontSize: '14px',
    color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[900],  // #21201C
    transition: 'all 0.2s ease',
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : alpha(neutral[100], 0.5),
    '& .MuiTableCell-body': {
      color: theme.palette.mode === 'dark' ? theme.palette.text.primary : neutral[900],
    },
    '& .row-actions': {
      opacity: 1,
      transform: 'translateX(0)',
    },
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
    '&:hover': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200],
    },
  },
  '&:last-child .MuiTableCell-body': {
    borderBottom: 'none',
  },
}))

export const RowActionsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  gap: theme.spacing(0.5),
  opacity: 0.5,
  transform: 'translateX(4px)',
  transition: 'all 0.2s ease',
}))

export const StyledCheckbox = styled(Checkbox)(({ theme }) => ({
  color: alpha(theme.palette.text.primary, 0.3),
  padding: theme.spacing(0.5),
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  },
  '&.Mui-checked': {
    color: theme.palette.text.primary,
  },
  '&.MuiCheckbox-indeterminate': {
    color: theme.palette.text.primary,
  },
}))

export const StyledTableSortLabel = styled(TableSortLabel)(({ theme }) => ({
  color: theme.palette.text.secondary,
  '&:hover': {
    color: theme.palette.text.primary,
  },
  '&.Mui-active': {
    color: theme.palette.text.primary,
    '& .MuiTableSortLabel-icon': {
      color: theme.palette.text.primary,
    },
  },
  '& .MuiTableSortLabel-icon': {
    fontSize: 16,
    transition: 'all 0.2s ease',
  },
}))

export const ShimmerSkeleton = styled(Skeleton)(({ theme }) => ({
  background: `linear-gradient(
    90deg,
    ${alpha(theme.palette.text.primary, 0.06)} 0%,
    ${alpha(theme.palette.text.primary, 0.12)} 50%,
    ${alpha(theme.palette.text.primary, 0.06)} 100%
  )`,
  backgroundSize: '200% 100%',
  animation: `${shimmer} 1.5s infinite`,
  borderRadius: 6,
}))

export const StyledPagination = styled(TablePagination)(({ theme }) => ({
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  '& .MuiTablePagination-selectLabel, & .MuiTablePagination-displayedRows': {
    fontSize: 14,
    color: theme.palette.text.secondary,
  },
  '& .MuiTablePagination-select': {
    borderRadius: 8,
    fontSize: 14,
  },
  '& .MuiTablePagination-actions': {
    '& .MuiIconButton-root': {
      color: theme.palette.text.secondary,
      '&:hover': {
        backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
        color: theme.palette.text.primary,
      },
      '&.Mui-disabled': {
        color: alpha(theme.palette.text.primary, 0.2),
      },
    },
  },
}))

export const ExpandableRow = styled(TableRow)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.3),
  '& .MuiTableCell-body': {
    borderBottom: `1px solid ${alpha(theme.palette.divider, 0.15)}`,
  },
}))
