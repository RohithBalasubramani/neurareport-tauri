const LAST_EDIT_TYPE_LABELS = {
  manual: 'Manual edit',
  ai: 'AI edit',
  undo: 'Undo',
}

const LAST_EDIT_TYPE_COLORS = {
  manual: 'primary',
  ai: 'secondary',
  undo: 'warning',
}

const LAST_EDIT_TYPE_VARIANTS = {
  manual: 'filled',
  ai: 'filled',
  undo: 'outlined',
}

const pad = (value) => String(value).padStart(2, '0')

export const formatLastEditTimestamp = (isoString) => {
  if (!isoString) return null
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return null
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(
    date.getHours(),
  )}:${pad(date.getMinutes())}`
}

export const buildLastEditInfo = (source) => {
  if (!source || typeof source !== 'object') return null
  const rawType =
    typeof source.lastEditType === 'string' ? source.lastEditType.trim().toLowerCase() : null
  const type = rawType === 'manual' || rawType === 'ai' || rawType === 'undo' ? rawType : null
  const typeLabel = type ? LAST_EDIT_TYPE_LABELS[type] : null
  const timestampLabel = formatLastEditTimestamp(source.lastEditAt)
  if (!typeLabel && !timestampLabel) {
    return null
  }
  const chipLabel = typeLabel && timestampLabel
    ? `${typeLabel} \u00B7 ${timestampLabel}`
    : typeLabel || (timestampLabel ? `Edited ${timestampLabel}` : null)
  return {
    type,
    typeLabel,
    timestampLabel,
    chipLabel,
    color: (type && LAST_EDIT_TYPE_COLORS[type]) || 'default',
    variant: (type && LAST_EDIT_TYPE_VARIANTS[type]) || 'outlined',
  }
}
