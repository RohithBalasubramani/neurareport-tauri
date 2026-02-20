/**
 * Track Changes Panel
 * Version history sidebar with diff view and restore functionality.
 */
import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Tooltip,
  Paper,
  Chip,
  Stack,
  Button,
  Divider,
  CircularProgress,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Close as CloseIcon,
  Restore as RestoreIcon,
  Compare as CompareIcon,
  History as HistoryIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PanelContainer = styled(Box)(({ theme }) => ({
  width: 320,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: alpha(theme.palette.background.paper, 0.95),
  backdropFilter: 'blur(10px)',
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

const PanelContent = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}))

const VersionCard = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'isSelected',
})(({ theme, isSelected }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  cursor: 'pointer',
  transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
  border: `1px solid ${isSelected ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: isSelected ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50]) : 'transparent',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.04) : neutral[50],
  },
}))

const DiffAddition = styled('span')(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[200],
  color: theme.palette.text.primary,
  padding: '0 2px',
  borderRadius: 1,  // Figma spec: 8px
}))

const DiffDeletion = styled('span')(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[100],
  color: theme.palette.text.secondary,
  textDecoration: 'line-through',
  padding: '0 2px',
  borderRadius: 1,  // Figma spec: 8px
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
  fontSize: '0.75rem',
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function TrackChangesPanel({
  versions = [],
  loading = false,
  selectedVersion = null,
  onSelectVersion,
  onRestoreVersion,
  onCompareVersions,
  onClose,
}) {
  const theme = useTheme()
  const [compareMode, setCompareMode] = useState(false)
  const [compareVersions, setCompareVersions] = useState([])

  const handleVersionClick = useCallback((version) => {
    if (compareMode) {
      // In compare mode, select up to 2 versions
      if (compareVersions.includes(version.id)) {
        setCompareVersions(compareVersions.filter((v) => v !== version.id))
      } else if (compareVersions.length < 2) {
        setCompareVersions([...compareVersions, version.id])
      }
    } else {
      onSelectVersion?.(version)
    }
  }, [compareMode, compareVersions, onSelectVersion])

  const handleCompare = useCallback(() => {
    if (compareVersions.length === 2) {
      onCompareVersions?.(compareVersions[0], compareVersions[1])
    }
  }, [compareVersions, onCompareVersions])

  const handleRestore = useCallback((version, e) => {
    e.stopPropagation()
    onRestoreVersion?.(version)
  }, [onRestoreVersion])

  const toggleCompareMode = useCallback(() => {
    setCompareMode(!compareMode)
    setCompareVersions([])
  }, [compareMode])

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <PanelContainer>
      <PanelHeader>
        <Stack direction="row" alignItems="center" spacing={1}>
          <HistoryIcon sx={{ color: 'text.secondary', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
            Version History
          </Typography>
        </Stack>
        <Stack direction="row" spacing={0.5}>
          <Tooltip title={compareMode ? 'Exit compare mode' : 'Compare versions'}>
            <IconButton
              size="small"
              onClick={toggleCompareMode}
              data-testid="version-compare-toggle"
              aria-label="Compare versions"
              sx={{
                color: compareMode ? (theme.palette.mode === 'dark' ? neutral[300] : neutral[900]) : 'text.secondary',
                bgcolor: compareMode ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]) : 'transparent',
              }}
            >
              <CompareIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <IconButton size="small" onClick={onClose} data-testid="version-panel-close" aria-label="Close version history">
            <CloseIcon fontSize="small" />
          </IconButton>
        </Stack>
      </PanelHeader>

      {compareMode && (
        <Box sx={{ p: 2, borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Select 2 versions to compare
          </Typography>
          <ActionButton
            variant="contained"
            size="small"
            disabled={compareVersions.length !== 2}
            onClick={handleCompare}
            fullWidth
            data-testid="version-compare-button"
          >
            Compare Selected ({compareVersions.length}/2)
          </ActionButton>
        </Box>
      )}

      <PanelContent>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} />
          </Box>
        ) : versions.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <HistoryIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              No version history yet
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Changes will be tracked as you edit
            </Typography>
          </Box>
        ) : (
          versions.map((version, index) => (
            <VersionCard
              key={version.id}
              elevation={0}
              isSelected={
                compareMode
                  ? compareVersions.includes(version.id)
                  : selectedVersion?.id === version.id
              }
              onClick={() => handleVersionClick(version)}
              data-testid={`version-card-${version.id}`}
            >
              <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <Chip
                    label={`v${version.version}`}
                    size="small"
                    sx={{
                      borderRadius: 1,
                      fontWeight: 600,
                      fontSize: '12px',
                      bgcolor: index === 0 ? (theme.palette.mode === 'dark' ? neutral[700] : neutral[900]) : (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.08) : neutral[100]),
                      color: index === 0 ? 'common.white' : 'text.secondary',
                    }}
                  />
                  {index === 0 && (
                    <Chip
                      label="Current"
                      size="small"
                      variant="outlined"
                      sx={{ borderRadius: 1, fontSize: '10px' }}
                    />
                  )}
                </Stack>
                {!compareMode && index !== 0 && (
                  <Tooltip title="Restore this version">
                    <IconButton
                      size="small"
                      onClick={(e) => handleRestore(version, e)}
                      data-testid={`version-restore-${version.id}`}
                      aria-label={`Restore version ${version.version}`}
                      sx={{ color: 'text.secondary' }}
                    >
                      <RestoreIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </Stack>

              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                {formatDate(version.created_at)}
              </Typography>

              {version.author_name && (
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <PersonIcon sx={{ fontSize: 14, color: 'text.disabled' }} />
                  <Typography variant="caption" color="text.disabled">
                    {version.author_name}
                  </Typography>
                </Stack>
              )}

              {version.changes_summary && (
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    color: 'text.secondary',
                    fontStyle: 'italic',
                  }}
                >
                  {version.changes_summary}
                </Typography>
              )}
            </VersionCard>
          ))
        )}
      </PanelContent>
    </PanelContainer>
  )
}
