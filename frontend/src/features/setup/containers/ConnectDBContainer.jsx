import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import {
  Box, Stack, TextField, Button, Typography,
  Alert, InputAdornment, IconButton, Chip, Collapse, List, ListItemButton,
  ListItemText, Fade, Portal, Grid, FormControl, FormControlLabel,
  Checkbox, FormHelperText, ToggleButton, ToggleButtonGroup, Tooltip,
  MenuItem, OutlinedInput, Select
} from '@mui/material'
import { alpha, styled } from '@mui/material/styles'
import { useForm, Controller } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import {
  isMock,
  testConnection as apiTestConnection,
  upsertConnection as apiUpsertConnection,
  deleteConnection as apiDeleteConnection,
  healthcheckConnection as apiHealthcheckConnection,
} from '@/api/client'
import { checkHealth } from '@/api/health'
import * as mock from '@/api/mock'
import { useMutation } from '@tanstack/react-query'
import { useAppStore } from '@/stores'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import SpeedIcon from '@mui/icons-material/Speed'
import EditIcon from '@mui/icons-material/Edit'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight'
import StorageIcon from '@mui/icons-material/Storage'
import DnsIcon from '@mui/icons-material/Dns'
import LanIcon from '@mui/icons-material/Lan'
import HubIcon from '@mui/icons-material/Hub'
import CloseIcon from '@mui/icons-material/Close'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import ConfirmDialog from '@/components/ConfirmDialog.jsx'
import { useToast } from '@/components/ToastProvider.jsx'
import HeartbeatBadge from '@/components/HeartbeatBadge.jsx'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'
import EmptyState from '@/components/feedback/EmptyState.jsx'
import FormErrorSummary from '@/components/form/FormErrorSummary.jsx'
import TOOLTIP_COPY from '@/content/tooltipCopy.jsx'
import { savePersistedCache } from '@/hooks/useBootstrapState.js'
import useFormErrorFocus from '@/hooks/useFormErrorFocus.js'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { neutral, palette, fontFamilyMono } from '@/app/theme'
const sanitizeDbType = (value) => (typeof value === 'string' ? value.trim().toLowerCase() : '')
const trimString = (value) => (typeof value === 'string' ? value.trim() : '')
const formatHostPort = (host, port) => {
  const cleanHost = trimString(host)
  if (!cleanHost) return ''
  const numericPort = typeof port === 'number' ? port : Number(port)
  if (!numericPort || Number.isNaN(numericPort)) return cleanHost
  return `${cleanHost}:${numericPort}`
}
const buildAuthSegment = (username, password) => {
  const user = trimString(username)
  if (!user) return ''
  const encodedUser = encodeURIComponent(user)
  if (password != null && password !== '') {
    return `${encodedUser}:${encodeURIComponent(password)}@`
  }
  return `${encodedUser}@`
}
const defaultDisplayName = ({ db_type, host, port, database, databasePath }) => {
  const typeKey = sanitizeDbType(db_type || 'sqlite')
  if (typeKey === 'sqlite') {
    const source = trimString(databasePath) || trimString(database) || ''
    return `sqlite@${source}`
  }
  const hostPart = formatHostPort(host, port) || 'unknown'
  const dbPart = database ? `/${database}` : ''
  return `${typeKey}@${hostPart}${dbPart}`
}
const DB_CONFIG = {
  postgres: {
    label: 'PostgreSQL',
    defaultPort: 5432,
    buildUrl: ({ username, password, host, port, database }) => {
      const auth = buildAuthSegment(username, password)
      return `postgresql://${auth}${trimString(host)}${port ? `:${port}` : ''}/${encodeURIComponent(database)}`
    },
    buildDisplay: ({ host, port, database }) => defaultDisplayName({ db_type: 'postgres', host, port, database }),
  },
  mysql: {
    label: 'MySQL/MariaDB',
    defaultPort: 3306,
    buildUrl: ({ username, password, host, port, database }) => {
      const auth = buildAuthSegment(username, password)
      return `mysql+mysqldb://${auth}${trimString(host)}${port ? `:${port}` : ''}/${encodeURIComponent(database)}`
    },
    buildDisplay: ({ host, port, database }) => defaultDisplayName({ db_type: 'mysql', host, port, database }),
  },
  mssql: {
    label: 'SQL Server',
    defaultPort: 1433,
    driver: 'ODBC Driver 17 for SQL Server',
    buildUrl: ({ username, password, host, port, database, ssl, driver }) => {
      const auth = buildAuthSegment(username, password)
      const driverName = trimString(driver) || 'ODBC Driver 17 for SQL Server'
      const params = [`driver=${encodeURIComponent(driverName)}`]
      if (ssl) {
        params.push('Encrypt=yes', 'TrustServerCertificate=yes')
      }
      const query = params.length ? `?${params.join('&')}` : ''
      return `mssql+pyodbc://${auth}${trimString(host)}${port ? `:${port}` : ''}/${encodeURIComponent(database)}${query}`
    },
    buildDisplay: ({ host, port, database }) => defaultDisplayName({ db_type: 'mssql', host, port, database }),
  },
  sqlite: {
    label: 'SQLite',
    defaultPort: null,
    buildDisplay: ({ database }) => defaultDisplayName({ db_type: 'sqlite', database, databasePath: database }),
  },
}
const SUPPORTED_DB_TYPES = Object.keys(DB_CONFIG)

// Neutral grey accents per Figma design (no colored accents)
const DB_TYPE_META = {
  sqlite: {
    label: DB_CONFIG.sqlite.label,
    icon: StorageIcon,
    accent: neutral[700],  // Grey/1100
  },
  postgres: {
    label: DB_CONFIG.postgres.label,
    icon: DnsIcon,
    accent: neutral[500],  // Grey/1000
  },
  mysql: {
    label: DB_CONFIG.mysql.label,
    icon: LanIcon,
    accent: neutral[500],  // Grey/900
  },
  mssql: {
    label: DB_CONFIG.mssql.label,
    icon: HubIcon,
    accent: neutral[300],  // Grey/800
  },
}

const DB_TYPE_OPTIONS = [
  { value: 'sqlite', ...DB_TYPE_META.sqlite },
  { value: 'postgres', ...DB_TYPE_META.postgres },
  { value: 'mysql', ...DB_TYPE_META.mysql },
  { value: 'mssql', ...DB_TYPE_META.mssql },
]

const computeCurrentSignature = (values = {}) => JSON.stringify({
  name: trimString(values.name),
  db_type: sanitizeDbType(values.db_type),
  host: trimString(values.host),
  port: trimString(values.port),
  db_name: trimString(values.db_name),
  username: trimString(values.username),
  password: values.password || '',
  ssl: Boolean(values.ssl),
  driver: trimString(values.driver),
})

const DEFAULT_FORM_VALUES = {
  name: '',
  db_type: 'sqlite',
  host: '',
  port: '',
  db_name: '',
  username: '',
  password: '',
  ssl: false,
}


const CONTROL_HEIGHT = 44
const CONTROL_RADIUS = 12

const FORM_FIELD_ORDER = [
  'name',
  'db_type',
  'host',
  'port',
  'db_name',
  'username',
  'password',
  'ssl',
]

const FORM_FIELD_LABELS = {
  name: 'Connection name',
  db_type: 'Database type',
  host: 'Host',
  port: 'Port',
  db_name: 'Database',
  username: 'Username',
  password: 'Password',
  ssl: 'Use SSL',
}

const dbTypeToggleGroupSx = (theme) => ({
  marginTop: theme.spacing(1),
  display: 'grid',
  width: '100%',
  gap: theme.spacing(1),
  gridTemplateColumns: 'repeat(auto-fit, minmax(175px, 1fr))',
  [theme.breakpoints.down('sm')]: {
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
  },
  '& .MuiToggleButtonGroup-grouped': {
    margin: 0,
    border: 'none',
  },
})

const buildDbTypeButtonSx = (accent) => (theme) => {
  const accentColor = accent || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
  return {
    justifyContent: 'center',
    alignItems: 'center',
    textTransform: 'none',
    borderRadius: 8,
    border: `1px solid ${alpha(theme.palette.divider, 0.75)}`,
    padding: theme.spacing(1.1, 1.5),
    minHeight: 68,
    display: 'flex',
    flexDirection: 'row',
    gap: theme.spacing(1.1),
    minWidth: 0,
    backgroundColor: alpha(theme.palette.background.paper, 0.96),
    color: theme.palette.text.primary,
    transition: 'border-color 160ms cubic-bezier(0.22, 1, 0.36, 1), box-shadow 160ms cubic-bezier(0.22, 1, 0.36, 1), background-color 160ms cubic-bezier(0.22, 1, 0.36, 1), transform 160ms cubic-bezier(0.22, 1, 0.36, 1)',
    '& .db-type-icon': {
      width: 24,
      height: 24,
      borderRadius: 7,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: accentColor,
      backgroundColor: alpha(accentColor, 0.14),
      boxShadow: `0 4px 14px ${alpha(accentColor, 0.24)}`,
      flexShrink: 0,
    },
    '& .db-type-meta': {
      display: 'flex',
      flexDirection: 'column',
      gap: theme.spacing(0.25),
      alignItems: 'center',
      textAlign: 'center',
      minWidth: 0,
    },
    '&:hover': {
      borderColor: accentColor,
      backgroundColor: alpha(accentColor, 0.08),
    },
    '&:focus-visible': {
      outline: `2px solid ${alpha(accentColor, 0.5)}`,
      outlineOffset: 2,
    },
    '&.Mui-selected': {
      borderColor: accentColor,
      backgroundColor: alpha(accentColor, 0.14),
      boxShadow: `0 18px 36px ${alpha(accentColor, 0.28)}`,
      transform: 'translateY(-1px)',
    },
    '&.Mui-selected .db-type-icon': {
      backgroundColor: alpha(accentColor, 0.22),
    },
  }
}

const gridItemSx = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'stretch',
  flex: 1,
  minWidth: 0,
  maxWidth: '100%',
}

const StyledOutlinedInput = styled(OutlinedInput)(({ theme }) => ({
  borderRadius: CONTROL_RADIUS,
  height: CONTROL_HEIGHT,
  paddingRight: theme.spacing(1),
  '& .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '&:hover .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
    border: 'none',
  },
  '& .MuiOutlinedInput-input': {
    display: 'flex',
    alignItems: 'center',
    height: CONTROL_HEIGHT,
    padding: theme.spacing(1.1, 1.75),
  },
}))

const SelectField = ({
  value,
  options,
  menuProps: menuPropsProp,
  id,
  label,
  labelId,
  onChange,
  onBlur,
  inputRef,
  selectControlSx,
  error,
  helperText,
  widestLabel,
}) => {
  const normalizedValue = value ?? ''
  const ghostLabel = widestLabel || options.reduce((longest, opt) => (
    opt.label.length > longest.length ? opt.label : longest
  ), '')

  const baseMenuProps = {
    autoWidth: false,
    PaperProps: {
      elevation: 0,
      style: {
        borderRadius: '8px',
        borderTopLeftRadius: '12px',
        borderTopRightRadius: '12px',
        borderBottomRightRadius: '12px',
        borderBottomLeftRadius: '12px',
      },
      sx: {
        mt: 1.25,
        maxHeight: 320,
        minWidth: 360,
        borderRadius: '8px !important',
        borderTopLeftRadius: '12px !important',
        borderTopRightRadius: '12px !important',
        borderBottomRightRadius: '12px !important',
        borderBottomLeftRadius: '12px !important',
        border: `1px solid ${alpha(neutral[400], 0.28)}`,
        backgroundColor: 'rgba(255,255,255,0.98)',
        backdropFilter: 'blur(10px)',
        boxShadow: `0 22px 52px ${alpha(neutral[900], 0.22)}`,
        overflow: 'hidden',
        '&.MuiPaper-rounded': {
          borderRadius: '8px !important',
          borderTopLeftRadius: '12px !important',
          borderTopRightRadius: '12px !important',
          borderBottomRightRadius: '12px !important',
          borderBottomLeftRadius: '12px !important',
        },
      },
    },
    MenuListProps: {
      sx: { py: 1.1, px: 0.5 },
    },
  }

  const menuProps = {
    ...baseMenuProps,
    ...menuPropsProp,
  }
  if (menuPropsProp?.PaperProps) {
    menuProps.PaperProps = {
      ...baseMenuProps.PaperProps,
      ...menuPropsProp.PaperProps,
      sx: {
        ...baseMenuProps.PaperProps.sx,
        ...(menuPropsProp.PaperProps?.sx || {}),
      },
    }
  }
  if (menuPropsProp?.MenuListProps) {
    menuProps.MenuListProps = {
      ...baseMenuProps.MenuListProps,
      ...menuPropsProp.MenuListProps,
      sx: {
        ...(baseMenuProps.MenuListProps?.sx || {}),
        ...(menuPropsProp.MenuListProps?.sx || {}),
      },
    }
  }

  return (
    <Stack
      direction="row"
      spacing={1}
      alignItems="center"
      sx={{
        width: '100%',
        flexWrap: { xs: 'wrap', sm: 'nowrap' },
        rowGap: { xs: 1, sm: 0 },
        ml: { xs: 0, sm: 3 },
      }}
    >
      <Typography
        id={labelId}
        variant="caption"
        sx={(theme) => ({
          fontWeight: theme.typography.fontWeightBold,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: alpha(theme.palette.text.secondary, 0.85),
          minWidth: 72,
          whiteSpace: 'nowrap',
        })}
      >
        {label}
      </Typography>
      <FormControl
        size="small"
        margin="dense"
        variant="outlined"
        error={error}
        sx={[selectControlSx]}
        aria-labelledby={labelId}
      >
        <Select
          labelId={labelId}
          id={id}
          value={normalizedValue}
          onChange={onChange}
          onBlur={onBlur}
          inputRef={inputRef}
          input={(
            <StyledOutlinedInput
              sx={{
                pl: 0,
                pr: 3,
              }}
            />
          )}
          displayEmpty
          MenuProps={menuProps}
          sx={{
            display: 'block',
            width: '100%',
            '& .MuiSelect-select': {
              display: 'flex',
              alignItems: 'center',
              width: '100%',
              minWidth: 0,
              paddingTop: 0.5,
              paddingBottom: 0.5,
              boxSizing: 'border-box',
            },
            '& .MuiSelect-icon': {
              right: 12,
              color: 'text.secondary',
              opacity: 0.68,
            },
          }}
          renderValue={(selected) => {
            const selectedOption = options.find((opt) => opt.value === selected) || null
            const IconComponent = selectedOption?.icon
            const accentColor = selectedOption?.accent
            return (
                <Box sx={{ position: 'relative', width: '100%' }}>
                  <Stack direction="row" spacing={0.6} alignItems="center" sx={{ minWidth: 0, ml: 0.2, justifyContent: 'center' }}>
                    {IconComponent ? (
                    <Box
                      sx={(theme) => ({
                        width: 20,
                        height: 20,
                        borderRadius: 6,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
                        backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.12),
                        boxShadow: `0 4px 12px ${alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.18)}`,
                        flexShrink: 0,
                        ml: 0.1,
                      })}
                    >
                      <IconComponent fontSize="small" />
                    </Box>
                  ) : null}
                    <Box sx={{
                      flex: 1,
                      minWidth: 0,
                      overflow: 'hidden',
                    }}>
                    <Typography
                      variant="subtitle2"
                      component="span"
                      sx={(theme) => ({
                        fontWeight: theme.typography.fontWeightBold,
                        color: theme.palette.text.primary,
                        lineHeight: 1.2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        flexShrink: 0,
                        minWidth: 0,
                        textAlign: 'center',
                      })}
                    >
                      {selectedOption ? selectedOption.label : 'Choose a database'}
                    </Typography>
                  </Box>
                </Stack>
                <Box
                  aria-hidden
                  sx={{
                    position: 'absolute',
                    inset: 0,
                    opacity: 0,
                    whiteSpace: 'nowrap',
                    pointerEvents: 'none',
                  }}
                >
                  {ghostLabel}
                </Box>
              </Box>
            )
          }}
        >
          {options.map((opt) => {
            const IconComponent = opt.icon
            const accentColor = opt.accent
            return (
              <MenuItem
                key={opt.value}
                value={opt.value}
                sx={(theme) => ({
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 1.1,
                  py: 1.15,
                  px: 1.75,
                  borderRadius: 1,  // Figma spec: 8px
                  transition: 'background-color 140ms cubic-bezier(0.22, 1, 0.36, 1), transform 140ms cubic-bezier(0.22, 1, 0.36, 1)',
                  '&:hover': {
                    backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.08),
                    transform: 'translateX(4px)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.12),
                    color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
                    '&:hover': {
                      backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.16),
                    },
                  },
                })}
              >
                {IconComponent ? (
                  <Box
                    sx={(theme) => ({
                      width: 20,
                      height: 20,
                      borderRadius: 6,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]),
                      backgroundColor: alpha(accentColor || (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]), 0.1),
                      flexShrink: 0,
                      ml: 0.15,
                    })}
                  >
                    <IconComponent fontSize="small" />
                  </Box>
                ) : null}
                <Typography
                  variant="subtitle2"
                  component="span"
                  sx={(theme) => ({
                    fontWeight: theme.typography.fontWeightBold,
                    lineHeight: 1.2,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    flexShrink: 0,
                    minWidth: 0,
                    flex: 1,
                    textAlign: 'center',
                  })}
                >
                  {opt.label}
                </Typography>
              </MenuItem>
            )
          })}
        </Select>
        {helperText ? (
          <FormHelperText sx={{ mt: 0.75, mx: 0.5 }}>{helperText}</FormHelperText>
        ) : null}
      </FormControl>
    </Stack>
  )
}


/** ---------- validation ---------- */
const portField = yup
  .number()
  .transform((v, o) => (o === '' || o == null ? undefined : v))
  .typeError('Port must be a number')
  .integer()
  .min(1)
  .max(65535)



const schema = yup.object({
  name: yup
    .string()
    .trim()
    .max(80, 'Connection name must be 80 characters or less')
    .required('Connection name is required'),
  db_type: yup
    .string()
    .oneOf(SUPPORTED_DB_TYPES, 'Unsupported database type')
    .required('Database type is required'),
  host: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Host is required for remote databases'),
    otherwise: (f) => f.optional(),
  }),
  port: portField.when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Port is required for remote databases'),
    otherwise: (f) => f.optional(),
  }),
  db_name: yup.string().when('db_type', {
    is: (t) => t === 'sqlite',
    then: (f) => f.required('Database path is required for SQLite'),
    otherwise: (f) => f.required('Database name is required'),
  }),
  username: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Username is required'),
    otherwise: (f) => f.optional(),
  }),
  password: yup.string().when('db_type', {
    is: (t) => t !== 'sqlite',
    then: (f) => f.required('Password is required'),
    otherwise: (f) => f.optional(),
  }),
  ssl: yup.boolean().default(false),
}).required()



/** ---------- helpers ---------- */
const stripQuotes = (s) => (s || '').replace(/^["']|["']$/g, '')



/** Normalize form values into a connection payload. */
function normalizeConnection(values) {
  const typeKey = sanitizeDbType(values.db_type)
  if (!typeKey) throw new Error('Select a database type')
  if (!SUPPORTED_DB_TYPES.includes(typeKey)) {
    throw new Error(`Unsupported database type: ${values.db_type}`)
  }

  if (typeKey === 'sqlite') {
    const rawPath = stripQuotes(trimString(values.db_name))
    if (!rawPath) throw new Error('Provide a path to the SQLite .db file')

    const normalizedPath = rawPath.replace(/\\/g, '/').replace(/^\.\//, '')
    let db_url
    if (normalizedPath.startsWith('sqlite:')) {
      db_url = normalizedPath
    } else if (/^[a-zA-Z]:\//.test(normalizedPath)) {
      db_url = `sqlite:///${normalizedPath}`
    } else if (normalizedPath.startsWith('/')) {
      db_url = `sqlite://${normalizedPath}`
    } else {
      db_url = `sqlite:///${normalizedPath}`
    }

    return {
      db_type: 'sqlite',
      database: rawPath,
      databasePath: rawPath,
      path: rawPath,
      db_url,
      displayName: defaultDisplayName({ db_type: 'sqlite', databasePath: rawPath }),
      host: null,
      port: null,
      username: null,
      password: null,
      ssl: false,
      driver: null,
    }
  }

  const config = DB_CONFIG[typeKey]
  const host = trimString(values.host)
  if (!host) throw new Error('Host is required for remote databases')

  const database = trimString(values.db_name)
  if (!database) throw new Error('Database name is required')

  const username = trimString(values.username)
  const password = values.password != null ? values.password : ''
  if (password && !username) {
    throw new Error('Username is required when providing a password')
  }

  const rawPort = values.port
  const portValue =
    rawPort === '' || rawPort == null ? config.defaultPort : Number(rawPort)
  if (!Number.isInteger(portValue) || portValue <= 0 || portValue > 65535) {
    throw new Error('Port must be between 1 and 65535')
  }

  const ssl = Boolean(values.ssl)
  const db_url = config.buildUrl({
    username,
    password,
    host,
    port: portValue,
    database,
    ssl,
    driver: config.driver,
  })
  const displayName = config.buildDisplay
    ? config.buildDisplay({ host, port: portValue, database })
    : defaultDisplayName({ db_type: typeKey, host, port: portValue, database })

  return {
    db_type: typeKey,
    host,
    port: portValue,
    database,
    databasePath: null,
    path: database,
    username: username || null,
    password: password || '',
    ssl,
    driver: config.driver || null,
    db_url,
    displayName,
  }
}

/** The payload format we'll send to the backend. */
function payloadFromNormalized(n) {
  if (n.db_type === 'sqlite') {
    return {
      db_type: 'sqlite',
      db_url: n.db_url,
      database: n.database,
    }
  }

  return {
    db_type: n.db_type,
    db_url: n.db_url,
    host: n.host,
    port: n.port,
    database: n.database,
    username: n.username,
    password: n.password,
    ssl: Boolean(n.ssl),
    driver: n.driver,
  }
}



const pathToFileName = (value) => {
  if (typeof value !== 'string') return null
  const segments = value.split(/[/\\]+/).filter(Boolean)
  return segments.length ? segments[segments.length - 1] : value
}



const deriveSqliteUrl = (path) => {
  if (!path) return null
  const normalized = path.replace(/\\/g, '/').replace(/^\.\//, '')
  if (normalized.startsWith('sqlite:')) return normalized
  if (/^[a-zA-Z]:\//.test(normalized)) return `sqlite:///${normalized}`
  if (normalized.startsWith('/')) return `sqlite://${normalized}`
  return `sqlite:///${normalized}`
}



const formatSavedConnection = (record = {}, overrides = {}) => {
  const merged = { ...record, ...overrides }
  const id = merged.id || merged.backend_connection_id || merged.connection_id
  if (!id) return null

  const dbTypeRaw = merged.db_type || overrides.db_type || 'sqlite'
  const dbType = sanitizeDbType(dbTypeRaw || 'sqlite') || 'sqlite'

  const databasePath =
    merged.databasePath ||
    merged.database_path ||
    overrides.databasePath ||
    overrides.database_path ||
    null

  const databaseName =
    merged.database ||
    merged.database_name ||
    overrides.database ||
    overrides.database_name ||
    (dbType === 'sqlite' ? databasePath : null)

  const rawPortValue = merged.port ?? overrides.port ?? null
  const portValue =
    typeof rawPortValue === 'string'
      ? (rawPortValue.trim() ? Number(rawPortValue) : null)
      : rawPortValue

  const hostValue =
    dbType === 'sqlite'
      ? merged.host ?? overrides.host ?? databasePath
      : merged.host ?? overrides.host ?? merged.server ?? overrides.server ?? null

  const driver = merged.driver || overrides.driver || null
  const sslValue =
    typeof merged.ssl === 'boolean'
      ? merged.ssl
      : typeof overrides.ssl === 'boolean'
        ? overrides.ssl
        : undefined

  let summary = merged.summary || overrides.summary || null
  if (!summary) {
    if (dbType === 'sqlite') {
      summary = databasePath ? (pathToFileName(databasePath) || databasePath) : null
    } else {
      const hostPort = formatHostPort(hostValue, portValue) || hostValue || 'unknown'
      summary = databaseName ? `${hostPort}/${databaseName}` : hostPort
    }
  }

  const lastLatency =
    typeof merged.lastLatencyMs === 'number'
      ? merged.lastLatencyMs
      : typeof merged.last_latency_ms === 'number'
        ? merged.last_latency_ms
        : null

  const details = merged.details || merged.last_detail || overrides.details || null
  const dbUrl =
    merged.db_url ||
    overrides.db_url ||
    (dbType === 'sqlite' && databasePath ? deriveSqliteUrl(databasePath) : null)

  const name =
    merged.name ||
    overrides.name ||
    defaultDisplayName({
      db_type: dbType,
      host: hostValue,
      port: portValue,
      database: databaseName,
      databasePath,
    })

  return {
    id,
    backend_connection_id: merged.backend_connection_id || id,
    name,
    db_type: dbType,
    status: merged.status || overrides.status || 'unknown',
    summary,
    lastConnected: merged.lastConnected || merged.last_connected_at || overrides.lastConnected || null,
    lastLatencyMs: lastLatency,
    details,
    db_url: dbUrl,
    host: hostValue,
    port: portValue,
    database: databaseName,
    databasePath,
    driver,
    ssl: sslValue,
    hasCredentials: merged.hasCredentials ?? overrides.hasCredentials ?? true,
    tags: Array.isArray(merged.tags) ? merged.tags : Array.isArray(overrides.tags) ? overrides.tags : [],
  }
}

export default function ConnectDB() {
  const {
    connection,
    setConnection,
    setSetupStep,
    savedConnections,
    addSavedConnection,
    updateSavedConnection,
    removeSavedConnection,
    activeConnectionId,
    setActiveConnectionId,
  } = useAppStore()



  const toast = useToast()
  const { execute } = useInteraction()
  const [showPw, setShowPw] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [confirmSelect, setConfirmSelect] = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const deleteUndoRef = useRef(null)
  const [rowHeartbeat, setRowHeartbeat] = useState({})
  const [canSave, setCanSave] = useState(false)
  const testedSignatureRef = useRef(null)
  const currentSignatureRef = useRef('')
  const duplicateNameTimerRef = useRef(null)
  const [detailId, setDetailId] = useState(null)
  const listRef = useRef(null)
  const panelRef = useRef(null)
  const [detailAnchor, setDetailAnchor] = useState(null)
  const detailConnection = useMemo(() => savedConnections.find((c) => c.id === detailId) || null, [savedConnections, detailId])
  const detailHeartbeat = detailConnection ? rowHeartbeat[detailConnection.id] : null
  const detailStatus = detailConnection
    ? (detailHeartbeat?.status || (detailConnection.status === 'connected' ? 'healthy' : (detailConnection.status === 'failed' ? 'unreachable' : 'unknown')))
    : 'unknown'
  const detailLatency = detailConnection
    ? (detailHeartbeat?.latencyMs != null
      ? detailHeartbeat.latencyMs
      : detailConnection.lastLatencyMs != null
      ? detailConnection.lastLatencyMs
      : undefined)
    : undefined
  const detailNote = detailConnection ? (detailConnection.details || detailConnection.lastMessage || 'No recent notes') : 'No recent notes'
  const [lastLatencyMs, setLastLatencyMs] = useState(null)
  const [apiStatus, setApiStatus] = useState('unknown')



  useEffect(() => {
    if (!savedConnections.length) {
      if (detailId !== null) setDetailId(null)
      return
    }
    if (detailId == null) return
    const hasSelection = savedConnections.some((c) => c.id === detailId)
    if (!hasSelection) setDetailId(null)
  }, [savedConnections, detailId])



  useLayoutEffect(() => {
    if (typeof window === 'undefined') return undefined
    if (!detailConnection || !listRef.current) {
      setDetailAnchor(null)
      return undefined
    }



    const updatePosition = () => {
      const el = listRef.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0
      const maxViewportWidth = Math.max(320, viewportWidth - 32)
      const clampedWidth = Math.max(480, Math.min(640, rect.width))
      const width = Math.min(clampedWidth, maxViewportWidth)
      const panelEl = panelRef.current
      const measuredHeight = panelEl ? Math.min(panelEl.offsetHeight, viewportHeight - 96) : 0
      const fallbackHeight = Math.min(rect.height + 260, viewportHeight - 96)
      const height = measuredHeight || fallbackHeight
      const maxTop = Math.max(viewportHeight - height - 16, 16)
      const top = Math.min(Math.max(rect.top, 16), maxTop)
      const left = Math.min(Math.max(rect.left, 16), Math.max(viewportWidth - width - 16, 16))
      setDetailAnchor((prev) => {
        if (prev && prev.top === top && prev.left === left && prev.width === width) return prev
        return { top, left, width }
      })
    }



    updatePosition()
    const raf = window.requestAnimationFrame(updatePosition)
    window.addEventListener('resize', updatePosition)
    window.addEventListener('scroll', updatePosition, true)
    return () => {
      window.cancelAnimationFrame(raf)
      window.removeEventListener('resize', updatePosition)
      window.removeEventListener('scroll', updatePosition, true)
    }
  }, [detailConnection, detailId, savedConnections.length])



  const applySelection = (record) => {
    if (!record) return
    const targetId = record.backend_connection_id || record.id
    setActiveConnectionId(targetId)
    const fallbackUrl =
      record.db_url ||
      (sanitizeDbType(record.db_type) === 'sqlite'
        ? deriveSqliteUrl(record.databasePath || record.database || record.summary || '')
        : null)
    setConnection({
      saved: true,
      name: record.name,
      status: record.status,
      db_url: fallbackUrl || null,
      latencyMs: record.lastLatencyMs ?? null,
      lastMessage: record.details || record.status,
      details: record.details || record.status,
      connectionId: targetId,
      db_type: record.db_type,
      host: record.host ?? null,
      port: record.port ?? null,
      database: record.database ?? (sanitizeDbType(record.db_type) === 'sqlite' ? record.databasePath : null),
      driver: record.driver ?? null,
      ssl: record.ssl ?? false,
    })
    setDetailId(null)
    toast.show('Connection selected', 'success')
  }



  const requestSelect = (record) => {
    if (!record) return
    const targetId = record.backend_connection_id || record.id
    if (activeConnectionId && activeConnectionId !== targetId) {
      setConfirmSelect(record.id)
    } else {
      applySelection(record)
    }
  }



  const beginEditConnection = (record) => {
    if (!record) return
    setEditingId(record.id)
    const typeKey = sanitizeDbType(record.db_type || 'sqlite')
    const databaseValue =
      typeKey === 'sqlite'
        ? record.databasePath || record.database || record.summary || ''
        : record.database || ''
    const hostValue = typeKey === 'sqlite' ? '' : (record.host || '')
    const portValue =
      typeKey === 'sqlite'
        ? ''
        : record.port != null && record.port !== ''
          ? String(record.port)
          : ''
    reset({
      name: record.name || '',
      db_type: typeKey || 'sqlite',
      host: hostValue,
      port: portValue,
      db_name: databaseValue,
      username: '',
      password: '',
      ssl: Boolean(record.ssl),
    })
    const signature = computeCurrentSignature({
      name: record.name || '',
      db_type: typeKey || 'sqlite',
      host: hostValue,
      port: portValue,
      db_name: databaseValue,
      username: '',
      password: '',
      ssl: Boolean(record.ssl),
    })
    currentSignatureRef.current = signature
    testedSignatureRef.current = null
    setCanSave(false)
    setDetailId(null)
    setShowDetails(false)
    const normalizedUrl =
      record.db_url ||
      (sanitizeDbType(record.db_type) === 'sqlite'
        ? deriveSqliteUrl(record.databasePath || record.database || record.summary || '')
        : null)
    setConnection((prev) => ({
      ...prev,
      saved: true,
      status: record.status || prev.status || 'connected',
      name: record.name || prev.name || record.displayName || '',
      db_url: normalizedUrl,
      latencyMs: record.lastLatencyMs ?? prev.latencyMs ?? null,
      lastMessage: record.details || prev.lastMessage || '',
      details: record.details || prev.details || '',
      connectionId: record.backend_connection_id || prev.connectionId || record.id || null,
    }))
    setLastLatencyMs(record.lastLatencyMs ?? null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }



const {
  register,
  handleSubmit,
  formState: { errors, isSubmitted, submitCount },
  watch,
  reset,
  setValue,
  control,
  getValues,
  setError,
  clearErrors,
  setFocus,
} = useForm({
    mode: 'onChange',
    resolver: yupResolver(schema),
    defaultValues: { ...DEFAULT_FORM_VALUES },
  })

  useEffect(() => {
    currentSignatureRef.current = computeCurrentSignature(getValues())
  }, [getValues])

  useEffect(() => {
    const subscription = watch((values) => {
      const nextSignature = computeCurrentSignature(values)
      currentSignatureRef.current = nextSignature
      if (testedSignatureRef.current && testedSignatureRef.current !== nextSignature) {
        testedSignatureRef.current = null
        setCanSave(false)
      }
    })
    return () => subscription.unsubscribe()
  }, [watch])



  const dbType = watch('db_type')
  const dbTypeKey = sanitizeDbType(dbType)
  const isSQLite = dbTypeKey === 'sqlite'
const nameValue = watch('name')
const portValue = watch('port')
  const dbNameValue = watch('db_name')
  const activeDbConfig = dbTypeKey ? DB_CONFIG[dbTypeKey] : null
  const sqliteResolvedUrl = useMemo(() => {
    if (!isSQLite) return null
    const raw = trimString(dbNameValue)
    if (!raw) return null
    if (raw.startsWith('sqlite:')) return raw
    const normalized = raw.replace(/\\/g, '/')
    if (/^[a-zA-Z]:\//.test(normalized)) return `sqlite:///${normalized}`
    if (normalized.startsWith('/')) return `sqlite://${normalized}`
    return `sqlite:///${normalized}`
  }, [isSQLite, dbNameValue])
  const sqliteResolvedPath = useMemo(() => {
    if (!sqliteResolvedUrl) return null
    return sqliteResolvedUrl.replace(/^sqlite:?\/+/, '')
  }, [sqliteResolvedUrl])

  const checkDuplicateName = useCallback((candidate) => {
    const trimmed = trimString(candidate)
    if (!trimmed) return false
    const normalized = trimmed.toLowerCase()
    return savedConnections.some((conn) => {
      if (!conn?.name) return false
      if (editingId && conn.id === editingId) return false
      const existing = trimString(conn.name)
      return !!existing && existing.toLowerCase() === normalized
    })
  }, [savedConnections, editingId])

  const copySqlitePath = useCallback(async () => {
    if (!sqliteResolvedPath) return
    try {
      if (typeof navigator !== 'undefined' && navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(sqliteResolvedPath)
      } else {
        throw new Error('Clipboard API unavailable')
      }
      toast.show('Path copied to clipboard', 'success')
    } catch {
      try {
        const textarea = document.createElement('textarea')
        textarea.value = sqliteResolvedPath
        textarea.setAttribute('readonly', '')
        textarea.style.position = 'absolute'
        textarea.style.left = '-9999px'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        toast.show('Path copied to clipboard', 'success')
      } catch {
        toast.show('Unable to copy path', 'error')
      }
    }
  }, [sqliteResolvedPath, toast])



  useEffect(() => {
    if (!dbTypeKey || dbTypeKey === 'sqlite') return
    const config = DB_CONFIG[dbTypeKey]
    if (!config?.defaultPort) return
    if (!portValue) {
      setValue('port', String(config.defaultPort))
    }
  }, [dbTypeKey, portValue, setValue])



  const hostHelperText = errors.host?.message || (isSQLite ? 'Host not required for SQLite file connections' : 'Enter the database host or IP address.')
  const portHelperText = errors.port?.message
    || (isSQLite
      ? 'Port not required for SQLite'
      : (activeDbConfig?.defaultPort ? `Defaults to ${activeDbConfig.defaultPort}` : 'Enter the TCP port for the database service.'))
  const usernameHelperText = errors.username?.message || (isSQLite ? 'Username not required for SQLite' : 'Provide the database user with read access.')
  const passwordHelperText = errors.password?.message || (isSQLite ? 'Password not required for SQLite' : 'Provide the password for the database user.')
  const portPlaceholder = !isSQLite && activeDbConfig?.defaultPort ? String(activeDbConfig.defaultPort) : ''
  const sharedFieldSx = {
    '& .MuiOutlinedInput-root': {
      borderRadius: CONTROL_RADIUS,
      minHeight: CONTROL_HEIGHT,
      alignItems: 'center',
      width: '100%',
      boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
    },
    '& .MuiOutlinedInput-notchedOutline': {
      borderRadius: CONTROL_RADIUS,
      borderColor: 'divider',
    },
    '&:hover .MuiOutlinedInput-notchedOutline': {
      borderColor: 'divider',
    },
    '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
      borderColor: 'text.secondary',
      borderWidth: 2,
    },
    '& .MuiOutlinedInput-input': { py: 1.25 },
    '& .MuiInputLabel-root': (theme) => ({
      ...theme.typography.overline,
      color: theme.palette.text.secondary,
      letterSpacing: '0.14em',
    }),
  }
  const fieldSx = { width: '100%', flexGrow: 1, ...sharedFieldSx }

  useEffect(() => {
    if (duplicateNameTimerRef.current) {
      clearTimeout(duplicateNameTimerRef.current)
    }
    duplicateNameTimerRef.current = setTimeout(() => {
      const isDuplicate = checkDuplicateName(nameValue)
      if (isDuplicate) {
        if (errors.name?.type !== 'duplicate') {
          setError('name', { type: 'duplicate', message: 'Connection name already exists' })
        }
      } else if (errors.name?.type === 'duplicate') {
        clearErrors('name')
      }
      duplicateNameTimerRef.current = null
    }, 200)
    return () => {
      if (duplicateNameTimerRef.current) {
        clearTimeout(duplicateNameTimerRef.current)
        duplicateNameTimerRef.current = null
      }
    }
  }, [nameValue, checkDuplicateName, errors.name?.type, setError, clearErrors])

  useFormErrorFocus(
    { errors, isSubmitted, submitCount },
    setFocus,
    FORM_FIELD_ORDER,
  )

  const showErrorSummary = (isSubmitted || submitCount > 0) && Object.keys(errors || {}).length > 0

  const handleFocusErrorField = useCallback((fieldName) => {
    if (!fieldName) return
    try {
      setFocus(fieldName, { shouldSelect: true })
    } catch {
      /* field may be controlled via Controller without direct focus target */
    }
  }, [setFocus])



  /** ---- API health probe (uses real backend when not mock) ---- */
  useEffect(() => {
    let cancelled = false
    const probe = async () => {
      try {
        if (isMock) {
          await mock.health()
        } else {
          const ok = await checkHealth({ timeoutMs: 5000 })
          if (!ok) throw new Error()
        }
        if (!cancelled) setApiStatus('healthy')
      } catch {
        if (!cancelled) setApiStatus('unreachable')
      }
    }
    probe()
    const id = setInterval(probe, 15000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])



  /** ---- Test Connection ---- */
  const mutation = useMutation({
    mutationFn: async (formValues) => {
      const normalized = normalizeConnection(formValues)
      const payload = payloadFromNormalized(normalized)



      if (isMock) {
        const response = await mock.testConnection(payload)
        return { normalized, response }
      }



      const data = await apiTestConnection(payload)
      return {
        normalized,
        response: {
          ok: data.ok ?? true,
          details: data.details || 'Connected',
          latencyMs: typeof data.latency_ms === 'number' ? data.latency_ms : undefined,
          connection_id: data.connection_id,                // server id
          normalized: data.normalized || undefined,
        }
      }
    },
    onSuccess: ({ normalized, response }, formValues) => {
      const now = new Date().toISOString()
      const lm = response.latencyMs ?? null
      const typedName = (watch('name') || '').trim()



      setLastLatencyMs(lm)
      setConnection({
        status: 'connected',
        lastMessage: response.details,
        details: response.details,
        latencyMs: lm,
        db_url: normalized.db_url,
        name: typedName || normalized.displayName,
        lastCheckedAt: now,
        connectionId: response.connection_id,   // keep in connection state
        normalized: response.normalized,
        saved: false,
      })



      setActiveConnectionId(response.connection_id) // NEW: use backend connection_id
      setShowDetails(true)

      const signature = computeCurrentSignature(formValues || getValues())
      currentSignatureRef.current = signature
      testedSignatureRef.current = signature
      setCanSave(true)
      setSetupStep('generate')      // or 'upload' depending on your flow
      toast.show('Connection successful', 'success')
    },
    onError: (error) => {
      const detail = error?.message || 'Connection failed'
      const failedAt = new Date().toISOString()
      setCanSave(false)
      testedSignatureRef.current = null
      setConnection({ status: 'failed', lastMessage: detail, details: detail, lastCheckedAt: failedAt })
      setShowDetails(true)
      toast.show(detail, 'error')
    },
  })



const onSubmit = async (values) => {
    // SQLite uses the Database field as path. Host/Port/User/Pass ignored.
    if (checkDuplicateName(values.name)) {
      setError('name', { type: 'duplicate', message: 'Connection name already exists' })
      setCanSave(false)
      return
    }
    setCanSave(false)
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Test connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        dbType: sanitizeDbType(values.db_type),
        action: 'test_connection',
      },
      action: async () => mutation.mutateAsync(values),
    })
  }



  /** ---- Row healthcheck for saved rows ---- */
  const runRowTest = async (row) => {
    if (!row) return
    const now = new Date().toISOString()
    const connectionId = row.backend_connection_id || row.id
    const storeId = row.id || connectionId
    if (!storeId) {
      toast.show('Connection reference is missing. Please re-test and save this connection.', 'error')
      return
    }



    try {
      let latency = null
      let details = 'Healthcheck succeeded'
      const typeKey = sanitizeDbType(row.db_type)
      if (isMock) {
        const normalized = {
          db_type: typeKey,
          db_url:
            row.db_url ||
            (typeKey === 'sqlite'
              ? deriveSqliteUrl(row.databasePath || row.database || '')
              : undefined),
          host: row.host ?? null,
          port: row.port ?? null,
          database: row.database || row.databasePath || '',
          username: row.username || '',
          password: '',
          ssl: row.ssl ?? false,
          driver: row.driver ?? null,
        }
        const payload = payloadFromNormalized(normalized)
        const result = await mock.testConnection(payload)
        latency = result.latencyMs ?? result.latency_ms ?? null
        details = result.details || 'Connected'
        updateSavedConnection(storeId, {
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          details,
          db_url: normalized.db_url,
          host: normalized.host ?? (typeKey === 'sqlite' ? normalized.database : null),
          port: normalized.port ?? null,
          database: normalized.database,
          databasePath: typeKey === 'sqlite' ? normalized.database : null,
          driver: normalized.driver,
          ssl: normalized.ssl,
          backend_connection_id: connectionId || storeId,
        })
      } else {
        if (!connectionId) throw new Error('Connection is missing a server identifier. Please re-test and save it.')
        const res = await apiHealthcheckConnection(connectionId)
        latency = typeof res.latency_ms === 'number' ? res.latency_ms : null
        updateSavedConnection(storeId, {
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          details,
          backend_connection_id: connectionId,
          db_url:
            row.db_url ||
            (typeKey === 'sqlite'
              ? deriveSqliteUrl(row.databasePath || row.database || row.summary || '')
              : row.db_url || null),
          host:
            typeKey === 'sqlite'
              ? row.databasePath || row.database || null
              : row.host ?? null,
          port: row.port ?? null,
          database: row.database ?? (typeKey === 'sqlite' ? row.databasePath : null),
          databasePath: typeKey === 'sqlite' ? (row.databasePath || row.database || null) : null,
          driver: row.driver ?? null,
          ssl: row.ssl ?? undefined,
        })
      }



      setRowHeartbeat((prev) => ({
        ...prev,
        [storeId]: { status: 'healthy', latencyMs: latency, ts: Date.now() },
      }))



      if (
        activeConnectionId &&
        (activeConnectionId === connectionId || activeConnectionId === storeId)
      ) {
        const fallbackUrl =
          row.db_url ||
          (typeKey === 'sqlite'
            ? deriveSqliteUrl(row.databasePath || row.database || row.summary || '')
            : null)
        setConnection({
          status: 'connected',
          saved: true,
          name: row.name,
          db_url: fallbackUrl || null,
          latencyMs: latency,
          lastMessage: details,
          details,
          lastCheckedAt: now,
          connectionId: connectionId || storeId,
          db_type: row.db_type,
          host: row.host ?? (typeKey === 'sqlite' ? row.databasePath || row.database || null : null),
          port: row.port ?? null,
          database: row.database ?? (typeKey === 'sqlite' ? row.databasePath : null),
          driver: row.driver ?? null,
          ssl: row.ssl ?? false,
        })
        if (!isMock && connectionId) setActiveConnectionId(connectionId)
      }
      toast.show('Healthcheck succeeded', 'success')
    } catch (error) {
      const detail = error?.message || 'Healthcheck failed'
      updateSavedConnection(storeId, { status: 'failed', details: detail })
      setRowHeartbeat((prev) => ({
        ...prev,
        [storeId]: { status: 'unreachable', latencyMs: null, ts: Date.now() },
      }))
      if (
        activeConnectionId &&
        (activeConnectionId === connectionId || activeConnectionId === storeId)
      ) {
        setConnection({ status: 'failed', lastMessage: detail, details: detail, lastCheckedAt: now })
      }
      toast.show(detail, 'error')
      throw error
    } finally {
      const snapshot = useAppStore.getState()
      savePersistedCache({
        connections: snapshot.savedConnections,
        templates: snapshot.templates,
        lastUsed: snapshot.lastUsed,
      })
      setTimeout(() => setRowHeartbeat((prev) => {
        const next = { ...prev }
        Object.keys(next).forEach((k) => {
          if (Date.now() - next[k].ts > 2500) delete next[k]
        })
        return next
      }), 3000)
    }
  }

  const handleRowTest = async (row) => {
    if (!row) return
    await execute({
      type: InteractionType.EXECUTE,
      label: 'Healthcheck connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: row.backend_connection_id || row.id || null,
        dbType: sanitizeDbType(row.db_type),
        action: 'connection_healthcheck',
      },
      action: async () => runRowTest(row),
    })
  }



  /** ---- Save & Continue (persist to backend + store) ---- */
const runSave = async () => {
    const values = watch()
    const friendlyName = trimString(values.name)
    if (checkDuplicateName(friendlyName)) {
      setError('name', { type: 'duplicate', message: 'Connection name already exists' })
      return
    }
    let normalized
    try {
      normalized = normalizeConnection(values)
    } catch (e) {
      toast.show(e.message, 'error'); return
    }
    const finalName = friendlyName || normalized.displayName
    const currentSignature = computeCurrentSignature(values)
    const signatureMatches = testedSignatureRef.current && testedSignatureRef.current === currentSignature
    if (!canSave || !signatureMatches || connection.status !== 'connected' || connection.db_url !== normalized.db_url) {
      toast.show('Test the connection with the current settings before saving', 'warning')
      return
    }
    const now = new Date().toISOString()
    const latency = connection.latencyMs ?? lastLatencyMs ?? null
    const baseDetails = connection.details || connection.lastMessage || 'Connected'
    const existingRecord = editingId ? savedConnections.find((c) => c.id === editingId) : null
    const preferredId =
      connection.connectionId ||
      existingRecord?.backend_connection_id ||
      existingRecord?.id ||
      editingId ||
      null
    const normalizedHostForSave =
      normalized.db_type === 'sqlite' ? normalized.database : normalized.host
    const normalizedDatabasePath = normalized.db_type === 'sqlite' ? normalized.database : null



    try {
      let persisted
      if (isMock) {
        const fallbackId = preferredId || `conn_${Date.now()}`
        persisted = formatSavedConnection({
          id: fallbackId,
          name: finalName,
          db_type: normalized.db_type,
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          db_url: normalized.db_url,
          host: normalizedHostForSave,
          port: normalized.port,
          database: normalized.database,
          databasePath: normalizedDatabasePath,
          driver: normalized.driver,
          ssl: normalized.ssl,
          details: baseDetails,
          hasCredentials: true,
        })
      } else {
        const response = await apiUpsertConnection({
          id: preferredId,
          name: finalName,
          dbType: normalized.db_type,
          dbUrl: normalized.db_url,
          database: normalized.database,
          host: normalized.host,
          port: normalized.port,
          username: normalized.username,
          password: normalized.password,
          ssl: normalized.ssl,
          driver: normalized.driver,
          status: 'connected',
          latencyMs: latency,
        })
        persisted = formatSavedConnection(response, {
          name: finalName,
          status: 'connected',
          lastConnected: now,
          lastLatencyMs: latency,
          db_url: normalized.db_url,
          host: normalizedHostForSave,
          port: normalized.port,
          database: normalized.database,
          databasePath: normalizedDatabasePath,
          driver: normalized.driver,
          ssl: normalized.ssl,
          details: baseDetails,
          hasCredentials: true,
        })
      }



      if (!persisted) throw new Error('Unable to persist connection. Please try again.')



      if (editingId && editingId !== persisted.id) {
        removeSavedConnection(editingId)
      }



      addSavedConnection(persisted)
      const stateAfterSave = useAppStore.getState()
      savePersistedCache({
        connections: stateAfterSave.savedConnections,
        templates: stateAfterSave.templates,
        lastUsed: stateAfterSave.lastUsed,
      })
      setDetailId(persisted.id)
      setActiveConnectionId(persisted.backend_connection_id || persisted.id)



      setEditingId(null)
      setConnection({
        saved: true,
        status: 'connected',
        name: persisted.name,
        db_url: persisted.db_url,
        latencyMs: persisted.lastLatencyMs,
        lastMessage: persisted.details,
        details: persisted.details,
        connectionId: persisted.backend_connection_id || persisted.id,
        db_type: persisted.db_type,
        host: persisted.host ?? null,
        port: persisted.port ?? null,
        database: persisted.database ?? persisted.databasePath ?? null,
        driver: persisted.driver ?? null,
        ssl: persisted.ssl ?? false,
        lastCheckedAt: now,
      })
      testedSignatureRef.current = null
      reset({ ...DEFAULT_FORM_VALUES })
      setCanSave(false)
      setSetupStep('generate')
      toast.show('Connection saved', 'success')
    } catch (err) {
      toast.show(err?.message || 'Failed to save connection', 'error')
      throw err
    }
  }

  const handleSave = async () => {
    await execute({
      type: InteractionType.UPDATE,
      label: 'Save connection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      suppressSuccessToast: true,
      suppressErrorToast: true,
      intent: {
        connectionId: connection.connectionId || editingId || null,
        dbType: sanitizeDbType(watch('db_type')),
        action: 'save_connection',
      },
      action: async () => runSave(),
    })
  }



const lastHeartbeatLabel = useMemo(() => {
    if (!connection.lastCheckedAt) return 'Not tested yet'
    const ts = new Date(connection.lastCheckedAt)
    if (Number.isNaN(ts.getTime())) return 'Not tested yet'
    const delta = Date.now() - ts.getTime()
    if (delta < 0) return 'Just now'
    const seconds = Math.floor(delta / 1000)
    if (seconds < 60) return `${seconds || 1}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }, [connection.lastCheckedAt])

  const hbStatus = useMemo(() => {
    if (mutation.isPending) return 'testing'
    if (connection.status === 'connected') return 'healthy'
    if (connection.status === 'failed') return 'unreachable'
    return apiStatus
  }, [mutation.isPending, connection.status, apiStatus])

  const heartbeatChipColor = useMemo(() => {
    switch (hbStatus) {
      case 'healthy':
        return 'success'
      case 'testing':
        return 'warning'
      case 'unreachable':
        return 'error'
      default:
        return 'default'
    }
  }, [hbStatus])

  const showHeartbeatChip = useMemo(
    () => Boolean(connection.lastCheckedAt) || mutation.isPending,
    [connection.lastCheckedAt, mutation.isPending],
  )



  return (
    <Stack spacing={3}>
      <Surface
        component="section"
        aria-labelledby="connect-db-heading"
        sx={{ p: { xs: 2.5, md: 3 }, display: 'flex', flexDirection: 'column', gap: 2.5 }}
      >
        <SectionHeader
          id="connect-db-heading"
          eyebrow="Step 1"
          title="Connect Data Source"
          subtitle="Connected sources power report designs and report runs."
          helpContent={TOOLTIP_COPY.connectDatabase}
          helpPlacement="left"
          action={
            <Stack
              direction="row"
              alignItems="center"
              spacing={1}
              sx={{ flexWrap: 'wrap', justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}
            >
              <HeartbeatBadge
                status={hbStatus}
                latencyMs={connection.latencyMs ?? lastLatencyMs ?? undefined}
              />
              {showHeartbeatChip ? (
                <Chip
                  label="Last heartbeat"
                  size="small"
                  color={heartbeatChipColor}
                  variant={heartbeatChipColor === 'default' ? 'outlined' : 'filled'}
                  sx={{ fontWeight: 600 }}
                />
              ) : null}
              <Typography variant="caption" color="text.secondary">
                {lastHeartbeatLabel}
              </Typography>
            </Stack>
          }
        />

        <Alert severity="info" sx={{ borderRadius: 1 }}>
          <Stack spacing={0.5}>
            <Typography variant="subtitle2">Safe defaults</Typography>
            <Typography variant="body2">
              Use a read-only account when possible. Testing only checks connectivity.
              The active connection is used for report runs, and you can switch it anytime.
              Passwords stay hidden after save. Removing a connection only removes it from NeuraReport; it does not change your database.
            </Typography>
          </Stack>
        </Alert>



        <FormErrorSummary
          errors={errors}
          visible={showErrorSummary}
          fieldOrder={FORM_FIELD_ORDER}
          fieldLabels={FORM_FIELD_LABELS}
          onFocusField={handleFocusErrorField}
          description="Resolve the items below before testing or saving the connection."
          sx={{ mb: 2 }}
        />

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Box sx={{ mb: 3 }}>
            <Typography
              variant="overline"
              id="dbtype-label"
              sx={(theme) => ({
                display: 'block',
                fontWeight: theme.typography.fontWeightBold,
                letterSpacing: '0.12em',
                color: alpha(theme.palette.text.secondary, 0.75),
              })}
            >
              Database Type
            </Typography>
            <Controller
              name="db_type"
              control={control}
              render={({ field }) => (
                <FormControl component="fieldset" error={!!errors.db_type} fullWidth>
                  <ToggleButtonGroup
                    exclusive
                    color="standard"
                    value={field.value ?? 'sqlite'}
                    onChange={(_, value) => {
                      if (!value) return
                      field.onChange(value)
                    }}
                    onBlur={field.onBlur}
                    ref={field.ref}
                    sx={dbTypeToggleGroupSx}
                    aria-labelledby="dbtype-label"
                  >
                    {DB_TYPE_OPTIONS.map((option) => {
                      const IconComponent = option.icon
                      return (
                        <ToggleButton
                          key={option.value}
                          value={option.value}
                          disableRipple
                          sx={buildDbTypeButtonSx(option.accent)}
                          aria-label={option.label}
                        >
                          {IconComponent ? (
                            <Box className="db-type-icon">
                              <IconComponent fontSize="small" />
                            </Box>
                          ) : null}
                          <Box className="db-type-meta">
                            <Typography variant="subtitle2" sx={{ fontWeight: 600 }} noWrap>
                              {option.label}
                            </Typography>
                          </Box>
                        </ToggleButton>
                      )
                    })}
                  </ToggleButtonGroup>
                  <FormHelperText sx={{ mt: 1, textAlign: 'center' }}>
                    {errors.db_type?.message || 'Choose the database engine you are connecting to'}
                  </FormHelperText>
                </FormControl>
              )}
            />
          </Box>

          {/* Row 1: Name, Host, Port */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
            <TextField
              label="Connection Name"
              placeholder="e.g. Reporting Warehouse"
              fullWidth
              required
              size="small"
              margin="dense"
              variant="outlined"
              inputProps={{ maxLength: 80 }}
              error={!!errors.name}
              helperText={errors.name?.message || 'Used to save this connection preset'}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('name')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
            <TextField
              label="Host"
              fullWidth
              size="small"
              margin="dense"
              variant="outlined"
              disabled={isSQLite}
              error={!!errors.host}
              helperText={hostHelperText}
              placeholder={isSQLite ? '' : 'db.example.com'}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('host')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 4, md: 4, lg: 4 }} sx={gridItemSx}>
            <TextField
              label="Port"
              fullWidth
              size="small"
              margin="dense"
              variant="outlined"
              disabled={isSQLite}
              error={!!errors.port}
              helperText={portHelperText}
              placeholder={portPlaceholder}
              inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('port')}
            />
          </Grid>
        </Grid>

        {isSQLite && sqliteResolvedPath && (
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1}
            alignItems={{ xs: 'flex-start', sm: 'center' }}
            sx={{ mb: 2, backgroundColor: 'background.default', borderRadius: 1, px: 1.5, py: 1.25, border: '1px solid', borderColor: 'divider' }}
          >
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
              Resolved path:
            </Typography>
            <Typography
              variant="caption"
              sx={{
                fontFamily: 'var(--font-mono, monospace)',
                color: 'text.primary',
                wordBreak: 'break-all',
              }}
            >
              {sqliteResolvedPath}
            </Typography>
            <Tooltip title="Copy resolved path">
              <IconButton
                size="small"
                onClick={copySqlitePath}
                aria-label="Copy resolved path"
                sx={{ color: 'text.secondary' }}
              >
                <ContentCopyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>
        )}

        <Grid container spacing={2} alignItems="flex-start" sx={{ mb: 2 }}>
          <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
            <TextField
              label="Database"
              placeholder={isSQLite ? 'Path to .db file' : 'Database name'}
              fullWidth
              size="small"
              margin="dense"
              variant="outlined"
              error={!!errors.db_name}
              helperText={errors.db_name?.message || ' '}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('db_name')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
            <TextField
              label="Username"
              fullWidth
              size="small"
              margin="dense"
              variant="outlined"
              disabled={isSQLite}
              error={!!errors.username}
              helperText={usernameHelperText}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('username')}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 4, md: 4 }} sx={gridItemSx}>
            <TextField
              label="Password"
              type={showPw ? 'text' : 'password'}
              fullWidth
              size="small"
              margin="dense"
              variant="outlined"
              disabled={isSQLite}
              error={!!errors.password}
              helperText={passwordHelperText}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPw(v => !v)} edge="end" aria-label="toggle password visibility">
                      {showPw ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              InputLabelProps={{ shrink: true }}
              sx={fieldSx}
              {...register('password')}
            />
          </Grid>
        </Grid>



        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={1.5}
          alignItems={{ xs: 'stretch', md: 'center' }}
          sx={{ flexWrap: 'wrap', rowGap: 1.5 }}
        >
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            sx={{ flexWrap: 'wrap' }}
          >
            <Button
              variant="contained"
              disableElevation
              startIcon={<PlayArrowIcon />}
              sx={{ borderRadius: 1, px: 2.5, textTransform: 'none', bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[700] : neutral[900], color: 'common.white', '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? neutral[500] : neutral[700] } }}
              type="submit"
              disabled={mutation.isPending}
            >
              Test Connection
            </Button>
            <Button
              variant="outlined"
              type="button"
              onClick={handleSave}
              disabled={mutation.isPending || !canSave}
              startIcon={<ArrowForwardIcon />}
              sx={{ color: 'text.secondary', borderColor: (theme) => alpha(theme.palette.text.secondary, 0.3), '&:hover': { borderColor: 'text.secondary' } }}
            >
              Save & Continue
            </Button>
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap' }}>
            {mutation.isPending && (
              <Typography variant="body2" color="text.secondary" role="status" aria-live="polite">
                Testing connection...
              </Typography>
            )}
            {connection.status === 'connected' && (
              <Chip
                label="Connected"
                size="small"
                onClick={() => setShowDetails((v) => !v)}
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            )}
            {connection.status === 'failed' && (
              <Chip
                label="Failed"
                size="small"
                onClick={() => setShowDetails((v) => !v)}
                sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }}
              />
            )}
          </Stack>
          {!isSQLite && (
            <Controller
              name="ssl"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  sx={{ m: 0, whiteSpace: 'nowrap' }}
                  componentsProps={{
                    typography: {
                      sx: (theme) => ({
                        whiteSpace: 'nowrap',
                        fontWeight: theme.typography.fontWeightBold,
                      }),
                    },
                  }}
                  control={
                    <Checkbox
                      size="small"
                      checked={Boolean(field.value)}
                      onChange={(event) => field.onChange(event.target.checked)}
                    />
                  }
                  label="Use SSL"
                />
              )}
            />
          )}
        </Stack>
      </Box>



        <Box>
          <Collapse in={showDetails}>
            {connection.status === 'failed' && <Alert severity="error">{connection.lastMessage}</Alert>}
          </Collapse>
        </Box>



      </Surface>



      <Surface
        component="section"
        aria-labelledby="saved-connections-heading"
        sx={{ p: { xs: 2.5, md: 3 }, display: 'flex', flexDirection: 'column', gap: 2 }}
      >
        <SectionHeader
          id="saved-connections-heading"
          eyebrow="Step 2"
          title="Saved Connections"
          subtitle="Tested connections stay synced for quick reuse."
          helpContent={TOOLTIP_COPY.savedConnections}
          helpPlacement="left"
        />
        {savedConnections.length === 0 ? (
          <EmptyState
            size="medium"
            title="No saved connections yet"
            description="Test and save a connection to reuse it across report runs."
            sx={{ borderStyle: 'solid' }}
          />
        ) : (
          <Stack direction="column" spacing={2} alignItems="stretch">
            <Box
              ref={listRef}
              sx={{
                flex: '1 1 auto',
                maxHeight: { md: 480 },
                overflow: 'hidden',
                p: { xs: 2, md: 2.5 },
                pt: { xs: 0.75, md: 1 },
              }}
            >
              <List
                disablePadding
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 1.5,
                  flex: 1,
                  pr: 0,
                  overflowY: 'auto',
                  maxHeight: { md: 432 },
                  pt: 0,
                }}
              >
                {savedConnections.map((c) => {
                  const isActive = activeConnectionId === c.backend_connection_id || activeConnectionId === c.id
                  const isSelected = detailId === c.id
                  const heartbeat = rowHeartbeat[c.id]
                  const status = heartbeat?.status || (c.status === 'connected' ? 'healthy' : (c.status === 'failed' ? 'unreachable' : 'unknown'))
                  const latency = heartbeat?.latencyMs ?? c.lastLatencyMs ?? null
                  const lastConnected = c.lastConnected ? new Date(c.lastConnected).toLocaleString() : 'Never connected'
                  const typeKey = sanitizeDbType(c.db_type)
                  const locationDisplay =
                    typeKey === 'sqlite'
                      ? c.databasePath || c.database || c.summary || '-'
                      : `${formatHostPort(c.host, c.port) || c.host || '-'}${c.database ? `/${c.database}` : ''}`
                  const typeLabel = (c.db_type || 'unknown').toUpperCase()
                  return (
                    <ListItemButton
                      key={c.id}
                      onClick={() => setDetailId(c.id)}
                      selected={isSelected}
                      sx={{
                        alignItems: 'flex-start',
                        p: 2,
                        borderRadius: 1,  // Figma spec: 8px
                        border: '1px solid',
                        borderColor: isSelected ? 'text.secondary' : 'divider',
                        boxShadow: isSelected ? `0 12px 24px ${alpha(neutral[900], 0.12)}` : 'none',
                        backgroundColor: 'background.paper',
                        transition: 'border-color 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
                        '&:hover': {
                          borderColor: 'text.secondary',
                          boxShadow: `0 10px 20px ${alpha(neutral[900], 0.18)}`,
                        },
                      }}
                    >
                      <Stack direction="row" spacing={2} sx={{ width: '100%' }} alignItems="flex-start">
                        <ListItemText
                          primary={
                            <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
                              <Typography variant="subtitle2" noWrap title={c.name}>{c.name}</Typography>
                              {isActive && <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />}
                            </Stack>
                          }
                          secondary={
                            <Stack spacing={0.5} sx={{ mt: 0.25 }}>
                              <Typography variant="body2" color="text.secondary" noWrap title={locationDisplay || '-'}>
                                {locationDisplay || '-'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {typeLabel} - {lastConnected}
                              </Typography>
                            </Stack>
                          }
                          secondaryTypographyProps={{ component: 'div' }}
                          sx={{ my: 0, flex: 1, minWidth: 0 }}
                        />
                        <Stack spacing={0.75} alignItems="flex-end">
                          <HeartbeatBadge
                            size="small"
                            status={status}
                            latencyMs={latency != null ? latency : undefined}
                            tooltip={c.details || c.status || 'unknown'}
                          />
                          <KeyboardArrowRightIcon color="disabled" sx={{ transform: isSelected ? 'translateX(2px)' : 'none', transition: 'transform 0.2s cubic-bezier(0.22, 1, 0.36, 1)' }} />
                        </Stack>
                      </Stack>
                    </ListItemButton>
                  )
                })}
              </List>
            </Box>
          </Stack>
        )}
      </Surface>
      {detailConnection && (
        <Portal>
          <Fade in={!!detailConnection} timeout={200}>
            <Box
              sx={{
                position: 'fixed',
                inset: 0,
                zIndex: (theme) => theme.zIndex.drawer + 10,
                pointerEvents: 'none',
                display: 'flex',
                alignItems: { xs: 'flex-end', md: 'center' },
                justifyContent: { xs: 'center', md: 'flex-start' },
                p: { xs: 2, sm: 3, md: 0 },
              }}
            >
              <Box
                onClick={() => setDetailId(null)}
                sx={{
                  position: 'absolute',
                  inset: 0,
                  bgcolor: alpha(neutral[900], 0.32),
                  pointerEvents: 'auto',
                  zIndex: 0,
                }}
              />
              <Surface
                ref={panelRef}
                onClick={(event) => event.stopPropagation()}
                sx={[
                  (theme) => {
                    const anchor = detailAnchor
                    const base = {
                      width: anchor ? `${anchor.width}px` : 'min(92vw, 560px)',
                      maxWidth: anchor ? `${anchor.width}px` : 'min(92vw, 560px)',
                      pointerEvents: 'auto',
                      position: 'relative',
                      zIndex: 1,
                    }
                    if (anchor) {
                      base[theme.breakpoints.up('md')] = {
                        position: 'absolute',
                        top: anchor.top,
                        left: anchor.left,
                        width: anchor.width,
                        maxWidth: anchor.width,
                        transform: 'none',
                      }
                    } else {
                      base[theme.breakpoints.up('md')] = {
                        position: 'absolute',
                        top: theme.spacing(10),
                        left: theme.spacing(10),
                        width: 560,
                        maxWidth: 560,
                      }
                    }
                    return base
                  },
                  {
                    p: 0,
                    gap: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    borderRadius: '18px !important',
                    borderTopLeftRadius: '18px !important',
                    borderTopRightRadius: '18px !important',
                    borderBottomRightRadius: '18px !important',
                    borderBottomLeftRadius: '18px !important',
                    boxShadow: `0 12px 32px ${alpha(neutral[900], 0.14)}`,
                    maxHeight: {
                      xs: 'calc(100vh - 96px)',
                      sm: 'calc(100vh - 112px)',
                      md: 'calc(100vh - 128px)',
                    },
                    overflow: 'hidden',
                  },
                ]}
              >
                <Box
                  sx={{
                    px: 2,
                    py: 1.25,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  <Button
                    size="small"
                    onClick={() => setDetailId(null)}
                    sx={{
                      display: { xs: 'inline-flex', md: 'none' },
                      textTransform: 'none',
                      px: 0,
                      minWidth: 0,
                      color: 'text.secondary',
                    }}
                    startIcon={<KeyboardArrowRightIcon sx={{ transform: 'rotate(180deg)' }} />}
                  >
                    Back
                  </Button>
                  <Typography
                    variant="subtitle1"
                    noWrap
                    title={detailConnection.name}
                    sx={{ flexGrow: 1, minWidth: 0 }}
                  >
                    {detailConnection.name}
                  </Typography>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ flexShrink: 0 }}>
                    {activeConnectionId === detailConnection.backend_connection_id ||
                    activeConnectionId === detailConnection.id ? (
                      <Chip size="small" label="Active" sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200], color: 'text.secondary' }} />
                    ) : null}
                    <HeartbeatBadge
                      withText
                      size="small"
                      status={detailStatus}
                      latencyMs={detailLatency != null ? detailLatency : undefined}
                      tooltip={detailNote}
                    />
                  </Stack>
                  <IconButton
                    aria-label="Close details"
                    onClick={() => setDetailId(null)}
                    sx={{ color: 'text.secondary' }}
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
                <Box sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
                  <Stack spacing={1.5}>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
                        DB TYPE
                      </Typography>
                      <Typography variant="body2">
                        {detailConnection.db_type || '--'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
                        HOST / PATH
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: fontFamilyMono,
                          wordBreak: 'break-all',
                        }}
                      >
                        {detailConnection.host || detailConnection.db_url || '--'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
                        LATENCY
                      </Typography>
                      <Typography variant="body2">
                        {detailLatency != null ? `${Math.round(detailLatency)}ms` : '--'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
                        LAST CONNECTED
                      </Typography>
                      <Typography variant="body2">
                        {detailConnection.lastConnected
                          ? new Date(detailConnection.lastConnected).toLocaleString()
                          : 'Never connected'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mb: 0.25 }}>
                        NOTES
                      </Typography>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                        {detailNote || '--'}
                      </Typography>
                    </Box>
                  </Stack>
                </Box>
                <Box
                  sx={{
                    px: 2,
                    py: 1.25,
                    borderTop: '1px solid',
                    borderColor: 'divider',
                    display: 'flex',
                    gap: 1,
                    flexWrap: { xs: 'wrap', sm: 'nowrap' },
                    justifyContent: 'flex-start',
                  }}
                >
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<CheckCircleOutlineIcon />}
                    onClick={() => requestSelect(detailConnection)}
                  >
                    Select Connection
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<SpeedIcon />}
                    onClick={() => handleRowTest(detailConnection)}
                  >
                    Test Connection
                  </Button>
                  <Button
                    variant="text"
                    size="small"
                    startIcon={<EditIcon />}
                    onClick={() => beginEditConnection(detailConnection)}
                  >
                    Edit Settings
                  </Button>
                  <Button
                    variant="text"
                    size="small"
                    startIcon={<DeleteOutlineIcon />}
                    onClick={() => setConfirmDelete(detailConnection.id)}
                    sx={{ color: 'text.secondary' }}
                  >
                    Delete
                  </Button>
                </Box>
              </Surface>
            </Box>
          </Fade>
        </Portal>
      )}





      <ConfirmDialog
        open={!!confirmSelect}
        title="Replace Active Connection?"
        message="Selecting this connection will replace the current active one. Continue?"
        confirmText="Yes, select"
        onClose={() => setConfirmSelect(null)}
        onConfirm={() => {
          const id = confirmSelect
          const selected = savedConnections.find((x) => x.id === id)
          if (selected) applySelection(selected)
          setConfirmSelect(null)
        }}
      />



      <ConfirmDialog
        open={!!confirmDelete}
        title="Delete Connection"
        message="This will remove the saved connection from NeuraReport. You can undo within a few seconds."
        confirmText="Delete"
        onClose={() => setConfirmDelete(null)}
        onConfirm={() => {
          const id = confirmDelete
          const record = savedConnections.find((x) => x.id === id)
          if (!record) {
            setConfirmDelete(null)
            toast.show('Connection not found', 'error')
            return
          }
          const connectionId = record.backend_connection_id || record.id
          const wasActive =
            activeConnectionId === record.backend_connection_id ||
            activeConnectionId === record.id ||
            activeConnectionId === connectionId
          const previousConnectionState = connection
          const previousActiveId = activeConnectionId
          const previousDetailId = detailId
          const previousEditingId = editingId
          const previousHeartbeat = rowHeartbeat[id]

          const persistCache = () => {
            const stateNow = useAppStore.getState()
            savePersistedCache({
              connections: stateNow.savedConnections,
              templates: stateNow.templates,
              lastUsed: stateNow.lastUsed,
            })
          }

          const restoreConnection = () => {
            addSavedConnection(record)
            setRowHeartbeat((prev) => ({
              ...prev,
              ...(previousHeartbeat ? { [id]: previousHeartbeat } : {}),
            }))
            if (wasActive) {
              const currentActiveId = useAppStore.getState().activeConnectionId
              if (!currentActiveId) {
                setActiveConnectionId(previousActiveId || record.id)
                setConnection(previousConnectionState)
              }
            }
            if (previousDetailId) setDetailId(previousDetailId)
            if (previousEditingId === id) setEditingId(id)
            persistCache()
          }

          if (deleteUndoRef.current?.timeoutId) {
            clearTimeout(deleteUndoRef.current.timeoutId)
            deleteUndoRef.current = null
          }

          const remaining = savedConnections.filter((x) => x.id !== id)
          removeSavedConnection(id)
          setRowHeartbeat((prev) => {
            if (!prev[id]) return prev
            const next = { ...prev }
            delete next[id]
            return next
          })
          if (wasActive) {
            setActiveConnectionId(null)
            setConnection({ saved: false, status: 'disconnected', name: '', db_url: null, latencyMs: null })
          }
          if (editingId === id) {
            setEditingId(null)
          }
          setDetailId(null)
          if (!remaining.length) {
            setActiveConnectionId(null)
            setConnection({ saved: false, status: 'disconnected', name: '', db_url: null, latencyMs: null })
          }
          setConfirmDelete(null)
          persistCache()

          let undone = false
          const timeoutId = setTimeout(async () => {
            if (undone) return
            await execute({
              type: InteractionType.DELETE,
              label: 'Delete connection',
              reversibility: Reversibility.SYSTEM_MANAGED,
              suppressSuccessToast: true,
              suppressErrorToast: true,
              intent: {
                connectionId,
                action: 'delete_connection',
              },
              action: async () => {
                try {
                  if (!isMock && connectionId) {
                    await apiDeleteConnection(connectionId)
                  }
                  toast.show('Connection deleted', 'success')
                } catch (err) {
                  restoreConnection()
                  toast.show(err?.message || 'Failed to delete connection', 'error')
                  throw err
                } finally {
                  deleteUndoRef.current = null
                }
              },
            })
          }, 5000)

          deleteUndoRef.current = { timeoutId, id }

          toast.showWithUndo(
            `Connection "${record.name || record.id}" removed`,
            () => {
              undone = true
              clearTimeout(timeoutId)
              deleteUndoRef.current = null
              restoreConnection()
              toast.show('Connection restored', 'success')
            },
            { severity: 'info' }
          )
        }}
      />
    </Stack>
  )
}



