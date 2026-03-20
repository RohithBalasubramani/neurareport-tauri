/**
 * Canvas area with workflow nodes for WorkflowBuilderPage
 */
import React from 'react'
import {
  Box,
  Typography,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  Code as CodeIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { Canvas, WorkflowNode } from './WorkflowStyledComponents'
import { NODE_TYPES } from './WorkflowNodeTypes'

export default function WorkflowCanvas({
  workflowNodes,
  selectedNode,
  onSelectNode,
  onDeleteNode,
}) {
  const theme = useTheme()

  return (
    <Canvas>
      {workflowNodes.length > 0 ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'center' }}>
          {workflowNodes.map((node, index) => {
            const nodeType = NODE_TYPES.find((t) => t.type === node.type)
            const NodeIcon = nodeType?.icon || CodeIcon
            return (
              <React.Fragment key={node.id}>
                <WorkflowNode
                  onClick={() => onSelectNode(node)}
                  sx={{
                    borderColor: selectedNode?.id === node.id
                      ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700])
                      : undefined,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Box
                      sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1,  // Figma spec: 8px
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: alpha(theme.palette[nodeType?.color || 'primary'].main, 0.1),
                      }}
                    >
                      <NodeIcon color={nodeType?.color || 'primary'} />
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {node.label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {node.type}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteNode(node.id)
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </WorkflowNode>
                {index < workflowNodes.length - 1 && (
                  <Box
                    sx={{
                      width: 2,
                      height: 40,
                      bgcolor: alpha(theme.palette.divider, 0.5),
                      borderRadius: 1,
                    }}
                  />
                )}
              </React.Fragment>
            )
          })}
        </Box>
      ) : (
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="text.secondary">
            Add nodes from the palette to build your workflow
          </Typography>
        </Box>
      )}
    </Canvas>
  )
}
