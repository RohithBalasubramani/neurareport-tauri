/**
 * HTML Sanitization Utilities
 *
 * Centralizes DOMPurify configs for all dangerouslySetInnerHTML usage.
 * Each config is Object.freeze()-ed for stable useMemo references.
 */
import DOMPurify from 'dompurify'

/** Search highlights and inline rich text (mark, em, span only). */
export const HIGHLIGHT_CONFIG = Object.freeze({
  ALLOWED_TAGS: ['mark', 'em', 'strong', 'b', 'i', 'span', 'br'],
  ALLOWED_ATTR: ['class'],
  ALLOW_DATA_ATTR: false,
})

/** Syntax-highlighted code (diff viewer, code blocks). */
export const CODE_HIGHLIGHT_CONFIG = Object.freeze({
  ALLOWED_TAGS: ['span'],
  ALLOWED_ATTR: ['class'],
  ALLOW_DATA_ATTR: false,
})

/** SVG diagram content — allows safe SVG, blocks script injection. */
export const SVG_CONFIG = Object.freeze({
  USE_PROFILES: { svg: true, svgFilters: true },
  FORBID_TAGS: ['script', 'foreignObject', 'iframe', 'object', 'embed'],
  FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'],
})

/** Sanitize search highlight HTML. */
export function sanitizeHighlight(dirty) {
  return DOMPurify.sanitize(dirty || '', HIGHLIGHT_CONFIG)
}

/** Sanitize syntax-highlighted code. */
export function sanitizeCodeHighlight(dirty) {
  return DOMPurify.sanitize(dirty || '', CODE_HIGHLIGHT_CONFIG)
}

/** Sanitize SVG content. */
export function sanitizeSVG(dirty) {
  return DOMPurify.sanitize(dirty || '', SVG_CONFIG)
}
