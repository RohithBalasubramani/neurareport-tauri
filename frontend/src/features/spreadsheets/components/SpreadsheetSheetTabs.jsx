import { IconButton, Tooltip } from '@mui/material'
import { Add as AddIcon } from '@mui/icons-material'
import { SheetTabsContainer, SheetTab } from './styledComponents'

export default function SpreadsheetSheetTabs({
  sheets,
  activeSheetIndex,
  onSelectSheet,
  onRenameSheet,
  onDeleteSheet,
  onAddSheet,
}) {
  return (
    <SheetTabsContainer>
      {sheets?.map((sheet, index) => (
        <SheetTab
          key={index}
          label={sheet.name}
          size="small"
          active={activeSheetIndex === index}
          onClick={() => onSelectSheet(index)}
          onDoubleClick={() => onRenameSheet(index)}
          onDelete={
            sheets.length > 1
              ? () => onDeleteSheet(index)
              : undefined
          }
        />
      ))}
      <Tooltip title="Add Sheet">
        <IconButton size="small" onClick={onAddSheet}>
          <AddIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </SheetTabsContainer>
  )
}
