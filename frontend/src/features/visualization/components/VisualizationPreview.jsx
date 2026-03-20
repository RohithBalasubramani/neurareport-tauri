/**
 * Preview area for the visualization page.
 */
import React, { useState, useEffect, useRef } from 'react'
import mermaid from 'mermaid'
import { sanitizeSVG } from '@/utils/sanitize'
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  UploadFile as UploadFileIcon,
  Visibility as PreviewIcon,
} from '@mui/icons-material'

// =============================================================================
// MERMAID RENDERER
// =============================================================================

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'strict' })

function MermaidDiagram({ code }) {
  const containerRef = useRef(null)
  const [svgContent, setSvgContent] = useState('')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!code) return
    let cancelled = false
    const id = `mermaid-${Date.now()}`

    mermaid.render(id, code).then(({ svg }) => {
      if (!cancelled) {
        setSvgContent(svg)
        setError(null)
      }
    }).catch((err) => {
      if (!cancelled) {
        setError(err?.message || 'Failed to render diagram')
        setSvgContent('')
      }
    })

    return () => { cancelled = true }
  }, [code])

  if (error) {
    return (
      <Box>
        <Alert severity="warning" sx={{ mb: 2 }}>Diagram render issue — showing code</Alert>
        <Typography component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap', fontSize: 13 }}>
          {code}
        </Typography>
      </Box>
    )
  }

  if (!svgContent) return <CircularProgress size={24} />

  return (
    <Box
      ref={containerRef}
      dangerouslySetInnerHTML={{ __html: svgContent }}
      sx={{ '& svg': { maxWidth: '100%', height: 'auto' } }}
    />
  )
}

// =============================================================================
// PREVIEW AREA
// =============================================================================

export default function VisualizationPreview({
  activeDiagram,
  extractedTable,
  selectedType,
  inputData,
  generating,
  handleGenerate,
  fileInputRef,
  PreviewArea,
  PreviewCard,
  ActionButton,
}) {
  return (
    <PreviewArea sx={extractedTable || activeDiagram ? { justifyContent: 'flex-start', alignItems: 'stretch' } : {}}>
      {activeDiagram ? (
        <PreviewCard elevation={2}>
          {activeDiagram.mermaid_code ? (
            <MermaidDiagram code={activeDiagram.mermaid_code} />
          ) : activeDiagram.svg ? (
            <Box
              dangerouslySetInnerHTML={{ __html: sanitizeSVG(activeDiagram.svg) }}
              sx={{ '& svg': { maxWidth: '100%', height: 'auto' } }}
            />
          ) : activeDiagram.content ? (
            <Typography
              component="pre"
              sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}
            >
              {typeof activeDiagram.content === 'string'
                ? activeDiagram.content
                : JSON.stringify(activeDiagram.content, null, 2)}
            </Typography>
          ) : (
            <Typography color="text.secondary">No diagram data returned</Typography>
          )}
        </PreviewCard>
      ) : extractedTable ? (
        <Box sx={{ width: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {extractedTable.filename}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {extractedTable.rows.length} rows, {extractedTable.headers.length} columns
                {extractedTable.sheetCount > 1 ? ` (${extractedTable.sheetCount} sheets — showing first)` : ''}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                size="small"
                variant="outlined"
                startIcon={<UploadFileIcon />}
                onClick={() => fileInputRef.current?.click()}
                sx={{ textTransform: 'none' }}
              >
                Upload Another
              </Button>
              <ActionButton
                variant="contained"
                size="small"
                startIcon={generating ? <CircularProgress size={16} color="inherit" /> : <PreviewIcon />}
                onClick={handleGenerate}
                disabled={!inputData.trim() || generating}
              >
                {generating ? 'Generating...' : `Generate ${selectedType.name}`}
              </ActionButton>
            </Box>
          </Box>
          <TableContainer component={Paper} elevation={1} sx={{ maxHeight: 'calc(100vh - 220px)' }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper', color: 'text.secondary', fontSize: 11, py: 0.75 }}>#</TableCell>
                  {extractedTable.headers.map((h) => (
                    <TableCell key={h} sx={{ fontWeight: 700, bgcolor: 'background.paper', whiteSpace: 'nowrap', py: 0.75 }}>
                      {h}
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {extractedTable.rows.map((row, ri) => (
                  <TableRow key={ri} hover>
                    <TableCell sx={{ color: 'text.secondary', fontSize: 11, py: 0.5 }}>{ri + 1}</TableCell>
                    {row.map((cell, ci) => (
                      <TableCell key={ci} sx={{ whiteSpace: 'nowrap', py: 0.5 }}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      ) : (
        <Box sx={{ textAlign: 'center', maxWidth: 400 }}>
          <UploadFileIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            Upload Excel Data
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload an Excel or CSV file to extract data, then select a diagram type and generate a visualization.
          </Typography>
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={() => fileInputRef.current?.click()}
            sx={{ textTransform: 'none' }}
          >
            Upload Excel / CSV
          </Button>
        </Box>
      )}
    </PreviewArea>
  )
}
