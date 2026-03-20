import { sanitizeCodeHighlight } from '@/utils/sanitize'
import { neutral, secondary } from '@/app/theme'

// HTML escaping for safe dangerouslySetInnerHTML usage
export const escapeHtml = (str) =>
  str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// Simple HTML syntax highlighting
export function highlightHtml(text) {
  if (!text) return null

  text = escapeHtml(text)

  // Replace HTML tags
  const highlighted = text
    .replace(/(&lt;|<)(\/?)([\w-]+)/g, (match, bracket, slash, tag) => {
      return `<span class="html-bracket">&lt;</span><span class="html-slash">${slash}</span><span class="html-tag">${tag}</span>`
    })
    .replace(/(\s)([\w-]+)(=)/g, (match, space, attr, eq) => {
      return `${space}<span class="html-attr">${attr}</span><span class="html-eq">=</span>`
    })
    .replace(/("[^"]*"|'[^']*')/g, '<span class="html-string">$1</span>')
    .replace(/(>)/g, '<span class="html-bracket">$1</span>')
    .replace(/(\{[^}]+\})/g, '<span class="html-token">$1</span>')

  return <span dangerouslySetInnerHTML={{ __html: sanitizeCodeHighlight(highlighted) }} />
}

// Compute diff using LCS algorithm for better accuracy
export function computeDiff(beforeText, afterText, contextLines = 3) {
  const beforeLines = (beforeText || '').split('\n')
  const afterLines = (afterText || '').split('\n')

  const result = []
  let beforeIdx = 0
  let afterIdx = 0

  // Simple line-by-line diff
  const maxLen = Math.max(beforeLines.length, afterLines.length)

  let unchangedStart = null
  const unchangedBuffer = []

  for (let i = 0; i < maxLen; i++) {
    const beforeLine = beforeLines[i] ?? null
    const afterLine = afterLines[i] ?? null

    if (beforeLine === afterLine && beforeLine !== null) {
      // Unchanged line
      if (unchangedStart === null) {
        unchangedStart = i
      }
      unchangedBuffer.push({
        type: 'unchanged',
        lineNumber: { before: i + 1, after: i + 1 },
        content: beforeLine,
      })
    } else {
      // Flush unchanged buffer with context
      if (unchangedBuffer.length > 0) {
        if (unchangedBuffer.length <= contextLines * 2 + 1) {
          // Show all if small
          result.push(...unchangedBuffer)
        } else {
          // Show context + collapsed
          result.push(...unchangedBuffer.slice(0, contextLines))
          result.push({
            type: 'collapsed',
            count: unchangedBuffer.length - contextLines * 2,
            startLine: unchangedStart + contextLines + 1,
          })
          result.push(...unchangedBuffer.slice(-contextLines))
        }
        unchangedBuffer.length = 0
        unchangedStart = null
      }

      // Handle changed lines
      if (beforeLine !== null && afterLine !== null) {
        result.push({
          type: 'modified',
          lineNumber: { before: i + 1, after: i + 1 },
          beforeContent: beforeLine,
          afterContent: afterLine,
        })
      } else if (beforeLine !== null) {
        result.push({
          type: 'removed',
          lineNumber: { before: i + 1, after: null },
          content: beforeLine,
        })
      } else if (afterLine !== null) {
        result.push({
          type: 'added',
          lineNumber: { before: null, after: i + 1 },
          content: afterLine,
        })
      }
    }
  }

  // Flush remaining unchanged
  if (unchangedBuffer.length > 0) {
    if (unchangedBuffer.length <= contextLines) {
      result.push(...unchangedBuffer)
    } else {
      result.push(...unchangedBuffer.slice(0, contextLines))
      if (unchangedBuffer.length > contextLines) {
        result.push({
          type: 'collapsed',
          count: unchangedBuffer.length - contextLines,
          startLine: unchangedStart + contextLines + 1,
        })
      }
    }
  }

  return result
}

export const LINE_NUMBER_SX = {
  width: 48,
  minWidth: 48,
  px: 1,
  py: 0.5,
  bgcolor: 'action.hover',
  color: 'text.disabled',
  fontFamily: 'monospace',
  fontSize: '0.75rem',
  textAlign: 'right',
  userSelect: 'none',
  borderRight: '1px solid',
  borderColor: 'divider',
}

export const CONTENT_SX = {
  flex: 1,
  px: 1.5,
  py: 0.5,
  fontFamily: 'monospace',
  fontSize: '12px',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-all',
  minHeight: 24,
  '& .html-tag': { color: secondary.cyan[600] },
  '& .html-attr': { color: secondary.teal[500] },
  '& .html-string': { color: secondary.rose[400] },
  '& .html-bracket': { color: neutral[500] },
  '& .html-slash': { color: neutral[500] },
  '& .html-eq': { color: neutral[300] },
  '& .html-token': { color: secondary.emerald[400], fontWeight: 600 },
}
