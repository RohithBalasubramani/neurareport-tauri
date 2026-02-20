const WRITE_KEYWORDS = [
  'insert',
  'update',
  'delete',
  'drop',
  'alter',
  'create',
  'truncate',
  'replace',
  'merge',
  'grant',
  'revoke',
  'comment',
  'rename',
  'vacuum',
  'attach',
  'detach',
]

const WRITE_PATTERN = new RegExp(`\\b(${WRITE_KEYWORDS.join('|')})\\b`, 'i')

const stripSql = (sql) => {
  if (!sql) return ''
  let out = ''
  let inSingle = false
  let inDouble = false
  let inLineComment = false
  let inBlockComment = false

  for (let i = 0; i < sql.length; i += 1) {
    const ch = sql[i]
    const next = sql[i + 1]

    if (inLineComment) {
      if (ch === '\n') {
        inLineComment = false
        out += ' '
      }
      continue
    }

    if (inBlockComment) {
      if (ch === '*' && next === '/') {
        inBlockComment = false
        i += 1
        out += ' '
      }
      continue
    }

    if (!inSingle && !inDouble) {
      if (ch === '-' && next === '-') {
        inLineComment = true
        i += 1
        continue
      }
      if (ch === '/' && next === '*') {
        inBlockComment = true
        i += 1
        continue
      }
    }

    if (!inDouble && ch === "'") {
      inSingle = !inSingle
      out += ' '
      continue
    }

    if (!inSingle && ch === '"') {
      inDouble = !inDouble
      out += ' '
      continue
    }

    if (inSingle || inDouble) {
      out += ' '
      continue
    }

    out += ch
  }

  return out
}

export const getWriteOperation = (sql = '') => {
  const cleaned = stripSql(sql)
  const match = cleaned.match(WRITE_PATTERN)
  return match ? match[1].toLowerCase() : null
}

export const isWriteQuery = (sql = '') => Boolean(getWriteOperation(sql))
