import { useState, useMemo } from 'react'
import { Box, Typography, alpha } from '@mui/material'
import { computeDiff } from './diffUtils'
import DiffLine from './DiffLine'
import DiffToolbar from './DiffToolbar'

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
      <DiffToolbar
        stats={stats}
        diffIndices={diffIndices}
        currentDiffIndex={currentDiffIndex}
        viewMode={viewMode}
        onNavigateDiff={navigateDiff}
        onSetViewMode={setViewMode}
      />

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
