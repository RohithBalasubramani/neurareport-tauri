/**
 * Documents grid panel for SynthesisPage
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Description as DocIcon,
  Preview as PreviewIcon,
} from '@mui/icons-material';

export default function DocumentsPanel({
  documents,
  onAddClick,
  onPreview,
  onRemove,
}) {
  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Documents ({documents?.length || 0})
        </Typography>
        <Button
          variant="outlined"
          startIcon={<AddIcon />}
          onClick={onAddClick}
        >
          Add Document
        </Button>
      </Box>

      {documents?.length === 0 ? (
        <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
          Add documents to begin synthesis
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {documents?.map((doc) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={doc.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <DocIcon sx={{ color: 'text.secondary' }} />
                    <Typography variant="subtitle2" noWrap>
                      {doc.name}
                    </Typography>
                  </Box>
                  <Chip size="small" label={doc.doc_type} />
                </CardContent>
                <CardActions>
                  <Tooltip title="Preview">
                    <IconButton
                      size="small"
                      onClick={() => onPreview(doc)}
                    >
                      <PreviewIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <IconButton
                    size="small"
                    onClick={() => onRemove(doc)}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Paper>
  );
}
