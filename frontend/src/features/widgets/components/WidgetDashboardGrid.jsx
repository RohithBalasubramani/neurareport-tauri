import {
  Box,
  Typography,
  Chip,
  alpha,
  styled,
} from '@mui/material'
import WidgetRenderer from '@/features/dashboards/components/WidgetRenderer'
import { VARIANT_CONFIG } from '@/features/dashboards/constants/widgetVariants'

// ── Constants ────────────────────────────────────────────────────────────

const ROW_HEIGHT = 80 // px per grid row unit

// ── Styled ───────────────────────────────────────────────────────────────

const DashboardGrid = styled(Box)({
  display: 'grid',
  gridTemplateColumns: 'repeat(12, 1fr)',
  gridAutoRows: ROW_HEIGHT,
  gap: 12,
  width: '100%',
})

const WidgetCell = styled(Box)(({ theme }) => ({
  position: 'relative',
  borderRadius: 10,
  border: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
  transition: 'box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1), border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    boxShadow: `0 4px 24px ${alpha(theme.palette.common.black, 0.08)}`,
    borderColor: alpha(theme.palette.primary.main, 0.3),
  },
}))

const WidgetOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: 0,
  left: 0,
  right: 0,
  padding: theme.spacing(0.75, 1.5),
  background: `linear-gradient(transparent, ${alpha(theme.palette.background.paper, 0.92)})`,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  opacity: 0,
  transition: 'opacity 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '.MuiBox-root:hover > &': {
    opacity: 1,
  },
}))

export default function WidgetDashboardGrid({ widgets, cellMap, connectionId, loading, grid }) {
  return (
    <>
      <DashboardGrid>
        {widgets.map((widget) => {
          const { id, scenario, variant, question, relevance, size } = widget
          const cell = cellMap[id]
          const vConfig = VARIANT_CONFIG[variant]
          const label = vConfig?.label || variant || scenario

          // Use backend grid packing if available, else auto-size by widget size
          const sizeSpans = { compact: 3, normal: 4, expanded: 6, hero: 12 }
          const rowSpans = { compact: 3, normal: 4, expanded: 4, hero: 5 }
          const colSpan = cell
            ? `${cell.col_start} / ${cell.col_end}`
            : `span ${sizeSpans[size] || 4}`
          const rowSpan = cell
            ? `${cell.row_start} / ${cell.row_end}`
            : `span ${rowSpans[size] || 4}`

          return (
            <WidgetCell
              key={id}
              sx={{
                gridColumn: colSpan,
                gridRow: rowSpan,
              }}
            >
              <Box sx={{ height: '100%', width: '100%' }}>
                <WidgetRenderer
                  scenario={scenario}
                  variant={variant}
                  connectionId={connectionId}
                  showSourceBadge
                />
              </Box>
              <WidgetOverlay>
                <Typography
                  variant="caption"
                  sx={{ fontWeight: 600, flex: 1 }}
                  noWrap
                >
                  {question || label}
                </Typography>
                <Chip
                  label={`${Math.round(relevance * 100)}%`}
                  size="small"
                  color={relevance > 0.8 ? 'success' : 'default'}
                  variant="outlined"
                  sx={{ height: 18, fontSize: '10px' }}
                />
              </WidgetOverlay>
            </WidgetCell>
          )
        })}
      </DashboardGrid>

      {widgets.length === 0 && !loading && (
        <Box sx={{ py: 8, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No widgets recommended for this database.
          </Typography>
          <Typography variant="caption" color="text.disabled">
            Try a different query or check your database connection.
          </Typography>
        </Box>
      )}

      {/* Grid utilization */}
      {grid && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Typography variant="caption" color="text.disabled">
            {grid.total_cols}&times;{grid.total_rows} grid &middot; {grid.utilization_pct}%
            utilization
          </Typography>
        </Box>
      )}
    </>
  )
}
