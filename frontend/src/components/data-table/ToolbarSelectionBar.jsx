/**
 * Selection bar shown when rows are selected in DataTable
 */
import { Stack, Fade } from '@mui/material'
import { Delete as DeleteIcon } from '@mui/icons-material'
import {
  SelectionBar,
  SelectionText,
  SelectionBadge,
  SelectionAction,
  DeleteAction,
} from './DataTableToolbarStyled'

export default function ToolbarSelectionBar({
  numSelected,
  bulkActions,
  onBulkDelete,
}) {
  if (numSelected <= 0) return null

  return (
    <Fade in>
      <SelectionBar>
        <SelectionText>
          <SelectionBadge>{numSelected}</SelectionBadge>
          item{numSelected > 1 ? 's' : ''} selected
        </SelectionText>
        <Stack direction="row" spacing={1}>
          {bulkActions.map((action, index) => (
            <SelectionAction
              key={index}
              variant="outlined"
              size="small"
              startIcon={action.icon}
              onClick={action.onClick}
              disabled={action.disabled}
            >
              {action.label}
            </SelectionAction>
          ))}
          {onBulkDelete && (
            <DeleteAction
              variant="outlined"
              size="small"
              startIcon={<DeleteIcon sx={{ fontSize: 16 }} />}
              onClick={onBulkDelete}
            >
              Delete
            </DeleteAction>
          )}
        </Stack>
      </SelectionBar>
    </Fade>
  )
}
