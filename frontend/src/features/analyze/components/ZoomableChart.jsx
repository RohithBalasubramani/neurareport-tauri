import { useCallback, useMemo, useState, useRef } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Brush,
  Cell,
  ReferenceArea,
} from 'recharts'
import { Box, IconButton, Stack, Typography, Chip, CircularProgress, Tooltip as MuiTooltip, alpha } from '@mui/material'
import { neutral, palette, secondary } from '@/app/theme'
import ZoomOutMapIcon from '@mui/icons-material/ZoomOutMap'
import ZoomInIcon from '@mui/icons-material/ZoomIn'
import DownloadIcon from '@mui/icons-material/Download'

// Chart colors use secondary palette 500 values per Design System v4/v5
const CHART_COLORS = [
  secondary.violet[500],   // #8B5CF6
  secondary.emerald[500],  // #10B981
  secondary.cyan[500],     // #06B6D4
  secondary.rose[500],     // #F43F5E
  secondary.teal[500],     // #14B8A6
  secondary.fuchsia[500],  // #D946EF
  secondary.slate[500],    // #64748B
  secondary.zinc[500],     // #71717A
]

const CHART_MARGINS = { top: 8, right: 16, bottom: 24, left: 8 }

export default function ZoomableChart({
  data = [],
  spec = {},
  height = 350,
  showBrush = true,
  showZoomControls = true,
}) {
  const chartRef = useRef(null)
  const [exporting, setExporting] = useState(false)
  const [zoomState, setZoomState] = useState({
    refAreaLeft: null,
    refAreaRight: null,
    startIndex: 0,
    endIndex: null,
    isZoomed: false,
  })

  const { type = 'bar', xField, yFields = [], title } = spec

  const displayData = useMemo(() => {
    if (!data || data.length === 0) return []

    if (zoomState.isZoomed && zoomState.startIndex !== null) {
      const end = zoomState.endIndex ?? data.length
      return data.slice(zoomState.startIndex, end + 1)
    }
    return data
  }, [data, zoomState])

  const handleMouseDown = useCallback((e) => {
    if (!e?.activeLabel) return
    setZoomState((prev) => ({
      ...prev,
      refAreaLeft: e.activeLabel,
      refAreaRight: null,
    }))
  }, [])

  const handleMouseMove = useCallback((e) => {
    if (!zoomState.refAreaLeft || !e?.activeLabel) return
    setZoomState((prev) => ({
      ...prev,
      refAreaRight: e.activeLabel,
    }))
  }, [zoomState.refAreaLeft])

  const handleMouseUp = useCallback(() => {
    if (!zoomState.refAreaLeft || !zoomState.refAreaRight) {
      setZoomState((prev) => ({
        ...prev,
        refAreaLeft: null,
        refAreaRight: null,
      }))
      return
    }

    let left = zoomState.refAreaLeft
    let right = zoomState.refAreaRight

    const leftIndex = data.findIndex((d) => d[xField] === left)
    const rightIndex = data.findIndex((d) => d[xField] === right)

    if (leftIndex > rightIndex) {
      [left, right] = [right, left]
    }

    const startIdx = Math.min(leftIndex, rightIndex)
    const endIdx = Math.max(leftIndex, rightIndex)

    if (endIdx - startIdx < 1) {
      setZoomState((prev) => ({
        ...prev,
        refAreaLeft: null,
        refAreaRight: null,
      }))
      return
    }

    setZoomState({
      refAreaLeft: null,
      refAreaRight: null,
      startIndex: startIdx,
      endIndex: endIdx,
      isZoomed: true,
    })
  }, [zoomState.refAreaLeft, zoomState.refAreaRight, data, xField])

  const handleResetZoom = useCallback(() => {
    setZoomState({
      refAreaLeft: null,
      refAreaRight: null,
      startIndex: 0,
      endIndex: null,
      isZoomed: false,
    })
  }, [])

  const handleExportChart = useCallback(async () => {
    if (!chartRef.current) return

    setExporting(true)
    try {
      const svgElement = chartRef.current.querySelector('svg')
      if (!svgElement) {
        console.warn('No SVG found to export')
        return
      }

      // Clone the SVG to avoid modifying the original
      const clonedSvg = svgElement.cloneNode(true)

      // Add white background
      const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      bgRect.setAttribute('width', '100%')
      bgRect.setAttribute('height', '100%')
      bgRect.setAttribute('fill', 'white')
      clonedSvg.insertBefore(bgRect, clonedSvg.firstChild)

      // Get SVG dimensions
      const bbox = svgElement.getBoundingClientRect()
      clonedSvg.setAttribute('width', bbox.width)
      clonedSvg.setAttribute('height', bbox.height)

      // Convert SVG to data URL
      const svgData = new XMLSerializer().serializeToString(clonedSvg)
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
      const svgUrl = URL.createObjectURL(svgBlob)

      // Create canvas and draw SVG
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = new Image()

      img.onload = () => {
        canvas.width = bbox.width * 2 // 2x for higher resolution
        canvas.height = bbox.height * 2
        ctx.scale(2, 2)
        ctx.fillStyle = 'white'
        ctx.fillRect(0, 0, bbox.width, bbox.height)
        ctx.drawImage(img, 0, 0)

        // Download as PNG
        const pngUrl = canvas.toDataURL('image/png')
        const link = document.createElement('a')
        link.href = pngUrl
        link.download = `chart_${title || 'export'}_${Date.now()}.png`
        link.click()

        URL.revokeObjectURL(svgUrl)
        setExporting(false)
      }

      img.onerror = () => {
        // Fallback to SVG download
        const link = document.createElement('a')
        link.href = svgUrl
        link.download = `chart_${title || 'export'}_${Date.now()}.svg`
        link.click()

        URL.revokeObjectURL(svgUrl)
        setExporting(false)
      }

      img.src = svgUrl
    } catch (err) {
      console.error('Failed to export chart:', err)
      setExporting(false)
    }
  }, [title])

  const handleBrushChange = useCallback((range) => {
    if (!range) return
    const { startIndex, endIndex } = range
    if (startIndex !== undefined && endIndex !== undefined) {
      setZoomState((prev) => ({
        ...prev,
        startIndex,
        endIndex,
        isZoomed: startIndex > 0 || endIndex < data.length - 1,
      }))
    }
  }, [data.length])

  const renderChart = () => {
    if (!xField || yFields.length === 0) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height }}>
          <Typography color="text.secondary">Invalid chart configuration</Typography>
        </Box>
      )
    }

    if (!displayData || displayData.length === 0) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height }}>
          <Typography color="text.secondary">No data available</Typography>
        </Box>
      )
    }

    const commonProps = {
      data: displayData,
      margin: CHART_MARGINS,
      onMouseDown: type !== 'pie' ? handleMouseDown : undefined,
      onMouseMove: type !== 'pie' ? handleMouseMove : undefined,
      onMouseUp: type !== 'pie' ? handleMouseUp : undefined,
    }

    const zoomArea =
      zoomState.refAreaLeft && zoomState.refAreaRight ? (
        <ReferenceArea
          x1={zoomState.refAreaLeft}
          x2={zoomState.refAreaRight}
          strokeOpacity={0.3}
          fill={secondary.violet[500]}
          fillOpacity={0.3}
        />
      ) : null

    const brush = showBrush && type !== 'pie' && data.length > 10 ? (
      <Brush
        dataKey={xField}
        height={24}
        stroke={secondary.violet[500]}
        travellerWidth={8}
        onChange={handleBrushChange}
        startIndex={zoomState.startIndex}
        endIndex={zoomState.endIndex ?? data.length - 1}
      />
    ) : null

    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {yFields.map((field, idx) => (
              <Line
                key={field}
                type="monotone"
                dataKey={field}
                stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
            {zoomArea}
            {brush}
          </LineChart>
        )

      case 'pie':
        return (
          <PieChart>
            <Pie
              data={displayData}
              dataKey={yFields[0]}
              nameKey={xField}
              cx="50%"
              cy="50%"
              innerRadius="40%"
              outerRadius="75%"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              labelLine={{ stroke: neutral[500], strokeWidth: 1 }}
            >
              {displayData.map((entry, idx) => (
                <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        )

      case 'scatter':
        return (
          <ScatterChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xField} name={xField} tick={{ fontSize: 12 }} />
            <YAxis dataKey={yFields[0]} name={yFields[0]} tick={{ fontSize: 12 }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter
              name={yFields[0]}
              data={displayData}
              fill={CHART_COLORS[0]}
            />
            {zoomArea}
            {brush}
          </ScatterChart>
        )

      case 'bar':
      default:
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={xField} tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {yFields.map((field, idx) => (
              <Bar
                key={field}
                dataKey={field}
                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                radius={[4, 4, 0, 0]}
              />
            ))}
            {zoomArea}
            {brush}
          </BarChart>
        )
    }
  }

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          {title && (
            <Typography variant="subtitle1" fontWeight={600}>
              {title}
            </Typography>
          )}
          <Chip label={type.toUpperCase()} size="small" variant="outlined" />
          {zoomState.isZoomed && (
            <Chip label="Zoomed" size="small" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
          )}
        </Stack>

        <Stack direction="row" spacing={0.5} alignItems="center">
          <MuiTooltip title="Export chart as PNG">
            <IconButton
              size="small"
              onClick={handleExportChart}
              disabled={exporting}
            >
              {exporting ? (
                <CircularProgress size={16} />
              ) : (
                <DownloadIcon fontSize="small" />
              )}
            </IconButton>
          </MuiTooltip>
          {showZoomControls && type !== 'pie' && (
            <>
              <IconButton
                size="small"
                onClick={handleResetZoom}
                disabled={!zoomState.isZoomed}
                title="Reset zoom"
              >
                <ZoomOutMapIcon fontSize="small" />
              </IconButton>
              <Typography variant="caption" color="text.secondary">
                Drag to zoom
              </Typography>
            </>
          )}
        </Stack>
      </Stack>

      <Box ref={chartRef} sx={{ width: '100%', height }}>
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </Box>

      {spec.description && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {spec.description}
        </Typography>
      )}
    </Box>
  )
}
