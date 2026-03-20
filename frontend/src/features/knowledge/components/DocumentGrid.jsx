/**
 * Document grid view - cards for each document + empty state.
 */
import React from 'react'
import {
  Box, Typography, Grid, CardContent, CardActions,
  Chip, IconButton,
} from '@mui/material'
import {
  Star as StarIcon, StarBorder as StarBorderIcon,
  MoreVert as MoreIcon, FolderOpen as FolderOpenIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material'
import { DocumentCard, ActionButton } from './KnowledgeStyles'

export default function DocumentGrid({
  documents, loading,
  onToggleFavorite, onMenuOpen, onUploadClick,
}) {
  return (
    <>
      <Grid container spacing={2}>
        {documents.map((doc) => (
          <Grid item xs={12} sm={6} md={4} key={doc.id}>
            <DocumentCard>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap>
                      {doc.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {doc.file_type?.toUpperCase()} - {new Date(doc.updated_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                  <IconButton size="small" onClick={() => onToggleFavorite(doc.id)}>
                    {doc.is_favorite ? <StarIcon sx={{ color: 'text.secondary' }} /> : <StarBorderIcon />}
                  </IconButton>
                </Box>
                {doc.tags?.length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                    {doc.tags.slice(0, 3).map((tag) => (
                      <Chip key={tag} size="small" label={tag} variant="outlined" />
                    ))}
                  </Box>
                )}
              </CardContent>
              <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                <IconButton size="small" onClick={(e) => onMenuOpen(e, doc)}>
                  <MoreIcon fontSize="small" />
                </IconButton>
              </CardActions>
            </DocumentCard>
          </Grid>
        ))}
      </Grid>

      {documents.length === 0 && !loading && (
        <Box
          sx={{
            height: '50vh', display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
          }}
        >
          <FolderOpenIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No documents found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
            Upload your first document to start building your knowledge base.
            We support PDF, Word, Text, and Markdown files.
          </Typography>
          <ActionButton variant="contained" size="large" startIcon={<UploadIcon />} onClick={onUploadClick}>
            Upload Your First Document
          </ActionButton>
        </Box>
      )}
    </>
  )
}
