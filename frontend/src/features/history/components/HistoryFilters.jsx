/**
 * Filter controls for HistoryPage
 */
import React from 'react'
import {
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import { StyledFormControl } from '@/styles'
import { FilterContainer } from './HistoryStyledComponents'

export default function HistoryFilters({
  statusFilter,
  onStatusFilterChange,
  templateFilter,
  onTemplateFilterChange,
  templates,
}) {
  return (
    <FilterContainer direction="row" spacing={2}>
      <StyledFormControl size="small">
        <InputLabel>Status</InputLabel>
        <Select
          value={statusFilter}
          onChange={(e) => {
            const nextStatus = e.target.value
            onStatusFilterChange(nextStatus)
          }}
          label="Status"
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="completed">Completed</MenuItem>
          <MenuItem value="failed">Failed</MenuItem>
          <MenuItem value="running">Running</MenuItem>
          <MenuItem value="cancelled">Cancelled</MenuItem>
        </Select>
      </StyledFormControl>
      <StyledFormControl size="small" sx={{ minWidth: 200 }}>
        <InputLabel>Design</InputLabel>
        <Select
          value={templateFilter}
          onChange={(e) => {
            const nextTemplate = e.target.value
            onTemplateFilterChange(nextTemplate)
          }}
          label="Design"
        >
          <MenuItem value="">All Designs</MenuItem>
          {templates.map((tpl) => (
            <MenuItem key={tpl.id} value={tpl.id}>
              {tpl.name || tpl.id.slice(0, 12)}
            </MenuItem>
          ))}
        </Select>
      </StyledFormControl>
    </FilterContainer>
  )
}
