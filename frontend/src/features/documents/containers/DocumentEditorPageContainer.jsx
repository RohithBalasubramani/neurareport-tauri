/**
 * Document Editor Page Container
 * Slim orchestrator that delegates to hooks and sub-components.
 */
import { Typography, Alert } from '@mui/material'
import TrackChangesPanel from '../components/TrackChangesPanel'
import CommentsPanel from '../components/CommentsPanel'
import { PageContainer, EditorArea } from '../components/DocumentEditorStyles'
import DocumentEditorToolbar from '../components/DocumentEditorToolbar'
import DocumentSidebar from '../components/DocumentSidebar'
import DocumentEditorMain from '../components/DocumentEditorMain'
import {
  CreateDocumentDialog, DeleteDocumentDialog,
  TranslateDialog, ToneDialog,
} from '../components/DocumentDialogs'
import AIToolsMenu from '../components/AIToolsMenu'
import { useDocumentEditor } from '../hooks/useDocumentEditor'

export default function DocumentEditorPage() {
  const editor = useDocumentEditor()

  return (
    <PageContainer>
      <DocumentEditorToolbar
        currentDocument={editor.currentDocument}
        saving={editor.saving}
        comments={editor.comments}
        showDocList={editor.showDocList}
        setShowDocList={editor.setShowDocList}
        showVersions={editor.showVersions}
        showComments={editor.showComments}
        aiLoading={editor.aiLoading}
        onToggleVersions={editor.handleToggleVersions}
        onToggleComments={editor.handleToggleComments}
        onOpenAiMenu={editor.handleOpenAiMenu}
        onSave={editor.handleSave}
        onOpenCreateDialog={editor.handleOpenCreateDialog}
        onImport={editor.handleImport}
      />

      <EditorArea>
        {editor.showDocList && (
          <DocumentSidebar
            documents={editor.documents}
            currentDocument={editor.currentDocument}
            loading={editor.loading}
            onSelectDocument={editor.handleSelectDocument}
            onOpenCreateDialog={editor.handleOpenCreateDialog}
            onDeleteClick={(doc) => {
              editor.setDocToDelete(doc)
              editor.setDeleteConfirmOpen(true)
            }}
          />
        )}

        <DocumentEditorMain
          currentDocument={editor.currentDocument}
          editorContent={editor.editorContent}
          aiResult={editor.aiResult}
          clearAiResult={editor.clearAiResult}
          onEditorUpdate={editor.handleEditorUpdate}
          onSelectionChange={editor.handleSelectionChange}
          onOpenCreateDialog={editor.handleOpenCreateDialog}
        />

        {editor.showVersions && editor.currentDocument && (
          <TrackChangesPanel
            versions={editor.versions}
            loading={editor.loading}
            selectedVersion={editor.selectedVersion}
            onSelectVersion={editor.handleSelectVersion}
            onRestoreVersion={editor.handleRestoreVersion}
            onClose={() => editor.setShowVersions(false)}
          />
        )}

        {editor.showComments && editor.currentDocument && (
          <CommentsPanel
            comments={editor.comments}
            loading={editor.loading}
            highlightedCommentId={editor.highlightedCommentId}
            selectedText={editor.selectedText}
            onAddComment={editor.handleAddComment}
            onResolveComment={editor.handleResolveComment}
            onReplyComment={editor.handleReplyComment}
            onDeleteComment={editor.handleDeleteComment}
            onHighlightComment={editor.handleHighlightComment}
            onClose={() => editor.setShowComments(false)}
          />
        )}
      </EditorArea>

      <AIToolsMenu
        anchorEl={editor.aiMenuAnchor}
        onClose={editor.handleCloseAiMenu}
        onAIAction={editor.handleAIAction}
      />

      <CreateDocumentDialog
        open={editor.createDialogOpen}
        onClose={editor.handleCloseCreateDialog}
        newDocName={editor.newDocName}
        setNewDocName={editor.setNewDocName}
        selectedTemplateId={editor.selectedTemplateId}
        setSelectedTemplateId={editor.setSelectedTemplateId}
        onCreateDocument={editor.handleCreateDocument}
        loading={editor.loading}
      />

      <DeleteDocumentDialog
        open={editor.deleteConfirmOpen}
        onClose={() => editor.setDeleteConfirmOpen(false)}
        docToDelete={editor.docToDelete}
        onDeleteDocument={editor.handleDeleteDocument}
      />

      <TranslateDialog
        open={editor.translateDialogOpen}
        onClose={() => editor.setTranslateDialogOpen(false)}
        selectedLanguage={editor.selectedLanguage}
        setSelectedLanguage={editor.setSelectedLanguage}
        onTranslate={editor.handleTranslate}
      />

      <ToneDialog
        open={editor.toneDialogOpen}
        onClose={() => editor.setToneDialogOpen(false)}
        selectedTone={editor.selectedTone}
        setSelectedTone={editor.setSelectedTone}
        onAdjustTone={editor.handleAdjustTone}
      />

      {editor.error && (
        <Alert
          severity="error"
          onClose={() => editor.reset()}
          sx={{ position: 'fixed', bottom: 16, right: 16, maxWidth: 400, borderRadius: 1 }}
        >
          {editor.error}
        </Alert>
      )}

      {editor.autoSaveEnabled && editor.lastSaved && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            position: 'fixed',
            bottom: 16,
            left: 16,
            opacity: 0.7,
          }}
        >
          Auto-saved {editor.lastSaved.toLocaleTimeString()}
        </Typography>
      )}
    </PageContainer>
  )
}
