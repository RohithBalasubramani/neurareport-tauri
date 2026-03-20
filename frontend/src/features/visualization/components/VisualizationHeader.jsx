/**
 * Header bar for the Visualization page.
 */
import React from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  BarChart as ChartIcon,
  Code as CodeIcon,
  Image as ImageIcon,
} from '@mui/icons-material'
import SendToMenu from '@/components/common/SendToMenu'
import { OutputType, FeatureKey } from '@/utils/crossPageTypes'

export default function VisualizationHeader({
  activeDiagram,
  selectedType,
  title,
  handleExport,
  Header,
}) {
  return (
    <Header>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <ChartIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Visualization Studio
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Generate diagrams, charts, and visualizations
            </Typography>
          </Box>
        </Box>
        {activeDiagram && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <SendToMenu
              outputType={OutputType.DIAGRAM}
              payload={{
                title: `${selectedType.name}: ${title || 'Diagram'}`,
                data: { id: activeDiagram.id, svg: activeDiagram.svg, mermaid: activeDiagram.mermaid_code },
              }}
              sourceFeature={FeatureKey.VISUALIZATION}
            />
            <Tooltip title="Copy Mermaid Code">
              <IconButton onClick={() => handleExport('mermaid')}>
                <CodeIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Download PNG">
              <IconButton onClick={() => handleExport('png')}>
                <ImageIcon />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>
    </Header>
  )
}
