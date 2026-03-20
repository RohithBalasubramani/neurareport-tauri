import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  List,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  alpha,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  TableChart as SpreadsheetIcon,
} from '@mui/icons-material'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { FeatureKey } from '@/utils/crossPageTypes'
import { Sidebar, SidebarHeader, SpreadsheetListItem } from './styledComponents'

export default function SpreadsheetSidebar({
  spreadsheets,
  currentSpreadsheet,
  loading,
  onOpenCreateDialog,
  onSelectSpreadsheet,
  onDeleteSpreadsheet,
  onImportFromMenu,
}) {
  return (
    <Sidebar>
      <SidebarHeader>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Spreadsheets
        </Typography>
        <Tooltip title="New Spreadsheet">
          <IconButton size="small" onClick={onOpenCreateDialog}>
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
                onClick={() => onSelectSpreadsheet(ss.id)}
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
                    onDeleteSpreadsheet(ss.id)
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
          onImport={onImportFromMenu}
          fullWidth
        />
      </Box>
    </Sidebar>
  )
}
