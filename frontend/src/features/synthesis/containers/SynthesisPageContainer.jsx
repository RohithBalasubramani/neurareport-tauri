/**
 * Multi-Document Synthesis Page
 */
import React from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Merge as MergeIcon,
} from '@mui/icons-material';
import AiUsageNotice from '@/components/ai/AiUsageNotice';
import { useSynthesisPageState } from '../hooks/useSynthesisPageState';
import SessionsList from '../components/SessionsList';
import DocumentsPanel from '../components/DocumentsPanel';
import AnalysisPanel from '../components/AnalysisPanel';
import InconsistenciesPanel from '../components/InconsistenciesPanel';
import SynthesisResultPanel from '../components/SynthesisResultPanel';
import SynthesisDialogs from '../components/SynthesisDialogs';

export default function SynthesisPage() {
  const state = useSynthesisPageState();

  // Show loading during initial fetch
  if (state.initialLoading) {
    return (
      <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <MergeIcon />
          <Typography variant="h5">Multi-Document Synthesis</Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
          <CircularProgress />
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <MergeIcon /> Multi-Document Synthesis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Combine information from multiple documents with AI-powered analysis
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => state.setCreateDialogOpen(true)}
        >
          New Session
        </Button>
      </Box>

      {state.error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => state.reset()}>
          {state.error}
        </Alert>
      )}

      {state.currentSession && (
        <AiUsageNotice
          title="AI synthesis"
          description="Outputs are generated from the documents in this session. Review before sharing."
          chips={[
            { label: `Source: ${state.docCount} document${state.docCount === 1 ? '' : 's'}`, color: 'info', variant: 'outlined' },
            { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
            { label: 'Reversible: No source changes', color: 'success', variant: 'outlined' },
          ]}
          dense
          sx={{ mb: 2 }}
        />
      )}

      <Grid container spacing={3}>
        {/* Sessions List */}
        <Grid size={{ xs: 12, md: 3 }}>
          <SessionsList
            sessions={state.sessions}
            currentSession={state.currentSession}
            onSelectSession={state.getSession}
            onDeleteSession={(session) =>
              state.setDeleteSessionConfirm({ open: true, sessionId: session.id, sessionName: session.name })
            }
          />
        </Grid>

        {/* Main Content */}
        <Grid size={{ xs: 12, md: 9 }}>
          {state.currentSession ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <DocumentsPanel
                documents={state.currentSession.documents}
                onAddClick={() => state.setAddDocDialogOpen(true)}
                onPreview={state.handleOpenPreview}
                onRemove={(doc) =>
                  state.setRemoveDocConfirm({ open: true, docId: doc.id, docName: doc.name })
                }
              />

              {state.currentSession.documents?.length >= 2 && (
                <AnalysisPanel
                  loading={state.loading}
                  currentSession={state.currentSession}
                  selectedConnectionId={state.selectedConnectionId}
                  onConnectionChange={state.setSelectedConnectionId}
                  outputFormat={state.outputFormat}
                  onOutputFormatChange={state.setOutputFormat}
                  focusTopics={state.focusTopics}
                  onFocusTopicsChange={state.setFocusTopics}
                  onFindInconsistencies={state.handleFindInconsistencies}
                  onSynthesize={state.handleSynthesize}
                />
              )}

              <InconsistenciesPanel inconsistencies={state.inconsistencies} />
              <SynthesisResultPanel
                synthesisResult={state.synthesisResult}
                currentSession={state.currentSession}
              />
            </Box>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <MergeIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography color="text.secondary">
                Select a session or create a new one to begin
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      <SynthesisDialogs
        createDialogOpen={state.createDialogOpen}
        onCloseCreateDialog={() => state.setCreateDialogOpen(false)}
        newSessionName={state.newSessionName}
        onNewSessionNameChange={state.setNewSessionName}
        onCreateSession={state.handleCreateSession}
        addDocDialogOpen={state.addDocDialogOpen}
        onCloseAddDocDialog={() => state.setAddDocDialogOpen(false)}
        docName={state.docName}
        onDocNameChange={state.setDocName}
        docContent={state.docContent}
        onDocContentChange={state.setDocContent}
        docType={state.docType}
        onDocTypeChange={state.setDocType}
        onFileUpload={state.handleFileUpload}
        onAddDocument={state.handleAddDocument}
        previewOpen={state.previewOpen}
        previewDoc={state.previewDoc}
        onClosePreview={state.handleClosePreview}
        deleteSessionConfirm={state.deleteSessionConfirm}
        onCloseDeleteSession={() => state.setDeleteSessionConfirm({ open: false, sessionId: null, sessionName: '' })}
        onConfirmDeleteSession={state.handleDeleteSessionConfirm}
        removeDocConfirm={state.removeDocConfirm}
        onCloseRemoveDoc={() => state.setRemoveDocConfirm({ open: false, docId: null, docName: '' })}
        onConfirmRemoveDoc={state.handleRemoveDocConfirm}
      />
    </Box>
  );
}
