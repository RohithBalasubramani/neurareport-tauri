/**
 * Toolbar for the Document Editor page.
 */
import {
  Typography, Chip, IconButton, Stack, CircularProgress, useTheme, alpha,
} from '@mui/material'
import {
  Add as AddIcon, Save as SaveIcon, History as HistoryIcon,
  Comment as CommentIcon, AutoAwesome as AIIcon, FolderOpen as OpenIcon,
  Description as DocIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import { FeatureKey } from '@/utils/crossPageTypes'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { Toolbar, ActionButton } from './DocumentEditorStyles'

export default function DocumentEditorToolbar({
  currentDocument, saving, comments, showDocList, setShowDocList,
  showVersions, showComments, aiLoading,
  onToggleVersions, onToggleComments, onOpenAiMenu,
  onSave, onOpenCreateDialog, onImport,
}) {
  const theme = useTheme()

  return (
    <Toolbar>
      <Stack direction="row" alignItems="center" spacing={2}>
        <IconButton
          size="small"
          onClick={() => setShowDocList(!showDocList)}
          data-testid="toggle-doc-list"
          aria-label="Toggle documents list"
          sx={{ color: showDocList ? 'text.primary' : 'text.secondary' }}
        >
          <OpenIcon />
        </IconButton>
        <DocIcon sx={{ color: 'text.secondary' }} />
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          {currentDocument?.name || 'Documents'}
        </Typography>
        {currentDocument && (
          <>
            <Chip
              size="small"
              label={`v${currentDocument.version || 1}`}
              sx={{ borderRadius: 1 }}
            />
            {saving && (
              <Stack direction="row" alignItems="center" spacing={1}>
                <CircularProgress size={14} />
                <Typography variant="caption" color="text.secondary">
                  Saving...
                </Typography>
              </Stack>
            )}
          </>
        )}
      </Stack>

      <Stack direction="row" spacing={1}>
        {currentDocument ? (
          <>
            <ActionButton
              variant="outlined"
              size="small"
              startIcon={<HistoryIcon />}
              onClick={onToggleVersions}
              data-testid="doc-history-button"
              sx={{
                bgcolor: showVersions ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
              }}
            >
              History
            </ActionButton>
            <ActionButton
              variant="outlined"
              size="small"
              startIcon={<CommentIcon />}
              onClick={onToggleComments}
              data-testid="doc-comments-button"
              sx={{
                bgcolor: showComments ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]) : 'transparent',
              }}
            >
              Comments {comments.length > 0 && `(${comments.length})`}
            </ActionButton>
            <ActionButton
              variant="outlined"
              size="small"
              startIcon={aiLoading ? <CircularProgress size={16} /> : <AIIcon />}
              onClick={onOpenAiMenu}
              disabled={aiLoading}
              data-testid="doc-ai-tools-button"
            >
              AI Tools
            </ActionButton>
            <ActionButton
              variant="contained"
              size="small"
              startIcon={<SaveIcon />}
              onClick={onSave}
              disabled={saving}
              data-testid="doc-save-button"
            >
              Save
            </ActionButton>
          </>
        ) : (
          <>
            <ImportFromMenu
              currentFeature={FeatureKey.DOCUMENTS}
              onImport={onImport}
              size="small"
            />
            <ActionButton
              variant="contained"
              size="small"
              startIcon={<AddIcon />}
              onClick={onOpenCreateDialog}
              data-testid="doc-new-button"
            >
              New Document
            </ActionButton>
          </>
        )}
      </Stack>
    </Toolbar>
  )
}
