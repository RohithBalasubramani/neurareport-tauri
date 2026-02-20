/**
 * Shared Style Mixins & Helpers
 * Reusable style patterns, constants, and factory functions.
 */

import { alpha } from '@mui/material'

// ---------------------------------------------------------------------------
// EASING & TRANSITIONS
// ---------------------------------------------------------------------------

export const EASING = 'cubic-bezier(0.22, 1, 0.36, 1)'

export const transition = {
  fast: `all 0.15s cubic-bezier(0.22, 1, 0.36, 1)`,
  normal: `all 0.2s cubic-bezier(0.22, 1, 0.36, 1)`,
  slow: `all 0.3s cubic-bezier(0.22, 1, 0.36, 1)`,
}

// ---------------------------------------------------------------------------
// GLASS EFFECT
// ---------------------------------------------------------------------------

export const glass = (theme, opts = {}) => {
  const { blur = 20, opacity = 0.8, border = true } = opts
  return {
    backgroundColor: alpha(theme.palette.background.paper, opacity),
    backdropFilter: `blur(${blur}px)`,
    ...(border && {
      border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
    }),
  }
}

// ---------------------------------------------------------------------------
// SHADOWS
// ---------------------------------------------------------------------------

export const shadow = {
  card: (theme) =>
    `0 8px 32px ${alpha(theme.palette.common.black, 0.08)}`,
  cardHover: (theme) =>
    `0 12px 48px ${alpha(theme.palette.common.black, 0.12)}`,
  small: (theme) =>
    `0 4px 14px ${alpha(theme.palette.text.primary, 0.15)}`,
  focus: (theme) =>
    `0 0 0 3px ${alpha(theme.palette.text.primary, 0.08)}`,
}

// ---------------------------------------------------------------------------
// BACKGROUND PATTERNS
// ---------------------------------------------------------------------------

export const chartPaperGrid = (opacity = 0.02) =>
  `repeating-linear-gradient(to right, rgba(59, 130, 246, ${opacity}) 0, rgba(59, 130, 246, ${opacity}) 1px, transparent 1px, transparent 60px), repeating-linear-gradient(to bottom, rgba(59, 130, 246, ${opacity}) 0, rgba(59, 130, 246, ${opacity}) 1px, transparent 1px, transparent 60px)`
