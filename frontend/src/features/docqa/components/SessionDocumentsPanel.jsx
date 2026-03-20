/**
 * Documents section panel in the sidebar for the current session.
 */
import React from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Add as AddIcon,
  Description as DocIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { FeatureKey } from '@/utils/crossPageTypes'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { DocumentsSection } from './DocQAStyledComponents'

export default function SessionDocumentsPanel({
  currentSession,
  addDocument,
  setAddDocDialogOpen,
  setRemoveDocConfirm,
}) {
  const theme = useTheme()

  if (!currentSession) return null

  return (
    <DocumentsSection>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="overline" sx={{ color: 'text.secondary' }}>
          Documents
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <ImportFromMenu
            currentFeature={FeatureKey.DOCQA}
            onImport={(output) => {
              if (currentSession) {
                addDocument(currentSession.id, {
                  name: output.title || 'Imported',
                  content: typeof output.data === 'string' ? output.data : JSON.stringify(output.data),
                })
              }
            }}
            size="small"
          />
          <Tooltip title="Add document">
            <IconButton
              size="small"
              onClick={() => setAddDocDialogOpen(true)}
              aria-label="Add document"
              sx={{
                bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100],
                '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.12) : neutral[200] },
              }}
            >
              <AddIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {currentSession.documents?.map((doc) => (
          <Box
            key={doc.id}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1,
              borderRadius: 1.5,
              bgcolor: alpha(theme.palette.background.paper, 0.5),
              '&:hover': { bgcolor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50] },
            }}
          >
            <DocIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
            <Typography
              variant="caption"
              sx={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
            >
              {doc.name}
            </Typography>
            <IconButton
              size="small"
              onClick={() => setRemoveDocConfirm({ open: true, docId: doc.id, docName: doc.name })}
              sx={{ opacity: 0.5, '&:hover': { opacity: 1, color: 'text.primary' } }}
            >
              <CloseIcon sx={{ fontSize: 14 }} />
            </IconButton>
          </Box>
        ))}
        {(!currentSession.documents || currentSession.documents.length === 0) && (
          <Typography variant="caption" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
            No documents added yet
          </Typography>
        )}
      </Box>
    </DocumentsSection>
  )
}
