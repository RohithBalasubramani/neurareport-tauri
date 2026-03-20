import {
  Box,
  Typography,
  Popover,
  List,
  ListItemButton,
  ListItemText,
} from '@mui/material'
import { SCENARIO_VARIANTS, VARIANT_CONFIG } from '../constants/widgetVariants'

export default function VariantPickerPopover({
  anchorEl,
  widget,
  onClose,
  onSelect,
}) {
  return (
    <Popover
      open={Boolean(anchorEl)}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      transformOrigin={{ vertical: 'top', horizontal: 'left' }}
      slotProps={{
        paper: {
          sx: { maxHeight: 300, minWidth: 200, maxWidth: 260 },
        },
      }}
    >
      {widget && (
        <Box sx={{ py: 0.5 }}>
          <Typography
            variant="caption"
            sx={{ fontWeight: 600, px: 2, py: 0.5, color: 'text.secondary', display: 'block' }}
          >
            {widget.label} Variants
          </Typography>
          <List dense disablePadding>
            {(SCENARIO_VARIANTS[widget.type] || []).map((v) => {
              const vConfig = VARIANT_CONFIG[v]
              return (
                <ListItemButton
                  key={v}
                  onClick={() => onSelect(widget.type, v)}
                  sx={{ py: 0.5, px: 2 }}
                >
                  <ListItemText
                    primary={vConfig?.label || v}
                    secondary={vConfig?.description || ''}
                    primaryTypographyProps={{ variant: 'body2', fontSize: '14px' }}
                    secondaryTypographyProps={{ variant: 'caption', fontSize: '12px', noWrap: true }}
                  />
                </ListItemButton>
              )
            })}
          </List>
        </Box>
      )}
    </Popover>
  )
}
