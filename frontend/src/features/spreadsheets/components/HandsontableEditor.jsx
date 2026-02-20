/**
 * Handsontable Editor Component
 * Excel-like spreadsheet editor with full functionality.
 */
import { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { HotTable } from '@handsontable/react'
import { registerAllModules } from 'handsontable/registry'
import { HyperFormula } from 'hyperformula'
import 'handsontable/dist/handsontable.full.min.css'
import {
  Box,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import { neutral, palette } from '@/app/theme'
import {
  ContentCopy,
  ContentPaste,
  ContentCut,
  Delete,
  FormatBold,
  FormatItalic,
  FormatColorFill,
  FilterList,
  Sort,
  AddCircleOutline,
  RemoveCircleOutline,
  ViewColumn,
  TableRows,
} from '@mui/icons-material'

// Icon aliases for row/column operations (using available MUI icons)
const InsertRowAbove = AddCircleOutline
const InsertRowBelow = AddCircleOutline
const DeleteRow = RemoveCircleOutline
const InsertColumnLeft = ViewColumn
const InsertColumnRight = ViewColumn
const DeleteColumn = RemoveCircleOutline

// Register all Handsontable modules
registerAllModules()

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const EditorContainer = styled(Box)(({ theme }) => ({
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

// =============================================================================
// HELPERS
// =============================================================================

// Create HyperFormula instance for calculations
const hyperformulaInstance = HyperFormula.buildEmpty({
  licenseKey: 'gpl-v3',
})

// Default column headers (A-ZZ)
const generateColumnHeaders = (count) => {
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

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function HandsontableEditor({
  data = [],
  columns = 26,
  rows = 100,
  onCellChange,
  onSelectionChange,
  onFormulaBarUpdate,
  readOnly = false,
  contextMenuEnabled = true,
  formulas = true,
}) {
  const theme = useTheme()
  const hotRef = useRef(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [selectedRange, setSelectedRange] = useState(null)

  // Generate initial data if empty
  const initialData = useMemo(() => {
    if (data && data.length > 0) return data
    return Array(rows).fill(null).map(() => Array(columns).fill(''))
  }, [data, rows, columns])

  // Column headers
  const colHeaders = useMemo(() => generateColumnHeaders(columns), [columns])

  // Handle cell changes
  const handleAfterChange = useCallback((changes, source) => {
    if (!changes || source === 'loadData') return

    const cellChanges = changes.map(([row, col, oldValue, newValue]) => ({
      row,
      col,
      oldValue,
      newValue,
      cellRef: `${colHeaders[col]}${row + 1}`,
    }))

    onCellChange?.(cellChanges, source)
  }, [colHeaders, onCellChange])

  // Handle selection changes
  const handleAfterSelection = useCallback((row, col, row2, col2) => {
    const selection = {
      start: { row, col, ref: `${colHeaders[col]}${row + 1}` },
      end: { row: row2, col: col2, ref: `${colHeaders[col2]}${row2 + 1}` },
      isRange: row !== row2 || col !== col2,
    }
    setSelectedRange(selection)
    onSelectionChange?.(selection)

    // Update formula bar
    const hot = hotRef.current?.hotInstance
    if (hot) {
      const cellValue = hot.getDataAtCell(row, col)
      const cellMeta = hot.getCellMeta(row, col)
      onFormulaBarUpdate?.({
        cellRef: selection.start.ref,
        value: cellValue || '',
        formula: cellMeta?.formula || null,
      })
    }
  }, [colHeaders, onFormulaBarUpdate, onSelectionChange])

  // Handle context menu (right-click)
  const handleContextMenu = useCallback((event) => {
    event.preventDefault()
    setContextMenu({
      mouseX: event.clientX,
      mouseY: event.clientY,
    })
  }, [])

  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null)
  }, [])

  // Context menu actions
  const executeAction = useCallback((action) => {
    const hot = hotRef.current?.hotInstance
    if (!hot) return

    switch (action) {
      case 'copy':
        document.execCommand('copy')
        break
      case 'cut':
        document.execCommand('cut')
        break
      case 'paste':
        document.execCommand('paste')
        break
      case 'delete':
        if (selectedRange) {
          const { start, end } = selectedRange
          for (let r = Math.min(start.row, end.row); r <= Math.max(start.row, end.row); r++) {
            for (let c = Math.min(start.col, end.col); c <= Math.max(start.col, end.col); c++) {
              hot.setDataAtCell(r, c, '')
            }
          }
        }
        break
      case 'insert_row_above':
        if (selectedRange) hot.alter('insert_row_above', selectedRange.start.row)
        break
      case 'insert_row_below':
        if (selectedRange) hot.alter('insert_row_below', selectedRange.start.row)
        break
      case 'delete_row':
        if (selectedRange) hot.alter('remove_row', selectedRange.start.row)
        break
      case 'insert_col_left':
        if (selectedRange) hot.alter('insert_col_start', selectedRange.start.col)
        break
      case 'insert_col_right':
        if (selectedRange) hot.alter('insert_col_end', selectedRange.start.col)
        break
      case 'delete_col':
        if (selectedRange) hot.alter('remove_col', selectedRange.start.col)
        break
    }
    handleCloseContextMenu()
  }, [handleCloseContextMenu, selectedRange])

  // Handsontable settings
  const hotSettings = useMemo(() => ({
    data: initialData,
    colHeaders,
    rowHeaders: true,
    width: '100%',
    height: '100%',
    stretchH: 'all',
    autoWrapRow: true,
    autoWrapCol: true,
    readOnly,
    manualColumnResize: true,
    manualRowResize: true,
    manualColumnMove: true,
    manualRowMove: true,
    dropdownMenu: contextMenuEnabled,
    filters: true,
    multiColumnSorting: true,
    mergeCells: true,
    undo: true,
    autoColumnSize: { syncLimit: 100 },
    autoRowSize: { syncLimit: 100 },
    licenseKey: 'non-commercial-and-evaluation',
    // Enable formulas with HyperFormula
    formulas: formulas ? {
      engine: hyperformulaInstance,
    } : false,
    // Cell types
    cells: function(row, col) {
      const cellProperties = {}
      return cellProperties
    },
    // Comments
    comments: true,
    // Validation
    validator: (value, callback) => {
      callback(true)
    },
    afterChange: handleAfterChange,
    afterSelection: handleAfterSelection,
    afterScrollVertically: () => {},
    afterScrollHorizontally: () => {},
    contextMenu: contextMenuEnabled ? {
      items: {
        'copy': { name: 'Copy', disabled: false },
        'cut': { name: 'Cut', disabled: false },
        'hsep1': '---------',
        'row_above': { name: 'Insert row above' },
        'row_below': { name: 'Insert row below' },
        'remove_row': { name: 'Remove row' },
        'hsep2': '---------',
        'col_left': { name: 'Insert column left' },
        'col_right': { name: 'Insert column right' },
        'remove_col': { name: 'Remove column' },
        'hsep3': '---------',
        'undo': { name: 'Undo' },
        'redo': { name: 'Redo' },
      }
    } : false,
  }), [
    initialData,
    colHeaders,
    readOnly,
    contextMenuEnabled,
    formulas,
    handleAfterChange,
    handleAfterSelection,
  ])

  // External API methods
  useEffect(() => {
    // Expose hot instance methods through ref
    if (hotRef.current) {
      const hot = hotRef.current.hotInstance

      // Method to set cell value from formula bar
      hotRef.current.setSelectedCellValue = (value) => {
        if (selectedRange && hot) {
          hot.setDataAtCell(selectedRange.start.row, selectedRange.start.col, value)
        }
      }

      // Method to get current data
      hotRef.current.getData = () => hot?.getData() || []

      // Method to load data
      hotRef.current.loadData = (newData) => hot?.loadData(newData)

      // Method to insert row
      hotRef.current.insertRow = (index, amount = 1) => {
        hot?.alter('insert_row_below', index, amount)
      }

      // Method to insert column
      hotRef.current.insertColumn = (index, amount = 1) => {
        hot?.alter('insert_col_end', index, amount)
      }
    }
  }, [selectedRange])

  return (
    <EditorContainer>
      <HotTable
        ref={hotRef}
        settings={hotSettings}
      />
    </EditorContainer>
  )
}

// Export a ref-forwarding version for external access
export const HandsontableEditorRef = ({ forwardedRef, ...props }) => {
  const internalRef = useRef(null)

  useEffect(() => {
    if (forwardedRef) {
      forwardedRef.current = internalRef.current
    }
  }, [forwardedRef])

  return <HandsontableEditor ref={internalRef} {...props} />
}
