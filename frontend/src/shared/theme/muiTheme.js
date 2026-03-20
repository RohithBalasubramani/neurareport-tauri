import { alpha, createTheme } from '@mui/material/styles'
import { getThemeTokens } from './tokens.js'

/*
 * MUI theme bridge — single source of truth.
 *
 * All design token values come from tokens.js (JS objects).
 * CssBaseline injects them as CSS custom properties on :root
 * so domain CSS files can use var(--sys-*) / var(--ref-*).
 *
 * Component overrides migrated from app/theme.js Design System v5.
 */

/** Parse leading number from a CSS value string like '10px' or '120ms'. */
function num(val) {
  return Number.parseFloat(val) || 0
}

export function createAppMuiTheme(themeName = 'light') {
  const t = getThemeTokens(themeName)

  const shadows = Array(25).fill('none')
  shadows[1] = t['--sys-shadow-sm']
  shadows[2] = t['--sys-shadow-md']
  shadows[3] = t['--sys-shadow-lg']
  shadows[4] = t['--sys-shadow-focus']

  return createTheme({
    palette: {
      mode: 'light',
      primary: {
        main: t['--sys-color-accent'],
        dark: t['--sys-color-accent-hover'],
        light: t['--sys-color-accent-soft'],
        lighter: t['--sys-color-accent-soft'],
        contrastText: t['--sys-color-text-inverse'],
      },
      secondary: {
        main: t['--ref-color-neutral-500'],
        light: t['--ref-color-neutral-400'],
        dark: t['--ref-color-neutral-700'],
        lighter: t['--ref-color-neutral-100'],
        contrastText: t['--ref-color-neutral-900'],
      },
      success: {
        main: t['--sys-color-success'],
        light: t['--ref-color-emerald-400'],
        dark: t['--ref-color-emerald-600'],
        lighter: t['--sys-color-success-soft'],
        contrastText: '#000000',
      },
      warning: {
        main: t['--sys-color-warning'],
        light: t['--ref-color-amber-400'],
        dark: t['--ref-color-amber-600'],
        lighter: t['--sys-color-warning-soft'],
        contrastText: '#000000',
      },
      error: {
        main: t['--sys-color-error'],
        light: t['--ref-color-red-400'],
        dark: t['--ref-color-red-600'],
        lighter: t['--sys-color-error-soft'],
        contrastText: '#FFFFFF',
      },
      info: {
        main: t['--sys-color-info'],
        light: t['--ref-color-neutral-400'],
        dark: t['--ref-color-neutral-700'],
        lighter: t['--sys-color-info-soft'],
        contrastText: t['--ref-color-neutral-900'],
      },
      background: {
        default: t['--sys-color-bg-app'],
        paper: t['--sys-color-bg-surface'],
        surface: t['--sys-color-bg-surface'],
        overlay: t['--sys-color-bg-muted'],
        sidebar: t['--sys-color-bg-sidebar'],
      },
      text: {
        primary: t['--sys-color-text-primary'],
        secondary: t['--sys-color-text-secondary'],
        disabled: t['--sys-color-text-disabled'],
      },
      divider: t['--sys-color-border-default'],
      action: {
        hover: 'rgba(0, 0, 0, 0.04)',
        selected: 'rgba(0, 0, 0, 0.06)',
        disabled: 'rgba(0, 0, 0, 0.26)',
        disabledBackground: 'rgba(0, 0, 0, 0.06)',
        focus: 'rgba(0, 0, 0, 0.08)',
      },
      grey: {
        100: '#EDEDED',
        200: '#DEDEDE',
        300: '#BBBBBB',
        400: '#999999',
        500: '#7E7E7E',
        600: '#656565',
        700: '#444444',
        800: '#2A2A2A',
        900: '#1F1F1F',
        1000: '#1A1A1A',
        1100: '#111111',
        1200: '#0A0A0A',
      },
    },
    shape: {
      borderRadius: num(t['--sys-radius-card']),
    },
    spacing: 8,
    shadows,
    transitions: {
      duration: {
        shortest: num(t['--sys-duration-fast']),
        shorter: num(t['--sys-duration-fast']),
        short: num(t['--sys-duration-fast']),
        standard: num(t['--sys-duration-base']),
        complex: num(t['--sys-duration-slow']),
        enteringScreen: num(t['--sys-duration-base']),
        leavingScreen: num(t['--sys-duration-fast']),
      },
      easing: {
        easeInOut: t['--sys-ease-standard'],
        easeOut: 'ease-out',
        easeIn: 'ease-in',
        sharp: t['--sys-ease-standard'],
      },
    },

    // ========================================================================
    // TYPOGRAPHY — Design System v5
    // Display: Space Grotesk | Headings/Labels/Paragraphs: Inter
    // ========================================================================
    typography: {
      fontFamily: t['--sys-font-family-base'],
      fontWeightLight: 400,
      fontWeightRegular: 400,
      fontWeightMedium: 500,
      fontWeightBold: 600,

      displayLarge: {
        fontFamily: t['--sys-font-family-display'],
        fontSize: '52px',
        fontWeight: 600,
        lineHeight: '56px',
        letterSpacing: '-0.04em',
        '@media (max-width: 768px)': { fontSize: '44px', lineHeight: '48px' },
      },
      displaySmall: {
        fontFamily: t['--sys-font-family-display'],
        fontSize: '44px',
        fontWeight: 600,
        lineHeight: '48px',
        letterSpacing: '-0.04em',
        '@media (max-width: 768px)': { fontSize: '36px', lineHeight: '44px' },
      },
      h1: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '40px',
        fontWeight: 600,
        lineHeight: '48px',
        letterSpacing: '0.02em',
        '@media (max-width: 768px)': { fontSize: '36px', lineHeight: '44px' },
      },
      h2: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '36px',
        fontWeight: 600,
        lineHeight: '44px',
        letterSpacing: '0.02em',
        '@media (max-width: 768px)': { fontSize: '32px', lineHeight: '40px' },
      },
      h3: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '32px',
        fontWeight: 600,
        lineHeight: '40px',
        letterSpacing: 0,
        '@media (max-width: 768px)': { fontSize: '28px', lineHeight: '36px' },
      },
      h4: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '28px',
        fontWeight: 500,
        lineHeight: '36px',
        letterSpacing: 0,
        '@media (max-width: 768px)': { fontSize: '24px', lineHeight: '32px' },
      },
      h5: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '24px',
        fontWeight: 500,
        lineHeight: '32px',
        letterSpacing: 0,
        '@media (max-width: 768px)': { fontSize: '20px', lineHeight: '28px' },
      },
      h6: {
        fontFamily: t['--sys-font-family-heading'],
        fontSize: '20px',
        fontWeight: 500,
        lineHeight: '28px',
        letterSpacing: 0,
        '@media (max-width: 768px)': { fontSize: '18px', lineHeight: '24px' },
      },
      subtitle1: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '16px',
        fontWeight: 500,
        lineHeight: '18px',
        letterSpacing: 0,
      },
      subtitle2: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '14px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: 0,
      },
      body1: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '16px',
        fontWeight: 400,
        lineHeight: '24px',
        letterSpacing: 0,
      },
      body2: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '14px',
        fontWeight: 400,
        lineHeight: '20px',
        letterSpacing: 0,
      },
      caption: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '12px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: '0.02em',
      },
      overline: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '10px',
        fontWeight: 500,
        lineHeight: '14px',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
      },
      button: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '14px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: 0,
        textTransform: 'none',
      },
      code: {
        fontFamily: t['--sys-font-family-mono'],
        fontSize: '14px',
      },
      paragraphLarge: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '18px',
        fontWeight: 400,
        lineHeight: '28px',
        letterSpacing: 0,
      },
      paragraphXSmall: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '12px',
        fontWeight: 400,
        lineHeight: '20px',
        letterSpacing: 0,
      },
      navigationItem: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '16px',
        fontWeight: 500,
        lineHeight: '18px',
      },
      smallText: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '12px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: '0.02em',
      },
      tinyText: {
        fontFamily: t['--sys-font-family-base'],
        fontSize: '10px',
        fontWeight: 500,
        lineHeight: '14px',
        letterSpacing: '0.04em',
      },
    },

    // ========================================================================
    // COMPONENT OVERRIDES — Design System v5
    // ========================================================================
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          ':root': {
            ...t,
            colorScheme: 'light',
          },
          html: {
            WebkitFontSmoothing: 'antialiased',
            MozOsxFontSmoothing: 'grayscale',
          },
          body: {
            margin: 0,
            padding: 0,
            backgroundColor: t['--sys-color-bg-app'],
            color: t['--sys-color-text-primary'],
            fontFamily: t['--sys-font-family-base'],
            fontSize: '0.875rem',
            lineHeight: 1.5,
          },
          '#root': { minHeight: '100vh' },
          '*, *::before, *::after': { boxSizing: 'border-box' },
          'code, pre': { fontFamily: t['--sys-font-family-mono'] },
          '::selection': {
            backgroundColor: alpha(t['--sys-color-accent'], 0.2),
            color: 'inherit',
          },
          '::-webkit-scrollbar': { width: 8, height: 8 },
          '::-webkit-scrollbar-track': { backgroundColor: 'transparent' },
          '::-webkit-scrollbar-thumb': {
            backgroundColor: alpha(t['--sys-color-text-primary'], 0.15),
            borderRadius: 4,
            '&:hover': {
              backgroundColor: alpha(t['--sys-color-text-primary'], 0.25),
            },
          },
          '@keyframes fadeIn': {
            from: { opacity: 0 },
            to: { opacity: 1 },
          },
          '@keyframes slideUp': {
            from: { opacity: 0, transform: 'translateY(8px)' },
            to: { opacity: 1, transform: 'translateY(0)' },
          },
        },
      },

      // Paper
      MuiPaper: {
        defaultProps: { elevation: 1 },
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            backgroundColor: t['--sys-color-bg-surface'],
            borderRadius: num(t['--sys-radius-card']),
            border: 'none',
          },
          outlined: {
            border: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: 'none',
          },
          elevation0: { boxShadow: 'none' },
          elevation1: { boxShadow: t['--ref-shadow-xsmall'] },
          elevation2: {
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04), 0 4px 8px rgba(16, 24, 40, 0.04)',
          },
          elevation3: {
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04), 0 4px 8px rgba(16, 24, 40, 0.06), 0 8px 16px rgba(16, 24, 40, 0.04)',
          },
        },
      },

      // Card
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-card']),
            backgroundColor: t['--ref-color-neutral-50'],
            border: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: t['--ref-shadow-xsmall'],
            transition: `border-color ${t['--sys-duration-base']} ${t['--sys-ease-standard']}, box-shadow ${t['--sys-duration-base']} ${t['--sys-ease-standard']}`,
            '&:not(:has(.MuiCardContent-root))': { padding: 24 },
            '&:hover': {
              borderColor: t['--ref-color-neutral-300'],
            },
          },
        },
      },
      MuiCardContent: {
        styleOverrides: {
          root: {
            padding: 24,
            '&:last-child': { paddingBottom: 24 },
          },
        },
      },

      // Button
      MuiButtonBase: {
        defaultProps: { disableRipple: true },
        styleOverrides: {
          root: {
            transition: `all ${t['--sys-duration-fast']} ${t['--sys-ease-standard']}`,
            '&:active': { transform: 'scale(0.97)' },
          },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-button']),
            fontWeight: 500,
            fontSize: '0.875rem',
            lineHeight: 1.143,
            padding: '8px 12px',
            minHeight: num(t['--sys-button-height']),
            transition: 'all 150ms ease',
            '&:focus-visible': {
              outline: `2px solid ${t['--sys-color-text-primary']}`,
              outlineOffset: 2,
              boxShadow: `0 0 0 4px ${alpha(t['--sys-color-text-primary'], 0.15)}`,
            },
          },
          contained: {
            backgroundColor: t['--sys-color-text-primary'],
            color: t['--sys-color-text-inverse'],
            '&:hover': { backgroundColor: t['--sys-color-text-secondary'] },
            '&:active': { backgroundColor: t['--ref-color-neutral-700'] },
            '&.Mui-disabled': {
              backgroundColor: t['--sys-color-border-default'],
              color: t['--sys-color-text-muted'],
              cursor: 'not-allowed',
              pointerEvents: 'auto',
            },
          },
          containedSecondary: {
            backgroundColor: t['--sys-color-bg-muted'],
            color: t['--sys-color-text-secondary'],
            border: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: 'none',
            '&:hover': { backgroundColor: t['--sys-color-bg-hover'], boxShadow: 'none' },
          },
          outlined: {
            borderColor: t['--sys-color-border-default'],
            color: t['--sys-color-text-secondary'],
            backgroundColor: t['--sys-color-bg-muted'],
            '&:hover': {
              backgroundColor: t['--sys-color-bg-hover'],
              borderColor: t['--ref-color-neutral-400'],
            },
            '&.Mui-disabled': {
              color: t['--sys-color-text-disabled'],
              borderColor: t['--sys-color-border-default'],
              backgroundColor: t['--sys-color-bg-app'],
              cursor: 'not-allowed',
              pointerEvents: 'auto',
            },
          },
          text: {
            color: t['--sys-color-text-secondary'],
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.04)',
              color: t['--sys-color-text-primary'],
            },
          },
          sizeSmall: { padding: '6px 8px', fontSize: '0.75rem', minHeight: 32 },
          sizeLarge: { padding: '12px 16px', fontSize: '1rem', minHeight: 44 },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            borderRadius: 6,
            color: t['--sys-color-text-muted'],
            transition: `all ${t['--sys-duration-fast']} ${t['--sys-ease-standard']}`,
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.03)',
              color: t['--sys-color-text-secondary'],
              '& .MuiSvgIcon-root': {
                filter: `drop-shadow(0 0 4px ${alpha(t['--sys-color-accent'], 0.3)})`,
              },
            },
            '&:focus-visible': {
              outline: `2px solid ${t['--sys-color-text-primary']}`,
              outlineOffset: 2,
              boxShadow: `0 0 0 4px ${alpha(t['--sys-color-text-primary'], 0.15)}`,
            },
          },
          sizeSmall: { padding: 6 },
          sizeMedium: { padding: 8 },
        },
      },

      // Chip/Pill
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-pill']),
            fontFamily: t['--sys-font-family-base'],
            fontWeight: 500,
            fontSize: '12px',
            height: 24,
          },
          filled: { backgroundColor: t['--sys-color-bg-muted'] },
          outlined: { borderColor: t['--sys-color-border-default'] },
          colorSuccess: {
            backgroundColor: t['--sys-color-success-soft'],
            color: t['--ref-color-emerald-600'],
            borderColor: 'transparent',
          },
          colorError: {
            backgroundColor: t['--sys-color-error-soft'],
            color: t['--sys-color-error'],
            borderColor: 'transparent',
          },
          colorWarning: {
            backgroundColor: t['--sys-color-warning-soft'],
            color: t['--ref-color-amber-600'],
            borderColor: 'transparent',
          },
          colorInfo: {
            backgroundColor: t['--sys-color-info-soft'],
            color: t['--sys-color-text-secondary'],
            borderColor: 'transparent',
          },
          sizeSmall: { height: 20, fontSize: '10px' },
        },
      },

      // Input / TextField
      MuiTextField: {
        defaultProps: { size: 'small', variant: 'outlined' },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-input']),
            fontFamily: t['--sys-font-family-base'],
            fontSize: '14px',
            backgroundColor: t['--sys-color-bg-input'],
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: t['--sys-color-border-muted'],
              borderWidth: 1,
              transition: `border-color ${t['--sys-duration-fast']} ease`,
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: t['--ref-color-neutral-400'],
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: t['--sys-color-text-primary'],
              borderWidth: 2,
            },
            '&.Mui-error .MuiOutlinedInput-notchedOutline': {
              borderColor: t['--sys-color-error'],
            },
          },
          input: {
            padding: '8px 12px',
            height: '24px',
            lineHeight: '20px',
            '&::placeholder': {
              fontFamily: t['--sys-font-family-base'],
              color: t['--sys-color-text-placeholder'],
              opacity: 1,
            },
          },
          inputSizeSmall: { padding: '6px 12px', height: '20px' },
          adornedStart: {
            paddingLeft: 12,
            '& .MuiInputAdornment-root': { marginRight: 8 },
          },
        },
      },
      MuiInputLabel: {
        styleOverrides: {
          root: {
            fontFamily: t['--sys-font-family-base'],
            fontSize: '12px',
            fontWeight: 500,
            lineHeight: '16px',
            letterSpacing: 'normal',
            color: t['--sys-color-text-secondary'],
            '&.Mui-focused': { color: t['--sys-color-text-primary'] },
          },
        },
      },
      MuiFormHelperText: {
        styleOverrides: {
          root: {
            marginTop: 6,
            fontSize: '0.75rem',
            color: t['--sys-color-text-muted'],
          },
        },
      },
      MuiSelect: {
        styleOverrides: {
          icon: { color: t['--sys-color-text-muted'] },
        },
      },

      // Menu / Dropdown
      MuiMenu: {
        styleOverrides: {
          paper: {
            borderRadius: num(t['--sys-radius-card']),
            backgroundColor: 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(12px)',
            border: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: t['--sys-shadow-md'],
            marginTop: 4,
          },
          list: { padding: 4 },
        },
      },
      MuiMenuItem: {
        styleOverrides: {
          root: {
            borderRadius: 4,
            fontSize: '0.875rem',
            padding: '8px 12px',
            margin: '2px 0',
            minHeight: 36,
            color: t['--sys-color-text-secondary'],
            '&:hover': {
              backgroundColor: 'rgba(0,0,0,0.03)',
              color: t['--sys-color-text-primary'],
            },
            '&.Mui-selected': {
              backgroundColor: 'rgba(0,0,0,0.04)',
              color: t['--sys-color-text-primary'],
              '&:hover': { backgroundColor: 'rgba(0,0,0,0.05)' },
            },
          },
        },
      },

      // Navigation
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-card']),
            padding: '10px 12px',
            minHeight: num(t['--sys-tab-height']),
            gap: 8,
            transition: 'all 150ms ease',
            color: t['--sys-color-text-secondary'],
            '&:hover': {
              backgroundColor: t['--sys-color-bg-muted'],
              color: t['--sys-color-text-primary'],
            },
            '&.Mui-selected': {
              backgroundColor: t['--sys-color-bg-hover'],
              color: t['--sys-color-text-primary'],
              '&:hover': { backgroundColor: t['--sys-color-bg-hover'] },
            },
          },
        },
      },
      MuiListItemIcon: {
        styleOverrides: {
          root: {
            minWidth: 28,
            width: num(t['--sys-icon-size']),
            height: num(t['--sys-icon-size']),
            color: t['--sys-color-text-muted'],
            '.Mui-selected &': { color: t['--sys-color-text-secondary'] },
          },
        },
      },
      MuiListItemText: {
        styleOverrides: {
          primary: {
            fontFamily: t['--sys-font-family-base'],
            fontSize: '16px',
            fontWeight: 500,
            lineHeight: 'normal',
            color: 'inherit',
          },
          secondary: {
            fontFamily: t['--sys-font-family-base'],
            fontSize: '12px',
            color: t['--sys-color-text-muted'],
          },
        },
      },

      MuiDivider: {
        styleOverrides: {
          root: { borderColor: t['--sys-color-border-default'] },
        },
      },

      // Avatar
      MuiAvatar: {
        styleOverrides: {
          root: {
            width: num(t['--sys-avatar-size']),
            height: num(t['--sys-avatar-size']),
            border: `1px solid ${t['--ref-color-neutral-400']}`,
            borderRadius: 32,
            backgroundColor: t['--sys-color-bg-muted'],
            color: t['--sys-color-text-secondary'],
            fontSize: '12px',
            fontFamily: t['--sys-font-family-base'],
            fontWeight: 500,
          },
        },
      },
      MuiBadge: {
        styleOverrides: {
          badge: { fontWeight: 600, fontSize: '0.625rem' },
        },
      },

      // Tooltip
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: t['--sys-color-bg-tooltip'],
            color: t['--sys-color-text-inverse'],
            fontSize: '0.75rem',
            fontWeight: 500,
            padding: '6px 10px',
            borderRadius: 6,
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          },
          arrow: { color: t['--sys-color-bg-tooltip'] },
        },
      },

      // Dialog
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 12,
            backgroundColor: t['--sys-color-bg-surface'],
            border: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: t['--sys-shadow-lg'],
          },
        },
      },
      MuiDialogTitle: {
        styleOverrides: {
          root: {
            fontSize: '1rem',
            fontWeight: 500,
            padding: '20px 24px 12px',
            color: t['--sys-color-text-primary'],
          },
        },
      },
      MuiDialogContent: {
        styleOverrides: { root: { padding: '12px 24px' } },
      },
      MuiDialogActions: {
        styleOverrides: {
          root: { padding: '12px 24px 20px', gap: 8, flexWrap: 'wrap' },
        },
      },

      // Drawer / Sidebar
      MuiDrawer: {
        styleOverrides: {
          paper: {
            width: num(t['--sys-sidebar-width']),
            backgroundColor: t['--sys-color-bg-sidebar'],
            borderRight: 'none',
            borderRadius: 0,
            boxShadow: 'none',
            padding: '20px 16px',
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: 'rgba(255, 255, 255, 0.85)',
            backdropFilter: 'blur(12px)',
            borderBottom: `1px solid ${t['--sys-color-border-default']}`,
            boxShadow: 'none',
          },
        },
      },
      MuiToolbar: {
        styleOverrides: {
          root: {
            minHeight: 56,
            '@media (min-width: 600px)': { minHeight: 56 },
          },
        },
      },

      // Tabs
      MuiTabs: {
        styleOverrides: {
          root: {
            minHeight: num(t['--sys-tab-height']),
            borderBottom: `1px solid ${t['--sys-color-border-default']}`,
          },
          indicator: {
            height: 2,
            borderRadius: 0,
            backgroundColor: t['--sys-color-text-primary'],
          },
          flexContainer: { gap: 0 },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontFamily: t['--sys-font-family-base'],
            fontWeight: 500,
            fontSize: '14px',
            minHeight: num(t['--sys-tab-height']),
            padding: '8px 32px',
            borderBottom: '2px solid transparent',
            color: t['--sys-color-text-secondary'],
            backgroundColor: 'transparent',
            transition: 'all 150ms ease',
            '&.Mui-selected': {
              fontWeight: 500,
              color: t['--sys-color-text-primary'],
              backgroundColor: t['--sys-color-bg-muted'],
            },
            '&:hover': {
              color: t['--sys-color-text-secondary'],
              backgroundColor: t['--sys-color-bg-app'],
            },
          },
        },
      },

      // Table
      MuiTable: {
        styleOverrides: {
          root: {
            borderCollapse: 'separate',
            borderSpacing: 0,
            backgroundColor: t['--sys-color-bg-surface'],
          },
        },
      },
      MuiTableContainer: {
        styleOverrides: { root: { border: 'none', borderRadius: 0 } },
      },
      MuiTableHead: {
        styleOverrides: {
          root: {
            '& .MuiTableCell-head': {
              backgroundColor: t['--ref-color-neutral-50'],
              fontFamily: t['--sys-font-family-base'],
              fontWeight: 500,
              fontSize: '12px',
              letterSpacing: '0.02em',
              color: t['--sys-color-text-secondary'],
              textTransform: 'none',
              borderBottom: `1px solid ${t['--sys-color-border-default']}`,
              height: num(t['--sys-table-header-height']),
              padding: '0 16px',
            },
          },
        },
      },
      MuiTableBody: {
        styleOverrides: {
          root: {
            '& .MuiTableRow-root': {
              '&:nth-of-type(even)': {
                backgroundColor: t['--ref-color-neutral-50'],
              },
              '&:hover': {
                backgroundColor: alpha(t['--sys-color-bg-muted'], 0.5),
              },
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: { height: num(t['--sys-table-row-height']) },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            fontFamily: t['--sys-font-family-base'],
            fontSize: '14px',
            color: t['--sys-color-text-primary'],
            padding: '0 16px',
            height: num(t['--sys-table-row-height']),
            borderBottom: `1px solid ${t['--sys-color-border-default']}`,
            borderLeft: 'none',
            borderRight: 'none',
          },
        },
      },
      MuiTablePagination: {
        styleOverrides: {
          root: {
            borderTop: '1px solid rgba(0,0,0,0.05)',
          },
          selectLabel: { fontSize: '0.75rem', color: t['--sys-color-text-muted'] },
          displayedRows: { fontSize: '0.75rem', color: t['--sys-color-text-muted'] },
        },
      },

      // Checkbox / Switch
      MuiCheckbox: {
        styleOverrides: {
          root: {
            color: t['--ref-color-neutral-400'],
            padding: 8,
            '&.Mui-checked': { color: t['--sys-color-text-primary'] },
            '&:hover': {
              backgroundColor: alpha(t['--sys-color-text-primary'], 0.04),
            },
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          root: { width: 44, height: 24, padding: 0 },
          switchBase: {
            padding: 2,
            '&.Mui-checked': {
              transform: 'translateX(20px)',
              color: '#FFFFFF',
              '& + .MuiSwitch-track': {
                backgroundColor: t['--sys-color-success'],
                opacity: 1,
              },
            },
          },
          thumb: {
            width: 20,
            height: 20,
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          },
          track: {
            borderRadius: 12,
            backgroundColor: t['--ref-color-neutral-400'],
            opacity: 1,
          },
        },
      },

      // Progress
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            height: 4,
            borderRadius: 2,
            backgroundColor: t['--sys-color-border-default'],
          },
          bar: {
            borderRadius: 2,
            backgroundColor: t['--sys-color-accent'],
          },
        },
      },
      MuiCircularProgress: {
        styleOverrides: {
          root: { color: t['--sys-color-accent'] },
        },
      },
      MuiSkeleton: {
        styleOverrides: {
          root: { backgroundColor: t['--sys-color-skeleton'] },
        },
      },

      // Alert
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: num(t['--sys-radius-card']),
            fontSize: '0.875rem',
            alignItems: 'flex-start',
            padding: '12px 16px',
            backgroundColor: t['--ref-color-neutral-50'],
            color: t['--sys-color-text-primary'],
            border: `1px solid ${t['--sys-color-border-default']}`,
          },
          standardSuccess: {
            backgroundColor: '#f0fdf4',
            color: t['--sys-color-text-primary'],
            border: '1px solid #bbf7d0',
            '& .MuiAlert-icon': { color: t['--ref-color-emerald-600'] },
          },
          standardError: {
            backgroundColor: t['--sys-color-error-soft'],
            color: t['--sys-color-text-primary'],
            border: `1px solid ${t['--ref-color-red-200']}`,
            '& .MuiAlert-icon': { color: t['--ref-color-red-600'] },
          },
          standardWarning: {
            backgroundColor: t['--sys-color-warning-soft'],
            color: t['--sys-color-text-primary'],
            border: `1px solid ${t['--ref-color-amber-200']}`,
            '& .MuiAlert-icon': { color: t['--ref-color-amber-600'] },
          },
          standardInfo: {
            backgroundColor: t['--ref-color-primary-50'],
            color: t['--sys-color-text-primary'],
            border: `1px solid ${t['--ref-color-primary-100']}`,
            '& .MuiAlert-icon': { color: t['--sys-color-accent'] },
          },
          icon: { marginRight: 12, padding: 0, opacity: 1 },
        },
      },
      MuiSnackbar: {
        styleOverrides: {
          root: {
            '& .MuiAlert-root': {
              boxShadow: '0 4px 24px rgba(0,0,0,0.1)',
            },
          },
        },
      },

      // Breadcrumbs & Link
      MuiBreadcrumbs: {
        styleOverrides: {
          separator: {
            color: t['--ref-color-neutral-400'],
            marginLeft: 8,
            marginRight: 8,
          },
          li: {
            '& .MuiTypography-root': { fontSize: '0.875rem' },
          },
        },
      },
      MuiLink: {
        styleOverrides: {
          root: {
            color: t['--sys-color-accent'],
            textDecorationColor: alpha(t['--sys-color-accent'], 0.4),
            '&:hover': {
              color: t['--sys-color-accent-hover'],
              textDecorationColor: t['--sys-color-accent-hover'],
            },
          },
        },
      },

      // Accordion
      MuiAccordion: {
        defaultProps: { disableGutters: true, elevation: 0 },
        styleOverrides: {
          root: {
            backgroundColor: t['--ref-color-neutral-50'],
            border: `1px solid ${t['--sys-color-border-default']}`,
            borderRadius: num(t['--sys-radius-card']),
            '&:before': { display: 'none' },
            '&:not(:last-child)': { marginBottom: 8 },
            '&.Mui-expanded': {
              margin: 0,
              '&:not(:last-child)': { marginBottom: 8 },
            },
          },
        },
      },
      MuiAccordionSummary: {
        styleOverrides: {
          root: {
            padding: '0 16px',
            minHeight: 56,
            '&.Mui-expanded': { minHeight: 56 },
          },
          content: {
            margin: '12px 0',
            '&.Mui-expanded': { margin: '12px 0' },
          },
          expandIconWrapper: { color: t['--ref-color-neutral-400'] },
        },
      },
      MuiAccordionDetails: {
        styleOverrides: {
          root: {
            padding: '0 16px 16px',
            fontFamily: t['--sys-font-family-base'],
            fontSize: '14px',
            lineHeight: '20px',
            color: t['--sys-color-text-muted'],
          },
        },
      },
    },
  })
}
