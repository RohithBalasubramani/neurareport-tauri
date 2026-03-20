/**
 * Custom hook: all state, effects, and callbacks for SpreadsheetEditorPage.
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import useSpreadsheetStore from '@/stores/spreadsheetStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

const getCellRef = (row, col) => {
  let colName = ''
  let tempCol = col
  while (tempCol >= 0) {
    colName = String.fromCharCode((tempCol % 26) + 65) + colName
    tempCol = Math.floor(tempCol / 26) - 1
  }
  return `${colName}${row + 1}`
}

export { getCellRef }

export function useSpreadsheetEditor() {
  const toast = useToast()
  const { execute } = useInteraction()
  const { connections, activeConnectionId } = useSharedData()

  const {
    spreadsheets,
    currentSpreadsheet,
    activeSheetIndex,
    selectedCells,
    loading,
    saving,
    error,
    fetchSpreadsheets,
    createSpreadsheet,
    getSpreadsheet,
    updateSpreadsheet,
    deleteSpreadsheet,
    updateCells,
    addSheet,
    deleteSheet,
    renameSheet,
    setActiveSheetIndex,
    setSelectedCells,
    createPivotTable,
    generateFormula,
    importCsv,
    importExcel,
    exportSpreadsheet,
    reset,
  } = useSpreadsheetStore()

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newSpreadsheetName, setNewSpreadsheetName] = useState('')
  const [selectedConnectionId, setSelectedConnectionId] = useState('')
  const [currentCellRef, setCurrentCellRef] = useState('A1')
  const [currentCellValue, setCurrentCellValue] = useState('')
  const [currentCellFormula, setCurrentCellFormula] = useState(null)
  const [localData, setLocalData] = useState([])
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [aiDialogOpen, setAiDialogOpen] = useState(false)
  const [aiPrompt, setAiPrompt] = useState('')
  const [exportMenuAnchor, setExportMenuAnchor] = useState(null)
  const [moreMenuAnchor, setMoreMenuAnchor] = useState(null)
  const [renameDialogOpen, setRenameDialogOpen] = useState(false)
  const [newSheetName, setNewSheetName] = useState('')
  const [sheetToRename, setSheetToRename] = useState(null)
  const fileInputRef = useRef(null)
  const handsontableRef = useRef(null)

  // Cross-page: accept table data from other features
  useIncomingTransfer(FeatureKey.SPREADSHEETS, {
    [TransferAction.OPEN_IN]: async (payload) => {
      const tableData = payload.data || {}
      const columns = tableData.columns || []
      const rows = tableData.rows || []
      const cellData = {}
      columns.forEach((col, colIdx) => {
        const colLetter = String.fromCharCode(65 + colIdx)
        cellData[`${colLetter}1`] = { value: typeof col === 'string' ? col : col.name || `Col${colIdx + 1}` }
      })
      rows.forEach((row, rowIdx) => {
        const rowValues = Array.isArray(row) ? row : Object.values(row)
        rowValues.forEach((val, colIdx) => {
          if (colIdx < 26) {
            const colLetter = String.fromCharCode(65 + colIdx)
            cellData[`${colLetter}${rowIdx + 2}`] = { value: val }
          }
        })
      })
      const spreadsheet = await createSpreadsheet({
        name: payload.title || 'Imported Data',
        sheets: [{ name: 'Sheet 1', data: cellData }],
      })
      if (spreadsheet) getSpreadsheet(spreadsheet.id)
    },
  })

  useEffect(() => {
    fetchSpreadsheets()
    return () => reset()
  }, [fetchSpreadsheets, reset])

  // Convert sheet data to 2D array for Handsontable
  useEffect(() => {
    if (currentSpreadsheet?.sheets?.[activeSheetIndex]?.data) {
      const sheetData = currentSpreadsheet.sheets[activeSheetIndex].data
      const rows = []
      const maxRow = 100
      const maxCol = 26

      for (let r = 0; r < maxRow; r++) {
        const row = []
        for (let c = 0; c < maxCol; c++) {
          const cellKey = getCellRef(r, c)
          const cellData = sheetData[cellKey]
          row.push(cellData?.formula || cellData?.value || '')
        }
        rows.push(row)
      }
      setLocalData(rows)
    } else {
      setLocalData(Array(100).fill(null).map(() => Array(26).fill('')))
    }
  }, [currentSpreadsheet, activeSheetIndex])

  const executeUI = useCallback((label, action, intent = {}) => {
    return execute({
      type: InteractionType.EXECUTE,
      label,
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'spreadsheets', ...intent },
      action,
    })
  }, [execute])

  const handleOpenCreateDialog = useCallback(() => {
    return executeUI('Open create spreadsheet', () => setCreateDialogOpen(true))
  }, [executeUI])

  const handleCloseCreateDialog = useCallback(() => {
    return executeUI('Close create spreadsheet', () => {
      setCreateDialogOpen(false)
      setNewSpreadsheetName('')
      setSelectedConnectionId('')
    })
  }, [executeUI])

  const handleOpenAiDialog = useCallback(() => {
    return executeUI('Open AI formula', () => setAiDialogOpen(true))
  }, [executeUI])

  const handleCloseAiDialog = useCallback(() => {
    return executeUI('Close AI formula', () => {
      setAiDialogOpen(false)
      setAiPrompt('')
    })
  }, [executeUI])

  const handleTriggerImport = useCallback(() => {
    return executeUI('Import spreadsheet', () => fileInputRef.current?.click())
  }, [executeUI])

  const handleSelectSpreadsheet = useCallback((spreadsheetId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Open spreadsheet',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'spreadsheets', spreadsheetId },
      action: async () => {
        await getSpreadsheet(spreadsheetId)
        setHasUnsavedChanges(false)
      },
    })
  }, [execute, getSpreadsheet])

  const handleCreateSpreadsheet = useCallback(() => {
    if (!newSpreadsheetName) return undefined
    return execute({
      type: InteractionType.CREATE,
      label: 'Create spreadsheet',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'spreadsheets', name: newSpreadsheetName, connectionId: selectedConnectionId || undefined },
      action: async () => {
        const spreadsheet = await createSpreadsheet({
          name: newSpreadsheetName,
          sheets: [{ name: 'Sheet 1', data: {} }],
          connectionId: selectedConnectionId || undefined,
        })
        if (spreadsheet) {
          setCreateDialogOpen(false)
          setNewSpreadsheetName('')
          setSelectedConnectionId('')
          toast.show('Spreadsheet created', 'success')
        }
        return spreadsheet
      },
    })
  }, [createSpreadsheet, execute, newSpreadsheetName, selectedConnectionId, toast])

  const handleDeleteSpreadsheet = useCallback((spreadsheetId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete spreadsheet',
      reversibility: Reversibility.REQUIRES_CONFIRMATION,
      intent: { source: 'spreadsheets', spreadsheetId },
      action: async () => {
        const success = await deleteSpreadsheet(spreadsheetId)
        if (success) {
          toast.show('Spreadsheet deleted', 'success')
        }
        return success
      },
    })
  }, [deleteSpreadsheet, execute, toast])

  const handleCellChange = useCallback((changes, source) => {
    if (source === 'loadData') return
    if (!changes) return

    setHasUnsavedChanges(true)

    setLocalData((prev) => {
      const newData = prev.map((row) => [...row])
      changes.forEach(([row, col, oldVal, newVal]) => {
        if (newData[row]) {
          newData[row][col] = newVal
        }
      })
      return newData
    })
  }, [])

  const handleSelectionChange = useCallback((row, col, row2, col2) => {
    const cellRef = getCellRef(row, col)
    setCurrentCellRef(cellRef)

    const value = localData[row]?.[col] || ''
    setCurrentCellValue(value)
    setCurrentCellFormula(value.startsWith('=') ? value : null)
  }, [localData])

  const handleFormulaBarChange = useCallback((value) => {
    setCurrentCellValue(value)
  }, [])

  const handleFormulaBarApply = useCallback((value) => {
    const match = currentCellRef.match(/^([A-Z]+)(\d+)$/)
    if (!match) return

    const colLetters = match[1]
    const row = parseInt(match[2], 10) - 1
    let col = 0
    for (let i = 0; i < colLetters.length; i++) {
      col = col * 26 + (colLetters.charCodeAt(i) - 64)
    }
    col -= 1

    setLocalData((prev) => {
      const newData = prev.map((r) => [...r])
      if (newData[row]) {
        newData[row][col] = value
      }
      return newData
    })
    setHasUnsavedChanges(true)
  }, [currentCellRef])

  const handleFormulaBarCancel = useCallback(() => {
    const match = currentCellRef.match(/^([A-Z]+)(\d+)$/)
    if (!match) return

    const colLetters = match[1]
    const row = parseInt(match[2], 10) - 1
    let col = 0
    for (let i = 0; i < colLetters.length; i++) {
      col = col * 26 + (colLetters.charCodeAt(i) - 64)
    }
    col -= 1

    setCurrentCellValue(localData[row]?.[col] || '')
  }, [currentCellRef, localData])

  const handleSave = useCallback(() => {
    if (!currentSpreadsheet) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Save spreadsheet',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id },
      action: async () => {
        const cellDataObj = {}
        localData.forEach((row, rowIndex) => {
          row.forEach((value, colIndex) => {
            if (value !== '') {
              const cellKey = getCellRef(rowIndex, colIndex)
              const isFormula = typeof value === 'string' && value.startsWith('=')
              cellDataObj[cellKey] = {
                value: isFormula ? '' : value,
                formula: isFormula ? value : null,
              }
            }
          })
        })

        await updateCells(currentSpreadsheet.id, activeSheetIndex, cellDataObj)
        setHasUnsavedChanges(false)
        toast.show('Spreadsheet saved', 'success')
      },
    })
  }, [activeSheetIndex, currentSpreadsheet, execute, localData, toast, updateCells])

  const handleImport = useCallback((e) => {
    const file = e.target.files[0]
    if (!file) return

    const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')

    execute({
      type: InteractionType.UPLOAD,
      label: 'Import spreadsheet',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'spreadsheets', filename: file.name },
      action: async () => {
        const result = isExcel
          ? await importExcel(file)
          : await importCsv(file)
        if (result) {
          toast.show('File imported successfully', 'success')
        }
      },
    }).finally(() => {
      e.target.value = ''
    })
  }, [execute, importCsv, importExcel, toast])

  const handleExport = useCallback((format) => {
    if (!currentSpreadsheet) return undefined
    setExportMenuAnchor(null)
    return execute({
      type: InteractionType.DOWNLOAD,
      label: 'Export spreadsheet',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id, format },
      action: async () => {
        const blob = await exportSpreadsheet(currentSpreadsheet.id, format)
        if (blob) {
          const url = URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `${currentSpreadsheet.name}.${format}`
          a.click()
          URL.revokeObjectURL(url)
          toast.show(`Exported to ${format.toUpperCase()}`, 'success')
        } else {
          toast.show('Export not available', 'warning')
        }
      },
    })
  }, [currentSpreadsheet, execute, exportSpreadsheet, toast])

  const handleAIFormula = useCallback(() => {
    if (!aiPrompt || !currentSpreadsheet) return undefined
    return execute({
      type: InteractionType.GENERATE,
      label: 'Generate formula',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id },
      action: async () => {
        const result = await generateFormula(currentSpreadsheet.id, aiPrompt)
        if (result?.formula) {
          setCurrentCellValue(result.formula)
          handleFormulaBarApply(result.formula)
          toast.show('Formula generated', 'success')
        }
        setAiDialogOpen(false)
        setAiPrompt('')
        return result
      },
    })
  }, [aiPrompt, currentSpreadsheet, execute, generateFormula, handleFormulaBarApply, toast])

  const handleSelectSheet = useCallback((index) => {
    return executeUI('Switch sheet', () => setActiveSheetIndex(index), { index })
  }, [executeUI, setActiveSheetIndex])

  const handleAddSheet = useCallback(() => {
    if (!currentSpreadsheet) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Add sheet',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id },
      action: async () => {
        const nextIndex = (currentSpreadsheet.sheets?.length || 0) + 1
        await addSheet(currentSpreadsheet.id, `Sheet ${nextIndex}`)
        toast.show('Sheet added', 'success')
      },
    })
  }, [addSheet, currentSpreadsheet, execute, toast])

  const handleRenameSheet = useCallback(() => {
    if (!currentSpreadsheet || sheetToRename === null || !newSheetName) return undefined
    return execute({
      type: InteractionType.UPDATE,
      label: 'Rename sheet',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id },
      action: async () => {
        await renameSheet(currentSpreadsheet.id, sheetToRename, newSheetName)
        setRenameDialogOpen(false)
        setNewSheetName('')
        setSheetToRename(null)
        toast.show('Sheet renamed', 'success')
      },
    })
  }, [currentSpreadsheet, execute, newSheetName, renameSheet, sheetToRename, toast])

  const handleDeleteSheet = useCallback((index) => {
    if (!currentSpreadsheet || currentSpreadsheet.sheets?.length <= 1) {
      toast.show('Cannot delete the only sheet', 'warning')
      return undefined
    }
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete sheet',
      reversibility: Reversibility.REQUIRES_CONFIRMATION,
      intent: { source: 'spreadsheets', spreadsheetId: currentSpreadsheet.id, sheetIndex: index },
      action: async () => {
        await deleteSheet(currentSpreadsheet.id, index)
        toast.show('Sheet deleted', 'success')
      },
    })
  }, [currentSpreadsheet, deleteSheet, execute, toast])

  const handleDismissError = useCallback(() => {
    return executeUI('Dismiss spreadsheet error', () => reset())
  }, [executeUI, reset])

  const openRenameDialog = useCallback((index) => {
    setSheetToRename(index)
    setNewSheetName(currentSpreadsheet?.sheets?.[index]?.name || '')
    setRenameDialogOpen(true)
  }, [currentSpreadsheet])

  const handleImportFromMenu = useCallback(async (output) => {
    const { columns, rows } = output.data || {}
    const cellData = {}
    if (columns && rows) {
      columns.forEach((col, ci) => {
        if (ci < 26) {
          const letter = String.fromCharCode(65 + ci)
          cellData[`${letter}1`] = { value: typeof col === 'string' ? col : col.name || `Col${ci + 1}` }
        }
      })
      rows.forEach((row, ri) => {
        const vals = Array.isArray(row) ? row : Object.values(row)
        vals.forEach((v, ci) => {
          if (ci < 26) {
            const letter = String.fromCharCode(65 + ci)
            cellData[`${letter}${ri + 2}`] = { value: v }
          }
        })
      })
    }
    const spreadsheet = await createSpreadsheet({
      name: output.title || 'Imported Data',
      sheets: [{ name: 'Sheet 1', data: cellData }],
    })
    if (spreadsheet) {
      getSpreadsheet(spreadsheet.id)
      toast.show(`Created spreadsheet from "${output.title}"`, 'success')
    }
  }, [createSpreadsheet, getSpreadsheet, toast])

  return {
    // Refs
    fileInputRef,
    handsontableRef,
    // Store data
    spreadsheets,
    currentSpreadsheet,
    activeSheetIndex,
    loading,
    saving,
    error,
    // Local state
    createDialogOpen,
    newSpreadsheetName,
    setNewSpreadsheetName,
    selectedConnectionId,
    setSelectedConnectionId,
    currentCellRef,
    currentCellValue,
    currentCellFormula,
    localData,
    hasUnsavedChanges,
    aiDialogOpen,
    aiPrompt,
    setAiPrompt,
    exportMenuAnchor,
    setExportMenuAnchor,
    renameDialogOpen,
    setRenameDialogOpen,
    newSheetName,
    setNewSheetName,
    // Handlers
    handleOpenCreateDialog,
    handleCloseCreateDialog,
    handleOpenAiDialog,
    handleCloseAiDialog,
    handleTriggerImport,
    handleSelectSpreadsheet,
    handleCreateSpreadsheet,
    handleDeleteSpreadsheet,
    handleCellChange,
    handleSelectionChange,
    handleFormulaBarChange,
    handleFormulaBarApply,
    handleFormulaBarCancel,
    handleSave,
    handleImport,
    handleExport,
    handleAIFormula,
    handleSelectSheet,
    handleAddSheet,
    handleRenameSheet,
    handleDeleteSheet,
    handleDismissError,
    openRenameDialog,
    handleImportFromMenu,
  }
}
