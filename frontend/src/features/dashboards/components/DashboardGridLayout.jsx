/**
 * Dashboard Grid Layout
 * React-grid-layout wrapper for drag-drop dashboard building.
 */
import { useState, useCallback, useMemo } from 'react'
import { Responsive, WidthProvider } from 'react-grid-layout'
import { Box, styled, alpha } from '@mui/material'
import { neutral, palette } from '@/app/theme'
import 'react-grid-layout/css/styles.css'
import 'react-resizable/css/styles.css'

const ResponsiveGridLayout = WidthProvider(Responsive)

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const GridContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  '& .react-grid-item': {
    transition: 'transform 200ms cubic-bezier(0.22, 1, 0.36, 1), all 200ms cubic-bezier(0.22, 1, 0.36, 1)',
    '&.react-grid-placeholder': {
      backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
      border: `2px dashed ${theme.palette.mode === 'dark' ? neutral[500] : neutral[700]}`,
      borderRadius: 8,  // Figma spec: 8px
    },
  },
  '& .react-grid-item.cssTransforms': {
    transitionProperty: 'transform',
  },
  '& .react-grid-item > .react-resizable-handle': {
    background: 'none',
    '&::after': {
      content: '""',
      position: 'absolute',
      right: 5,
      bottom: 5,
      width: 10,
      height: 10,
      borderRight: `2px solid ${alpha(theme.palette.text.primary, 0.3)}`,
      borderBottom: `2px solid ${alpha(theme.palette.text.primary, 0.3)}`,
      borderRadius: '0 0 4px 0',
    },
  },
  '& .react-grid-item:hover > .react-resizable-handle::after': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
  },
}))

// =============================================================================
// DEFAULT BREAKPOINTS & COLS
// =============================================================================

const BREAKPOINTS = { lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }
const COLS = { lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }
const ROW_HEIGHT = 80
const MARGIN = [16, 16]

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function DashboardGridLayout({
  widgets = [],
  layout = [],
  onLayoutChange,
  onWidgetResize,
  children,
  editable = true,
  rowHeight = ROW_HEIGHT,
  margin = MARGIN,
}) {
  const [currentBreakpoint, setCurrentBreakpoint] = useState('lg')

  // Generate layout from widgets if not provided
  const computedLayout = useMemo(() => {
    if (layout.length > 0) return layout

    return widgets.map((widget, index) => ({
      i: widget.id,
      x: widget.x ?? (index % 3) * 4,
      y: widget.y ?? Math.floor(index / 3) * 3,
      w: widget.w ?? 4,
      h: widget.h ?? 3,
      minW: widget.minW ?? 2,
      minH: widget.minH ?? 2,
      maxW: widget.maxW ?? 12,
      maxH: widget.maxH ?? 10,
    }))
  }, [layout, widgets])

  // Generate responsive layouts
  const layouts = useMemo(() => {
    const lg = computedLayout
    const md = computedLayout.map((item) => ({
      ...item,
      w: Math.min(item.w, 10),
      x: Math.min(item.x, 10 - item.w),
    }))
    const sm = computedLayout.map((item) => ({
      ...item,
      w: Math.min(item.w, 6),
      x: 0,
    }))
    const xs = computedLayout.map((item) => ({
      ...item,
      w: 4,
      x: 0,
    }))
    const xxs = computedLayout.map((item) => ({
      ...item,
      w: 2,
      x: 0,
    }))

    return { lg, md, sm, xs, xxs }
  }, [computedLayout])

  const handleLayoutChange = useCallback((currentLayout, allLayouts) => {
    onLayoutChange?.(currentLayout, allLayouts)
  }, [onLayoutChange])

  const handleBreakpointChange = useCallback((newBreakpoint) => {
    setCurrentBreakpoint(newBreakpoint)
  }, [])

  const handleResizeStop = useCallback((layout, oldItem, newItem) => {
    onWidgetResize?.(newItem.i, { w: newItem.w, h: newItem.h })
  }, [onWidgetResize])

  return (
    <GridContainer>
      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={BREAKPOINTS}
        cols={COLS}
        rowHeight={rowHeight}
        margin={margin}
        containerPadding={margin}
        isDraggable={editable}
        isResizable={editable}
        onLayoutChange={handleLayoutChange}
        onBreakpointChange={handleBreakpointChange}
        onResizeStop={handleResizeStop}
        draggableHandle=".widget-drag-handle"
        useCSSTransforms
        compactType="vertical"
      >
        {children}
      </ResponsiveGridLayout>
    </GridContainer>
  )
}

/**
 * Helper to generate a unique widget ID
 */
export function generateWidgetId() {
  return `widget_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Default widget dimensions by type
 */
export const DEFAULT_WIDGET_SIZES = {
  chart: { w: 4, h: 3, minW: 2, minH: 2 },
  metric: { w: 2, h: 2, minW: 2, minH: 1 },
  table: { w: 6, h: 4, minW: 3, minH: 2 },
  text: { w: 4, h: 2, minW: 2, minH: 1 },
  filter: { w: 3, h: 1, minW: 2, minH: 1 },
  map: { w: 6, h: 4, minW: 4, minH: 3 },
  image: { w: 3, h: 3, minW: 2, minH: 2 },
}
