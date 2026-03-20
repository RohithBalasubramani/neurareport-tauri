import {
  Box,
  Typography,
  Button,
  Alert,
  Breadcrumbs,
  Link,
} from '@mui/material'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import { Link as RouterLink } from 'react-router-dom'

import Surface from '@/components/layout/Surface.jsx'
import AiUsageNotice from '@/components/ai/AiUsageNotice.jsx'
import DraftRecoveryBanner from '../components/DraftRecoveryBanner.jsx'

import EditorHeader from '../components/EditorHeader.jsx'
import EditorContent from '../components/EditorContent.jsx'
import EditorDialogs from '../components/EditorDialogs.jsx'
import { useTemplateEditor } from '../hooks/useTemplateEditor.js'

const surfaceStackSx = {
  gap: { xs: 2, md: 2.5 },
}

export default function TemplateEditor() {
  const editor = useTemplateEditor()
  const {
    templateId, template, referrer, breadcrumbLabel,
    loading, html, setHtml, initialHtml,
    instructions, setInstructions, previewUrl,
    saving, aiBusy, undoBusy, error,
    editMode, diffOpen, setDiffOpen,
    shortcutsOpen, setShortcutsOpen,
    previewFullscreen, setPreviewFullscreen,
    modeSwitchConfirm, setModeSwitchConfirm,
    dirty, hasInstructions, diffSummary, history, lastEditInfo,
    hasDraft, draftData, lastSaved, saveDraft, discardDraft,
    handleSave, handleApplyAi, handleUndo, handleBack,
    handleEditModeChange, handleChatHtmlUpdate,
    handleChatApplySuccess, handleRestoreDraft,
    toast, setEditMode,
  } = editor

  return (
    <>
      <Box sx={{ mb: 2 }}>
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          aria-label="breadcrumb"
        >
          <Link
            component={RouterLink}
            to={referrer}
            underline="hover"
            color="text.secondary"
            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
          >
            {breadcrumbLabel}
          </Link>
            <Typography color="text.primary" fontWeight={600}>
              Edit Design
            </Typography>
        </Breadcrumbs>
      </Box>

      <Surface sx={surfaceStackSx}>
        <EditorHeader
          template={template}
          templateId={templateId}
          editMode={editMode}
          onEditModeChange={handleEditModeChange}
          onShortcutsOpen={() => setShortcutsOpen(true)}
          onBack={handleBack}
          breadcrumbLabel={breadcrumbLabel}
          lastEditInfo={lastEditInfo}
          diffSummary={diffSummary}
          lastSaved={lastSaved}
          dirty={dirty}
        />

        <AiUsageNotice
          dense
          title="AI editing"
          description="AI edits apply to this report design. Review changes before saving."
          chips={[
            { label: 'Source: Design + instructions', color: 'info', variant: 'outlined' },
            { label: 'Confidence: Review required', color: 'warning', variant: 'outlined' },
            { label: 'Undo available', color: 'success', variant: 'outlined' },
          ]}
          sx={{ mb: 1 }}
        />

        <DraftRecoveryBanner
          show={hasDraft && !loading && editMode === 'manual'}
          draftData={draftData}
          onRestore={handleRestoreDraft}
          onDiscard={discardDraft}
        />

        {error && (
          <Alert
            severity="error"
            action={
              <Button color="inherit" size="small" component={RouterLink} to={referrer}>
                Back
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        <EditorContent
          loading={loading}
          error={error}
          html={html}
          setHtml={setHtml}
          templateId={templateId}
          template={template}
          editMode={editMode}
          previewUrl={previewUrl}
          previewFullscreen={previewFullscreen}
          setPreviewFullscreen={setPreviewFullscreen}
          instructions={instructions}
          setInstructions={setInstructions}
          dirty={dirty}
          hasInstructions={hasInstructions}
          saving={saving}
          aiBusy={aiBusy}
          undoBusy={undoBusy}
          history={history}
          referrer={referrer}
          handleSave={handleSave}
          handleApplyAi={handleApplyAi}
          handleUndo={handleUndo}
          setDiffOpen={setDiffOpen}
          handleChatHtmlUpdate={handleChatHtmlUpdate}
          handleChatApplySuccess={handleChatApplySuccess}
        />
      </Surface>

      <EditorDialogs
        diffOpen={diffOpen}
        setDiffOpen={setDiffOpen}
        shortcutsOpen={shortcutsOpen}
        setShortcutsOpen={setShortcutsOpen}
        modeSwitchConfirm={modeSwitchConfirm}
        setModeSwitchConfirm={setModeSwitchConfirm}
        initialHtml={initialHtml}
        html={html}
        dirty={dirty}
        saving={saving}
        handleSave={handleSave}
        saveDraft={saveDraft}
        instructions={instructions}
        setEditMode={setEditMode}
        toast={toast}
      />
    </>
  )
}
