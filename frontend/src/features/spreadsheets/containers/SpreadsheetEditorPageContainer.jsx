/**
 * Spreadsheet Editor Page Container
 * Excel-like spreadsheet editor with Handsontable and HyperFormula.
 */
import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Paper,
  List,
  ListItem,
  ListItemButton,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  TableChart as SpreadsheetIcon,
  Save as SaveIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Functions as FormulaIcon,
  PivotTableChart as PivotIcon,
  AutoAwesome as AIIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  TextFormat as FormatIcon,
  MoreVert as MoreIcon,
  Edit as EditIcon,
  FileCopy as CopyIcon,
  ContentCut as CutIcon,
  ContentPaste as PasteIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
} from '@mui/icons-material'
import useSpreadsheetStore from '@/stores/spreadsheetStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import { neutral, palette } from '@/app/theme'
import HandsontableEditor from '../components/HandsontableEditor'
import FormulaBar from '../components/FormulaBar'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Sidebar = styled(Box)(({ theme }) => ({
  width: 300,
  display: 'flex',
  flexDirection: 'column',
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
}))

const SidebarHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}))

const MainContent = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
}))

const Toolbar = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
  gap: theme.spacing(1),
}))

const SpreadsheetArea = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'hidden',
  backgroundColor: theme.palette.background.paper,
}))

const SheetTabs = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0.5, 1),
  borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  minHeight: 40,
  gap: theme.spacing(0.5),
}))

const SheetTab = styled(Chip, {
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({
  borderRadius: '4px 4px 0 0',
  height: 28,
  fontSize: '14px',
  backgroundColor: active
    ? theme.palette.background.paper
    : alpha(theme.palette.background.default, 0.5),
  border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  borderBottom: active ? 'none' : `1px solid ${alpha(theme.palette.divider, 0.2)}`,
  '&:hover': {
    backgroundColor: active
      ? theme.palette.background.paper
      : theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 6,
  textTransform: 'none',
  fontWeight: 500,
  minWidth: 'auto',
  fontSize: '14px',
}))

const SpreadsheetListItem = styled(ListItemButton, {
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({
  borderRadius: 8,
  marginBottom: theme.spacing(0.5),
  backgroundColor: active ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]) : 'transparent',
  '&:hover': {
    backgroundColor: active
      ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.15) : neutral[100])
      : alpha(theme.palette.action.hover, 0.05),
  },
}))

const EmptyState = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  textAlign: 'center',
}))

// =============================================================================
// COLUMN HELPERS
// =============================================================================

const COLUMNS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const getCellRef = (row, col) => {
  // Convert col index to letter (0 = A, 25 = Z, 26 = AA, etc.)
  let colName = ''
  let tempCol = col
  while (tempCol >= 0) {
    colName = String.fromCharCode((tempCol % 26) + 65) + colName
    tempCol = Math.floor(tempCol / 26) - 1
  }
  return `${colName}${row + 1}`
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function SpreadsheetEditorPage() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const { connections, activeConnectionId } = useSharedData()

  // Cross-page: accept table data from other features (Query, Federation)
  useIncomingTransfer(FeatureKey.SPREADSHEETS, {
    [TransferAction.OPEN_IN]: async (payload) => {
      const tableData = payload.data || {}
      const columns = tableData.columns || []
      const rows = tableData.rows || []
      // Build cell data from columns/rows
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

  useEffect(() => {
    fetchSpreadsheets()
    return () => reset()
  }, [fetchSpreadsheets, reset])

  // Convert sheet data to 2D array for Handsontable
  useEffect(() => {
    if (currentSpreadsheet?.sheets?.[activeSheetIndex]?.data) {
      const sheetData = currentSpreadsheet.sheets[activeSheetIndex].data
      // Convert from { A1: { value, formula }, B1: ... } to 2D array
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
      // Empty grid
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

  // Handsontable callbacks
  const handleCellChange = useCallback((changes, source) => {
    if (source === 'loadData') return
    if (!changes) return

    setHasUnsavedChanges(true)

    // Update local data
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
    // Parse currentCellRef to get row/col
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
    // Reset to original value
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
        // Convert 2D array back to object format
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

  return (
    <PageContainer>
      {/* Sidebar - Spreadsheet List */}
      <Sidebar>
        <SidebarHeader>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Spreadsheets
          </Typography>
          <Tooltip title="New Spreadsheet">
            <IconButton size="small" onClick={handleOpenCreateDialog}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </SidebarHeader>

        <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
          {loading && spreadsheets.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          ) : spreadsheets.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              No spreadsheets yet
            </Typography>
          ) : (
            <List disablePadding>
              {spreadsheets.map((ss) => (
                <SpreadsheetListItem
                  key={ss.id}
                  active={currentSpreadsheet?.id === ss.id}
                  onClick={() => handleSelectSpreadsheet(ss.id)}
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <SpreadsheetIcon sx={{ color: 'text.secondary' }} fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={ss.name}
                    secondary={`${ss.sheets?.length || 1} ${(ss.sheets?.length || 1) === 1 ? 'sheet' : 'sheets'}`}
                    primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteSpreadsheet(ss.id)
                    }}
                    aria-label={`Delete ${ss.name}`}
                    sx={{ opacity: 0, '.MuiListItemButton-root:hover &': { opacity: 0.5 }, '&:hover': { opacity: 1 } }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </SpreadsheetListItem>
              ))}
            </List>
          )}
        </Box>

        <Box sx={{ p: 1.5, borderTop: (theme) => `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
          <ImportFromMenu
            currentFeature={FeatureKey.SPREADSHEETS}
            onImport={async (output) => {
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
            }}
            fullWidth
          />
        </Box>
      </Sidebar>

      {/* Main Content */}
      <MainContent>
        {currentSpreadsheet ? (
          <>
            {/* Toolbar */}
            <Toolbar>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {currentSpreadsheet.name}
                </Typography>
                {hasUnsavedChanges && (
                  <Chip
                    label="Unsaved"
                    size="small"
                    sx={{ height: 20, fontSize: '12px', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
                  />
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="Undo">
                  <IconButton size="small">
                    <UndoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Redo">
                  <IconButton size="small">
                    <RedoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />

                <ActionButton
                  size="small"
                  startIcon={<UploadIcon />}
                  onClick={handleTriggerImport}
                >
                  Import
                </ActionButton>
                <ActionButton
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={(e) => setExportMenuAnchor(e.currentTarget)}
                >
                  Export
                </ActionButton>
                <ActionButton
                  size="small"
                  startIcon={<AIIcon />}
                  onClick={handleOpenAiDialog}
                >
                  AI Formula
                </ActionButton>
                <ActionButton
                  variant="contained"
                  size="small"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={saving || !hasUnsavedChanges}
                >
                  {saving ? 'Saving...' : 'Save'}
                </ActionButton>
              </Box>
            </Toolbar>

            {/* Formula Bar */}
            <FormulaBar
              cellRef={currentCellRef}
              value={currentCellValue}
              formula={currentCellFormula}
              onChange={handleFormulaBarChange}
              onApply={handleFormulaBarApply}
              onCancel={handleFormulaBarCancel}
              disabled={!currentSpreadsheet}
            />

            {/* Spreadsheet Grid */}
            <SpreadsheetArea>
              <HandsontableEditor
                ref={handsontableRef}
                data={localData}
                onCellChange={handleCellChange}
                onSelectionChange={handleSelectionChange}
                formulas={true}
              />
            </SpreadsheetArea>

            {/* Sheet Tabs */}
            <SheetTabs>
              {currentSpreadsheet.sheets?.map((sheet, index) => (
                <SheetTab
                  key={index}
                  label={sheet.name}
                  size="small"
                  active={activeSheetIndex === index}
                  onClick={() => handleSelectSheet(index)}
                  onDoubleClick={() => openRenameDialog(index)}
                  onDelete={
                    currentSpreadsheet.sheets.length > 1
                      ? () => handleDeleteSheet(index)
                      : undefined
                  }
                />
              ))}
              <Tooltip title="Add Sheet">
                <IconButton size="small" onClick={handleAddSheet}>
                  <AddIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </SheetTabs>
          </>
        ) : (
          <EmptyState>
            <SpreadsheetIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
              No Spreadsheet Selected
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3 }}>
              Create a new spreadsheet or select one from the sidebar.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <ActionButton
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleOpenCreateDialog}
              >
                Create Spreadsheet
              </ActionButton>
              <ActionButton
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={handleTriggerImport}
              >
                Import File
              </ActionButton>
            </Box>
          </EmptyState>
        )}

        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".csv,.xlsx,.xls"
          onChange={handleImport}
        />
      </MainContent>

      {/* Create Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={handleCloseCreateDialog}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Create New Spreadsheet</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Spreadsheet Name"
            value={newSpreadsheetName}
            onChange={(e) => setNewSpreadsheetName(e.target.value)}
            sx={{ mt: 2 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newSpreadsheetName) {
                handleCreateSpreadsheet()
              }
            }}
          />
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={setSelectedConnectionId}
            label="Import from Connection (Optional)"
            size="small"
            showStatus
          />
          {selectedConnectionId && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              Data from the selected connection will be imported into the new spreadsheet.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateSpreadsheet}
            disabled={!newSpreadsheetName || loading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Rename Sheet Dialog */}
      <Dialog
        open={renameDialogOpen}
        onClose={() => setRenameDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Rename Sheet</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Sheet Name"
            value={newSheetName}
            onChange={(e) => setNewSheetName(e.target.value)}
            sx={{ mt: 2 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newSheetName) {
                handleRenameSheet()
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleRenameSheet}
            disabled={!newSheetName}
          >
            Rename
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI Formula Dialog */}
      <Dialog
        open={aiDialogOpen}
        onClose={handleCloseAiDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AIIcon sx={{ color: 'text.secondary' }} />
            Generate Formula with AI
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Describe what you want to calculate in plain English.
          </Typography>
          <TextField
            autoFocus
            fullWidth
            multiline
            rows={3}
            placeholder="e.g., Sum all values in column A where column B equals 'Sales'"
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            The formula will be inserted into the currently selected cell ({currentCellRef})
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAiDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAIFormula}
            disabled={!aiPrompt}
            startIcon={<AIIcon />}
          >
            Generate
          </Button>
        </DialogActions>
      </Dialog>

      {/* Export Menu */}
      <Menu
        anchorEl={exportMenuAnchor}
        open={Boolean(exportMenuAnchor)}
        onClose={() => setExportMenuAnchor(null)}
      >
        <MenuItem onClick={() => handleExport('csv')}>
          <ListItemText primary="CSV" secondary="Comma-separated values" />
        </MenuItem>
        <MenuItem onClick={() => handleExport('xlsx')}>
          <ListItemText primary="Excel (.xlsx)" secondary="Microsoft Excel format" />
        </MenuItem>
        <MenuItem onClick={() => handleExport('json')}>
          <ListItemText primary="JSON" secondary="JavaScript Object Notation" />
        </MenuItem>
      </Menu>

      {error && (
        <Alert
          severity="error"
          onClose={handleDismissError}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400 }}
        >
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}
