/**
 * NeuraReport Design Tokens
 *
 * Architecture mirrors webshell's token system:
 *   REF_TOKENS (raw palette) → DEFAULT_SYS_TOKENS (semantic) → getThemeTokens()
 *
 * Values are sourced from the existing app/theme.js Design System v5.
 * Every var() reference is resolved to its final raw value.
 */

// ---------------------------------------------------------------------------
// REF_TOKENS — raw palette & primitive values (--ref-*)
// ---------------------------------------------------------------------------

export const REF_TOKENS = {
  /* neutral — warm paper tones (NeuraReport Design System v5) */
  '--ref-color-neutral-50': '#fdfdfc',
  '--ref-color-neutral-100': '#f4f2ed',
  '--ref-color-neutral-200': '#d4d2cc',
  '--ref-color-neutral-300': '#d4d2cc',
  '--ref-color-neutral-400': '#9CA3AF',
  '--ref-color-neutral-500': '#6f6f69',
  '--ref-color-neutral-700': '#374151',
  '--ref-color-neutral-900': '#111827',

  /* primary — blue accent (NeuraReport brand) */
  '--ref-color-primary-50': '#EFF6FF',
  '--ref-color-primary-100': '#DBEAFE',
  '--ref-color-primary-300': '#6A9EFA',
  '--ref-color-primary-500': '#3B82F6',
  '--ref-color-primary-600': '#2563EB',
  '--ref-color-primary-900': '#1D4ED8',

  /* emerald — success/positive */
  '--ref-color-emerald-50': '#ECFDF5',
  '--ref-color-emerald-100': '#D1FAE5',
  '--ref-color-emerald-200': '#A7F3D0',
  '--ref-color-emerald-300': '#6EE7B7',
  '--ref-color-emerald-400': '#34D399',
  '--ref-color-emerald-500': '#22C55E',
  '--ref-color-emerald-600': '#16A34A',
  '--ref-color-emerald-700': '#15803D',
  '--ref-color-emerald-800': '#166534',
  '--ref-color-emerald-900': '#14532D',

  /* amber — warning/caution */
  '--ref-color-amber-50': '#fffbeb',
  '--ref-color-amber-100': '#FEF3C7',
  '--ref-color-amber-200': '#FDE68A',
  '--ref-color-amber-300': '#FCD34D',
  '--ref-color-amber-400': '#FBBF24',
  '--ref-color-amber-500': '#F59E0B',
  '--ref-color-amber-600': '#D97706',
  '--ref-color-amber-700': '#B45309',
  '--ref-color-amber-800': '#92400E',
  '--ref-color-amber-900': '#78350F',

  /* red — error/danger */
  '--ref-color-red-50': '#fef2f2',
  '--ref-color-red-100': '#FEE2E2',
  '--ref-color-red-200': '#FECACA',
  '--ref-color-red-300': '#FCA5A5',
  '--ref-color-red-400': '#F87171',
  '--ref-color-red-500': '#EF4444',
  '--ref-color-red-600': '#DC2626',
  '--ref-color-red-700': '#B91C1C',
  '--ref-color-red-800': '#991B1B',
  '--ref-color-red-900': '#7F1D1D',

  /* blue — extended blue palette (charts, legacy compat) */
  '--ref-color-blue-100': '#D5E4FF',
  '--ref-color-blue-200': '#A5C4FC',
  '--ref-color-blue-300': '#6A9EFA',
  '--ref-color-blue-400': '#3B82F6',
  '--ref-color-blue-500': '#2563EB',
  '--ref-color-blue-600': '#1D4ED8',
  '--ref-color-blue-700': '#1E40AF',
  '--ref-color-blue-800': '#1E3A8A',
  '--ref-color-blue-900': '#172554',

  /* secondary accent palettes — charts, tags, badges only */
  /* slate */
  '--ref-color-slate-50': '#F8FAFC',
  '--ref-color-slate-100': '#F1F5F9',
  '--ref-color-slate-200': '#E2E8F0',
  '--ref-color-slate-300': '#CBD5E1',
  '--ref-color-slate-400': '#94A3B8',
  '--ref-color-slate-500': '#64748B',
  '--ref-color-slate-600': '#475569',
  '--ref-color-slate-700': '#334155',
  '--ref-color-slate-800': '#1E293B',
  '--ref-color-slate-900': '#0F172A',

  /* zinc */
  '--ref-color-zinc-50': '#FAFAFA',
  '--ref-color-zinc-100': '#F4F4F5',
  '--ref-color-zinc-200': '#E4E4E7',
  '--ref-color-zinc-300': '#D4D4D8',
  '--ref-color-zinc-400': '#A1A1AA',
  '--ref-color-zinc-500': '#71717A',
  '--ref-color-zinc-600': '#52525B',
  '--ref-color-zinc-700': '#3F3F46',
  '--ref-color-zinc-800': '#27272A',
  '--ref-color-zinc-900': '#18181B',

  /* stone */
  '--ref-color-stone-50': '#FAFAF9',
  '--ref-color-stone-100': '#F5F5F4',
  '--ref-color-stone-200': '#E7E5E4',
  '--ref-color-stone-300': '#D6D3D1',
  '--ref-color-stone-400': '#A8A29E',
  '--ref-color-stone-500': '#78716C',
  '--ref-color-stone-600': '#57534E',
  '--ref-color-stone-700': '#44403C',
  '--ref-color-stone-800': '#292524',
  '--ref-color-stone-900': '#1C1917',

  /* teal */
  '--ref-color-teal-50': '#F0FDFA',
  '--ref-color-teal-100': '#CCFBF1',
  '--ref-color-teal-200': '#99F6E4',
  '--ref-color-teal-300': '#5EEAD4',
  '--ref-color-teal-400': '#2DD4BF',
  '--ref-color-teal-500': '#14B8A6',
  '--ref-color-teal-600': '#0D9488',
  '--ref-color-teal-700': '#0F766E',
  '--ref-color-teal-800': '#115E59',
  '--ref-color-teal-900': '#134E4A',

  /* cyan */
  '--ref-color-cyan-50': '#ECFEFF',
  '--ref-color-cyan-100': '#CFFAFE',
  '--ref-color-cyan-200': '#A5F3FC',
  '--ref-color-cyan-300': '#67E8F9',
  '--ref-color-cyan-400': '#22D3EE',
  '--ref-color-cyan-500': '#06B6D4',
  '--ref-color-cyan-600': '#0891B2',
  '--ref-color-cyan-700': '#0E7490',
  '--ref-color-cyan-800': '#155E75',
  '--ref-color-cyan-900': '#164E63',

  /* violet */
  '--ref-color-violet-50': '#F5F3FF',
  '--ref-color-violet-100': '#EDE9FE',
  '--ref-color-violet-200': '#DDD6FE',
  '--ref-color-violet-300': '#C4B5FD',
  '--ref-color-violet-400': '#A78BFA',
  '--ref-color-violet-500': '#8B5CF6',
  '--ref-color-violet-600': '#7C3AED',
  '--ref-color-violet-700': '#6D28D9',
  '--ref-color-violet-800': '#5B21B6',
  '--ref-color-violet-900': '#4C1D95',

  /* fuchsia */
  '--ref-color-fuchsia-50': '#FDF4FF',
  '--ref-color-fuchsia-100': '#FAE8FF',
  '--ref-color-fuchsia-200': '#F5D0FE',
  '--ref-color-fuchsia-300': '#F0ABFC',
  '--ref-color-fuchsia-400': '#E879F9',
  '--ref-color-fuchsia-500': '#D946EF',
  '--ref-color-fuchsia-600': '#C026D3',
  '--ref-color-fuchsia-700': '#A21CAF',
  '--ref-color-fuchsia-800': '#86198F',
  '--ref-color-fuchsia-900': '#701A75',

  /* rose */
  '--ref-color-rose-50': '#FFF1F2',
  '--ref-color-rose-100': '#FFE4E6',
  '--ref-color-rose-200': '#FECDD3',
  '--ref-color-rose-300': '#FDA4AF',
  '--ref-color-rose-400': '#FB7185',
  '--ref-color-rose-500': '#F43F5E',
  '--ref-color-rose-600': '#E11D48',
  '--ref-color-rose-700': '#BE123C',
  '--ref-color-rose-800': '#9F1239',
  '--ref-color-rose-900': '#881337',

  /* purple — charts/badges */
  '--ref-color-purple-100': '#EDE9FE',
  '--ref-color-purple-200': '#DDD6FE',
  '--ref-color-purple-300': '#C4B5FD',
  '--ref-color-purple-400': '#A78BFA',
  '--ref-color-purple-500': '#8B5CF6',
  '--ref-color-purple-600': '#7C3AED',
  '--ref-color-purple-700': '#6D28D9',
  '--ref-color-purple-800': '#5B21B6',
  '--ref-color-purple-900': '#4C1D95',

  /* green — legacy compat */
  '--ref-color-green-100': '#D1F4E0',
  '--ref-color-green-200': '#A3E9C1',
  '--ref-color-green-300': '#08C18F',
  '--ref-color-green-400': '#08C18F',
  '--ref-color-green-500': '#22C55E',
  '--ref-color-green-600': '#16A34A',
  '--ref-color-green-700': '#15803D',
  '--ref-color-green-800': '#166534',
  '--ref-color-green-900': '#14532D',

  /* yellow */
  '--ref-color-yellow-100': '#FEF3C7',
  '--ref-color-yellow-200': '#FDE68A',
  '--ref-color-yellow-300': '#FCD34D',
  '--ref-color-yellow-400': '#FBBF24',
  '--ref-color-yellow-500': '#F59E0B',
  '--ref-color-yellow-600': '#D97706',
  '--ref-color-yellow-700': '#B45309',
  '--ref-color-yellow-800': '#92400E',
  '--ref-color-yellow-900': '#78350F',

  /* radius */
  '--ref-radius-xs': '4px',
  '--ref-radius-sm': '6px',
  '--ref-radius-base': '8px',
  '--ref-radius-md': '8px',
  '--ref-radius-toggle': '12px',
  '--ref-radius-lg': '12px',
  '--ref-radius-xl': '24px',
  '--ref-radius-pill': '999px',
  '--ref-radius-circle': '100px',
  '--ref-radius-zoom': '35px',

  /* shadows */
  '--ref-shadow-xsmall': '0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
  '--ref-shadow-sm': '0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
  '--ref-shadow-md': '0 2px 8px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.1)',
  '--ref-shadow-lg': '0 2px 8px rgba(0, 0, 0, 0.06), 0 16px 48px rgba(0, 0, 0, 0.12)',
  '--ref-shadow-ai-panel': '0px 4px 8.4px rgba(0, 0, 0, 0.25)',
}

// ---------------------------------------------------------------------------
// DEFAULT_SYS_TOKENS — semantic tokens (--sys-*) — this IS the light theme
// ---------------------------------------------------------------------------

export const DEFAULT_SYS_TOKENS = {
  /* backgrounds */
  '--sys-color-bg-app': '#fdfdfc',
  '--sys-color-bg-surface': '#FFFFFF',
  '--sys-color-bg-elevated': '#FFFFFF',
  '--sys-color-bg-muted': '#f4f2ed',
  '--sys-color-bg-overlay': 'rgba(17, 24, 39, 0.5)',
  '--sys-color-bg-tooltip': '#111827',
  '--sys-color-bg-input': '#f4f2ed',
  '--sys-color-bg-sidebar': '#fdfdfc',
  '--sys-color-bg-hover': '#d4d2cc',
  '--sys-color-bg-active': '#d4d2cc',

  /* text */
  '--sys-color-text-primary': '#111827',
  '--sys-color-text-secondary': '#374151',
  '--sys-color-text-muted': '#6f6f69',
  '--sys-color-text-disabled': '#9CA3AF',
  '--sys-color-text-placeholder': '#6f6f69',
  '--sys-color-text-inverse': '#FFFFFF',

  /* borders */
  '--sys-color-border-default': '#d4d2cc',
  '--sys-color-border-muted': '#d4d2cc',
  '--sys-color-border-strong': '#d4d2cc',
  '--sys-color-border-subtle': '#d4d2cc',

  /* accent (blue) */
  '--sys-color-accent': '#3B82F6',
  '--sys-color-accent-hover': '#2563EB',
  '--sys-color-accent-soft': '#EFF6FF',
  '--sys-color-accent-light': '#6A9EFA',

  /* status */
  '--sys-color-success': '#22C55E',
  '--sys-color-success-soft': '#D1F4E0',
  '--sys-color-warning': '#F59E0B',
  '--sys-color-warning-soft': '#FEF3C7',
  '--sys-color-error': '#EF4444',
  '--sys-color-error-soft': '#FEE2E2',
  '--sys-color-info': '#6f6f69',
  '--sys-color-info-soft': '#f4f2ed',

  /* shadows */
  '--sys-shadow-sm': '0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
  '--sys-shadow-md': '0 2px 8px rgba(0, 0, 0, 0.06), 0 8px 24px rgba(0, 0, 0, 0.1)',
  '--sys-shadow-lg': '0 2px 8px rgba(0, 0, 0, 0.06), 0 16px 48px rgba(0, 0, 0, 0.12)',
  '--sys-shadow-focus': '0 0 0 3px rgba(59, 130, 246, 0.4)',

  /* radius */
  '--sys-radius-card': '8px',
  '--sys-radius-button': '8px',
  '--sys-radius-input': '8px',
  '--sys-radius-pill': '24px',
  '--sys-radius-circle': '100px',

  /* spacing */
  '--sys-space-1': '4px',
  '--sys-space-2': '8px',
  '--sys-space-3': '12px',
  '--sys-space-4': '16px',
  '--sys-space-5': '20px',
  '--sys-space-6': '24px',
  '--sys-space-8': '32px',
  '--sys-space-10': '40px',

  /* typography */
  '--sys-font-family-display': '"Space Grotesk", "Inter", system-ui, sans-serif',
  '--sys-font-family-heading': '"Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  '--sys-font-family-base': '"Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  '--sys-font-family-mono': '"Courier New", SFMono-Regular, Menlo, Monaco, Consolas, monospace',

  '--sys-font-size-xs': '10px',
  '--sys-font-size-sm': '12px',
  '--sys-font-size-base': '14px',
  '--sys-font-size-md': '16px',
  '--sys-font-size-lg': '18px',
  '--sys-font-size-xl': '20px',
  '--sys-font-size-2xl': '24px',
  '--sys-font-size-3xl': '28px',
  '--sys-font-size-4xl': '32px',
  '--sys-font-size-5xl': '36px',
  '--sys-font-size-6xl': '40px',
  '--sys-font-size-7xl': '44px',
  '--sys-font-size-8xl': '52px',

  '--sys-font-weight-regular': '400',
  '--sys-font-weight-medium': '500',
  '--sys-font-weight-semibold': '600',
  '--sys-font-weight-bold': '700',

  /* motion */
  '--sys-duration-fast': '150ms',
  '--sys-duration-base': '200ms',
  '--sys-duration-slow': '300ms',
  '--sys-ease-standard': 'cubic-bezier(0.22, 1, 0.36, 1)',

  /* dimensions */
  '--sys-sidebar-width': '250px',
  '--sys-details-panel-width': '400px',
  '--sys-taskbar-height': '48px',
  '--sys-content-padding': '20px',
  '--sys-tab-height': '40px',
  '--sys-button-height': '40px',
  '--sys-input-height': '40px',
  '--sys-table-header-height': '60px',
  '--sys-table-row-height': '60px',
  '--sys-avatar-size': '28px',
  '--sys-icon-size': '20px',
  '--sys-status-dot-size': '8px',

  /* chart data series */
  '--sys-color-chart-blue': '#3B82F6',
  '--sys-color-chart-emerald': '#22C55E',
  '--sys-color-chart-amber': '#F59E0B',
  '--sys-color-chart-red': '#EF4444',
  '--sys-color-chart-violet': '#8B5CF6',
  '--sys-color-chart-teal': '#14B8A6',
  '--sys-color-chart-cyan': '#06B6D4',
  '--sys-color-chart-fuchsia': '#D946EF',
  '--sys-color-chart-rose': '#F43F5E',
  '--sys-color-chart-slate': '#64748B',

  /* skeleton loading */
  '--sys-color-skeleton': 'rgba(0, 0, 0, 0.11)',

  /* z-index */
  '--sys-z-base': '1',
  '--sys-z-drawer': '120',
  '--sys-z-popover': '140',
  '--sys-z-toast': '160',
  '--sys-z-modal': '180',
  '--sys-z-overlay': '200',
}

// ---------------------------------------------------------------------------
// Theme override registry (keyed by data-theme attribute value)
// Currently only light theme — dark theme can be added later
// ---------------------------------------------------------------------------

const THEME_OVERRIDES = {
  light: {},
}

// ---------------------------------------------------------------------------
// getThemeTokens(themeName)
// Returns the full merged token set for a given theme.
// ---------------------------------------------------------------------------

/**
 * Return every design token for a given theme, merging in order:
 *   REF_TOKENS  ->  DEFAULT_SYS_TOKENS  ->  theme-specific overrides
 *
 * @param {string} themeName  Currently only 'light'
 * @returns {Record<string, string>}
 */
export function getThemeTokens(themeName = 'light') {
  const overrides = THEME_OVERRIDES[themeName] || {}
  return { ...REF_TOKENS, ...DEFAULT_SYS_TOKENS, ...overrides }
}
