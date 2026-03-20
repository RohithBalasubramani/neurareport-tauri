/**
 * More options menu + Column Settings dialog for DataTableToolbar
 */
import { useState, useCallback } from 'react'
import {
  Button,
  Stack,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  alpha,
  useTheme,
} from '@mui/material'
import {
  Download as DownloadIcon,
  ViewColumn as ColumnsIcon,
} from '@mui/icons-material'
import {
  StyledMenu,
  MenuSection,
  MenuLabel,
  StyledMenuItem,
} from './DataTableToolbarStyled'

export default function ToolbarMoreMenu({
  moreAnchor,
  onMoreClose,
  columns,
  hiddenColumns,
  visibleColumnCount,
  canConfigureColumns,
  onToggleColumn,
  onResetColumns,
  onExportCsv,
  onExportJson,
  exportCsvDisabled,
  exportJsonDisabled,
}) {
  const theme = useTheme()
  const [columnSettingsOpen, setColumnSettingsOpen] = useState(false)

  const handleOpenColumnSettings = useCallback(() => {
    if (!canConfigureColumns) return
    setColumnSettingsOpen(true)
    onMoreClose()
  }, [canConfigureColumns, onMoreClose])

  const handleCloseColumnSettings = useCallback(() => {
    setColumnSettingsOpen(false)
  }, [])

  const handleExportCsv = useCallback(() => {
    if (exportCsvDisabled || !onExportCsv) return
    onExportCsv()
    onMoreClose()
  }, [exportCsvDisabled, onExportCsv, onMoreClose])

  const handleExportJson = useCallback(() => {
    if (exportJsonDisabled || !onExportJson) return
    onExportJson()
    onMoreClose()
  }, [exportJsonDisabled, onExportJson, onMoreClose])

  return (
    <>
      <StyledMenu
        anchorEl={moreAnchor}
        open={Boolean(moreAnchor)}
        onClose={onMoreClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuSection>
          <MenuLabel>Export</MenuLabel>
          <StyledMenuItem
            onClick={handleExportCsv}
            disabled={exportCsvDisabled || !onExportCsv}
          >
            <DownloadIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
            Export as CSV
          </StyledMenuItem>
          <StyledMenuItem
            onClick={handleExportJson}
            disabled={exportJsonDisabled || !onExportJson}
          >
            <DownloadIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
            Export as JSON
          </StyledMenuItem>
        </MenuSection>
        <Divider sx={{ my: 1, mx: 2, borderColor: alpha(theme.palette.divider, 0.1) }} />
        <MenuSection>
          <MenuLabel>View</MenuLabel>
          <StyledMenuItem onClick={handleOpenColumnSettings} disabled={!canConfigureColumns}>
            <ColumnsIcon sx={{ fontSize: 16, mr: 1.5, color: 'text.secondary' }} />
            Column Settings
          </StyledMenuItem>
        </MenuSection>
      </StyledMenu>

      <Dialog open={columnSettingsOpen} onClose={handleCloseColumnSettings} maxWidth="xs" fullWidth>
        <DialogTitle>Column Settings</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={1.5}>
            <Typography variant="body2" color="text.secondary">
              Choose which columns are visible in the table.
            </Typography>
            <FormGroup>
              {columns.map((column) => {
                if (!column?.field) return null
                const isVisible = !hiddenColumns.includes(column.field)
                const disableToggle = isVisible && visibleColumnCount <= 1
                return (
                  <FormControlLabel
                    key={column.field}
                    control={
                      <Checkbox
                        checked={isVisible}
                        onChange={() => onToggleColumn?.(column.field)}
                        disabled={disableToggle}
                      />
                    }
                    label={column.headerName || column.field}
                  />
                )
              })}
            </FormGroup>
            {visibleColumnCount <= 1 && (
              <Typography variant="caption" color="text.secondary">
                At least one column must remain visible.
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => onResetColumns?.()} disabled={!hiddenColumns.length || !onResetColumns}>
            Reset
          </Button>
          <Button onClick={handleCloseColumnSettings} variant="contained">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
