/**
 * Knowledge Library Sidebar - search, filters, collections, tags.
 */
import React from 'react'
import {
  Box, Typography, TextField, InputAdornment, List,
  ListItemIcon, ListItemText, Divider, IconButton, Chip,
  useTheme, alpha,
} from '@mui/material'
import {
  Search as SearchIcon, Add as AddIcon,
  Description as DocIcon, Star as StarIcon,
  AccountTree as GraphIcon, QuestionAnswer as FaqIcon,
  Folder as FolderIcon,
} from '@mui/icons-material'
import { Sidebar, CollectionItem } from './KnowledgeStyles'

export default function KnowledgeSidebar({
  searchQuery, onSearchQueryChange, onSearch,
  view, onViewChange, selectedCollection, onSelectCollection,
  collections, tags, knowledgeGraph, faq,
  onCreateCollectionOpen, onFetchDocuments,
}) {
  const theme = useTheme()

  return (
    <Sidebar>
      <Box sx={{ p: 2 }}>
        <TextField
          fullWidth size="small" placeholder="Search..."
          value={searchQuery}
          onChange={(e) => onSearchQueryChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <List dense sx={{ px: 1 }}>
        <CollectionItem
          button selected={view === 'all' && !selectedCollection}
          onClick={() => { onViewChange('all'); onSelectCollection(null); onFetchDocuments() }}
        >
          <ListItemIcon sx={{ minWidth: 36 }}><DocIcon fontSize="small" /></ListItemIcon>
          <ListItemText primary="All Documents" />
        </CollectionItem>
        <CollectionItem
          button selected={view === 'favorites'}
          onClick={() => { onViewChange('favorites'); onSelectCollection(null); onFetchDocuments({ favoritesOnly: true }) }}
        >
          <ListItemIcon sx={{ minWidth: 36 }}>
            <StarIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </ListItemIcon>
          <ListItemText primary="Favorites" />
        </CollectionItem>
        <CollectionItem button selected={view === 'graph'} onClick={() => onViewChange('graph')}>
          <ListItemIcon sx={{ minWidth: 36 }}>
            <GraphIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </ListItemIcon>
          <ListItemText
            primary="Knowledge Graph"
            secondary={knowledgeGraph ? `${knowledgeGraph.nodes?.length || 0} nodes` : null}
          />
        </CollectionItem>
        <CollectionItem button selected={view === 'faq'} onClick={() => onViewChange('faq')}>
          <ListItemIcon sx={{ minWidth: 36 }}>
            <FaqIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </ListItemIcon>
          <ListItemText primary="FAQ" secondary={faq.length ? `${faq.length} items` : null} />
        </CollectionItem>
      </List>

      <Divider sx={{ my: 1 }} />

      <Box sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="caption" sx={{ fontWeight: 600 }}>COLLECTIONS</Typography>
        <IconButton size="small" onClick={onCreateCollectionOpen}>
          <AddIcon fontSize="small" />
        </IconButton>
      </Box>
      <List dense sx={{ px: 1, flex: 1, overflow: 'auto' }}>
        {collections.map((collection) => (
          <CollectionItem
            key={collection.id} button
            selected={selectedCollection?.id === collection.id}
            onClick={() => onSelectCollection(collection)}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>
              <FolderIcon fontSize="small" sx={{ color: 'text.secondary' }} />
            </ListItemIcon>
            <ListItemText primary={collection.name} secondary={`${collection.document_count || 0} docs`} />
          </CollectionItem>
        ))}
      </List>

      <Box sx={{ p: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
        <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>TAGS</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {tags.slice(0, 10).map((tag) => (
            <Chip
              key={tag.id} size="small" label={tag.name} variant="filled"
              onClick={() => onFetchDocuments({ tags: [tag.name] })}
            />
          ))}
        </Box>
      </Box>
    </Sidebar>
  )
}
