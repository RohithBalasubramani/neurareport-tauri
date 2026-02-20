/**
 * Knowledge Library Page Container
 * Document library and knowledge management interface.
 */
import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  Divider,
  Tabs,
  Tab,
  useTheme,
  alpha,
  styled,
} from '@mui/material'
import {
  Search as SearchIcon,
  Add as AddIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as DocIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  LocalOffer as TagIcon,
  MoreVert as MoreIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  AutoAwesome as AIIcon,
  AccountTree as GraphIcon,
  QuestionAnswer as FaqIcon,
  FilterList as FilterIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material'
import useKnowledgeStore from '@/stores/knowledgeStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import ImportFromMenu from '@/components/common/ImportFromMenu'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { uploadDocument } from '@/api/knowledge'
import { neutral, palette } from '@/app/theme'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const PageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 64px)',
  backgroundColor: theme.palette.background.default,
}))

const Header = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.8),
}))

const ContentArea = styled(Box)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  overflow: 'hidden',
}))

const Sidebar = styled(Box)(({ theme }) => ({
  width: 260,
  borderRight: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  display: 'flex',
  flexDirection: 'column',
}))

const MainPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  padding: theme.spacing(3),
  overflow: 'auto',
}))

const DocumentCard = styled(Card)(({ theme }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 8px 24px ${alpha(theme.palette.text.primary, 0.05)}`,
  },
}))

const CollectionItem = styled(ListItem)(({ theme, selected }) => ({
  borderRadius: 8,
  marginBottom: 4,
  backgroundColor: selected ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.1) : neutral[100]) : 'transparent',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50],
  },
}))

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: 8,
  textTransform: 'none',
  fontWeight: 500,
}))

const UploadDropzone = styled(Box)(({ theme, isDragActive }) => ({
  border: `2px dashed ${isDragActive ? (theme.palette.mode === 'dark' ? neutral[500] : neutral[700]) : alpha(theme.palette.divider, 0.3)}`,
  borderRadius: 8,  // Figma spec: 8px
  padding: theme.spacing(6),
  textAlign: 'center',
  backgroundColor: isDragActive ? (theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.05) : neutral[50]) : alpha(theme.palette.background.paper, 0.5),
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.22, 1, 0.36, 1)',
  '&:hover': {
    borderColor: theme.palette.mode === 'dark' ? neutral[500] : neutral[700],
    backgroundColor: theme.palette.mode === 'dark' ? alpha(theme.palette.text.primary, 0.02) : neutral[50],
  },
}))

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function KnowledgePageContainer() {
  const theme = useTheme()
  const toast = useToast()
  const { execute } = useInteraction()
  const { connections, templates } = useSharedData()

  // Cross-page: accept documents from other features (Agents, Synthesis, etc.)
  useIncomingTransfer(FeatureKey.KNOWLEDGE, {
    [TransferAction.SAVE_TO]: async (payload) => {
      // Create a Blob from the content and upload it
      const content = typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content)
      const blob = new Blob([content], { type: 'text/plain' })
      const file = new File([blob], `${payload.title || 'Imported'}.txt`, { type: 'text/plain' })
      await uploadDocument(file, payload.title || 'Imported Document', selectedCollection?.id)
      fetchDocuments()
    },
  })

  const {
    documents,
    collections,
    tags,
    currentDocument,
    currentCollection,
    searchResults,
    relatedDocuments,
    knowledgeGraph,
    faq,
    stats,
    totalDocuments,
    loading,
    searching,
    error,
    fetchDocuments,
    fetchCollections,
    fetchTags,
    createCollection,
    deleteDocument,
    toggleFavorite,
    searchDocuments,
    autoTag,
    findRelated,
    buildKnowledgeGraph,
    generateFaq,
    fetchStats,
    reset,
  } = useKnowledgeStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCollection, setSelectedCollection] = useState(null)
  const [view, setView] = useState('all') // 'all', 'favorites', 'recent', 'graph', 'faq'
  const [createCollectionOpen, setCreateCollectionOpen] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchDocuments()
    fetchCollections()
    fetchTags()
    fetchStats()
    return () => reset()
  }, [fetchCollections, fetchDocuments, fetchStats, fetchTags, reset])

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      fetchDocuments()
      return
    }

    return execute({
      type: InteractionType.EXECUTE,
      label: 'Search library',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      suppressSuccessToast: true,
      intent: { source: 'knowledge', query: searchQuery },
      action: () => searchDocuments(searchQuery),
    })
  }, [execute, fetchDocuments, searchDocuments, searchQuery])

  const handleSelectCollection = useCallback((collection) => {
    setSelectedCollection(collection)
    if (collection) {
      fetchDocuments({ collectionId: collection.id })
    } else {
      fetchDocuments()
    }
  }, [fetchDocuments])

  const handleToggleFavorite = useCallback(async (docId) => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Toggle favorite',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'knowledge', documentId: docId },
      action: () => toggleFavorite(docId),
    })
  }, [execute, toggleFavorite])

  const handleDeleteDocument = useCallback(async (docId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete document',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'knowledge', documentId: docId },
      action: async () => {
        await deleteDocument(docId)
        toast.show('Document deleted', 'success')
      },
    })
  }, [deleteDocument, execute, toast])

  const handleAutoTag = useCallback(async (docId) => {
    return execute({
      type: InteractionType.UPDATE,
      label: 'Auto-tag document',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'knowledge', documentId: docId },
      action: async () => {
        await autoTag(docId)
        toast.show('Tags generated', 'success')
      },
    })
  }, [autoTag, execute, toast])

  const handleFindRelated = useCallback(async (docId) => {
    return execute({
      type: InteractionType.EXECUTE,
      label: 'Find related documents',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'knowledge', documentId: docId },
      action: () => findRelated(docId),
    })
  }, [execute, findRelated])

  const handleBuildGraph = useCallback(async () => {
    const documentIds = documents
      .map((doc) => doc?.id)
      .filter(Boolean)

    return execute({
      type: InteractionType.EXECUTE,
      label: 'Build knowledge graph',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'knowledge' },
      action: async () => {
        await buildKnowledgeGraph({ collectionId: selectedCollection?.id, documentIds })
        setView('graph')
        toast.show('Knowledge graph built', 'success')
      },
    })
  }, [buildKnowledgeGraph, documents, execute, selectedCollection?.id, toast])

  const handleGenerateFaq = useCallback(async () => {
    const documentIds = documents
      .map((doc) => doc?.id)
      .filter(Boolean)

    if (!documentIds.length) {
      toast.show('Upload at least one document before generating FAQ', 'warning')
      return null
    }

    return execute({
      type: InteractionType.EXECUTE,
      label: 'Generate FAQ',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      blocksNavigation: true,
      intent: { source: 'knowledge' },
      action: async () => {
        const response = await generateFaq({
          collectionId: selectedCollection?.id,
          documentIds,
          background: false,
        })
        if (response?.status === 'queued') {
          toast.show('FAQ generation queued', 'info')
        } else {
          setView('faq')
          toast.show('FAQ generated', 'success')
        }
      },
    })
  }, [documents, execute, generateFaq, selectedCollection?.id, toast])

  const handleCreateCollection = useCallback(async () => {
    if (!newCollectionName.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Create collection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'knowledge', name: newCollectionName },
      action: async () => {
        await createCollection({ name: newCollectionName })
        toast.show('Collection created', 'success')
        setNewCollectionName('')
        setCreateCollectionOpen(false)
      },
    })
  }, [createCollection, execute, newCollectionName, toast])

  const handleMenuOpen = (event, doc) => {
    setMenuAnchor(event.currentTarget)
    setSelectedDoc(doc)
  }

  const handleMenuClose = () => {
    setMenuAnchor(null)
    setSelectedDoc(null)
  }

  const handleUploadDocument = useCallback(async () => {
    if (!uploadFile) {
      toast.show('Please select a file to upload', 'warning')
      return
    }

    return execute({
      type: InteractionType.CREATE,
      label: 'Upload document',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'knowledge', fileName: uploadFile.name },
      action: async () => {
        setUploading(true)
        try {
          await uploadDocument(
            uploadFile,
            uploadTitle || uploadFile.name,
            selectedCollection?.id
          )

          toast.show('Document uploaded successfully!', 'success')
          setUploadDialogOpen(false)
          setUploadFile(null)
          setUploadTitle('')
          fetchDocuments()
        } catch (err) {
          toast.show(err.userMessage || err.message || 'Failed to upload document', 'error')
        } finally {
          setUploading(false)
        }
      },
    })
  }, [execute, fetchDocuments, selectedCollection, toast, uploadFile, uploadTitle])

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadFile(file)
      if (!uploadTitle) {
        setUploadTitle(file.name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const displayedDocs = view === 'favorites'
    ? documents.filter((d) => d.is_favorite)
    : searchQuery && searchResults.length > 0
    ? searchResults
    : documents

  return (
    <PageContainer>
      <Header>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FolderOpenIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Knowledge Library
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                <Typography variant="body2" color="text.secondary">
                  {stats?.total_documents || 0} documents in {stats?.total_collections || 0} collections
                </Typography>
                {connections.length > 0 && (
                  <Chip label={`${connections.length} connections`} size="small" variant="outlined" />
                )}
                {templates.length > 0 && (
                  <Chip label={`${templates.length} templates`} size="small" variant="outlined" />
                )}
              </Box>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <ImportFromMenu
              currentFeature={FeatureKey.KNOWLEDGE}
              onImport={async (output) => {
                const content = typeof output.data === 'string' ? output.data : JSON.stringify(output.data)
                const blob = new Blob([content], { type: 'text/plain' })
                const file = new File([blob], `${output.title || 'Imported'}.txt`, { type: 'text/plain' })
                await uploadDocument(file, output.title || 'Imported', selectedCollection?.id)
                fetchDocuments()
                toast.show(`"${output.title}" saved to library`, 'success')
              }}
            />
            <ActionButton
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => setUploadDialogOpen(true)}
            >
              Upload Document
            </ActionButton>
            <ActionButton
              startIcon={<GraphIcon />}
              onClick={handleBuildGraph}
              disabled={loading}
            >
              Knowledge Graph
            </ActionButton>
            <ActionButton
              startIcon={<FaqIcon />}
              onClick={handleGenerateFaq}
              disabled={loading}
            >
              Generate FAQ
            </ActionButton>
          </Box>
        </Box>
      </Header>

      <ContentArea>
        {/* Sidebar */}
        <Sidebar>
          <Box sx={{ p: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {/* Quick Filters */}
          <List dense sx={{ px: 1 }}>
            <CollectionItem
              button
              selected={view === 'all' && !selectedCollection}
              onClick={() => {
                setView('all')
                setSelectedCollection(null)
                fetchDocuments()
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <DocIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText primary="All Documents" />
            </CollectionItem>
            <CollectionItem
              button
              selected={view === 'favorites'}
              onClick={() => {
                setView('favorites')
                setSelectedCollection(null)
                fetchDocuments({ favoritesOnly: true })
              }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <StarIcon fontSize="small" sx={{ color: 'text.secondary' }} />
              </ListItemIcon>
              <ListItemText primary="Favorites" />
            </CollectionItem>
            <CollectionItem
              button
              selected={view === 'graph'}
              onClick={() => setView('graph')}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <GraphIcon fontSize="small" sx={{ color: 'text.secondary' }} />
              </ListItemIcon>
              <ListItemText
                primary="Knowledge Graph"
                secondary={knowledgeGraph ? `${knowledgeGraph.nodes?.length || 0} nodes` : null}
              />
            </CollectionItem>
            <CollectionItem
              button
              selected={view === 'faq'}
              onClick={() => setView('faq')}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>
                <FaqIcon fontSize="small" sx={{ color: 'text.secondary' }} />
              </ListItemIcon>
              <ListItemText
                primary="FAQ"
                secondary={faq.length ? `${faq.length} items` : null}
              />
            </CollectionItem>
          </List>

          <Divider sx={{ my: 1 }} />

          {/* Collections */}
          <Box sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              COLLECTIONS
            </Typography>
            <IconButton size="small" onClick={() => setCreateCollectionOpen(true)}>
              <AddIcon fontSize="small" />
            </IconButton>
          </Box>
          <List dense sx={{ px: 1, flex: 1, overflow: 'auto' }}>
            {collections.map((collection) => (
              <CollectionItem
                key={collection.id}
                button
                selected={selectedCollection?.id === collection.id}
                onClick={() => handleSelectCollection(collection)}
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <FolderIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                </ListItemIcon>
                <ListItemText
                  primary={collection.name}
                  secondary={`${collection.document_count || 0} docs`}
                />
              </CollectionItem>
            ))}
          </List>

          {/* Tags */}
          <Box sx={{ p: 2, borderTop: `1px solid ${alpha(theme.palette.divider, 0.1)}` }}>
            <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
              TAGS
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {tags.slice(0, 10).map((tag) => (
                <Chip
                  key={tag.id}
                  size="small"
                  label={tag.name}
                  variant="filled"
                  onClick={() => fetchDocuments({ tags: [tag.name] })}
                />
              ))}
            </Box>
          </Box>
        </Sidebar>

        {/* Main Panel */}
        <MainPanel>
          {loading && !documents.length && view !== 'graph' && view !== 'faq' ? (
            <Grid container spacing={2}>
              {Array.from({ length: 6 }).map((_, i) => (
                <Grid item xs={12} sm={6} md={4} key={i}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                      <Box sx={{ width: '70%', height: 20, bgcolor: alpha(theme.palette.text.primary, 0.08), borderRadius: 1 }} />
                      <Box sx={{ width: 24, height: 24, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: '50%' }} />
                    </Box>
                    <Box sx={{ width: '50%', height: 14, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1, mb: 1.5 }} />
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Box sx={{ width: 48, height: 20, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1 }} />
                      <Box sx={{ width: 56, height: 20, bgcolor: alpha(theme.palette.text.primary, 0.05), borderRadius: 1 }} />
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : view === 'graph' ? (
            /* Knowledge Graph View */
            knowledgeGraph ? (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Knowledge Graph
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {knowledgeGraph.nodes?.length || 0} nodes, {knowledgeGraph.edges?.length || 0} relationships
                    </Typography>
                  </Box>
                  <ActionButton
                    startIcon={<GraphIcon />}
                    onClick={handleBuildGraph}
                    disabled={loading}
                  >
                    Rebuild
                  </ActionButton>
                </Box>

                {/* Nodes */}
                <Typography variant="overline" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                  Entities
                </Typography>
                <Grid container spacing={1.5} sx={{ mb: 3 }}>
                  {knowledgeGraph.nodes?.map((node) => (
                    <Grid item xs={12} sm={6} md={4} key={node.id}>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 2,
                          borderRadius: 1,
                          transition: 'all 0.15s cubic-bezier(0.22, 1, 0.36, 1)',
                          '&:hover': { borderColor: 'text.secondary', transform: 'translateY(-1px)' },
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Chip
                            size="small"
                            label={node.type}
                            color={node.type === 'document' ? 'primary' : node.type === 'entity' ? 'secondary' : 'default'}
                            variant="outlined"
                          />
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {node.label}
                        </Typography>
                        {node.properties?.description && (
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                            {node.properties.description}
                          </Typography>
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>

                {/* Edges */}
                {knowledgeGraph.edges?.length > 0 && (
                  <>
                    <Typography variant="overline" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                      Relationships
                    </Typography>
                    <Paper variant="outlined" sx={{ borderRadius: 1 }}>
                      <List dense>
                        {knowledgeGraph.edges.map((edge, idx) => {
                          const sourceNode = knowledgeGraph.nodes?.find((n) => n.id === edge.source)
                          const targetNode = knowledgeGraph.nodes?.find((n) => n.id === edge.target)
                          return (
                            <ListItem key={idx} divider={idx < knowledgeGraph.edges.length - 1}>
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                      {sourceNode?.label || edge.source}
                                    </Typography>
                                    <Chip size="small" label={edge.type} variant="outlined" />
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                      {targetNode?.label || edge.target}
                                    </Typography>
                                  </Box>
                                }
                              />
                            </ListItem>
                          )
                        })}
                      </List>
                    </Paper>
                  </>
                )}
              </Box>
            ) : (
              <Box
                sx={{
                  height: '50vh',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <GraphIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No knowledge graph yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
                  Build a knowledge graph to visualize relationships between your documents, entities, and concepts.
                </Typography>
                <ActionButton
                  variant="contained"
                  size="large"
                  startIcon={<GraphIcon />}
                  onClick={handleBuildGraph}
                  disabled={loading || !documents.length}
                >
                  Build Knowledge Graph
                </ActionButton>
              </Box>
            )
          ) : view === 'faq' ? (
            /* FAQ View */
            faq.length > 0 ? (
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Frequently Asked Questions
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {faq.length} question{faq.length !== 1 ? 's' : ''} generated from your documents
                    </Typography>
                  </Box>
                  <ActionButton
                    startIcon={<FaqIcon />}
                    onClick={handleGenerateFaq}
                    disabled={loading}
                  >
                    Regenerate
                  </ActionButton>
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {faq.map((item, idx) => (
                    <Paper
                      key={idx}
                      variant="outlined"
                      sx={{ p: 2.5, borderRadius: 1 }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                        <FaqIcon sx={{ color: 'text.secondary', fontSize: 20, mt: 0.25, flexShrink: 0 }} />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1" sx={{ fontWeight: 600, mb: 1 }}>
                            {item.question}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                            {item.answer}
                          </Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1.5 }}>
                            {item.category && (
                              <Chip size="small" label={item.category} variant="outlined" />
                            )}
                            {item.confidence != null && (
                              <Chip
                                size="small"
                                label={`${Math.round(item.confidence * 100)}% confidence`}
                                variant="outlined"
                                color={item.confidence >= 0.8 ? 'success' : item.confidence >= 0.5 ? 'warning' : 'default'}
                              />
                            )}
                          </Box>
                        </Box>
                      </Box>
                    </Paper>
                  ))}
                </Box>
              </Box>
            ) : (
              <Box
                sx={{
                  height: '50vh',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <FaqIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No FAQ generated yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
                  Generate FAQ from your documents to surface the most important questions and answers.
                </Typography>
                <ActionButton
                  variant="contained"
                  size="large"
                  startIcon={<FaqIcon />}
                  onClick={handleGenerateFaq}
                  disabled={loading || !documents.length}
                >
                  Generate FAQ
                </ActionButton>
              </Box>
            )
          ) : (
            /* Documents View (default) */
            <>
              <Grid container spacing={2}>
                {displayedDocs.map((doc) => (
                  <Grid item xs={12} sm={6} md={4} key={doc.id}>
                    <DocumentCard>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600 }} noWrap>
                              {doc.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                              {doc.file_type?.toUpperCase()} - {new Date(doc.updated_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                          <IconButton
                            size="small"
                            onClick={() => handleToggleFavorite(doc.id)}
                          >
                            {doc.is_favorite ? <StarIcon sx={{ color: 'text.secondary' }} /> : <StarBorderIcon />}
                          </IconButton>
                        </Box>
                        {doc.tags?.length > 0 && (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                            {doc.tags.slice(0, 3).map((tag) => (
                              <Chip key={tag} size="small" label={tag} variant="outlined" />
                            ))}
                          </Box>
                        )}
                      </CardContent>
                      <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
                        <IconButton size="small" onClick={(e) => handleMenuOpen(e, doc)}>
                          <MoreIcon fontSize="small" />
                        </IconButton>
                      </CardActions>
                    </DocumentCard>
                  </Grid>
                ))}
              </Grid>

              {displayedDocs.length === 0 && !loading && (
                <Box
                  sx={{
                    height: '50vh',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <FolderOpenIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No documents found
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center', maxWidth: 400 }}>
                    Upload your first document to start building your knowledge base.
                    We support PDF, Word, Text, and Markdown files.
                  </Typography>
                  <ActionButton
                    variant="contained"
                    size="large"
                    startIcon={<UploadIcon />}
                    onClick={() => setUploadDialogOpen(true)}
                  >
                    Upload Your First Document
                  </ActionButton>
                </Box>
              )}
            </>
          )}
        </MainPanel>
      </ContentArea>

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { handleAutoTag(selectedDoc?.id); handleMenuClose(); }}>
          <ListItemIcon><AIIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Auto-tag</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { handleFindRelated(selectedDoc?.id); handleMenuClose(); }}>
          <ListItemIcon><SearchIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Find Related</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => { handleDeleteDocument(selectedDoc?.id); handleMenuClose(); }}>
          <ListItemIcon><DeleteIcon fontSize="small" sx={{ color: 'text.secondary' }} /></ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create Collection Dialog */}
      <Dialog open={createCollectionOpen} onClose={() => setCreateCollectionOpen(false)}>
        <DialogTitle>Create Collection</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Collection Name"
            value={newCollectionName}
            onChange={(e) => setNewCollectionName(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateCollectionOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateCollection}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Upload Document Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => !uploading && setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Upload a document to add it to your knowledge library. Supported formats: PDF, DOCX, TXT, MD, HTML
          </Typography>

          <UploadDropzone
            onClick={() => document.getElementById('document-upload-input')?.click()}
            sx={{ mb: 3 }}
          >
            <input
              id="document-upload-input"
              type="file"
              accept=".pdf,.docx,.doc,.txt,.md,.html"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <UploadIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
            {uploadFile ? (
              <>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  {uploadFile.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {(uploadFile.size / 1024 / 1024).toFixed(2)} MB - Click to change
                </Typography>
              </>
            ) : (
              <>
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Click to select a file
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or drag and drop here
                </Typography>
              </>
            )}
          </UploadDropzone>

          <TextField
            fullWidth
            label="Document Title"
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            placeholder="Enter a title for this document"
            sx={{ mb: 2 }}
          />

          {selectedCollection && (
            <Alert severity="info">
              This document will be added to the "{selectedCollection.name}" collection.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleUploadDocument}
            disabled={!uploadFile || uploading}
            startIcon={uploading ? <CircularProgress size={16} /> : <UploadIcon />}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}
    </PageContainer>
  )
}
