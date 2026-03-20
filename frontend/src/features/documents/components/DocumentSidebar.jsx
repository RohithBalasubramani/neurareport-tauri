/**
 * Documents list sidebar for the Document Editor page.
 */
import {
  Box, Typography, IconButton, Tooltip, Stack, CircularProgress,
} from '@mui/material'
import {
  Delete as DeleteIcon, Description as DocIcon, NoteAdd as NewIcon,
} from '@mui/icons-material'
import {
  DocumentsList, DocumentsHeader, DocumentsContent, DocumentItem,
} from './DocumentEditorStyles'

export default function DocumentSidebar({
  documents, currentDocument, loading,
  onSelectDocument, onOpenCreateDialog, onDeleteClick,
}) {
  return (
    <DocumentsList>
      <DocumentsHeader>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Documents
        </Typography>
        <Tooltip title="New Document">
          <IconButton size="small" onClick={onOpenCreateDialog} data-testid="doc-sidebar-new-button" aria-label="New Document">
            <NewIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </DocumentsHeader>
      <DocumentsContent>
        {loading && documents.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : documents.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              No documents yet
            </Typography>
          </Box>
        ) : (
          documents.map((doc) => (
            <DocumentItem
              key={doc.id}
              elevation={0}
              isActive={currentDocument?.id === doc.id}
              onClick={() => onSelectDocument(doc.id)}
              data-testid={`doc-item-${doc.id}`}
            >
              <Stack direction="row" alignItems="center" spacing={1}>
                <DocIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 500,
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {doc.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(doc.updated_at).toLocaleDateString()}
                  </Typography>
                </Box>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDeleteClick(doc)
                  }}
                  data-testid={`doc-delete-${doc.id}`}
                  aria-label={`Delete ${doc.name}`}
                  sx={{ opacity: 0, transition: 'opacity 0.15s ease', '.MuiPaper-root:hover &': { opacity: 0.5 }, '&:hover': { opacity: '1 !important' } }}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Stack>
            </DocumentItem>
          ))
        )}
      </DocumentsContent>
    </DocumentsList>
  )
}
