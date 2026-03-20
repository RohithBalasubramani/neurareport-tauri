/**
 * Custom hook for Ingestion Page state and actions.
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import useIngestionStore from '@/stores/ingestionStore'
import useSharedData from '@/hooks/useSharedData'
import { useToast } from '@/components/ToastProvider'
import { useInteraction, InteractionType, Reversibility } from '@/components/ux/governance'

export function useIngestionPage() {
  const toast = useToast()
  const { execute } = useInteraction()
  const fileInputRef = useRef(null)
  const { connections, activeConnectionId } = useSharedData()
  const {
    uploads,
    watchers,
    transcriptionJobs,
    imapAccounts,
    uploadProgress,
    loading,
    uploading,
    error,
    uploadFile,
    uploadBulk,
    uploadZip,
    importFromUrl,
    clipUrl,
    createWatcher,
    fetchWatchers,
    startWatcher,
    stopWatcher,
    deleteWatcher,
    transcribeFile,
    connectImapAccount,
    fetchImapAccounts,
    syncImapAccount,
    reset,
  } = useIngestionStore()

  const [activeMethod, setActiveMethod] = useState('upload')
  const [isDragging, setIsDragging] = useState(false)
  const [urlInput, setUrlInput] = useState('')
  const [watcherPath, setWatcherPath] = useState('')
  const [createWatcherOpen, setCreateWatcherOpen] = useState(false)
  const [selectedConnectionId, setSelectedConnectionId] = useState(activeConnectionId || '')

  useEffect(() => {
    fetchWatchers()
    fetchImapAccounts()
    return () => reset()
  }, [fetchImapAccounts, fetchWatchers, reset])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e) => {
    e.preventDefault()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length === 0) return

    return execute({
      type: InteractionType.CREATE,
      label: `Upload ${files.length} file(s)`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', fileCount: files.length },
      action: async () => {
        if (files.length === 1) {
          await uploadFile(files[0])
        } else {
          await uploadBulk(files)
        }
        toast.show(`${files.length} file(s) uploaded`, 'success')
      },
    })
  }, [execute, toast, uploadBulk, uploadFile])

  const handleFileSelect = useCallback(async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    return execute({
      type: InteractionType.CREATE,
      label: `Upload ${files.length} file(s)`,
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', fileCount: files.length },
      action: async () => {
        if (files.length === 1) {
          const isZip = files[0].name.endsWith('.zip')
          if (isZip) {
            await uploadZip(files[0])
          } else {
            await uploadFile(files[0])
          }
        } else {
          await uploadBulk(files)
        }
        toast.show(`${files.length} file(s) uploaded`, 'success')
      },
    })
  }, [execute, toast, uploadBulk, uploadFile, uploadZip])

  const handleUrlImport = useCallback(async () => {
    if (!urlInput.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Import from URL',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', url: urlInput },
      action: async () => {
        await importFromUrl(urlInput)
        toast.show('URL imported', 'success')
        setUrlInput('')
      },
    })
  }, [execute, importFromUrl, toast, urlInput])

  const handleClipUrl = useCallback(async () => {
    if (!urlInput.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Clip web page',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', url: urlInput },
      action: async () => {
        await clipUrl(urlInput)
        toast.show('Page clipped', 'success')
        setUrlInput('')
      },
    })
  }, [clipUrl, execute, toast, urlInput])

  const handleCreateWatcher = useCallback(async () => {
    if (!watcherPath.trim()) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Create folder watcher',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'ingestion', path: watcherPath },
      action: async () => {
        await createWatcher(watcherPath)
        toast.show('Watcher created', 'success')
        setWatcherPath('')
        setCreateWatcherOpen(false)
      },
    })
  }, [createWatcher, execute, toast, watcherPath])

  const handleToggleWatcher = useCallback(async (watcher) => {
    const isRunning = watcher.status === 'running'
    return execute({
      type: InteractionType.UPDATE,
      label: isRunning ? 'Stop watcher' : 'Start watcher',
      reversibility: Reversibility.FULLY_REVERSIBLE,
      intent: { source: 'ingestion', watcherId: watcher.id },
      action: async () => {
        if (isRunning) {
          await stopWatcher(watcher.id)
          toast.show('Watcher stopped', 'info')
        } else {
          await startWatcher(watcher.id)
          toast.show('Watcher started', 'success')
        }
      },
    })
  }, [execute, startWatcher, stopWatcher, toast])

  const handleDeleteWatcher = useCallback(async (watcherId) => {
    return execute({
      type: InteractionType.DELETE,
      label: 'Delete watcher',
      reversibility: Reversibility.SYSTEM_MANAGED,
      intent: { source: 'ingestion', watcherId },
      action: async () => {
        await deleteWatcher(watcherId)
        toast.show('Watcher deleted', 'success')
      },
    })
  }, [deleteWatcher, execute, toast])

  const handleTranscribe = useCallback(async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    return execute({
      type: InteractionType.CREATE,
      label: 'Transcribe file',
      reversibility: Reversibility.SYSTEM_MANAGED,
      blocksNavigation: true,
      intent: { source: 'ingestion', filename: file.name },
      action: async () => {
        await transcribeFile(file)
        toast.show('Transcription started', 'success')
      },
    })
  }, [execute, toast, transcribeFile])

  return {
    // Store state
    uploads,
    watchers,
    transcriptionJobs,
    uploadProgress,
    loading,
    error,
    // Refs
    fileInputRef,
    // Local state
    activeMethod,
    setActiveMethod,
    isDragging,
    urlInput,
    setUrlInput,
    watcherPath,
    setWatcherPath,
    createWatcherOpen,
    setCreateWatcherOpen,
    selectedConnectionId,
    setSelectedConnectionId,
    // Handlers
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    handleUrlImport,
    handleClipUrl,
    handleCreateWatcher,
    handleToggleWatcher,
    handleDeleteWatcher,
    handleTranscribe,
  }
}
