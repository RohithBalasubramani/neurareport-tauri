import { useMemo } from 'react'
import Box from '@mui/material/Box'
import { alpha } from '@mui/material/styles'
import { neutral } from '@/app/theme'

import { DEFAULT_PAGE_DIMENSIONS } from '../utils/preview'
import useScaledIframePreview, { parseMarginGuides } from './useScaledIframePreview'

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
  const { containerRef, iframeRef, scale, contentSize, aspect } = useScaledIframePreview({
    pageWidth,
    pageHeight,
    frameAspectRatio,
    fit,
    clampToParentHeight,
    src,
  })

  const marginGuideConfig = useMemo(() => parseMarginGuides(marginGuides), [marginGuides])

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
