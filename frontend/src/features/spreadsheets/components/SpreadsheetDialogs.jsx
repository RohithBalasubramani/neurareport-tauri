import {
  Box,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  ListItemText,
} from '@mui/material'
import { AutoAwesome as AIIcon } from '@mui/icons-material'
import ConnectionSelector from '@/components/common/ConnectionSelector'

export default function SpreadsheetDialogs({
  // Create dialog
  createDialogOpen,
  newSpreadsheetName,
  onNewSpreadsheetNameChange,
  selectedConnectionId,
  onSelectedConnectionIdChange,
  onCloseCreateDialog,
  onCreateSpreadsheet,
  loading,
  // Rename dialog
  renameDialogOpen,
  newSheetName,
  onNewSheetNameChange,
  onCloseRenameDialog,
  onRenameSheet,
  // AI dialog
  aiDialogOpen,
  aiPrompt,
  onAiPromptChange,
  onCloseAiDialog,
  onAIFormula,
  currentCellRef,
  // Export menu
  exportMenuAnchor,
  onCloseExportMenu,
  onExport,
}) {
  return (
    <>
      {/* Create Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={onCloseCreateDialog}
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
            onChange={(e) => onNewSpreadsheetNameChange(e.target.value)}
            sx={{ mt: 2 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newSpreadsheetName) {
                onCreateSpreadsheet()
              }
            }}
          />
          <ConnectionSelector
            value={selectedConnectionId}
            onChange={onSelectedConnectionIdChange}
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
          <Button onClick={onCloseCreateDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={onCreateSpreadsheet}
            disabled={!newSpreadsheetName || loading}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Rename Sheet Dialog */}
      <Dialog
        open={renameDialogOpen}
        onClose={onCloseRenameDialog}
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
            onChange={(e) => onNewSheetNameChange(e.target.value)}
            sx={{ mt: 2 }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newSheetName) {
                onRenameSheet()
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onCloseRenameDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={onRenameSheet}
            disabled={!newSheetName}
          >
            Rename
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI Formula Dialog */}
      <Dialog
        open={aiDialogOpen}
        onClose={onCloseAiDialog}
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
            onChange={(e) => onAiPromptChange(e.target.value)}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            The formula will be inserted into the currently selected cell ({currentCellRef})
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={onCloseAiDialog}>Cancel</Button>
          <Button
            variant="contained"
            onClick={onAIFormula}
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
        onClose={onCloseExportMenu}
      >
        <MenuItem onClick={() => onExport('csv')}>
          <ListItemText primary="CSV" secondary="Comma-separated values" />
        </MenuItem>
        <MenuItem onClick={() => onExport('xlsx')}>
          <ListItemText primary="Excel (.xlsx)" secondary="Microsoft Excel format" />
        </MenuItem>
        <MenuItem onClick={() => onExport('json')}>
          <ListItemText primary="JSON" secondary="JavaScript Object Notation" />
        </MenuItem>
      </Menu>
    </>
  )
}
