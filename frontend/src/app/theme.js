import { alpha, createTheme } from '@mui/material/styles'

// ============================================================================
// DESIGN SYSTEM v5 — Desktop UI Overhaul
// Fonts: Inter (UI/body), Courier New (code/mono), Space Grotesk (display/brand)
// Colors: Neutral (warm paper) + Primary (blue) + Status + Secondary accent palettes
// ============================================================================

// ============================================================================
// FONT FAMILIES
// ============================================================================
const fontFamilyDisplay = '"Space Grotesk", "Inter", system-ui, sans-serif'
const fontFamilyHeading = '"Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
const fontFamilyBody = '"Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif'
const fontFamilyMono = '"Courier New", SFMono-Regular, Menlo, Monaco, Consolas, monospace'
// Backward compat alias — Inter serves both heading and UI roles
const fontFamilyUI = fontFamilyBody

// ============================================================================
// CANONICAL COLOR TOKENS — Design System v4
// ============================================================================

// Neutral palette (50-900) — warm paper tones for light surfaces
// Rules: 50-100 never for text. 900 never as background.
const neutral = {
  50: '#fdfdfc',     // Warm paper page backgrounds — aligned with desktop taskbar bg
  100: '#f4f2ed',    // Warm cream cards, background fills — aligned with desktop hover
  200: '#d4d2cc',    // Borders, dividers — aligned with desktop separator color
  300: '#d4d2cc',    // Input outlines, separators
  400: '#9CA3AF',    // Disabled icons
  500: '#6f6f69',    // Muted / helper text — aligned with desktop icon color
  700: '#374151',    // Default body text
  900: '#111827',    // Headings, high-emphasis text
}

// Primary palette (Brand / Action) — blue accent
// Rules: Only 500-600 for CTAs. Never replace status colors.
const primary = {
  50: '#EFF6FF',     // Subtle blue backgrounds, hover fills
  100: '#DBEAFE',    // Light blue accents
  300: '#6A9EFA',    // Secondary blue emphasis
  500: '#3B82F6',    // Primary CTAs, links (blue-500)
  600: '#2563EB',    // Hover / active states (blue-600)
  900: '#1D4ED8',    // Strong emphasis (blue-700)
}

// Status colors — semantic only, never decorative
const status = {
  success: '#22C55E',
  warning: '#F59E0B',
  destructive: '#EF4444',
}

// ============================================================================
// SECONDARY (ACCENT) PALETTES — for charts, tags, badges, categorization only
// Rules: Forbidden for primary CTAs, body text, headings, or destructive states.
// ============================================================================
const secondarySlate = {
  50: '#F8FAFC', 100: '#F1F5F9', 200: '#E2E8F0', 300: '#CBD5E1',
  400: '#94A3B8', 500: '#64748B', 600: '#475569', 700: '#334155',
  800: '#1E293B', 900: '#0F172A',
}
const secondaryZinc = {
  50: '#FAFAFA', 100: '#F4F4F5', 200: '#E4E4E7', 300: '#D4D4D8',
  400: '#A1A1AA', 500: '#71717A', 600: '#52525B', 700: '#3F3F46',
  800: '#27272A', 900: '#18181B',
}
const secondaryStone = {
  50: '#FAFAF9', 100: '#F5F5F4', 200: '#E7E5E4', 300: '#D6D3D1',
  400: '#A8A29E', 500: '#78716C', 600: '#57534E', 700: '#44403C',
  800: '#292524', 900: '#1C1917',
}
const secondaryTeal = {
  50: '#F0FDFA', 100: '#CCFBF1', 200: '#99F6E4', 300: '#5EEAD4',
  400: '#2DD4BF', 500: '#14B8A6', 600: '#0D9488', 700: '#0F766E',
  800: '#115E59', 900: '#134E4A',
}
const secondaryEmerald = {
  50: '#ECFDF5', 100: '#D1FAE5', 200: '#A7F3D0', 300: '#6EE7B7',
  400: '#34D399', 500: '#10B981', 600: '#059669', 700: '#047857',
  800: '#065F46', 900: '#064E3B',
}
const secondaryCyan = {
  50: '#ECFEFF', 100: '#CFFAFE', 200: '#A5F3FC', 300: '#67E8F9',
  400: '#22D3EE', 500: '#06B6D4', 600: '#0891B2', 700: '#0E7490',
  800: '#155E75', 900: '#164E63',
}
const secondaryViolet = {
  50: '#F5F3FF', 100: '#EDE9FE', 200: '#DDD6FE', 300: '#C4B5FD',
  400: '#A78BFA', 500: '#8B5CF6', 600: '#7C3AED', 700: '#6D28D9',
  800: '#5B21B6', 900: '#4C1D95',
}
const secondaryFuchsia = {
  50: '#FDF4FF', 100: '#FAE8FF', 200: '#F5D0FE', 300: '#F0ABFC',
  400: '#E879F9', 500: '#D946EF', 600: '#C026D3', 700: '#A21CAF',
  800: '#86198F', 900: '#701A75',
}
const secondaryRose = {
  50: '#FFF1F2', 100: '#FFE4E6', 200: '#FECDD3', 300: '#FDA4AF',
  400: '#FB7185', 500: '#F43F5E', 600: '#E11D48', 700: '#BE123C',
  800: '#9F1239', 900: '#881337',
}

const secondary = {
  slate: secondarySlate,
  zinc: secondaryZinc,
  stone: secondaryStone,
  teal: secondaryTeal,
  emerald: secondaryEmerald,
  cyan: secondaryCyan,
  violet: secondaryViolet,
  fuchsia: secondaryFuchsia,
  rose: secondaryRose,
}

// ============================================================================
// BACKWARD-COMPATIBLE ALIASES
// These map old token names to new Design System v4 values so that all 97
// consumer files continue to work without code changes.
// ============================================================================

// Legacy internal palette (for dark mode, which remains unchanged)
const palette = {
  brand: {
    primary: neutral[900],
    secondary: neutral[900],
  },
  scale: {
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
  green: {
    100: '#D1F4E0', 200: '#A3E9C1', 300: '#08C18F', 400: '#08C18F',
    500: '#22C55E', 600: '#16A34A', 700: '#15803D', 800: '#166534', 900: '#14532D',
  },
  blue: {
    100: '#D5E4FF', 200: '#A5C4FC', 300: '#6A9EFA', 400: '#3B82F6',
    500: '#2563EB', 600: '#1D4ED8', 700: '#1E40AF', 800: '#1E3A8A', 900: '#172554',
  },
  yellow: {
    100: '#FEF3C7', 200: '#FDE68A', 300: '#FCD34D', 400: '#FBBF24',
    500: '#F59E0B', 600: '#D97706', 700: '#B45309', 800: '#92400E', 900: '#78350F',
  },
  red: {
    100: '#FEE2E2', 200: '#FECACA', 300: '#FCA5A5', 400: '#F87171',
    500: '#EF4444', 600: '#DC2626', 700: '#B91C1C', 800: '#991B1B', 900: '#7F1D1D',
  },
  purple: {
    100: '#EDE9FE', 200: '#DDD6FE', 300: '#C4B5FD', 400: '#A78BFA',
    500: '#8B5CF6', 600: '#7C3AED', 700: '#6D28D9', 800: '#5B21B6', 900: '#4C1D95',
  },
}

const figmaShadow = {
  xsmall: '0 2px 8px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)',
  aiPanel: '0px 4px 8.4px rgba(0,0,0,0.25)',
}

const figmaSpacing = {
  sidebarWidth: 250,
  detailsPanelWidth: 400,
  taskbarHeight: 48,
  contentPadding: 20,
  cardBorderRadius: 8,
  buttonBorderRadius: 8,
  pillBorderRadius: 24,
  circleBorderRadius: 100,
}

const figmaComponents = {
  tabs: {
    height: 40,
    borderBottom: `1px solid ${neutral[200]}`,
    paddingHorizontal: 32,
    paddingVertical: 8,
  },
  searchInput: { width: 240, height: 40, iconSize: 20 },
  filterButton: { height: 40, gap: 8 },
  viewToggle: { borderRadius: 8 },
  zoomControls: { height: 40, borderRadius: 35, iconSize: 24, gap: 12 },
  dataTable: { headerHeight: 60, rowHeight: 60, cellPadding: 16 },
  deviceDetailsPanel: { width: 400, sectionHeaderHeight: 40, rowHeight: 40, padding: 20 },
  aiAssistantPanel: { width: 394, minHeight: 114, borderRadius: '4px 4px 0 0', inputHeight: 48, padding: 16 },
  notificationCard: { width: 394, borderRadius: '4px 4px 0 0', padding: 16 },
  userAvatar: { size: 28, borderRadius: 32 },
  statusIndicator: { dotSize: 8, gap: 6 },
  scrollbar: { width: 20.156, borderRadius: 4 },
}

// ============================================================================
// DARK THEME (legacy — unchanged until dark mode spec is provided)
// ============================================================================
const darkTheme = {
  palette: {
    mode: 'dark',
    primary: {
      main: palette.scale[200],
      light: palette.scale[100],
      dark: palette.scale[300],
      lighter: alpha(palette.scale[200], 0.15),
      contrastText: '#000000',
    },
    secondary: {
      main: palette.scale[400],
      light: palette.scale[300],
      dark: palette.scale[500],
      lighter: alpha(palette.scale[400], 0.1),
      contrastText: '#FFFFFF',
    },
    success: {
      main: palette.green[400],
      light: palette.green[300],
      dark: palette.green[500],
      lighter: alpha(palette.green[400], 0.15),
      contrastText: '#000000',
    },
    warning: {
      main: palette.yellow[400],
      light: palette.yellow[300],
      dark: palette.yellow[500],
      lighter: alpha(palette.yellow[400], 0.15),
      contrastText: '#000000',
    },
    error: {
      main: palette.red[500],
      light: palette.red[400],
      dark: palette.red[600],
      lighter: alpha(palette.red[500], 0.15),
      contrastText: '#FFFFFF',
    },
    info: {
      main: palette.scale[400],
      light: palette.scale[300],
      dark: palette.scale[500],
      lighter: alpha(palette.scale[400], 0.1),
      contrastText: '#FFFFFF',
    },
    background: {
      default: palette.scale[1100],
      paper: palette.scale[1000],
      surface: palette.scale[900],
      overlay: palette.scale[800],
    },
    text: {
      primary: palette.scale[100],
      secondary: palette.scale[400],
      disabled: palette.scale[600],
    },
    divider: alpha(palette.scale[100], 0.08),
    action: {
      hover: alpha(palette.scale[100], 0.05),
      selected: alpha(palette.scale[100], 0.08),
      disabled: alpha(palette.scale[100], 0.3),
      disabledBackground: alpha(palette.scale[100], 0.12),
      focus: alpha(palette.scale[100], 0.12),
    },
    grey: palette.scale,
  },
}

// ============================================================================
// LIGHT THEME — Design System v4
// ============================================================================
const lightTheme = {
  palette: {
    mode: 'light',
    // Primary — blue accent for CTAs and interactive elements
    primary: {
      main: primary[500],          // #3B82F6
      light: primary[300],         // #6A9EFA
      dark: primary[600],          // #2563EB
      lighter: primary[50],        // #EFF6FF
      contrastText: '#FFFFFF',
    },
    // Secondary — neutral for non-primary UI
    secondary: {
      main: neutral[700],          // #374151
      light: neutral[500],         // #6B7280
      dark: neutral[900],          // #111827
      lighter: neutral[100],       // #F3F4F3
      contrastText: '#FFFFFF',
    },
    success: {
      main: status.success,        // #22C55E
      light: '#4ADE80',
      dark: '#16A34A',
      lighter: '#D1F4E0',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: status.warning,        // #F59E0B
      light: '#FBBF24',
      dark: '#D97706',
      lighter: '#FEF3C7',
      contrastText: '#000000',
    },
    error: {
      main: status.destructive,    // #EF4444
      light: '#F87171',
      dark: '#DC2626',
      lighter: '#FEE2E2',
      contrastText: '#FFFFFF',
    },
    info: {
      main: neutral[500],          // #6B7280
      light: neutral[400],         // #9CA3AF
      dark: neutral[700],          // #374151
      lighter: neutral[100],       // #F3F4F3
      contrastText: neutral[900],
    },
    // Backgrounds — warm paper surface system
    background: {
      default: neutral[50],        // #fbfaf7 — warm paper page background
      paper: '#FFFFFF',            // Cards, panels
      surface: '#FFFFFF',
      overlay: neutral[100],       // #f6f5f2 — warm cream
      sidebar: neutral[50],        // #fbfaf7 — warm paper sidebar
    },
    // Text — 3-tier hierarchy
    text: {
      primary: neutral[900],       // #111827
      secondary: neutral[700],     // #374151
      disabled: neutral[400],      // #9CA3AF
    },
    divider: neutral[200],         // #E5E7E6
    action: {
      hover: 'rgba(0, 0, 0, 0.04)',
      selected: 'rgba(0, 0, 0, 0.06)',
      disabled: 'rgba(0, 0, 0, 0.26)',
      disabledBackground: 'rgba(0, 0, 0, 0.06)',
      focus: 'rgba(0, 0, 0, 0.08)',
    },
    grey: palette.scale,
  },
}

// ============================================================================
// THEME FACTORY
// ============================================================================
function createAppTheme(mode = 'dark') {
  const themeOptions = mode === 'dark' ? darkTheme : lightTheme
  const isDark = mode === 'dark'

  return createTheme({
    ...themeOptions,
    shape: {
      borderRadius: 8,
    },
    spacing: 8,

    // ========================================================================
    // TYPOGRAPHY — Desktop UI Overhaul
    // Display: Space Grotesk | Headings/Labels/Paragraphs: Inter
    // Responsive: Desktop sizes with mobile breakpoints at 768px
    // ========================================================================
    typography: {
      fontFamily: fontFamilyBody,
      fontWeightLight: 400,
      fontWeightRegular: 400,
      fontWeightMedium: 500,
      fontWeightBold: 600,

      // Display Large — Space Grotesk, 52/56 desktop, 44/48 mobile, 600
      displayLarge: {
        fontFamily: fontFamilyDisplay,
        fontSize: '52px',
        fontWeight: 600,
        lineHeight: '56px',
        letterSpacing: '-0.04em',
        '@media (max-width: 768px)': {
          fontSize: '44px',
          lineHeight: '48px',
        },
      },
      // Display Small — Space Grotesk, 44/48 desktop, 36/44 mobile, 600
      displaySmall: {
        fontFamily: fontFamilyDisplay,
        fontSize: '44px',
        fontWeight: 600,
        lineHeight: '48px',
        letterSpacing: '-0.04em',
        '@media (max-width: 768px)': {
          fontSize: '36px',
          lineHeight: '44px',
        },
      },
      // H1 — Inter, 40/48 desktop, 36/44 mobile, 600
      h1: {
        fontFamily: fontFamilyHeading,
        fontSize: '40px',
        fontWeight: 600,
        lineHeight: '48px',
        letterSpacing: '0.02em',
        '@media (max-width: 768px)': {
          fontSize: '36px',
          lineHeight: '44px',
        },
      },
      // H2 — Inter, 36/44 desktop, 32/40 mobile, 600
      h2: {
        fontFamily: fontFamilyHeading,
        fontSize: '36px',
        fontWeight: 600,
        lineHeight: '44px',
        letterSpacing: '0.02em',
        '@media (max-width: 768px)': {
          fontSize: '32px',
          lineHeight: '40px',
        },
      },
      // H3 — Inter, 32/40 desktop, 28/36 mobile, 600, 0%
      h3: {
        fontFamily: fontFamilyHeading,
        fontSize: '32px',
        fontWeight: 600,
        lineHeight: '40px',
        letterSpacing: 0,
        '@media (max-width: 768px)': {
          fontSize: '28px',
          lineHeight: '36px',
        },
      },
      // H4 — Inter, 28/36 desktop, 24/32 mobile, 500, 0%
      h4: {
        fontFamily: fontFamilyHeading,
        fontSize: '28px',
        fontWeight: 500,
        lineHeight: '36px',
        letterSpacing: 0,
        '@media (max-width: 768px)': {
          fontSize: '24px',
          lineHeight: '32px',
        },
      },
      // H5 — Inter, 24/32 desktop, 20/28 mobile, 500, 0%
      h5: {
        fontFamily: fontFamilyHeading,
        fontSize: '24px',
        fontWeight: 500,
        lineHeight: '32px',
        letterSpacing: 0,
        '@media (max-width: 768px)': {
          fontSize: '20px',
          lineHeight: '28px',
        },
      },
      // H6 — Inter, 20/28 desktop, 18/24 mobile, 500, 0%
      h6: {
        fontFamily: fontFamilyHeading,
        fontSize: '20px',
        fontWeight: 500,
        lineHeight: '28px',
        letterSpacing: 0,
        '@media (max-width: 768px)': {
          fontSize: '18px',
          lineHeight: '24px',
        },
      },
      // Label Large — Inter, 16/18, 500, 0%
      subtitle1: {
        fontFamily: fontFamilyBody,
        fontSize: '16px',
        fontWeight: 500,
        lineHeight: '18px',
        letterSpacing: 0,
      },
      // Label Medium — Inter, 14/16, 500, 0%
      subtitle2: {
        fontFamily: fontFamilyBody,
        fontSize: '14px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: 0,
      },
      // Paragraph Medium — Inter, 16/24, 400, 0% (default body text)
      body1: {
        fontFamily: fontFamilyBody,
        fontSize: '16px',
        fontWeight: 400,
        lineHeight: '24px',
        letterSpacing: 0,
      },
      // Paragraph Small — Inter, 14/20, 400, 0% (dense UI text)
      body2: {
        fontFamily: fontFamilyBody,
        fontSize: '14px',
        fontWeight: 400,
        lineHeight: '20px',
        letterSpacing: 0,
      },
      // Label Small — Inter, 12/16, 500, +2% (badges, chips)
      caption: {
        fontFamily: fontFamilyBody,
        fontSize: '12px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: '0.02em',
      },
      // Label XSmall — Inter, 10/14, 500, +10% (helper UI, webshell section style)
      overline: {
        fontFamily: fontFamilyBody,
        fontSize: '10px',
        fontWeight: 500,
        lineHeight: '14px',
        letterSpacing: '0.1em',
        textTransform: 'uppercase',
      },
      // Button — Label Medium
      button: {
        fontFamily: fontFamilyBody,
        fontSize: '14px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: 0,
        textTransform: 'none',
      },
      // Code — Courier New
      code: {
        fontFamily: fontFamilyMono,
        fontSize: '14px',
      },
      // Paragraph Large — Inter, 18/28, 400, 0% (long-form text)
      paragraphLarge: {
        fontFamily: fontFamilyBody,
        fontSize: '18px',
        fontWeight: 400,
        lineHeight: '28px',
        letterSpacing: 0,
      },
      // Paragraph XSmall — Inter, 12/20, 400, 0% (captions)
      paragraphXSmall: {
        fontFamily: fontFamilyBody,
        fontSize: '12px',
        fontWeight: 400,
        lineHeight: '20px',
        letterSpacing: 0,
      },
      // Custom: Navigation item (Label Large alias)
      navigationItem: {
        fontFamily: fontFamilyBody,
        fontSize: '16px',
        fontWeight: 500,
        lineHeight: '18px',
      },
      // Custom: Small text (Label Small alias)
      smallText: {
        fontFamily: fontFamilyBody,
        fontSize: '12px',
        fontWeight: 500,
        lineHeight: '16px',
        letterSpacing: '0.02em',
      },
      // Custom: Tiny text (Label XSmall alias)
      tinyText: {
        fontFamily: fontFamilyBody,
        fontSize: '10px',
        fontWeight: 500,
        lineHeight: '14px',
        letterSpacing: '0.04em',
      },
    },

    // ========================================================================
    // COMPONENT OVERRIDES — Design System v4
    // ========================================================================
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          ':root': {
            colorScheme: mode,
            '--font-body': fontFamilyBody,
            '--font-mono': fontFamilyMono,
            '--border-color': isDark ? 'rgba(255,255,255,0.08)' : neutral[200],
            '--surface-color': isDark ? palette.scale[900] : '#FFFFFF',
            '--sidebar-color': isDark ? palette.scale[1000] : '#FFFFFF',
          },
          html: {
            WebkitFontSmoothing: 'antialiased',
            MozOsxFontSmoothing: 'grayscale',
          },
          body: {
            margin: 0,
            padding: 0,
            backgroundColor: isDark ? palette.scale[1100] : neutral[50],
            color: isDark ? palette.scale[100] : neutral[900],
            fontFamily: fontFamilyBody,
            fontSize: '0.875rem',
            lineHeight: 1.5,
          },
          '#root': {
            minHeight: '100vh',
          },
          '*, *::before, *::after': {
            boxSizing: 'border-box',
          },
          'code, pre': {
            fontFamily: fontFamilyMono,
          },
          '::selection': {
            backgroundColor: alpha(primary[500], 0.2),
            color: 'inherit',
          },
          '::-webkit-scrollbar': {
            width: 8,
            height: 8,
          },
          '::-webkit-scrollbar-track': {
            backgroundColor: 'transparent',
          },
          '::-webkit-scrollbar-thumb': {
            backgroundColor: isDark ? alpha(palette.scale[100], 0.15) : alpha(neutral[900], 0.15),
            borderRadius: 4,
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.25) : alpha(neutral[900], 0.25),
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

      // ====================================================================
      // PAPER — shadow-only, no borders
      // ====================================================================
      MuiPaper: {
        defaultProps: { elevation: 1 },
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            backgroundColor: isDark ? palette.scale[1000] : '#FFFFFF',
            borderRadius: 8,
            border: 'none',
          },
          outlined: {
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : neutral[200]}`,
            boxShadow: 'none',
          },
          elevation0: { boxShadow: 'none' },
          elevation1: {
            boxShadow: isDark ? '0 4px 12px rgba(0,0,0,0.3)' : figmaShadow.xsmall,
          },
          elevation2: {
            boxShadow: isDark
              ? '0 6px 16px rgba(0,0,0,0.35)'
              : '0 1px 2px rgba(16, 24, 40, 0.04), 0 4px 8px rgba(16, 24, 40, 0.04)',
          },
          elevation3: {
            boxShadow: isDark
              ? '0 8px 24px rgba(0,0,0,0.4)'
              : '0 1px 2px rgba(16, 24, 40, 0.04), 0 4px 8px rgba(16, 24, 40, 0.06), 0 8px 16px rgba(16, 24, 40, 0.04)',
          },
        },
      },

      // ====================================================================
      // CARD — bg Neutral 50, border Neutral 200
      // ====================================================================
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            borderRadius: 8,
            backgroundColor: isDark ? palette.scale[1000] : neutral[50],
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : neutral[200]}`,
            boxShadow: isDark ? 'none' : figmaShadow.xsmall,
            transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
            // Add default padding for cards without CardContent
            '&:not(:has(.MuiCardContent-root))': {
              padding: 24,
            },
            '&:hover': {
              borderColor: isDark ? alpha(palette.scale[100], 0.15) : neutral[300],
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

      // ====================================================================
      // BUTTON — Primary 500 bg, Primary 600 hover
      // Label: Label Medium (Inter 14px/500)
      // ====================================================================
      MuiButtonBase: {
        defaultProps: { disableRipple: true },
        styleOverrides: {
          root: {
            transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
            '&:active': {
              transform: 'scale(0.97)',
            },
          },
        },
      },
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 500,
            fontSize: '0.875rem',
            lineHeight: 1.143,
            padding: '8px 12px',
            minHeight: 40,
            transition: 'all 150ms ease',
            '&:focus-visible': {
              outline: `2px solid ${isDark ? palette.scale[400] : neutral[900]}`,
              outlineOffset: 2,
              boxShadow: `0 0 0 4px ${isDark ? alpha(palette.scale[400], 0.25) : alpha(neutral[900], 0.15)}`,
            },
          },
          // Contained primary — dark neutral (consistent across all pages)
          contained: {
            backgroundColor: isDark ? palette.scale[300] : neutral[900],
            color: isDark ? palette.scale[1100] : '#FFFFFF',
            '&:hover': {
              backgroundColor: isDark ? palette.scale[200] : neutral[700],
            },
            '&:active': {
              backgroundColor: isDark ? palette.scale[100] : neutral[800],
            },
            '&.Mui-disabled': {
              backgroundColor: isDark ? palette.scale[800] : neutral[200],
              color: isDark ? palette.scale[600] : neutral[500],
              cursor: 'not-allowed',
              pointerEvents: 'auto',
            },
          },
          // Secondary contained — neutral
          containedSecondary: {
            backgroundColor: isDark ? palette.scale[800] : neutral[100],
            color: isDark ? palette.scale[100] : neutral[700],
            border: `1px solid ${isDark ? palette.scale[700] : neutral[200]}`,
            boxShadow: 'none',
            '&:hover': {
              backgroundColor: isDark ? palette.scale[700] : neutral[200],
              boxShadow: 'none',
            },
          },
          // Outlined — flat with border
          outlined: {
            borderColor: isDark ? palette.scale[700] : neutral[300],
            color: isDark ? palette.scale[100] : neutral[700],
            backgroundColor: isDark ? alpha(palette.scale[100], 0.05) : neutral[100],
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.08) : neutral[200],
              borderColor: isDark ? palette.scale[600] : neutral[400],
            },
            '&.Mui-disabled': {
              color: isDark ? palette.scale[600] : neutral[400],
              borderColor: isDark ? palette.scale[800] : neutral[200],
              backgroundColor: isDark ? alpha(palette.scale[100], 0.03) : neutral[50],
              cursor: 'not-allowed',
              pointerEvents: 'auto',
            },
          },
          // Text button
          text: {
            color: isDark ? palette.scale[400] : neutral[700],
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.05) : 'rgba(0,0,0,0.04)',
              color: isDark ? palette.scale[200] : neutral[900],
            },
          },
          sizeSmall: {
            padding: '6px 8px',
            fontSize: '0.75rem',
            minHeight: 32,
          },
          sizeLarge: {
            padding: '12px 16px',
            fontSize: '1rem',
            minHeight: 44,
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            borderRadius: 6,
            color: isDark ? palette.scale[500] : neutral[500],
            transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.06) : 'rgba(0,0,0,0.03)',
              color: isDark ? palette.scale[200] : neutral[700],
              '& .MuiSvgIcon-root': {
                filter: `drop-shadow(0 0 4px ${alpha(primary[500], 0.3)})`,
              },
            },
            '&:focus-visible': {
              outline: `2px solid ${isDark ? palette.scale[400] : neutral[900]}`,
              outlineOffset: 2,
              boxShadow: `0 0 0 4px ${isDark ? alpha(palette.scale[400], 0.25) : alpha(neutral[900], 0.15)}`,
            },
          },
          sizeSmall: { padding: 6 },
          sizeMedium: { padding: 8 },
        },
      },

      // ====================================================================
      // CHIP/PILL — 24px pill shape
      // ====================================================================
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: figmaSpacing.pillBorderRadius,
            fontFamily: fontFamilyBody,
            fontWeight: 500,
            fontSize: '12px',
            height: 24,
          },
          filled: {
            backgroundColor: isDark ? alpha(palette.scale[100], 0.1) : neutral[100],
          },
          outlined: {
            borderColor: isDark ? alpha(palette.scale[100], 0.15) : neutral[200],
          },
          colorSuccess: {
            backgroundColor: isDark ? alpha(palette.green[400], 0.15) : palette.green[100],
            color: isDark ? palette.green[400] : palette.green[600],
            borderColor: 'transparent',
          },
          colorError: {
            backgroundColor: isDark ? alpha(palette.red[500], 0.15) : palette.red[100],
            color: isDark ? palette.red[400] : status.destructive,
            borderColor: 'transparent',
          },
          colorWarning: {
            backgroundColor: isDark ? alpha(palette.yellow[400], 0.15) : palette.yellow[100],
            color: isDark ? palette.yellow[400] : palette.yellow[600],
            borderColor: 'transparent',
          },
          colorInfo: {
            backgroundColor: isDark ? alpha(palette.scale[100], 0.1) : neutral[100],
            color: isDark ? palette.scale[300] : neutral[700],
            borderColor: 'transparent',
          },
          sizeSmall: {
            height: 20,
            fontSize: '10px',
          },
        },
      },

      // ====================================================================
      // INPUT / TEXT FIELD
      // Label: Label Small / Neutral 700
      // Text: Paragraph Small / Neutral 900
      // Placeholder: Neutral 500
      // Border: Neutral 300, focus Primary 500
      // ====================================================================
      MuiTextField: {
        defaultProps: { size: 'small', variant: 'outlined' },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontFamily: fontFamilyBody,
            fontSize: '14px',
            backgroundColor: isDark ? palette.scale[900] : neutral[100],
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: isDark ? alpha(palette.scale[100], 0.12) : neutral[300],
              borderWidth: 1,
              transition: 'border-color 150ms ease',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: isDark ? alpha(palette.scale[100], 0.25) : neutral[400],
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: isDark ? palette.scale[300] : neutral[900],
              borderWidth: 2,
            },
            '&.Mui-error .MuiOutlinedInput-notchedOutline': {
              borderColor: status.destructive,
            },
          },
          input: {
            // Paragraph Small — 14/20, 400, 0% per PDF spec
            padding: '8px 12px',
            height: '24px',
            lineHeight: '20px',
            '&::placeholder': {
              fontFamily: fontFamilyBody,
              color: isDark ? palette.scale[500] : neutral[500],
              opacity: 1,
            },
          },
          inputSizeSmall: {
            padding: '6px 12px',
            height: '20px',
          },
          adornedStart: {
            paddingLeft: 12,
            '& .MuiInputAdornment-root': { marginRight: 8 },
          },
        },
      },
      MuiInputLabel: {
        styleOverrides: {
          root: {
            // Label Small — 12/16, 500 per PDF spec (letterSpacing normalized to avoid rendering gaps)
            fontFamily: fontFamilyBody,
            fontSize: '12px',
            fontWeight: 500,
            lineHeight: '16px',
            letterSpacing: 'normal',
            color: isDark ? palette.scale[400] : neutral[700],
            '&.Mui-focused': {
              color: isDark ? palette.scale[200] : neutral[900],
            },
          },
        },
      },
      MuiFormHelperText: {
        styleOverrides: {
          root: {
            marginTop: 6,
            fontSize: '0.75rem',
            color: isDark ? palette.scale[500] : neutral[500],
          },
        },
      },
      MuiSelect: {
        styleOverrides: {
          icon: { color: isDark ? palette.scale[500] : neutral[500] },
        },
      },

      // ====================================================================
      // MENU / DROPDOWN
      // ====================================================================
      MuiMenu: {
        styleOverrides: {
          paper: {
            borderRadius: 8,
            backgroundColor: isDark ? palette.scale[900] : 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(12px)',
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.1) : neutral[200]}`,
            boxShadow: isDark
              ? '0 4px 24px rgba(0,0,0,0.4)'
              : '0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.1)',
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
            color: isDark ? palette.scale[300] : neutral[700],
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.05) : 'rgba(0,0,0,0.03)',
              color: isDark ? palette.scale[100] : neutral[900],
            },
            '&.Mui-selected': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.08) : 'rgba(0,0,0,0.04)',
              color: isDark ? palette.scale[100] : neutral[900],
              '&:hover': {
                backgroundColor: isDark ? alpha(palette.scale[100], 0.1) : 'rgba(0,0,0,0.05)',
              },
            },
          },
        },
      },

      // ====================================================================
      // NAVIGATION ITEMS
      // ====================================================================
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: '10px 12px',
            minHeight: 40,
            gap: 8,
            transition: 'all 150ms ease',
            color: isDark ? palette.scale[400] : neutral[700],
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.05) : neutral[100],
              color: isDark ? palette.scale[200] : neutral[900],
            },
            '&.Mui-selected': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.08) : neutral[200],
              color: isDark ? palette.scale[100] : neutral[900],
              '&:hover': {
                backgroundColor: isDark ? alpha(palette.scale[100], 0.1) : neutral[200],
              },
            },
          },
        },
      },
      MuiListItemIcon: {
        styleOverrides: {
          root: {
            minWidth: 28,
            width: 20,
            height: 20,
            color: isDark ? palette.scale[500] : neutral[500],
            '.Mui-selected &': {
              color: isDark ? palette.scale[200] : neutral[700],
            },
          },
        },
      },
      MuiListItemText: {
        styleOverrides: {
          primary: {
            fontFamily: fontFamilyBody,
            fontSize: '16px',
            fontWeight: 500,
            lineHeight: 'normal',
            color: 'inherit',
          },
          secondary: {
            fontFamily: fontFamilyBody,
            fontSize: '12px',
            color: isDark ? palette.scale[500] : neutral[500],
          },
        },
      },

      MuiDivider: {
        styleOverrides: {
          root: {
            borderColor: isDark ? alpha(palette.scale[100], 0.08) : neutral[200],
          },
        },
      },

      // ====================================================================
      // AVATAR
      // ====================================================================
      MuiAvatar: {
        styleOverrides: {
          root: {
            width: figmaComponents.userAvatar.size,
            height: figmaComponents.userAvatar.size,
            border: isDark ? `1px solid ${palette.scale[600]}` : `1px solid ${neutral[400]}`,
            borderRadius: figmaComponents.userAvatar.borderRadius,
            backgroundColor: isDark ? palette.scale[800] : neutral[100],
            color: isDark ? palette.scale[300] : neutral[700],
            fontSize: '12px',
            fontFamily: fontFamilyBody,
            fontWeight: 500,
          },
        },
      },
      MuiBadge: {
        styleOverrides: {
          badge: { fontWeight: 600, fontSize: '0.625rem' },
        },
      },

      // ====================================================================
      // TOOLTIP
      // ====================================================================
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: isDark ? palette.scale[800] : palette.scale[1000],
            color: isDark ? palette.scale[100] : palette.scale[100],
            fontSize: '0.75rem',
            fontWeight: 500,
            padding: '6px 10px',
            borderRadius: 6,
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          },
          arrow: {
            color: isDark ? palette.scale[800] : palette.scale[1000],
          },
        },
      },

      // ====================================================================
      // DIALOG
      // ====================================================================
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 12,
            backgroundColor: isDark ? palette.scale[1000] : '#FFFFFF',
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.1) : neutral[200]}`,
            boxShadow: isDark
              ? '0 16px 48px rgba(0,0,0,0.4)'
              : '0 2px 8px rgba(0,0,0,0.06), 0 16px 48px rgba(0,0,0,0.12)',
          },
        },
      },
      MuiDialogTitle: {
        styleOverrides: {
          root: {
            fontSize: '1rem',
            fontWeight: 500,
            padding: '20px 24px 12px',
            color: isDark ? palette.scale[100] : neutral[900],
          },
        },
      },
      MuiDialogContent: {
        styleOverrides: {
          root: { padding: '12px 24px' },
        },
      },
      MuiDialogActions: {
        styleOverrides: {
          root: { padding: '12px 24px 20px', gap: 8, flexWrap: 'wrap' },
        },
      },

      // ====================================================================
      // DRAWER / SIDEBAR
      // ====================================================================
      MuiDrawer: {
        styleOverrides: {
          paper: {
            width: figmaSpacing.sidebarWidth,
            backgroundColor: isDark ? palette.scale[1000] : neutral[50],
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
            backgroundColor: isDark ? palette.scale[1000] : 'rgba(255, 255, 255, 0.85)',
            backdropFilter: 'blur(12px)',
            borderBottom: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : neutral[200]}`,
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

      // ====================================================================
      // TABS — Primary amber accent
      // ====================================================================
      MuiTabs: {
        styleOverrides: {
          root: {
            minHeight: 40,
            borderBottom: isDark
              ? `1px solid ${alpha(palette.scale[100], 0.1)}`
              : `1px solid ${neutral[200]}`,
          },
          indicator: {
            height: 2,
            borderRadius: 0,
            backgroundColor: isDark ? palette.scale[100] : neutral[900],
          },
          flexContainer: { gap: 0 },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontFamily: fontFamilyBody,
            fontWeight: 500,
            fontSize: '14px',
            minHeight: 40,
            padding: '8px 32px',
            borderBottom: '2px solid transparent',
            color: isDark ? palette.scale[500] : neutral[700],
            backgroundColor: 'transparent',
            transition: 'all 150ms ease',
            '&.Mui-selected': {
              fontWeight: 500,
              color: isDark ? palette.scale[100] : neutral[900],
              backgroundColor: isDark ? alpha(palette.scale[100], 0.08) : neutral[100],
            },
            '&:hover': {
              color: isDark ? palette.scale[300] : neutral[700],
              backgroundColor: isDark ? alpha(palette.scale[100], 0.04) : neutral[50],
            },
          },
        },
      },

      // ====================================================================
      // TABLE — Header: Label Small / Neutral 700
      //         Cell: Paragraph Small / Neutral 900
      //         Divider: Neutral 200, Zebra: Neutral 50
      // ====================================================================
      MuiTable: {
        styleOverrides: {
          root: {
            borderCollapse: 'separate',
            borderSpacing: 0,
            backgroundColor: isDark ? palette.scale[1000] : '#FFFFFF',
          },
        },
      },
      MuiTableContainer: {
        styleOverrides: {
          root: { border: 'none', borderRadius: 0 },
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: {
            '& .MuiTableCell-head': {
              backgroundColor: isDark ? palette.scale[900] : neutral[50],
              fontFamily: fontFamilyBody,
              fontWeight: 500,
              fontSize: '12px',
              letterSpacing: '0.02em',
              color: isDark ? palette.scale[400] : neutral[700],
              textTransform: 'none',
              borderBottom: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : neutral[200]}`,
              height: 60,
              padding: `0 ${figmaComponents.dataTable.cellPadding}px`,
            },
          },
        },
      },
      MuiTableBody: {
        styleOverrides: {
          root: {
            '& .MuiTableRow-root': {
              '&:nth-of-type(even)': {
                backgroundColor: isDark ? 'transparent' : neutral[50],
              },
              '&:hover': {
                backgroundColor: isDark ? alpha(palette.scale[100], 0.02) : alpha(neutral[100], 0.5),
              },
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: { height: 60 },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            fontFamily: fontFamilyBody,
            fontSize: '14px',
            color: isDark ? palette.scale[200] : neutral[900],
            padding: `0 ${figmaComponents.dataTable.cellPadding}px`,
            height: 60,
            borderBottom: `1px solid ${isDark ? alpha(palette.scale[100], 0.06) : neutral[200]}`,
            borderLeft: 'none',
            borderRight: 'none',
          },
        },
      },
      MuiTablePagination: {
        styleOverrides: {
          root: {
            borderTop: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : 'rgba(0,0,0,0.05)'}`,
          },
          selectLabel: { fontSize: '0.75rem', color: isDark ? palette.scale[500] : neutral[500] },
          displayedRows: { fontSize: '0.75rem', color: isDark ? palette.scale[500] : neutral[500] },
        },
      },

      // ====================================================================
      // CHECKBOX / SWITCH — Primary 500 checked
      // ====================================================================
      MuiCheckbox: {
        styleOverrides: {
          root: {
            color: isDark ? palette.scale[600] : neutral[400],
            padding: 8,
            '&.Mui-checked': {
              color: isDark ? palette.scale[200] : neutral[900],
            },
            '&:hover': {
              backgroundColor: isDark ? alpha(palette.scale[100], 0.04) : alpha(neutral[900], 0.04),
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
                backgroundColor: isDark ? palette.scale[200] : '#22c55e',
                opacity: 1,
              },
            },
          },
          thumb: { width: 20, height: 20, boxShadow: '0 2px 4px rgba(0,0,0,0.2)' },
          track: {
            borderRadius: 12,
            backgroundColor: isDark ? palette.scale[700] : neutral[400],
            opacity: 1,
          },
        },
      },

      // ====================================================================
      // PROGRESS — Primary 500
      // ====================================================================
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            height: 4,
            borderRadius: 2,
            backgroundColor: isDark ? palette.scale[800] : neutral[200],
          },
          bar: {
            borderRadius: 2,
            backgroundColor: isDark ? palette.scale[400] : primary[500],
          },
        },
      },
      MuiCircularProgress: {
        styleOverrides: {
          root: {
            color: isDark ? palette.scale[400] : primary[500],
          },
        },
      },
      MuiSkeleton: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? alpha(palette.scale[100], 0.1) : alpha(neutral[900], 0.11),
          },
        },
      },

      // ====================================================================
      // ALERT
      // ====================================================================
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontSize: '0.875rem',
            alignItems: 'flex-start',
            padding: '12px 16px',
            backgroundColor: isDark ? alpha(palette.scale[100], 0.05) : neutral[50],
            color: isDark ? palette.scale[200] : neutral[900],
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.1) : neutral[200]}`,
          },
          standardSuccess: {
            backgroundColor: isDark ? alpha(palette.green[400], 0.08) : '#f0fdf4',
            color: isDark ? palette.scale[200] : neutral[900],
            border: `1px solid ${isDark ? alpha(palette.green[400], 0.2) : '#bbf7d0'}`,
            '& .MuiAlert-icon': { color: isDark ? palette.green[400] : palette.green[600] },
          },
          standardError: {
            backgroundColor: isDark ? alpha(palette.red[500], 0.08) : '#fef2f2',
            color: isDark ? palette.scale[200] : neutral[900],
            border: `1px solid ${isDark ? alpha(palette.red[500], 0.2) : '#fecaca'}`,
            '& .MuiAlert-icon': { color: isDark ? palette.red[400] : palette.red[600] },
          },
          standardWarning: {
            backgroundColor: isDark ? alpha(palette.yellow[400], 0.08) : '#fffbeb',
            color: isDark ? palette.scale[200] : neutral[900],
            border: `1px solid ${isDark ? alpha(palette.yellow[400], 0.2) : '#fde68a'}`,
            '& .MuiAlert-icon': { color: isDark ? palette.yellow[400] : palette.yellow[600] },
          },
          standardInfo: {
            backgroundColor: isDark ? alpha(palette.blue[400], 0.08) : '#eff6ff',
            color: isDark ? palette.scale[200] : neutral[900],
            border: `1px solid ${isDark ? alpha(palette.blue[400], 0.2) : '#bfdbfe'}`,
            '& .MuiAlert-icon': { color: isDark ? palette.blue[400] : palette.blue[500] },
          },
          icon: {
            marginRight: 12,
            padding: 0,
            opacity: 1,
          },
        },
      },
      MuiSnackbar: {
        styleOverrides: {
          root: {
            '& .MuiAlert-root': {
              boxShadow: isDark
                ? '0 4px 24px rgba(0,0,0,0.4)'
                : '0 4px 24px rgba(0,0,0,0.1)',
            },
          },
        },
      },

      // ====================================================================
      // BREADCRUMBS & LINK
      // ====================================================================
      MuiBreadcrumbs: {
        styleOverrides: {
          separator: {
            color: isDark ? palette.scale[600] : neutral[400],
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
            color: isDark ? palette.scale[300] : primary[500],
            textDecorationColor: isDark ? alpha(palette.scale[300], 0.4) : alpha(primary[500], 0.4),
            '&:hover': {
              color: isDark ? palette.scale[100] : primary[600],
              textDecorationColor: isDark ? palette.scale[100] : primary[600],
            },
          },
        },
      },

      // ====================================================================
      // ACCORDION — Design System v4 Component Mapping
      // Container: bg Neutral 50 / White, border Neutral 200
      // Title: H6 (20/28, 500) / Neutral 900
      // Subtext: Paragraph Small (14/20, 400) / Neutral 500
      // Badge: bg Primary 50, text Primary 600
      // Icon: Neutral 900 @ 20% opacity
      // ====================================================================
      MuiAccordion: {
        defaultProps: { disableGutters: true, elevation: 0 },
        styleOverrides: {
          root: {
            backgroundColor: isDark ? palette.scale[1000] : neutral[50],
            border: `1px solid ${isDark ? alpha(palette.scale[100], 0.08) : neutral[200]}`,
            borderRadius: 8,
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
          expandIconWrapper: {
            color: isDark ? palette.scale[500] : neutral[400],
          },
        },
      },
      MuiAccordionDetails: {
        styleOverrides: {
          root: {
            padding: '0 16px 16px',
            fontFamily: fontFamilyBody,
            fontSize: '14px',
            lineHeight: '20px',
            color: isDark ? palette.scale[400] : neutral[500],
          },
        },
      },
    },
  })
}

// Export default light theme
const theme = createAppTheme('light')

export default theme

// ============================================================================
// EXPORTS — Canonical + backward-compatible aliases
// ============================================================================
export {
  createAppTheme,
  palette,
  // New canonical tokens (Design System v4)
  neutral,
  primary,
  status,
  secondary,
  fontFamilyDisplay,
  // Font families
  fontFamilyHeading,
  fontFamilyUI,
  fontFamilyBody,
  fontFamilyMono,
  // Layout & component tokens
  figmaShadow,
  figmaSpacing,
  figmaComponents,
}
