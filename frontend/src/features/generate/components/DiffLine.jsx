import {
  Box,
  Typography,
  alpha,
} from '@mui/material'
import { neutral } from '@/app/theme'
import UnfoldMoreIcon from '@mui/icons-material/UnfoldMore'
import AddIcon from '@mui/icons-material/Add'
import RemoveIcon from '@mui/icons-material/Remove'
import { highlightHtml, LINE_NUMBER_SX, CONTENT_SX } from './diffUtils'

export default function DiffLine({ item, viewMode, expanded, onToggleExpand, syntaxHighlight }) {
  const lineNumberSx = LINE_NUMBER_SX
  const contentSx = CONTENT_SX

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
    return <ModifiedLine item={item} viewMode={viewMode} syntaxHighlight={syntaxHighlight} lineNumberSx={lineNumberSx} contentSx={contentSx} />
  }

  return null
}

function ModifiedLine({ item, viewMode, syntaxHighlight, lineNumberSx, contentSx }) {
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
