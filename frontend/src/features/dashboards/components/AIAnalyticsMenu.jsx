/**
 * AI Analytics dropdown menu.
 */
import React from 'react'
import { Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material'
import {
  AutoAwesome as AIIcon,
  TrendingUp as TrendIcon,
  Warning as AnomalyIcon,
} from '@mui/icons-material'

export default function AIAnalyticsMenu({ anchorEl, onClose, onAction }) {
  return (
    <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={onClose}>
      <MenuItem onClick={() => onAction('insights')}>
        <ListItemIcon><AIIcon /></ListItemIcon>
        <ListItemText>Generate Insights</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAction('trends')}>
        <ListItemIcon><TrendIcon /></ListItemIcon>
        <ListItemText>Predict Trends</ListItemText>
      </MenuItem>
      <MenuItem onClick={() => onAction('anomalies')}>
        <ListItemIcon><AnomalyIcon /></ListItemIcon>
        <ListItemText>Detect Anomalies</ListItemText>
      </MenuItem>
    </Menu>
  )
}
