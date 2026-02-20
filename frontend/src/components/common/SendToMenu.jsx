/**
 * SendToMenu – "Open in..." dropdown button for producer pages.
 *
 * Dynamically discovers which target pages accept the given output type
 * and renders a menu of contextual actions (e.g. "Chat with this", "Save to Knowledge").
 *
 * Props:
 *   outputType    – OutputType enum value
 *   payload       – { title, content, data, ... } to send
 *   sourceFeature – FeatureKey of the current page
 *   label?        – button label (default: "Open in...")
 *   variant?      – MUI button variant (default: "outlined")
 *   size?         – MUI button size (default: "small")
 *   disabled?     – disable the button
 */
import { useState, useCallback } from 'react'
import { Button, Menu, MenuItem, ListItemIcon, ListItemText, Typography } from '@mui/material'
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded'
import ChatRoundedIcon from '@mui/icons-material/ChatRounded'
import SaveRoundedIcon from '@mui/icons-material/SaveRounded'
import AddRoundedIcon from '@mui/icons-material/AddRounded'
import DescriptionRoundedIcon from '@mui/icons-material/DescriptionRounded'
import TableChartRoundedIcon from '@mui/icons-material/TableChartRounded'
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded'
import AutoFixHighRoundedIcon from '@mui/icons-material/AutoFixHighRounded'
import BarChartRoundedIcon from '@mui/icons-material/BarChartRounded'
import SummarizeRoundedIcon from '@mui/icons-material/SummarizeRounded'
import useCrossPageActions from '@/hooks/useCrossPageActions'
import { FEATURE_ACTIONS, TransferAction } from '@/utils/crossPageTypes'

const ACTION_ICONS = {
  [TransferAction.CHAT_WITH]: ChatRoundedIcon,
  [TransferAction.SAVE_TO]: SaveRoundedIcon,
  [TransferAction.ADD_TO]: AddRoundedIcon,
  [TransferAction.CREATE_FROM]: DescriptionRoundedIcon,
  [TransferAction.OPEN_IN]: TableChartRoundedIcon,
  [TransferAction.ENRICH]: AutoFixHighRoundedIcon,
  [TransferAction.VISUALIZE]: BarChartRoundedIcon,
}

const TARGET_ICONS = {
  docqa: ChatRoundedIcon,
  knowledge: SaveRoundedIcon,
  documents: DescriptionRoundedIcon,
  spreadsheets: TableChartRoundedIcon,
  dashboards: DashboardRoundedIcon,
  enrichment: AutoFixHighRoundedIcon,
  visualization: BarChartRoundedIcon,
  synthesis: AddRoundedIcon,
  summary: SummarizeRoundedIcon,
  reports: DescriptionRoundedIcon,
}

export default function SendToMenu({
  outputType,
  payload,
  sourceFeature,
  label = 'Open in\u2026',
  variant = 'outlined',
  size = 'small',
  disabled = false,
}) {
  const { sendTo, getAvailableTargets } = useCrossPageActions(sourceFeature)
  const [anchorEl, setAnchorEl] = useState(null)
  const targets = getAvailableTargets(outputType)

  const handleOpen = useCallback((e) => setAnchorEl(e.currentTarget), [])
  const handleClose = useCallback(() => setAnchorEl(null), [])

  const handleSelect = useCallback(
    (target) => {
      handleClose()
      const actionInfo = FEATURE_ACTIONS[target.key]
      if (actionInfo) {
        sendTo(target.key, actionInfo.action, payload)
      } else {
        sendTo(target.key, TransferAction.OPEN_IN, payload)
      }
    },
    [handleClose, payload, sendTo],
  )

  if (targets.length === 0) return null

  return (
    <>
      <Button
        variant={variant}
        size={size}
        disabled={disabled}
        startIcon={<OpenInNewRoundedIcon />}
        onClick={handleOpen}
        sx={{ textTransform: 'none', fontWeight: 500 }}
      >
        {label}
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        slotProps={{ paper: { sx: { minWidth: 220 } } }}
      >
        {targets.map((target) => {
          const actionInfo = FEATURE_ACTIONS[target.key]
          const IconComp =
            TARGET_ICONS[target.key] ||
            ACTION_ICONS[actionInfo?.action] ||
            OpenInNewRoundedIcon

          return (
            <MenuItem key={target.key} onClick={() => handleSelect(target)}>
              <ListItemIcon>
                <IconComp fontSize="small" />
              </ListItemIcon>
              <ListItemText>
                <Typography variant="body2">
                  {actionInfo?.label || `Open in ${target.label}`}
                </Typography>
              </ListItemText>
            </MenuItem>
          )
        })}
      </Menu>
    </>
  )
}
