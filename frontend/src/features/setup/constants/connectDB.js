import StorageIcon from '@mui/icons-material/Storage'
import DnsIcon from '@mui/icons-material/Dns'
import LanIcon from '@mui/icons-material/Lan'
import HubIcon from '@mui/icons-material/Hub'
import { neutral } from '@/app/theme'

export const sanitizeDbType = (value) => (typeof value === 'string' ? value.trim().toLowerCase() : '')
export const trimString = (value) => (typeof value === 'string' ? value.trim() : '')

export const formatHostPort = (host, port) => {
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

export const defaultDisplayName = ({ db_type, host, port, database, databasePath }) => {
  const typeKey = sanitizeDbType(db_type || 'sqlite')
  if (typeKey === 'sqlite') {
    const source = trimString(databasePath) || trimString(database) || ''
    return `sqlite@${source}`
  }
  const hostPart = formatHostPort(host, port) || 'unknown'
  const dbPart = database ? `/${database}` : ''
  return `${typeKey}@${hostPart}${dbPart}`
}

export const DB_CONFIG = {
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

export const SUPPORTED_DB_TYPES = Object.keys(DB_CONFIG)

// Neutral grey accents per Figma design (no colored accents)
export const DB_TYPE_META = {
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

export const DB_TYPE_OPTIONS = [
  { value: 'sqlite', ...DB_TYPE_META.sqlite },
  { value: 'postgres', ...DB_TYPE_META.postgres },
  { value: 'mysql', ...DB_TYPE_META.mysql },
  { value: 'mssql', ...DB_TYPE_META.mssql },
]

export const computeCurrentSignature = (values = {}) => JSON.stringify({
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

export const DEFAULT_FORM_VALUES = {
  name: '',
  db_type: 'sqlite',
  host: '',
  port: '',
  db_name: '',
  username: '',
  password: '',
  ssl: false,
}

export const CONTROL_HEIGHT = 44
export const CONTROL_RADIUS = 12

export const FORM_FIELD_ORDER = [
  'name',
  'db_type',
  'host',
  'port',
  'db_name',
  'username',
  'password',
  'ssl',
]

export const FORM_FIELD_LABELS = {
  name: 'Connection name',
  db_type: 'Database type',
  host: 'Host',
  port: 'Port',
  db_name: 'Database',
  username: 'Username',
  password: 'Password',
  ssl: 'Use SSL',
}

export const stripQuotes = (s) => (s || '').replace(/^["']|["']$/g, '')

export const pathToFileName = (value) => {
  if (typeof value !== 'string') return null
  const segments = value.split(/[/\\]+/).filter(Boolean)
  return segments.length ? segments[segments.length - 1] : value
}

export const deriveSqliteUrl = (path) => {
  if (!path) return null
  const normalized = path.replace(/\\/g, '/').replace(/^\.\//, '')
  if (normalized.startsWith('sqlite:')) return normalized
  if (/^[a-zA-Z]:\//.test(normalized)) return `sqlite:///${normalized}`
  if (normalized.startsWith('/')) return `sqlite://${normalized}`
  return `sqlite:///${normalized}`
}

/** Normalize form values into a connection payload. */
export function normalizeConnection(values) {
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
export function payloadFromNormalized(n) {
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

export const formatSavedConnection = (record = {}, overrides = {}) => {
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
