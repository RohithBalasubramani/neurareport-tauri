import { HyperFormula } from 'hyperformula'
import { Box, alpha, styled } from '@mui/material'
import { neutral } from '@/app/theme'

// Create HyperFormula instance for calculations
export const hyperformulaInstance = HyperFormula.buildEmpty({
  licenseKey: 'gpl-v3',
})

// Default column headers (A-ZZ)
export const generateColumnHeaders = (count) => {
  const headers = []
  for (let i = 0; i < count; i++) {
    let header = ''
    let num = i
    while (num >= 0) {
      header = String.fromCharCode((num % 26) + 65) + header
      num = Math.floor(num / 26) - 1
    }
    headers.push(header)
  }
  return headers
}

export const EditorContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'hidden',
  '& .handsontable': {
    fontFamily: theme.typography.fontFamily,
    fontSize: '14px',
  },
  '& .handsontable th': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
    fontWeight: 600,
  },
  '& .handsontable td': {
    verticalAlign: 'middle',
  },
  '& .handsontable td.area': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100],
  },
  '& .handsontable .htContextMenu': {
    borderRadius: 8,
    boxShadow: theme.shadows[8],
  },
  '& .handsontable .wtBorder.current': {
    backgroundColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))
