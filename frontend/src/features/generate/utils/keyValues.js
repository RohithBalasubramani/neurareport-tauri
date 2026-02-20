export function normalizeKeyValuePayload(keyValues) {
  if (!keyValues || typeof keyValues !== 'object') return null
  const cleaned = {}
  const ALL_SENTINELS = new Set(['all', 'select all', '__NR_SELECT_ALL__'])
  Object.entries(keyValues).forEach(([token, value]) => {
    const name = typeof token === 'string' ? token.trim() : ''
    if (!name) return
    const base = Array.isArray(value) ? value : [value]
    const seen = new Set()
    const normalized = []
    let sawAll = false
    base.forEach((raw) => {
      const text = raw == null ? '' : String(raw).trim()
      if (!text || seen.has(text)) return
      if (ALL_SENTINELS.has(text.toLowerCase())) {
        sawAll = true
        return
      }
      seen.add(text)
      normalized.push(text)
    })
    if (!normalized.length) {
      if (sawAll) {
        cleaned[name] = 'All'
      }
      return
    }
    if (sawAll) {
      cleaned[name] = 'All'
      return
    }
    cleaned[name] = normalized.length === 1 ? normalized[0] : normalized
  })
  return Object.keys(cleaned).length ? cleaned : null
}
