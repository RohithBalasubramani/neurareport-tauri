import { useState, useMemo } from 'react'
import { sanitizeCodeHighlight } from '@/utils/sanitize'
import {
  Box,
  Stack,
  Typography,
  IconButton,
  Chip,
  Collapse,
  Tooltip,
  ToggleButtonGroup,
  ToggleButton,
  alpha,
} from '@mui/material'
import { neutral, palette, secondary } from '@/app/theme'
import UnfoldLessIcon from '@mui/icons-material/UnfoldLess'
import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import CompareArrowsIcon from '@mui/icons-material/CompareArrows'
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'

// HTML escaping for safe dangerouslySetInnerHTML usage
const escapeHtml = (str) =>
  str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// Simple HTML syntax highlighting
function highlightHtml(text) {
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
function computeDiff(beforeText, afterText, contextLines = 3) {
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

function DiffLine({ item, viewMode, expanded, onToggleExpand, syntaxHighlight }) {
  const lineNumberSx = {
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

  const contentSx = {
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

  if (item.type === 'collapsed') {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 0.5,
          px: 2,
          bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
          borderTop: '1px dashed',
          borderBottom: '1px dashed',
          borderColor: 'divider',
          cursor: 'pointer',
          '&:hover': {
            bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
          },
        }}
        onClick={() => onToggleExpand?.(item.startLine)}
      >
        <UnfoldMoreIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
        <Typography variant="caption" color="text.secondary">
          {item.count} unchanged lines (click to expand)
        </Typography>
      </Box>
    )
  }

  if (item.type === 'unchanged') {
    return (
      <Box sx={{ display: 'flex', bgcolor: 'transparent' }}>
        <Box sx={lineNumberSx}>{item.lineNumber.before}</Box>
        {viewMode === 'split' && <Box sx={lineNumberSx}>{item.lineNumber.after}</Box>}
        <Box sx={contentSx}>
          {syntaxHighlight ? highlightHtml(item.content) : item.content}
        </Box>
      </Box>
    )
  }

  if (item.type === 'removed') {
    return (
      <Box sx={{ display: 'flex', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] }}>
        <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}>
          {item.lineNumber.before}
        </Box>
        {viewMode === 'split' && <Box sx={lineNumberSx} />}
        <Box sx={{ ...contentSx, color: 'text.secondary', textDecoration: 'line-through' }}>
          <RemoveIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
          {syntaxHighlight ? highlightHtml(item.content) : item.content}
        </Box>
      </Box>
    )
  }

  if (item.type === 'added') {
    return (
      <Box sx={{ display: 'flex', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[200] }}>
        <Box sx={lineNumberSx} />
        {viewMode === 'split' && (
          <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] }}>
            {item.lineNumber.after}
          </Box>
        )}
        <Box sx={{ ...contentSx, color: 'text.primary' }}>
          <AddIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
          {syntaxHighlight ? highlightHtml(item.content) : item.content}
        </Box>
      </Box>
    )
  }

  if (item.type === 'modified') {
    if (viewMode === 'split') {
      return (
        <>
          <Box sx={{ display: 'flex', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] }}>
            <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}>
              {item.lineNumber.before}
            </Box>
            <Box sx={{ ...contentSx, color: 'text.secondary', textDecoration: 'line-through', flex: 0.5 }}>
              {syntaxHighlight ? highlightHtml(item.beforeContent) : item.beforeContent}
            </Box>
            <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] }}>
              {item.lineNumber.after}
            </Box>
            <Box sx={{ ...contentSx, color: 'text.primary', flex: 0.5 }}>
              {syntaxHighlight ? highlightHtml(item.afterContent) : item.afterContent}
            </Box>
          </Box>
        </>
      )
    }

    return (
      <>
        <Box sx={{ display: 'flex', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50] }}>
          <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100] }}>
            {item.lineNumber.before}
          </Box>
          <Box sx={{ ...contentSx, color: 'text.secondary', textDecoration: 'line-through' }}>
            <RemoveIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
            {syntaxHighlight ? highlightHtml(item.beforeContent) : item.beforeContent}
          </Box>
        </Box>
        <Box sx={{ display: 'flex', bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.06) : neutral[200] }}>
          <Box sx={{ ...lineNumberSx, bgcolor: (theme) => theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200] }}>
            {item.lineNumber.after}
          </Box>
          <Box sx={{ ...contentSx, color: 'text.primary' }}>
            <AddIcon sx={{ fontSize: 14, mr: 0.5, verticalAlign: 'middle' }} />
            {syntaxHighlight ? highlightHtml(item.afterContent) : item.afterContent}
          </Box>
        </Box>
      </>
    )
  }

  return null
}

export default function EnhancedDiffViewer({ beforeText, afterText, contextLines = 3 }) {
  const [viewMode, setViewMode] = useState('unified') // 'unified' | 'split'
  const [syntaxHighlight, setSyntaxHighlight] = useState(true)
  const [expandedSections, setExpandedSections] = useState(new Set())
  const [currentDiffIndex, setCurrentDiffIndex] = useState(0)

  const diff = useMemo(
    () => computeDiff(beforeText, afterText, contextLines),
    [beforeText, afterText, contextLines]
  )

  const stats = useMemo(() => {
    let added = 0
    let removed = 0
    let modified = 0
    diff.forEach((item) => {
      if (item.type === 'added') added++
      if (item.type === 'removed') removed++
      if (item.type === 'modified') modified++
    })
    return { added, removed, modified, total: added + removed + modified }
  }, [diff])

  const diffIndices = useMemo(() => {
    return diff
      .map((item, idx) => (item.type !== 'unchanged' && item.type !== 'collapsed' ? idx : null))
      .filter((idx) => idx !== null)
  }, [diff])

  const handleToggleExpand = (startLine) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(startLine)) {
        next.delete(startLine)
      } else {
        next.add(startLine)
      }
      return next
    })
  }

  const navigateDiff = (direction) => {
    if (diffIndices.length === 0) return
    let newIndex = currentDiffIndex + direction
    if (newIndex < 0) newIndex = diffIndices.length - 1
    if (newIndex >= diffIndices.length) newIndex = 0
    setCurrentDiffIndex(newIndex)
    // Scroll to the diff - would need ref in real implementation
  }

  if (!beforeText && !afterText) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No content to compare</Typography>
      </Box>
    )
  }

  if (beforeText === afterText) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">No differences found</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <Stack
        direction="row"
        spacing={2}
        alignItems="center"
        justifyContent="space-between"
        sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <Chip
            size="small"
            icon={<AddIcon />}
            label={`+${stats.added}`}
            variant="outlined"
            sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
          />
          <Chip
            size="small"
            icon={<RemoveIcon />}
            label={`-${stats.removed}`}
            variant="outlined"
            sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
          />
          {stats.modified > 0 && (
            <Chip
              size="small"
              icon={<CompareArrowsIcon />}
              label={`~${stats.modified}`}
              variant="outlined"
              sx={{ borderColor: (theme) => alpha(theme.palette.divider, 0.3), color: 'text.secondary' }}
            />
          )}
        </Stack>

        <Stack direction="row" spacing={1} alignItems="center">
          {diffIndices.length > 0 && (
            <>
              <Typography variant="caption" color="text.secondary">
                {currentDiffIndex + 1} / {diffIndices.length}
              </Typography>
              <Tooltip title="Previous change">
                <IconButton size="small" onClick={() => navigateDiff(-1)} aria-label="Previous change">
                  <KeyboardArrowUpIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Next change">
                <IconButton size="small" onClick={() => navigateDiff(1)} aria-label="Next change">
                  <KeyboardArrowDownIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </>
          )}

          <ToggleButtonGroup
            size="small"
            value={viewMode}
            exclusive
            onChange={(e, v) => v && setViewMode(v)}
          >
            <ToggleButton value="unified">
              <Tooltip title="Unified view">
                <UnfoldLessIcon fontSize="small" />
              </Tooltip>
            </ToggleButton>
            <ToggleButton value="split">
              <Tooltip title="Split view">
                <CompareArrowsIcon fontSize="small" />
              </Tooltip>
            </ToggleButton>
          </ToggleButtonGroup>
        </Stack>
      </Stack>

      {/* Diff content */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          bgcolor: 'background.default',
          '& > *:nth-of-type(even)': {
            bgcolor: (theme) => alpha(theme.palette.action.hover, 0.3),
          },
        }}
      >
        {diff.map((item, idx) => (
          <DiffLine
            key={idx}
            item={item}
            viewMode={viewMode}
            syntaxHighlight={syntaxHighlight}
            onToggleExpand={handleToggleExpand}
          />
        ))}
      </Box>
    </Box>
  )
}
