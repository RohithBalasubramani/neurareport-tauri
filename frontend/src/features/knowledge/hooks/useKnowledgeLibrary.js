/**
 * Custom hook: all state, effects, and handlers for Knowledge Library.
 */
import { useState, useEffect, useCallback } from 'react'
import useKnowledgeStore from '@/stores/knowledgeStore'
import useSharedData from '@/hooks/useSharedData'
import useIncomingTransfer from '@/hooks/useIncomingTransfer'
import { TransferAction, FeatureKey } from '@/utils/crossPageTypes'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'
import { uploadDocument } from '@/api/knowledge'

export function useKnowledgeLibrary() {
  const toast = useToast()
  const { execute } = useInteraction()
  const { connections, templates } = useSharedData()

  const {
    documents, collections, tags, currentDocument, currentCollection,
    searchResults, relatedDocuments, knowledgeGraph, faq, stats,
    totalDocuments, loading, searching, error,
    fetchDocuments, fetchCollections, fetchTags, createCollection,
    deleteDocument, toggleFavorite, searchDocuments,
    autoTag, findRelated, buildKnowledgeGraph, generateFaq,
    fetchStats, reset,
  } = useKnowledgeStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCollection, setSelectedCollection] = useState(null)
  const [view, setView] = useState('all')
  const [createCollectionOpen, setCreateCollectionOpen] = useState(false)
  const [newCollectionName, setNewCollectionName] = useState('')
  const [menuAnchor, setMenuAnchor] = useState(null)
  const [selectedDoc, setSelectedDoc] = useState(null)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploading, setUploading] = useState(false)

  useIncomingTransfer(FeatureKey.KNOWLEDGE, {
    [TransferAction.SAVE_TO]: async (payload) => {
      const content = typeof payload.content === 'string' ? payload.content : JSON.stringify(payload.content)
      const blob = new Blob([content], { type: 'text/plain' })
      const file = new File([blob], `${payload.title || 'Imported'}.txt`, { type: 'text/plain' })
      await uploadDocument(file, payload.title || 'Imported Document', selectedCollection?.id)
      fetchDocuments()
    },
  })

  useEffect(() => {
    fetchDocuments()
    fetchCollections()
    fetchTags()
    fetchStats()
    return () => reset()
  }, [fetchCollections, fetchDocuments, fetchStats, fetchTags, reset])

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) { fetchDocuments(); return }
    return execute({
      type: InteractionType.EXECUTE, label: 'Search library',
      reversibility: Reversibility.FULLY_REVERSIBLE, suppressSuccessToast: true,
      intent: { source: 'knowledge', query: searchQuery },
      action: () => searchDocuments(searchQuery),
    })
  }, [execute, fetchDocuments, searchDocuments, searchQuery])

  const handleSelectCollection = useCallback((collection) => {
    setSelectedCollection(collection)
    if (collection) fetchDocuments({ collectionId: collection.id })
    else fetchDocuments()
  }, [fetchDocuments])

  const handleToggleFavorite = useCallback(async (docId) => {
    return execute({
      type: InteractionType.UPDATE, label: 'Toggle favorite',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'knowledge', documentId: docId },
      action: () => toggleFavorite(docId),
    })
  }, [execute, toggleFavorite])

  const handleDeleteDocument = useCallback(async (docId) => {
    return execute({
      type: InteractionType.DELETE, label: 'Delete document',
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
      type: InteractionType.UPDATE, label: 'Auto-tag document',
      reversibility: Reversibility.SYSTEM_MANAGED, blocksNavigation: true,
      intent: { source: 'knowledge', documentId: docId },
      action: async () => {
        await autoTag(docId)
        toast.show('Tags generated', 'success')
      },
    })
  }, [autoTag, execute, toast])

  const handleFindRelated = useCallback(async (docId) => {
    return execute({
      type: InteractionType.EXECUTE, label: 'Find related documents',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'knowledge', documentId: docId },
      action: () => findRelated(docId),
    })
  }, [execute, findRelated])

  const handleBuildGraph = useCallback(async () => {
    const documentIds = documents.map((doc) => doc?.id).filter(Boolean)
    return execute({
      type: InteractionType.EXECUTE, label: 'Build knowledge graph',
      reversibility: Reversibility.FULLY_REVERSIBLE, blocksNavigation: true,
      intent: { source: 'knowledge' },
      action: async () => {
        await buildKnowledgeGraph({ collectionId: selectedCollection?.id, documentIds })
        setView('graph')
        toast.show('Knowledge graph built', 'success')
      },
    })
  }, [buildKnowledgeGraph, documents, execute, selectedCollection?.id, toast])

  const handleGenerateFaq = useCallback(async () => {
    const documentIds = documents.map((doc) => doc?.id).filter(Boolean)
    if (!documentIds.length) {
      toast.show('Upload at least one document before generating FAQ', 'warning')
      return null
    }
    return execute({
      type: InteractionType.EXECUTE, label: 'Generate FAQ',
      reversibility: Reversibility.FULLY_REVERSIBLE, blocksNavigation: true,
      intent: { source: 'knowledge' },
      action: async () => {
        const response = await generateFaq({
          collectionId: selectedCollection?.id, documentIds, background: false,
        })
        if (response?.status === 'queued') toast.show('FAQ generation queued', 'info')
        else { setView('faq'); toast.show('FAQ generated', 'success') }
      },
    })
  }, [documents, execute, generateFaq, selectedCollection?.id, toast])

  const handleCreateCollection = useCallback(async () => {
    if (!newCollectionName.trim()) return
    return execute({
      type: InteractionType.CREATE, label: 'Create collection',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'knowledge', name: newCollectionName },
      action: async () => {
        await createCollection({ name: newCollectionName })
        toast.show('Collection created', 'success')
        setNewCollectionName(''); setCreateCollectionOpen(false)
      },
    })
  }, [createCollection, execute, newCollectionName, toast])

  const handleMenuOpen = (event, doc) => {
    setMenuAnchor(event.currentTarget); setSelectedDoc(doc)
  }
  const handleMenuClose = () => {
    setMenuAnchor(null); setSelectedDoc(null)
  }

  const handleUploadDocument = useCallback(async () => {
    if (!uploadFile) { toast.show('Please select a file to upload', 'warning'); return }
    return execute({
      type: InteractionType.CREATE, label: 'Upload document',
      reversibility: Reversibility.SYSTEM_MANAGED, blocksNavigation: true,
      intent: { source: 'knowledge', fileName: uploadFile.name },
      action: async () => {
        setUploading(true)
        try {
          await uploadDocument(uploadFile, uploadTitle || uploadFile.name, selectedCollection?.id)
          toast.show('Document uploaded successfully!', 'success')
          setUploadDialogOpen(false); setUploadFile(null); setUploadTitle('')
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
      if (!uploadTitle) setUploadTitle(file.name.replace(/\.[^/.]+$/, ''))
    }
  }

  const handleImport = useCallback(async (output) => {
    const content = typeof output.data === 'string' ? output.data : JSON.stringify(output.data)
    const blob = new Blob([content], { type: 'text/plain' })
    const file = new File([blob], `${output.title || 'Imported'}.txt`, { type: 'text/plain' })
    await uploadDocument(file, output.title || 'Imported', selectedCollection?.id)
    fetchDocuments()
    toast.show(`"${output.title}" saved to library`, 'success')
  }, [fetchDocuments, selectedCollection, toast])

  const displayedDocs = view === 'favorites'
    ? documents.filter((d) => d.is_favorite)
    : searchQuery && searchResults.length > 0
    ? searchResults
    : documents

  return {
    // Store state
    documents, collections, tags, knowledgeGraph, faq, stats,
    loading, searching, error, connections, templates,
    // Local state
    searchQuery, setSearchQuery, selectedCollection,
    view, setView, createCollectionOpen, setCreateCollectionOpen,
    newCollectionName, setNewCollectionName,
    menuAnchor, selectedDoc,
    uploadDialogOpen, setUploadDialogOpen,
    uploadFile, uploadTitle, setUploadTitle, uploading,
    displayedDocs,
    // Handlers
    handleSearch, handleSelectCollection, handleToggleFavorite,
    handleDeleteDocument, handleAutoTag, handleFindRelated,
    handleBuildGraph, handleGenerateFaq, handleCreateCollection,
    handleMenuOpen, handleMenuClose,
    handleUploadDocument, handleFileSelect, handleImport,
    fetchDocuments,
  }
}
