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
  Stack,
  CircularProgress,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Close as CloseIcon,
  Compare as CompareIcon,
  History as HistoryIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import {
  PanelContainer,
  PanelHeader,
  PanelContent,
  ActionButton,
} from './trackChangesStyles'
import VersionCardItem from './VersionCardItem'

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

  const toggleCompareMode = useCallback(() => {
    setCompareMode(!compareMode)
    setCompareVersions([])
  }, [compareMode])

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
            <VersionCardItem
              key={version.id}
              version={version}
              index={index}
              isSelected={
                compareMode
                  ? compareVersions.includes(version.id)
                  : selectedVersion?.id === version.id
              }
              compareMode={compareMode}
              onVersionClick={handleVersionClick}
              onRestore={onRestoreVersion}
            />
          ))
        )}
      </PanelContent>
    </PanelContainer>
  )
}
