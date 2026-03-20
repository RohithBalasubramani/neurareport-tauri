/**
 * Knowledge Graph view - entities and relationships.
 */
import React from 'react'
import {
  Box, Typography, Grid, Paper, Chip, List, ListItem, ListItemText,
} from '@mui/material'
import { AccountTree as GraphIcon } from '@mui/icons-material'
import { ActionButton } from './KnowledgeStyles'

export default function KnowledgeGraphView({ knowledgeGraph, loading, documents, onBuildGraph }) {
  if (!knowledgeGraph) {
    return (
      <Box
        sx={{
          height: '50vh', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}
      >
        <GraphIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No knowledge graph yet
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
          Build a knowledge graph to visualize relationships between your documents, entities, and concepts.
        </Typography>
        <ActionButton
          variant="contained" size="large" startIcon={<GraphIcon />}
          onClick={onBuildGraph} disabled={loading || !documents.length}
        >
          Build Knowledge Graph
        </ActionButton>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Knowledge Graph</Typography>
          <Typography variant="body2" color="text.secondary">
            {knowledgeGraph.nodes?.length || 0} nodes, {knowledgeGraph.edges?.length || 0} relationships
          </Typography>
        </Box>
        <ActionButton startIcon={<GraphIcon />} onClick={onBuildGraph} disabled={loading}>
          Rebuild
        </ActionButton>
      </Box>

      <Typography variant="overline" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>Entities</Typography>
      <Grid container spacing={1.5} sx={{ mb: 3 }}>
        {knowledgeGraph.nodes?.map((node) => (
          <Grid item xs={12} sm={6} md={4} key={node.id}>
            <Paper
              variant="outlined"
              sx={{
                p: 2, borderRadius: 1,
                transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
                '&:hover': { borderColor: 'text.secondary', transform: 'translateY(-1px)' },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Chip
                  size="small" label={node.type}
                  color={node.type === 'document' ? 'primary' : node.type === 'entity' ? 'secondary' : 'default'}
                  variant="outlined"
                />
              </Box>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>{node.label}</Typography>
              {node.properties?.description && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  {node.properties.description}
                </Typography>
              )}
            </Paper>
          </Grid>
        ))}
      </Grid>

      {knowledgeGraph.edges?.length > 0 && (
        <>
          <Typography variant="overline" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
            Relationships
          </Typography>
          <Paper variant="outlined" sx={{ borderRadius: 1 }}>
            <List dense>
              {knowledgeGraph.edges.map((edge, idx) => {
                const sourceNode = knowledgeGraph.nodes?.find((n) => n.id === edge.source)
                const targetNode = knowledgeGraph.nodes?.find((n) => n.id === edge.target)
                return (
                  <ListItem key={idx} divider={idx < knowledgeGraph.edges.length - 1}>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {sourceNode?.label || edge.source}
                          </Typography>
                          <Chip size="small" label={edge.type} variant="outlined" />
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {targetNode?.label || edge.target}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                )
              })}
            </List>
          </Paper>
        </>
      )}
    </Box>
  )
}
