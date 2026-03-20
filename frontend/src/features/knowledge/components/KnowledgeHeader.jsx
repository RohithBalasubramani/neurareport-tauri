/**
 * Knowledge Library page header with stats and action buttons.
 */
import React from 'react'
import { Box, Typography, Chip } from '@mui/material'
import {
  FolderOpen as FolderOpenIcon,
  AccountTree as GraphIcon,
  QuestionAnswer as FaqIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { FeatureKey } from '@/utils/crossPageTypes'
import { Header, ActionButton } from './KnowledgeStyles'

export default function KnowledgeHeader({
  stats, connections, templates, loading,
  onUploadClick, onBuildGraph, onGenerateFaq, onImport,
}) {
  return (
    <Header>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FolderOpenIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Knowledge Library
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
              <Typography variant="body2" color="text.secondary">
                {stats?.total_documents || 0} documents in {stats?.total_collections || 0} collections
              </Typography>
              {connections.length > 0 && (
                <Chip label={`${connections.length} connections`} size="small" variant="outlined" />
              )}
              {templates.length > 0 && (
                <Chip label={`${templates.length} templates`} size="small" variant="outlined" />
              )}
            </Box>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <ImportFromMenu currentFeature={FeatureKey.KNOWLEDGE} onImport={onImport} />
          <ActionButton variant="contained" startIcon={<UploadIcon />} onClick={onUploadClick}>
            Upload Document
          </ActionButton>
          <ActionButton startIcon={<GraphIcon />} onClick={onBuildGraph} disabled={loading}>
            Knowledge Graph
          </ActionButton>
          <ActionButton startIcon={<FaqIcon />} onClick={onGenerateFaq} disabled={loading}>
            Generate FAQ
          </ActionButton>
        </Box>
      </Box>
    </Header>
  )
}
