/**
 * Handsontable Editor Component
 * Excel-like spreadsheet editor with full functionality.
 */
import { useCallback, useEffect, useRef, useState, useMemo } from 'react'
import { HotTable } from '@handsontable/react'
import { registerAllModules } from 'handsontable/registry'
import 'handsontable/dist/handsontable.full.min.css'
import { useTheme } from '@mui/material'
import { EditorContainer, hyperformulaInstance, generateColumnHeaders } from './handsontableHelpers'

// Register all Handsontable modules
registerAllModules()

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
  const hotRef = useRef(null)
  const [selectedRange, setSelectedRange] = useState(null)

  const initialData = useMemo(() => {
    if (data && data.length > 0) return data
    return Array(rows).fill(null).map(() => Array(columns).fill(''))
  }, [data, rows, columns])

  const colHeaders = useMemo(() => generateColumnHeaders(columns), [columns])

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

  const handleAfterSelection = useCallback((row, col, row2, col2) => {
    const selection = {
      start: { row, col, ref: `${colHeaders[col]}${row + 1}` },
      end: { row: row2, col: col2, ref: `${colHeaders[col2]}${row2 + 1}` },
      isRange: row !== row2 || col !== col2,
    }
    setSelectedRange(selection)
    onSelectionChange?.(selection)

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
    formulas: formulas ? {
      engine: hyperformulaInstance,
    } : false,
    cells: function(row, col) {
      const cellProperties = {}
      return cellProperties
    },
    comments: true,
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

  useEffect(() => {
    if (hotRef.current) {
      const hot = hotRef.current.hotInstance

      hotRef.current.setSelectedCellValue = (value) => {
        if (selectedRange && hot) {
          hot.setDataAtCell(selectedRange.start.row, selectedRange.start.col, value)
        }
      }

      hotRef.current.getData = () => hot?.getData() || []
      hotRef.current.loadData = (newData) => hot?.loadData(newData)

      hotRef.current.insertRow = (index, amount = 1) => {
        hot?.alter('insert_row_below', index, amount)
      }

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
