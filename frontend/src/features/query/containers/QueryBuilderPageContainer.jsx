/**
 * Premium Query Builder Page
 * Slim orchestrator — state lives in useQueryBuilderState hook,
 * UI sections are separate components.
 */
import {
  Box,
  Typography,
  Stack,
  Select,
  MenuItem,
  InputLabel,
  CircularProgress,
  Alert,
  useTheme,
  styled,
} from '@mui/material'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import BookmarkIcon from '@mui/icons-material/Bookmark'
import HistoryIcon from '@mui/icons-material/History'
import StorageIcon from '@mui/icons-material/Storage'

import { fadeInUp, GlassCard, StyledFormControl } from '@/styles'
import AiUsageNotice from '@/components/ai/AiUsageNotice'
import ConfirmModal from '@/components/modal/ConfirmModal'
import { useQueryBuilderState } from '../hooks/useQueryBuilderState'
import SavedQueriesPanel from '../components/SavedQueriesPanel'
import HistoryPanel from '../components/HistoryPanel'
import GeneratedSqlCard from '../components/GeneratedSqlCard'
import QueryResultsCard from '../components/QueryResultsCard'
import SaveQueryDialog from '../components/SaveQueryDialog'
import { HeaderButton, PrimaryButton, StyledTextField } from '../components/styledComponents'

const PageContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  maxWidth: 1400,
  margin: '0 auto',
  width: '100%',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}))

const HeaderContainer = styled(Stack)(({ theme }) => ({
  marginBottom: theme.spacing(3),
  animation: `${fadeInUp} 0.5s ease-out`,
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function QueryBuilderPage() {
  const theme = useTheme()
  const s = useQueryBuilderState()
  const connectionLabelId = 'query-builder-connection-label'

  return (
    <PageContainer>
      <HeaderContainer direction="row" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="h5" fontWeight={600} sx={{ color: theme.palette.text.primary }}>
            Query Builder
          </Typography>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            Ask questions in natural language and get SQL queries
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <HeaderButton variant="outlined" size="small" startIcon={<BookmarkIcon />} onClick={() => s.setShowSaved(!s.showSaved)}>
            Saved ({s.savedQueries.length})
          </HeaderButton>
          <HeaderButton variant="outlined" size="small" startIcon={<HistoryIcon />} onClick={() => s.setShowHistory(!s.showHistory)}>
            History
          </HeaderButton>
        </Stack>
      </HeaderContainer>

      <AiUsageNotice
        title="AI query draft"
        description="AI turns questions into SQL using the selected connection's schema. Review the SQL before executing."
        chips={[
          { label: `Source: ${s.selectedConnectionLabel}`, variant: 'outlined' },
          { label: 'Confidence: Varies per query', variant: 'outlined' },
          { label: 'Read-only recommended', variant: 'outlined' },
        ]}
        dense
        sx={{ mb: 2 }}
      />

      <SavedQueriesPanel
        open={s.showSaved}
        savedQueries={s.savedQueries}
        onLoadQuery={s.loadSavedQuery}
        onDeleteClick={(q) => s.setDeleteSavedConfirm({ open: true, queryId: q.id, queryName: q.name })}
      />
      <HistoryPanel
        open={s.showHistory}
        queryHistory={s.queryHistory}
        onSelectHistory={(h) => { s.setCurrentQuestion(h.question); s.setGeneratedSQL(h.sql) }}
        onDeleteClick={(h) => s.setDeleteHistoryConfirm({ open: true, entryId: h.id, question: h.question })}
      />

      <GlassCard>
        <StyledFormControl fullWidth size="small">
          <InputLabel id={connectionLabelId}>Database Connection</InputLabel>
          <Select
            value={s.selectedConnectionId || ''} label="Database Connection" labelId={connectionLabelId}
            id="query-builder-connection-select" onChange={(e) => s.setSelectedConnection(e.target.value)}
            startAdornment={<StorageIcon sx={{ mr: 1, color: theme.palette.text.secondary }} />}
          >
            {s.connections.map((conn) => (
              <MenuItem key={conn.id} value={conn.id}>{conn.name || conn.database_path}</MenuItem>
            ))}
          </Select>
        </StyledFormControl>
        {s.schema && (
          <Box mt={2}>
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              Available tables: {s.schema.tables?.map((t) => t.name).join(', ')}
            </Typography>
          </Box>
        )}
      </GlassCard>

      <GlassCard>
        <StyledTextField
          fullWidth multiline minRows={2} maxRows={4}
          placeholder="Ask a question about your data... (e.g., 'Show me all customers who made purchases last month')"
          value={s.currentQuestion} onChange={(e) => s.setCurrentQuestion(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter' && e.ctrlKey) s.handleGenerate() }}
        />
        <Stack direction="row" justifyContent="space-between" alignItems="center" mt={2}>
          <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>Press Ctrl+Enter to generate</Typography>
          <PrimaryButton
            startIcon={s.isGenerating ? <CircularProgress size={16} color="inherit" /> : <AutoFixHighIcon />}
            onClick={s.handleGenerate} disabled={!s.currentQuestion.trim() || !s.selectedConnectionId || s.isGenerating}
          >
            {s.isGenerating ? 'Generating...' : 'Generate SQL'}
          </PrimaryButton>
        </Stack>
      </GlassCard>

      {s.error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: 1 }} onClose={() => s.setError(null)}>{s.error}</Alert>
      )}

      <GeneratedSqlCard
        generatedSQL={s.generatedSQL} confidence={s.confidence} explanation={s.explanation}
        warnings={s.warnings} includeTotal={s.includeTotal} isExecuting={s.isExecuting}
        writeOperation={s.writeOperation} executeDisabledReason={s.executeDisabledReason}
        selectedConnectionId={s.selectedConnectionId} onSqlChange={s.setGeneratedSQL}
        onCopySQL={s.handleCopySQL} onOpenSaveDialog={() => s.setShowSaveDialog(true)}
        onExecute={s.handleExecute} onSetIncludeTotal={s.setIncludeTotal}
      />
      <QueryResultsCard
        results={s.results} columns={s.columns} tableColumns={s.tableColumns}
        totalCount={s.totalCount} executionTimeMs={s.executionTimeMs} currentQuestion={s.currentQuestion}
      />
      <SaveQueryDialog
        open={s.showSaveDialog} saveName={s.saveName} saveDescription={s.saveDescription}
        onClose={() => s.setShowSaveDialog(false)} onSaveNameChange={s.setSaveName}
        onSaveDescriptionChange={s.setSaveDescription} onSave={s.handleSave}
      />
      <ConfirmModal
        open={s.deleteSavedConfirm.open}
        onClose={() => s.setDeleteSavedConfirm({ open: false, queryId: null, queryName: '' })}
        onConfirm={() => { s.handleDeleteSaved(s.deleteSavedConfirm.queryId); s.setDeleteSavedConfirm({ open: false, queryId: null, queryName: '' }) }}
        title="Delete Saved Query"
        message={`Are you sure you want to delete "${s.deleteSavedConfirm.queryName}"? This action cannot be undone.`}
        confirmLabel="Delete" severity="error"
      />
      <ConfirmModal
        open={s.deleteHistoryConfirm.open}
        onClose={() => s.setDeleteHistoryConfirm({ open: false, entryId: null, question: '' })}
        onConfirm={() => { s.handleDeleteHistory(s.deleteHistoryConfirm.entryId); s.setDeleteHistoryConfirm({ open: false, entryId: null, question: '' }) }}
        title="Delete History Entry"
        message={`Are you sure you want to delete this history entry? "${s.deleteHistoryConfirm.question?.substring(0, 50)}${s.deleteHistoryConfirm.question?.length > 50 ? '...' : ''}"`}
        confirmLabel="Delete" severity="warning"
      />
    </PageContainer>
  )
}
