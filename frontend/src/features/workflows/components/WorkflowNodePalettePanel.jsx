/**
 * Node palette sidebar for WorkflowBuilderPage
 */
import React from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Divider,
  CardContent,
} from '@mui/material'
import { NodePalette, NodeCard } from './WorkflowStyledComponents'
import { getGroupedNodeTypes } from './WorkflowNodeTypes'

export default function WorkflowNodePalettePanel({
  onAddNode,
  pendingApprovals,
  onApproveStep,
  onRejectStep,
}) {
  const groupedNodeTypes = getGroupedNodeTypes()

  return (
    <NodePalette>
      <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
        Add Node
      </Typography>
      {Object.entries(groupedNodeTypes).map(([category, nodes]) => (
        <Box key={category} sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            {category}
          </Typography>
          {nodes.map((node) => (
            <NodeCard
              key={node.type}
              variant="outlined"
              onClick={() => onAddNode(node)}
            >
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <node.icon color={node.color} fontSize="small" />
                  <Typography variant="body2">{node.label}</Typography>
                </Box>
              </CardContent>
            </NodeCard>
          ))}
        </Box>
      ))}

      {pendingApprovals.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
            Pending Approvals ({pendingApprovals.length})
          </Typography>
          {pendingApprovals.map((approval) => (
            <Paper key={approval.id} variant="outlined" sx={{ p: 1.5, mb: 1 }}>
              <Typography variant="caption" sx={{ fontWeight: 500 }}>
                {approval.workflow_name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => onApproveStep(approval.execution_id, approval.step_id)}
                >
                  Approve
                </Button>
                <Button
                  size="small"
                  variant="outlined"
                  sx={{ color: 'text.secondary' }}
                  onClick={() => onRejectStep(approval.execution_id, approval.step_id)}
                >
                  Reject
                </Button>
              </Box>
            </Paper>
          ))}
        </>
      )}
    </NodePalette>
  )
}
