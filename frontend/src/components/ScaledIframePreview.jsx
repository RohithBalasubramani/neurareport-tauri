import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Box from '@mui/material/Box'
import { alpha } from '@mui/material/styles'
import { neutral, secondary } from '@/app/theme'

import { DEFAULT_PAGE_DIMENSIONS } from '../utils/preview'

const MIN_SCALE = 0.01

const getDevicePixelRatio = () =>
  (typeof window !== 'undefined' && window.devicePixelRatio) ? window.devicePixelRatio : 1

const parseCssLength = (value) => {
  if (!value || value === 'none' || value === 'auto' || typeof value !== 'string') return null
  const lower = value.toLowerCase()
  const numeric = Number.parseFloat(lower)
  if (!Number.isFinite(numeric) || numeric <= 0) return null
  if (lower.endsWith('px')) return numeric
  if (typeof window !== 'undefined') {
    if (lower.endsWith('vh')) {
      return window.innerHeight * (numeric / 100)
    }
    if (lower.endsWith('vw')) {
      return window.innerWidth * (numeric / 100)
    }
  }
  return null
}

const roundScaleForDpr = (scale) => {
  if (!Number.isFinite(scale) || scale <= 0) return 1
  const dpr = getDevicePixelRatio()
  const factor = Math.max(100, Math.round(dpr * 100))
  return Math.max(MIN_SCALE, Math.round(scale * factor) / factor)
}

const parseAspectRatio = (value) => {
  if (value == null) return null

  const fromNumbers = (wRaw, hRaw) => {
    const w = Number(wRaw)
    const h = Number(hRaw)
    if (!Number.isFinite(w) || !Number.isFinite(h) || w <= 0 || h <= 0) return null
    return {
      css: `${w} / ${h}`,
      ratio: w / h,
    }
  }

  if (Array.isArray(value) && value.length === 2) {
    return fromNumbers(value[0], value[1])
  }

  if (typeof value === 'number') {
    return value > 0 ? fromNumbers(value, 1) : null
  }

  if (typeof value === 'string') {
    const trimmed = value.trim()
    if (!trimmed) return null
    const slashMatch = trimmed.match(/^(\d*\.?\d+)\s*\/\s*(\d*\.?\d+)$/)
    if (slashMatch) {
      return fromNumbers(slashMatch[1], slashMatch[2])
    }
    const numeric = Number(trimmed)
    if (Number.isFinite(numeric) && numeric > 0) {
      return fromNumbers(numeric, 1)
    }
    return {
      css: trimmed,
      ratio: null,
    }
  }

  return null
}

/**
 * Keeps HTML previews crisp by measuring the iframe content and scaling it
 * to the available container box. We read the iframe body (when same-origin)
 * after load, and fall back to declared page dimensions otherwise.
 * Scale recalculates on iframe load, container resize, and window resize/zoom.
 * `fit` lets callers force scaling by width/height instead of the default "contain".
 */
export default function ScaledIframePreview({
  src,
  title,
  pageWidth = DEFAULT_PAGE_DIMENSIONS.width,
  pageHeight = DEFAULT_PAGE_DIMENSIONS.height,
  sx,
  loading = 'lazy',
  background = 'white',
  frameAspectRatio = null,
  fit = 'contain', // layout fit strategy for scaling
  contentAlign = 'center',
  pageShadow = false,
  pageBorderColor = alpha(neutral[900], 0.12),
  pageRadius = 0,
  marginGuides = false,
  clampToParentHeight = false,
  pageChrome = true,
}) {
  const containerRef = useRef(null)
  const iframeRef = useRef(null)
  const rafRef = useRef(null)
  const timeoutRef = useRef(null)
  const [scale, setScale] = useState(1)
  const [contentSize, setContentSize] = useState({
    width: pageWidth,
    height: pageHeight,
  })
  const contentSizeRef = useRef(contentSize)
  const aspect = useMemo(() => parseAspectRatio(frameAspectRatio), [frameAspectRatio])
  const marginGuideConfig = useMemo(() => {
    if (!marginGuides) return null
    if (typeof marginGuides === 'object') {
      const inset = Math.max(0, Number(marginGuides.inset ?? marginGuides.offset ?? 36))
      return {
        inset,
        color: marginGuides.color || alpha(secondary.violet[500], 0.28),
      }
    }
    return {
      inset: 36,
      color: alpha(secondary.violet[500], 0.28),
    }
  }, [marginGuides])

  const schedule = useCallback((cb) => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = requestAnimationFrame(() => {
      rafRef.current = null
      cb()
    })
  }, [])

  const updateScale = useCallback(
    (dims) => {
      const target = dims || contentSizeRef.current
      const container = containerRef.current
      if (!container || !target.width || !target.height) return

      const rect = container.getBoundingClientRect()
      const availableWidth = rect.width || container.clientWidth || target.width
      let availableHeightRaw = rect.height || container.clientHeight || 0
      if (!availableHeightRaw && aspect?.ratio) {
        availableHeightRaw = availableWidth / aspect.ratio
      }
      if (!availableHeightRaw) {
        availableHeightRaw = target.height
      }
      if (clampToParentHeight) {
        let ancestor = container.parentElement
        while (ancestor) {
          const ancestorRect = ancestor.getBoundingClientRect?.()
          const ancestorHeight = ancestorRect?.height || ancestor.clientHeight || 0
          const computedStyle = typeof window !== 'undefined' ? window.getComputedStyle?.(ancestor) : null
          if (computedStyle) {
            const maxHeightPx = parseCssLength(computedStyle.maxHeight)
            if (maxHeightPx) {
              availableHeightRaw = Math.min(availableHeightRaw, maxHeightPx)
            }
            const heightPx = parseCssLength(computedStyle.height)
            if (heightPx) {
              availableHeightRaw = Math.min(availableHeightRaw, heightPx)
            }
          }
          if (ancestorHeight > 0) {
            availableHeightRaw = Math.min(availableHeightRaw, ancestorHeight)
            break
          }
          ancestor = ancestor.parentElement
        }
      }
      const widthRatio = availableWidth / target.width
      const heightRatio = availableHeightRaw > 0 ? availableHeightRaw / target.height : widthRatio
      let rawScale
      if (fit === 'width') {
        rawScale = widthRatio
        if (heightRatio > 0 && heightRatio < rawScale) {
          rawScale = heightRatio
        }
      } else if (fit === 'height') {
        rawScale = heightRatio
      } else {
        rawScale = Math.min(widthRatio, heightRatio)
      }
      if (!Number.isFinite(rawScale) || rawScale <= 0) {
        rawScale = 1
      }
      const nextScale = roundScaleForDpr(rawScale)

      setScale((prev) => (Math.abs(prev - nextScale) < 0.002 ? prev : nextScale))
    },
    [aspect?.ratio, fit, clampToParentHeight],
  )

  const applyContentSize = useCallback(
    (dims) => {
      const safe = {
        width: Math.max(1, Math.ceil(dims?.width || pageWidth)),
        height: Math.max(1, Math.ceil(dims?.height || pageHeight)),
      }
      contentSizeRef.current = safe
      setContentSize(safe)
      schedule(() => updateScale(safe))
    },
    [pageHeight, pageWidth, schedule, updateScale],
  )

  const measureIframeContent = useCallback(() => {
    const fallback = { width: pageWidth, height: pageHeight }
    const iframe = iframeRef.current
    if (!iframe) return fallback

    try {
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (!doc) return fallback
      const body = doc.body
      const html = doc.documentElement
      if (body) {
        body.style.overflow = 'hidden'
      }
      if (html) {
        html.style.overflow = 'hidden'
      }
      const measuredWidth = Math.max(
        body?.scrollWidth || 0,
        body?.offsetWidth || 0,
        html?.scrollWidth || 0,
        html?.offsetWidth || 0,
        fallback.width,
      )
      const measuredHeight = Math.max(
        body?.scrollHeight || 0,
        body?.offsetHeight || 0,
        html?.scrollHeight || 0,
        html?.offsetHeight || 0,
        fallback.height,
      )
      return {
        width: Math.ceil(measuredWidth),
        height: Math.ceil(measuredHeight),
      }
    } catch {
      // Cross-origin frames cannot be inspected; fall back to declared dimensions.
      return fallback
    }
  }, [pageHeight, pageWidth])

  const refreshContentSize = useCallback(() => {
    const dims = measureIframeContent()
    applyContentSize(dims)
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    // re-measure shortly after load in case fonts/styles settle asynchronously
    timeoutRef.current = setTimeout(() => {
      timeoutRef.current = null
      const postDims = measureIframeContent()
      applyContentSize(postDims)
    }, 150)
  }, [applyContentSize, measureIframeContent])

  useEffect(() => {
    const iframe = iframeRef.current
    if (!iframe) return undefined
    const handleLoad = () => refreshContentSize()
    iframe.addEventListener('load', handleLoad)
    return () => {
      iframe.removeEventListener('load', handleLoad)
    }
  }, [refreshContentSize, src])

  useEffect(() => {
    applyContentSize({ width: pageWidth, height: pageHeight })
  }, [applyContentSize, pageHeight, pageWidth, src])

  useEffect(() => {
    if (typeof ResizeObserver === 'undefined') {
      return undefined
    }
    const container = containerRef.current
    if (!container) return undefined
    const observer = new ResizeObserver(() => schedule(() => updateScale()))
    observer.observe(container)
    return () => observer.disconnect()
  }, [schedule, updateScale])

  useEffect(() => {
    const handleWindowResize = () => schedule(() => updateScale())
    window.addEventListener('resize', handleWindowResize)
    return () => window.removeEventListener('resize', handleWindowResize)
  }, [schedule, updateScale])

  useEffect(
    () => () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    },
    [],
  )

  const scaledHeight = contentSize.height * scale
  const scaledWidth = contentSize.width * scale
  const alignTop = contentAlign === 'top'
  const containerStyles = {
    position: 'relative',
    width: '100%',
    overflow: 'hidden',
    ...sx,
  }
  if (aspect?.css) {
    containerStyles.aspectRatio = aspect.css
    containerStyles.height = 'auto'
  }
  const positioned = Boolean(aspect?.css)
  const resolvedPageRadius = pageChrome && Number.isFinite(Number(pageRadius))
    ? Math.max(Number(pageRadius), 0)
    : 0
  const resolvedPageShadow = pageChrome && pageShadow
    ? (typeof pageShadow === 'string' ? pageShadow : `0 32px 48px ${alpha(neutral[900], 0.18)}`)
    : 'none'
  const resolvedBorderColor = pageChrome && typeof pageBorderColor === 'string' && pageBorderColor.trim()
    ? pageBorderColor
    : null
  const resolvedBackground = pageChrome ? background : 'transparent'
  const marginInset = marginGuideConfig
    ? Math.max(0, Math.min(marginGuideConfig.inset, Math.min(contentSize.width, contentSize.height) / 2))
    : 0

  return (
    <Box ref={containerRef} sx={containerStyles}>
      <Box
        sx={{
          position: positioned ? 'absolute' : 'relative',
          top: positioned ? (alignTop ? 0 : '50%') : 0,
          left: positioned ? '50%' : 0,
          width: contentSize.width,
          height: contentSize.height,
          transform: `scale(${scale})`,
          transformOrigin: 'top left',
          pointerEvents: 'auto',
        }}
        style={
          positioned
            ? {
                marginLeft: `${-scaledWidth / 2}px`,
                ...(alignTop ? {} : { marginTop: `${-scaledHeight / 2}px` }),
              }
            : undefined
        }
      >
        <Box
          sx={{
            width: contentSize.width,
            height: contentSize.height,
            borderRadius: resolvedPageRadius,
            overflow: 'hidden',
            bgcolor: resolvedBackground,
            boxShadow: resolvedPageShadow,
            border: resolvedBorderColor ? `1px solid ${resolvedBorderColor}` : 'none',
            position: 'relative',
          }}
        >
          <iframe
            ref={iframeRef}
            src={src}
            title={title}
            loading={loading}
            style={{
              width: contentSize.width,
              height: contentSize.height,
              border: 0,
              display: 'block',
              background: pageChrome ? background : undefined,
            }}
          />
          {marginGuideConfig && marginInset > 0 && (
            <Box
              aria-hidden
              sx={{
                position: 'absolute',
                inset: marginInset,
                border: '1px dashed',
                borderColor: marginGuideConfig.color,
                borderRadius: Math.max(resolvedPageRadius - 6, 0),
                pointerEvents: 'none',
              }}
              style={{
                borderStyle: 'dashed',
              }}
            />
          )}
        </Box>
      </Box>
      {!positioned && (
        <Box sx={{ width: '100%', height: scaledHeight, visibility: 'hidden', pointerEvents: 'none' }} />
      )}
    </Box>
  )
}
