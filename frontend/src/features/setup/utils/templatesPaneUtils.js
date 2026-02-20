export const ALL_OPTION = '__ALL__'

export const SCHEDULE_FREQUENCY_OPTIONS = [
  { value: 'hourly', label: 'Every hour' },
  { value: 'six_hours', label: 'Every 6 hours' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
]

export const surfaceStackSx = {
  gap: { xs: 2, md: 2.5 },
}

export const previewFrameSx = {
  width: '100%',
  maxWidth: { xs: 260, sm: 280, md: 300, lg: 320 },
  aspectRatio: '210 / 297',
  borderRadius: 1,
  border: '1px solid',
  borderColor: 'divider',
  bgcolor: 'background.paper',
  overflow: 'hidden',
  position: 'relative',
  display: 'flex',
  alignItems: 'flex-start',
  justifyContent: 'center',
  mx: 'auto',
  p: 1,
}

export const parseEmailTargets = (value) => {
  if (!value) return []
  return value
    .split(/[,;]+/)
    .map((entry) => (entry == null ? '' : String(entry).trim()))
    .filter((entry, idx, arr) => entry && arr.indexOf(entry) === idx)
}

export const formatScheduleDate = (value) => {
  if (!value) return 'Pending'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

export const toSqlFromDayjs = (d) => (d && d.isValid && d.isValid())
  ? d.format('YYYY-MM-DD HH:mm:00')
  : ''

export const formatDisplayDate = (d) => (d && typeof d?.isValid === 'function' && d.isValid())
  ? d.format('MMM D, YYYY h:mm A')
  : ''

export const includeConn = (body, connectionId) =>
  connectionId ? { ...body, connection_id: connectionId } : body

export const buildDownloadUrl = (url) => {
  if (!url) return ''
  try {
    const u = new URL(url)
    u.searchParams.set('download', '1')
    return u.toString()
  } catch {
    const sep = url.includes('?') ? '&' : '?'
    return `${url}${sep}download=1`
  }
}

export const addKeyValues = (body, keyValues) => {
  if (!keyValues || typeof keyValues !== 'object') return body
  const cleaned = {}
  Object.entries(keyValues).forEach(([token, rawValue]) => {
    const name = typeof token === 'string' ? token.trim() : ''
    if (!name) return
    let values = []
    let sawAll = false
    if (Array.isArray(rawValue)) {
      const seen = new Set()
      rawValue.forEach((entry) => {
        if (entry === ALL_OPTION) {
          sawAll = true
          return
        }
        const text = entry == null ? '' : String(entry).trim()
        if (!text || seen.has(text)) return
        seen.add(text)
        values.push(text)
      })
    } else if (rawValue != null) {
      const text = String(rawValue).trim()
      if (text && text !== ALL_OPTION) {
        values = [text]
      } else if (text === ALL_OPTION) {
        sawAll = true
      }
    }
    if (!values.length) {
      if (sawAll) {
        cleaned[name] = 'All'
      }
      return
    }
    cleaned[name] = values.length === 1 ? values[0] : values
  })
  if (!Object.keys(cleaned).length) return body
  return { ...body, key_values: cleaned }
}

export const formatTokenLabel = (token) => {
  if (!token) return ''
  return token
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/(^|\s)([a-z])/g, (match, prefix, char) => `${prefix}${char.toUpperCase()}`)
}

export const getTemplateKind = (template) => (template?.kind === 'excel' ? 'excel' : 'pdf')

export const formatCount = (value) => {
  const num = Number(value || 0)
  if (!Number.isFinite(num)) return '0'
  return num.toLocaleString()
}
