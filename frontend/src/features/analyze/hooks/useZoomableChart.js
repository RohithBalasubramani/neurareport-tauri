import { useCallback, useMemo, useState, useRef } from 'react'

export function useZoomableChart({ data = [], spec = {}, title }) {
  const chartRef = useRef(null)
  const [exporting, setExporting] = useState(false)
  const [zoomState, setZoomState] = useState({
    refAreaLeft: null,
    refAreaRight: null,
    startIndex: 0,
    endIndex: null,
    isZoomed: false,
  })

  const { xField } = spec

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

      const clonedSvg = svgElement.cloneNode(true)

      const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
      bgRect.setAttribute('width', '100%')
      bgRect.setAttribute('height', '100%')
      bgRect.setAttribute('fill', 'white')
      clonedSvg.insertBefore(bgRect, clonedSvg.firstChild)

      const bbox = svgElement.getBoundingClientRect()
      clonedSvg.setAttribute('width', bbox.width)
      clonedSvg.setAttribute('height', bbox.height)

      const svgData = new XMLSerializer().serializeToString(clonedSvg)
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
      const svgUrl = URL.createObjectURL(svgBlob)

      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = new Image()

      img.onload = () => {
        canvas.width = bbox.width * 2
        canvas.height = bbox.height * 2
        ctx.scale(2, 2)
        ctx.fillStyle = 'white'
        ctx.fillRect(0, 0, bbox.width, bbox.height)
        ctx.drawImage(img, 0, 0)

        const pngUrl = canvas.toDataURL('image/png')
        const link = document.createElement('a')
        link.href = pngUrl
        link.download = `chart_${title || 'export'}_${Date.now()}.png`
        link.click()

        URL.revokeObjectURL(svgUrl)
        setExporting(false)
      }

      img.onerror = () => {
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

  return {
    chartRef,
    exporting,
    zoomState,
    displayData,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleResetZoom,
    handleExportChart,
    handleBrushChange,
  }
}
