/**
 * Sidebar for the Document Q&A page: sessions list, documents panel, connection selector.
 */
import React from 'react'
import {
  Box,
  Typography,
  TextField,
  IconButton,
  InputAdornment,
  Fade,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  QuestionAnswer as QAIcon,
  Folder as FolderIcon,
  InsertDriveFile as FileIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import { neutral } from '@/app/theme'
import ConnectionSelector from '@/components/common/ConnectionSelector'
import {
  Sidebar,
  SidebarHeader,
  SessionList,
  SessionCard,
  DocumentChip,
  NewSessionButton,
} from './DocQAStyledComponents'
import SessionDocumentsPanel from './SessionDocumentsPanel'

export default function DocQASidebar({
  currentSession,
  filteredSessions,
  searchQuery,
  setSearchQuery,
  getSession,
  setCreateDialogOpen,
  setDeleteSessionConfirm,
  setAddDocDialogOpen,
  setRemoveDocConfirm,
  addDocument,
  selectedConnectionId,
  setSelectedConnectionId,
}) {
  const theme = useTheme()

  return (
    <Sidebar>
      <SidebarHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
          <Box
            sx={{
              width: 40, height: 40, borderRadius: 1,
              background: theme.palette.mode === 'dark' ? neutral[700] : neutral[900],
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            <QAIcon sx={{ color: 'common.white', fontSize: 24 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 600, lineHeight: 1.2 }}>Document Q&A</Typography>
            <Typography variant="caption" color="text.secondary">AI-powered analysis</Typography>
          </Box>
        </Box>
        <NewSessionButton fullWidth startIcon={<AddIcon />} onClick={() => setCreateDialogOpen(true)}>
          New Session
        </NewSessionButton>
        <TextField
          fullWidth size="small" placeholder="Search sessions..." value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)} sx={{ mt: 2 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
              </InputAdornment>
            ),
            sx: {
              borderRadius: 1,
              backgroundColor: alpha(theme.palette.background.paper, 0.5),
              '& fieldset': { borderColor: alpha(theme.palette.divider, 0.1) },
            },
          }}
        />
      </SidebarHeader>

      <SessionList>
        <Typography variant="overline" sx={{ color: 'text.secondary', px: 1, display: 'block', mb: 1 }}>
          Sessions ({filteredSessions.length})
        </Typography>
        {filteredSessions.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <FolderIcon sx={{ fontSize: 40, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary">
              {searchQuery ? 'No matching sessions' : 'No sessions yet'}
            </Typography>
          </Box>
        ) : (
          filteredSessions.map((session, index) => (
            <Fade in key={session.id} style={{ transitionDelay: `${index * 50}ms` }}>
              <SessionCard selected={currentSession?.id === session.id} onClick={() => getSession(session.id)}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <Box sx={{ flex: 1, minWidth: 0, pl: 1 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{ fontWeight: currentSession?.id === session.id ? 600 : 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                    >
                      {session.name}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                      <DocumentChip size="small" icon={<FileIcon />} label={`${session.documents?.length || 0} docs`} />
                    </Box>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={(e) => { e.stopPropagation(); setDeleteSessionConfirm({ open: true, sessionId: session.id, sessionName: session.name }) }}
                    sx={{ opacity: 0.5, '&:hover': { opacity: 1, color: 'text.primary' } }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </Box>
              </SessionCard>
            </Fade>
          ))
        )}
      </SessionList>

      <SessionDocumentsPanel
        currentSession={currentSession}
        addDocument={addDocument}
        setAddDocDialogOpen={setAddDocDialogOpen}
        setRemoveDocConfirm={setRemoveDocConfirm}
      />

      <Box sx={{ p: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <ConnectionSelector
          value={selectedConnectionId} onChange={setSelectedConnectionId}
          label="Enrich with Database (Optional)" size="small" showStatus fullWidth
        />
      </Box>
    </Sidebar>
  )
}
