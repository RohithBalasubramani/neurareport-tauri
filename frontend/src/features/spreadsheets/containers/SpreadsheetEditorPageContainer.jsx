/**
 * Spreadsheet Editor Page Container
 * Slim orchestrator — logic in useSpreadsheetEditor, UI in sub-components.
 */
import React from 'react'
import { Alert } from '@mui/material'
import { useSpreadsheetEditor } from '../hooks/useSpreadsheetEditor'
import { PageContainer, MainContent, SpreadsheetArea } from '../components/styledComponents'
import SpreadsheetSidebar from '../components/SpreadsheetSidebar'
import SpreadsheetToolbar from '../components/SpreadsheetToolbar'
import SpreadsheetSheetTabs from '../components/SpreadsheetSheetTabs'
import SpreadsheetEmptyState from '../components/SpreadsheetEmptyState'
import SpreadsheetDialogs from '../components/SpreadsheetDialogs'
import HandsontableEditor from '../components/HandsontableEditor'
import FormulaBar from '../components/FormulaBar'

export default function SpreadsheetEditorPage() {
  const {
    fileInputRef,
    handsontableRef,
    spreadsheets,
    currentSpreadsheet,
    activeSheetIndex,
    loading,
    saving,
    error,
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
  } = useSpreadsheetEditor()

  return (
    <PageContainer>
      <SpreadsheetSidebar
        spreadsheets={spreadsheets}
        currentSpreadsheet={currentSpreadsheet}
        loading={loading}
        onOpenCreateDialog={handleOpenCreateDialog}
        onSelectSpreadsheet={handleSelectSpreadsheet}
        onDeleteSpreadsheet={handleDeleteSpreadsheet}
        onImportFromMenu={handleImportFromMenu}
      />

      <MainContent>
        {currentSpreadsheet ? (
          <>
            <SpreadsheetToolbar
              spreadsheetName={currentSpreadsheet.name}
              hasUnsavedChanges={hasUnsavedChanges}
              saving={saving}
              onTriggerImport={handleTriggerImport}
              onExportClick={(e) => setExportMenuAnchor(e.currentTarget)}
              onOpenAiDialog={handleOpenAiDialog}
              onSave={handleSave}
            />

            <FormulaBar
              cellRef={currentCellRef}
              value={currentCellValue}
              formula={currentCellFormula}
              onChange={handleFormulaBarChange}
              onApply={handleFormulaBarApply}
              onCancel={handleFormulaBarCancel}
              disabled={!currentSpreadsheet}
            />

            <SpreadsheetArea>
              <HandsontableEditor
                ref={handsontableRef}
                data={localData}
                onCellChange={handleCellChange}
                onSelectionChange={handleSelectionChange}
                formulas={true}
              />
            </SpreadsheetArea>

            <SpreadsheetSheetTabs
              sheets={currentSpreadsheet.sheets}
              activeSheetIndex={activeSheetIndex}
              onSelectSheet={handleSelectSheet}
              onRenameSheet={openRenameDialog}
              onDeleteSheet={handleDeleteSheet}
              onAddSheet={handleAddSheet}
            />
          </>
        ) : (
          <SpreadsheetEmptyState
            onOpenCreateDialog={handleOpenCreateDialog}
            onTriggerImport={handleTriggerImport}
          />
        )}

        <input
          ref={fileInputRef}
          type="file"
          hidden
          accept=".csv,.xlsx,.xls"
          onChange={handleImport}
        />
      </MainContent>

      <SpreadsheetDialogs
        createDialogOpen={createDialogOpen}
        newSpreadsheetName={newSpreadsheetName}
        onNewSpreadsheetNameChange={setNewSpreadsheetName}
        selectedConnectionId={selectedConnectionId}
        onSelectedConnectionIdChange={setSelectedConnectionId}
        onCloseCreateDialog={handleCloseCreateDialog}
        onCreateSpreadsheet={handleCreateSpreadsheet}
        loading={loading}
        renameDialogOpen={renameDialogOpen}
        newSheetName={newSheetName}
        onNewSheetNameChange={setNewSheetName}
        onCloseRenameDialog={() => setRenameDialogOpen(false)}
        onRenameSheet={handleRenameSheet}
        aiDialogOpen={aiDialogOpen}
        aiPrompt={aiPrompt}
        onAiPromptChange={setAiPrompt}
        onCloseAiDialog={handleCloseAiDialog}
        onAIFormula={handleAIFormula}
        currentCellRef={currentCellRef}
        exportMenuAnchor={exportMenuAnchor}
        onCloseExportMenu={() => setExportMenuAnchor(null)}
        onExport={handleExport}
      />

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
